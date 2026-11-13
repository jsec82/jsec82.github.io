# Weijden Security — Security Engineering Portfolio
**Live URL:** https://weijdensecurity.nl/  
**Version:** Dashboard V3, reviewed 9 November 2026

## Website
The homepage presents a clear learning journey, four Microsoft Core Focus Areas, exactly three public work categories (CTFs, Cases, Labs), and a certification/learning timeline. The original portrait is restricted to the header. All four approved public case records and their status/evidence limitations remain accessible using the original project URLs.

## Modular, reviewable source
- `site-src/pages/`: page-specific HTML templates (each `.tmpl` is the reviewed source of the corresponding public route). Layout and content can be adjusted without altering unrelated pages.
- `assets/dashboard.css`: isolated dashboard design tokens and responsive layout. Existing CSS remains available for legacy pages.
- `assets/dashboard.js`: progressive enhancement for menu, status, work-type, search, focus and roadmap filters. The public HTML content does not require JavaScript to display.
- `content/projects.json`: existing public case register; changes require evidence review and synchronized template edits.
- `content/focus-map.json`: public technology-to-case mapping. Private Academy content is never synchronized automatically.
- `scripts/build.py`: deterministic generator that copies reviewed page sources, assets and canonical metadata to `dist/`, retaining the old About, Skills and Activity URLs.
- `scripts/check_release.py`: prevents committed HTML/assets from drifting from the versioned build outputs.

## Security and data integrity
- CSP restricts resources to the origin. No external runtime libraries, analytics, accounts or contact forms.
- Custom domain, canonical metadata, sitemap, robots and GitHub Pages CNAME are preserved.
- SC-900 and TryHackMe Pre Security are learner-reported, MD-102 is an active exam target, SC-300 is planned, and AZ-104/SC-200 are selected learning rather than claimed credentials. No completion percentage is invented.
- Sanitized project outputs keep user-reported observations and unresolved Intune/ESP limitations explicit.
- Static automated security validation is not a penetration test or substitute for live HTTPS/header checks.


## Hands-on Engineering preview and security review — 13 November 2026

- The bilingual [Hands-on Security Engineering project section](./site-src/pages/projects/engineering/index.html.tmpl) is prepared **only on a review branch** with three planned flagships, dedicated NL/EN detail pages and homepage/Projects/Roadmap navigation.
- The [security and release assessment](./SECURITY-REVIEW-2026-11-13.md) records verified static controls, added SVG/CSS negative tests, repository bytecode cleanup and unresolved hosting requirements.
- **Do not merge this PR into main without separate publication authorization and a verified Pages publishing source.** History shows GitHub Pages builds following pushes to main. The manually triggered deployment workflow does not, by itself, prevent that.
- The current preview is **not a live feature**, and passing CI is not a claim of fully verified TLS/headers, accessibility or vulnerability-free operation.

## Local tests
```bash
python scripts/validate.py
python scripts/build.py
python scripts/test_links.py
python scripts/security_audit.py
python scripts/check_release.py
python -m unittest discover -s tests -p 'test_*.py' -v
```
Only publish reviewed content. The GitHub Pages branch source may still auto-deploy on a main push; enforce a manual deployment gate separately in repository settings if required.


## Bilingual V3.1 release (9 November 2026)

- Dutch homepage remains `/`, English at `/en/`. Nine user-facing routes per language with a contextual language switch.
- Canonical and hreflang URL pairs, strict CSP, image metadata preflight and source/build integrity checks must pass before publication.
- Project images reuse existing 1600x900 scalable SVG illustrations, including a dedicated FakeBank cover. This version includes three small, local SVG work-category icons.
- `scripts/build.py` builds from individual, reviewable templates in `site-src/pages/` and keeps the three legacy routes.
- Do not treat planned or user-reported outcomes as independently certified. Publication is manual; no data sync to private GitHub.
- Rollback branch: `rollback/dashboard-v3-before-bilingual-20261109`, reference commit `a4a1964442b0e1f6f815a7fb1fa264b3cd002df3`. To roll back, create a new commit restoring this snapshot instead of force-pushing main.
