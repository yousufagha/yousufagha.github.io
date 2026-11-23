# yousufagha.github.io

Portfolio site. Astro, deployed to GitHub Pages via Actions.

## Source of truth

Content lives in JSON and nowhere else:

- `src/data/profile.json`: intro, at-a-glance facts, the Dubai and Melbourne journey under the banner, the Now section, experience (start and end months; durations are calculated at build), publications, certifications, contact, and `hiddenRepos` (repos never named on the site).
- `src/data/projects.json`: the projects. Statuses: `shipped`, `in-build`, `planned`.
- `src/data/insights.json`: figures computed from the project datasets (ITW601 job ads, Beats reviews) that drive the explorer and the dot plot.

`/llms.txt` is generated from the same JSON at build time, so the profile for AI assistants never drifts from the page.

Edit the JSON, push to `main`, and the site rebuilds and deploys automatically.

## Local dev

```
npm install
npm run dev      # localhost:4321
npm run build    # output in dist/
```

## First-time deploy

1. Create a repo named `yousufagha.github.io` and push this code to `main`.
2. Repo Settings → Pages → Source: GitHub Actions.
3. The included workflow (`.github/workflows/deploy.yml`) handles build and deploy on every push.

## Contribution graph (self-hosted)

The GitHub activity graph is generated into `public/github-contribution.svg` by
`scripts/gen_contrib_svg.py`, which reads your live contribution data from
GitHub and renders a static SVG. No third-party runtime service.

The deploy workflow regenerates it on every build, including a daily scheduled
rebuild. Repos listed in `HIDDEN_REPOS` in `scripts/gen_github_stats.py` are never
shown. To refresh manually, run the workflow from the Actions tab, or locally:

```
python scripts/gen_contrib_svg.py yousufagha public/github-contribution.svg
```
