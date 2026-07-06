# yousufagha.github.io

Portfolio site. Astro, deployed to GitHub Pages via Actions.

## Source of truth

Content lives in two JSON files and nowhere else:

- `src/data/projects.json`: the projects section. Update this alongside the weekly scoreboard. Statuses: `shipped`, `in-build`, `planned`. Only list `signals` (CI, DEMO, etc.) that are actually true.
- `src/data/profile.json`: hero, evidence ledger, experience, certifications, contact.

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

The workflow `.github/workflows/contribution-graph.yml` runs it daily (~01:17
Melbourne) and commits the SVG only when it changes. To refresh manually, run
the workflow from the Actions tab, or locally:

```
python scripts/gen_contrib_svg.py yousufagha public/github-contribution.svg
```
