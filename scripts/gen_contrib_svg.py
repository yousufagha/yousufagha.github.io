#!/usr/bin/env python3
"""Render a GitHub contribution grid as a static SVG, self-hosted, no third-party runtime dependency.

Renders a single calendar year (Jan-Dec), matching the year view on a GitHub
profile, rather than the rolling last-52-weeks the endpoint returns by default.

Usage: python scripts/gen_contrib_svg.py <github_user> <output_path> [year]
"""
import sys, re, os, datetime, urllib.request

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def fetch(user, year):
    # The same endpoint the profile uses. Passing an explicit range is what makes
    # it return a calendar year instead of the trailing 52 weeks.
    url = (f"https://github.com/users/{user}/contributions"
           f"?from={year}-01-01&to={year}-12-31")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def parse(html):
    days = re.findall(r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*data-level="(\d)"', html)
    if not days:
        alt = re.findall(r'data-level="(\d)"[^>]*data-date="(\d{4}-\d{2}-\d{2})"', html)
        days = [(d, l) for l, d in alt]
    return {d: int(l) for d, l in days}


def build_svg(levels, year):
    if not levels:
        raise SystemExit("No contribution data parsed.")

    palette = ['#EBEDF0', '#9BD9BE', '#5FBF95', '#2E9C6F', '#1E7A5A']
    cell, gap, pad = 11, 3, 4
    label_h = 15   # room for the month row above the grid

    # Fixed calendar-year window. Days before the first Sunday and after 31 Dec
    # still render as empty cells, exactly as GitHub's year view does — the empty
    # months are part of the honest picture, not something to crop out.
    jan1 = datetime.date(year, 1, 1)
    dec31 = datetime.date(year, 12, 31)
    start = jan1 - datetime.timedelta(days=(jan1.weekday() + 1) % 7)  # back to Sunday

    cols, cur = [], start
    while cur <= dec31:
        col = []
        for _ in range(7):
            col.append((cur, levels.get(cur.isoformat(), 0)))
            cur += datetime.timedelta(days=1)
        cols.append(col)

    W = pad * 2 + len(cols) * (cell + gap) - gap
    H = pad * 2 + label_h + 7 * (cell + gap) - gap

    # One label per month, positioned at the column holding that month's 1st.
    labels = []
    seen = set()
    for ci, col in enumerate(cols):
        for (d, _) in col:
            if d.year == year and d.month not in seen:
                seen.add(d.month)
                x = pad + ci * (cell + gap)
                labels.append(
                    f'<text x="{x}" y="{pad + 10}" font-family="ui-monospace, SFMono-Regular, monospace" '
                    f'font-size="9" letter-spacing="0.5" fill="#43514B">{MONTHS[d.month - 1]}</text>'
                )
                break

    rects = []
    for ci, col in enumerate(cols):
        for ri, (d, lv) in enumerate(col):
            # Trim the stubs either side of the year so the grid reads as 2026 only.
            if d.year != year:
                continue
            x = pad + ci * (cell + gap)
            y = pad + label_h + ri * (cell + gap)
            rects.append(
                f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" fill="{palette[lv]}"/>'
            )

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'width="{W}" height="{H}" role="img" '
            f'aria-label="GitHub contribution graph for {year}">\n'
            + "".join(labels) + "".join(rects) + "\n</svg>\n")


if __name__ == "__main__":
    user = sys.argv[1] if len(sys.argv) > 1 else "yousufagha"
    out = sys.argv[2] if len(sys.argv) > 2 else "public/github-contribution.svg"
    year = int(sys.argv[3]) if len(sys.argv) > 3 else datetime.date.today().year

    svg = build_svg(parse(fetch(user, year)), year)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write(svg)
    print(f"Wrote {out} for {year} ({len(svg)} bytes)")
