#!/usr/bin/env python3
"""Render a GitHub contribution grid as a static SVG, self-hosted, no third-party runtime dependency.
Usage: python scripts/gen_contrib_svg.py <github_user> <output_path>
"""
import sys, re, os, datetime, urllib.request

def fetch(user):
    url = f"https://github.com/users/{user}/contributions"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")

def parse(html):
    days = re.findall(r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*data-level="(\d)"', html)
    if not days:
        alt = re.findall(r'data-level="(\d)"[^>]*data-date="(\d{4}-\d{2}-\d{2})"', html)
        days = [(d, l) for l, d in alt]
    return {d: int(l) for d, l in days}

def build_svg(levels):
    if not levels:
        raise SystemExit("No contribution data parsed.")
    palette = ['#EBEDF0', '#9BD9BE', '#5FBF95', '#2E9C6F', '#1E7A5A']
    dates = sorted(levels)
    start = datetime.date.fromisoformat(dates[0])
    end = datetime.date.fromisoformat(dates[-1])
    start -= datetime.timedelta(days=(start.weekday() + 1) % 7)  # back to Sunday
    cell, gap, pad = 11, 3, 4
    cols, cur = [], start
    while cur <= end:
        col = []
        for _ in range(7):
            col.append(levels.get(cur.isoformat(), 0))
            cur += datetime.timedelta(days=1)
        cols.append(col)
    W = pad * 2 + len(cols) * (cell + gap) - gap
    H = pad * 2 + 7 * (cell + gap) - gap
    rects = []
    for ci, col in enumerate(cols):
        for ri, lv in enumerate(col):
            x = pad + ci * (cell + gap)
            y = pad + ri * (cell + gap)
            rects.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" fill="{palette[lv]}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'width="{W}" height="{H}" role="img" '
            f'aria-label="GitHub contribution graph">\n' + "".join(rects) + "\n</svg>\n")

if __name__ == "__main__":
    user = sys.argv[1] if len(sys.argv) > 1 else "yousufagha"
    out = sys.argv[2] if len(sys.argv) > 2 else "public/github-contribution.svg"
    svg = build_svg(parse(fetch(user)))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write(svg)
    print(f"Wrote {out} ({len(svg)} bytes)")
