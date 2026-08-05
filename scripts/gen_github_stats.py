#!/usr/bin/env python3
"""Fetch this year's GitHub contribution stats and write them as JSON for the build.

Usage: python scripts/gen_github_stats.py <github_user> <output_path>
Requires GITHUB_TOKEN in the environment (the GraphQL API rejects anonymous calls).

Deliberately stdlib-only, matching gen_contrib_svg.py — the site has no runtime
dependency on any third-party service beyond GitHub itself.
"""
import sys, os, json, datetime, urllib.request, urllib.error

API = "https://api.github.com/graphql"

# contributionsCollection accepts a window of at most one year, which is exactly
# what we want: 1 Jan of the current year through now.
QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      # The headline figure. This is the exact number GitHub renders above your
      # own contribution graph, so anyone clicking through can verify it. A
      # hand-rolled sum of the four type totals below drifts from it, because the
      # calendar buckets by day and counts some events differently.
      contributionCalendar { totalContributions }
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      commitContributionsByRepository(maxRepositories: 100) {
        repository { nameWithOwner url isPrivate }
        contributions { totalCount }
      }
    }
  }
}
"""


def fetch(user, token):
    now = datetime.datetime.now(datetime.timezone.utc)
    start = datetime.datetime(now.year, 1, 1, tzinfo=datetime.timezone.utc)
    payload = json.dumps({
        "query": QUERY,
        "variables": {
            "login": user,
            "from": start.isoformat(),
            "to": now.isoformat(),
        },
    }).encode()

    req = urllib.request.Request(
        API,
        data=payload,
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "yousufagha-portfolio-stats",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.loads(r.read().decode())

    # GraphQL returns HTTP 200 with an errors array, so this has to be checked
    # explicitly rather than relying on urlopen raising.
    if "errors" in body:
        raise SystemExit(f"GraphQL error: {body['errors']}")
    if not body.get("data", {}).get("user"):
        raise SystemExit(f"No such user: {user}")
    return body["data"]["user"]["contributionsCollection"], now.year


def shape(c, year):
    breakdown = {
        "commits": c["totalCommitContributions"],
        "pullRequests": c["totalPullRequestContributions"],
        "issues": c["totalIssueContributions"],
        "reviews": c["totalPullRequestReviewContributions"],
    }

    # Public repos only. A private repo would show a name a visitor can't open,
    # and an unverifiable number on a page whose whole claim is verifiability.
    repos = [
        {
            "name": r["repository"]["nameWithOwner"],
            "url": r["repository"]["url"],
            "commits": r["contributions"]["totalCount"],
        }
        for r in c["commitContributionsByRepository"]
        if not r["repository"]["isPrivate"]
    ]
    repos.sort(key=lambda r: r["commits"], reverse=True)

    return {
        "year": year,
        "generated": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        # Headline comes straight from GitHub's own calendar total, not from
        # summing `breakdown` — the two are close but not identical, and only the
        # calendar figure matches what a visitor sees on the profile page.
        "total": c["contributionCalendar"]["totalContributions"],
        "breakdown": breakdown,
        "topRepos": repos[:3],
        # Drives the "and N other repositories" line, mirroring how GitHub's own
        # activity overview phrases it.
        "repoCount": len(repos),
    }


if __name__ == "__main__":
    user = sys.argv[1] if len(sys.argv) > 1 else "yousufagha"
    out = sys.argv[2] if len(sys.argv) > 2 else "src/data/github-stats.json"

    # STATS_TOKEN first. The default Actions GITHUB_TOKEN is a repo-scoped
    # installation token: it returns the contribution calendar, but zeroes for
    # issue/PR/review contributions across the whole account. A classic PAT with
    # read:user returns the real breakdown.
    token = os.environ.get("STATS_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("No token set — the GraphQL API rejects anonymous requests.")

    data = shape(*fetch(user, token))

    b = data["breakdown"]
    if b["pullRequests"] + b["issues"] + b["reviews"] == 0 and b["commits"] > 0:
        print("WARNING: only commit contributions came back. This is what a "
              "repo-scoped GITHUB_TOKEN returns — set a STATS_TOKEN secret "
              "(classic PAT, read:user) to get the real breakdown.")

    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    print(f"Wrote {out}: {data['total']} contributions in {data['year']}, "
          f"top repo {data['topRepos'][0]['name'] if data['topRepos'] else 'n/a'}")
