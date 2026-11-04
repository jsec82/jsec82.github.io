# Jeroen · Security Engineering Portfolio

**Public website:** https://weijdensecurity.nl/ (verified GitHub Pages custom domain). GitHub Pages still uses the public repository `jsec82/jsec82.github.io`; keep the root `CNAME` file and generated `dist/CNAME` with `weijdensecurity.nl`.

**Version:** V2.2 | **Deployment:** GitHub Pages (public) | **Public identity:** Jeroen

A responsive, evidence-led portfolio site based on the approved dark Microsoft Security dashboard design. It uses a high-impact hero visual, real case summaries and separate recruiter-oriented project pages. All content is curated and reviewed before it is committed to this public repository.

## What's included

- `CNAME`: GitHub Pages domain mapping (`weijdensecurity.nl`); also generated into `dist/CNAME`.
- `index.html`: published homepage with globe, focus areas, selected projects, lab timeline and contact; generated from curated content.
- `projects/*.html`: curated project details with an Evidence Snapshot table.
- `content/projects.json`: the single human-reviewable list of published cases and statuses.
- `content/lab-log.json`: reviewed activity entries (not a live feed).
- `content/site.json`: name, professional tagline and approved public links.
- `assets/`: static, locally hosted visual assets, scripts and styling (no tracking services).
- `scripts/build.py`: rebuilds site from curated JSON, recreating `dist/` from scratch.
- `scripts/validate.py`: baseline sensitive-information and status validation.
- `scripts/test_links.py`: static links and anchors checks.
- `.github/workflows/validate.yml`: tests code changes; does not publish.
- `.github/workflows/deploy-pages.yml`: optional manual GitHub Actions deployment workflow if the Pages source is changed to GitHub Actions. The current Pages configuration uses branch publishing.

## Current, source-grounded cases

| Case | Status as of 3 Nov 2026 | What is proven |
|---|---|---|
| OhSINT | Completed, guided | 7/7 TryHackMe questions completed with support; XMP-exif metadata investigation; coach-supplied Wi-Fi answer independently unverified |
| Windows Autopilot and Intune enrollment | In progress | AzureAdJoined YES, DomainJoined NO, AzureAdPrt YES, Intune device managed by Microsoft Intune, all user-observed; ESP and effective policy outcomes pending |
| Identity & detection engineering | Planned | No implemented detection case yet |

**Do not present conceptual illustrations as evidence.** The globe and the three thumbnail graphics were adapted from the previously approved concept artwork. These are decorative marketing graphics, not screenshots of actual security consoles.

## Local build

Requires Python 3.10+ for the static build. No runtime framework, external fonts, cookies, network calls or telemetry.

```bash
python scripts/validate.py
python scripts/build.py
python scripts/test_links.py
python -m http.server 8080 --directory dist
```

Browse to `http://localhost:8080`.

Visual browser verification is documented separately in the private release audit. Browser tests were performed in memory because the authoring environment blocks local URL navigation; final live browser and accessibility testing is still required.

## Publication policy

The private source repository stays private. The public website uses a separate repository `jsec82/jsec82.github.io` and may receive only approved, sanitized content.

**Publishing is approval-gated:** prepare a sanitized change, run validation, obtain Jeroen's explicit approval for the exact public payload, and only then update this public repository. GitHub Pages currently publishes from `main` after an approved commit. Do not commit unapproved content, even in a draft branch, because this is a public repository.

After content changes, run `python scripts/validate.py`, `python scripts/build.py` and `python scripts/test_links.py`, then commit the reviewed `dist/` output at the repository root (`index.html`, `projects/`, `assets/`, `.nojekyll`, `CNAME`, `robots.txt`, `sitemap.xml`). Branch publishing deploys those static files automatically. The manual GitHub Actions deployment workflow is an alternative only after selecting `Settings → Pages → Build and deployment → Source → GitHub Actions`.

The site **does not yet automatically sync** with the private repo. A private-source workflow that prepares publication proposals could be added later if approved; it must not publish private files or raw log data by itself. No content or activity is pulled live from the private repository.

© Jeroen. No license is granted for the source or artwork beyond normal viewing of the public website.

## Website navigation

The site has dedicated recruiter-oriented routes for [Projects](https://weijdensecurity.nl/projects/), [Skills](https://weijdensecurity.nl/skills/), [About](https://weijdensecurity.nl/about/) and [Lab log](https://weijdensecurity.nl/activity/). A curated summary remains on the homepage. The build script generates these pages from reviewed public content; project-status filters are an optional client-side enhancement.

Only add public updates after owner approval; the source learning repository remains private.


## Security & Reliability V2.2

- Strict meta Content Security Policy with locally hosted scripts/assets only.
- Security/a11y-baseline lint, image metadata scan, negative unit tests, deterministic release integrity gate.
- Pinned GitHub Actions SHAs, least-privilege permissions, no persisted checkout credentials.
- To STOP automatic branch publishing, owner must change Settings → Pages → Source to GitHub Actions. Only then is manual workflow_dispatch the publication path; enter the reviewed main SHA.
- Owner should configure branch protection and required reviewers for the github-pages environment (where supported). Manual workflow inputs alone do not provide independent approval.
- Meta CSP cannot enforce frame-ancestors or HSTS; live header/TLS testing remains separate.

## V2.3 — Focus navigation, portrait and clearer illustrations

- Four existing Core Focus Areas cards link to /focus/?area=... to show only reviewed public cases for Intune, Entra, Defender or Sentinel.
- The existing Featured Projects cards, project content and completed/in-progress/planned status evidence remain unchanged.
- Three 1600×900 native vector SVG cover illustrations are used as decorative visual aids, never as claimed console screenshots or lab verification.
- Jeroen's supplied, metadata-stripped, 400×400 WebP portrait appears in the existing homepage About panel and the About page.
- The existing hero globe is slightly smaller on desktop; the text column is moderately wider.
- The V2.2 security and publication process stays in place. Only approved public case data appears on focus filters.
