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
