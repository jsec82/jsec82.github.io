# Jeroen · Security Engineering Portfolio

**Version:** V2.0 | **Deployment:** not yet published | **Public identity:** Jeroen

A responsive, evidence-led portfolio site based on the approved dark Microsoft Security dashboard design. It uses a high-impact hero visual, real case summaries and separate recruiter-oriented project pages. All content is intended for review before being committed to a public repository.

## What's included

- `index.html`: generated homepage with globe, focus areas, selected projects, lab timeline and contact.
- `projects/*.html`: curated project details with an Evidence Snapshot table.
- `content/projects.json`: the single human-reviewable list of published cases and statuses.
- `content/lab-log.json`: reviewed activity entries (not a live feed).
- `content/site.json`: name, professional tagline and approved public links.
- `assets/`: static, locally hosted visual assets, scripts and styling (no tracking services).
- `scripts/build.py`: rebuilds site from curated JSON, recreating `dist/` from scratch.
- `scripts/validate.py`: baseline sensitive-information and status validation.
- `scripts/test_links.py`: static links and anchors checks.
- `.github/workflows/validate.yml`: tests code changes; does not publish.
- `.github/workflows/deploy-pages.yml`: manual deployment to GitHub Pages, only after owner's decision.

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

Publishing is **manual**: update the reviewed content files, pass tests, obtain Jeroen's approval for the exact public payload **before committing it to a public repository**, and then use `Actions → Publish reviewed portfolio to GitHub Pages → Run workflow`.

The site **does not yet automatically sync** with the private repo. A private-source workflow that prepares publication proposals could be added later if approved; it must not publish private files or raw log data by itself. See [Publishing and updates](GITHUB-PAGES-SETUP.md).

© Jeroen. No license is granted for the source or artwork beyond normal viewing of the public website.
