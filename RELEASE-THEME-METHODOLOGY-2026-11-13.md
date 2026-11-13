# Website V3.3 release and rollback record — 13 November 2026

**Scope:** the approved home layout, a dark/light theme toggle, localized learning/evidence methodology pages, navigation and test updates.

**Pre-release main commit:** `d1d1a23282d0a0a70d199ee0b6022204974afae6`

## Data and behavior boundaries

The new site does not ingest private Academy information. `content/projects.json`, `content/lab-log.json`, `content/focus-map.json` and certification/roadmap case data are not modified. Completed CTF practice, learner-observed Intune/Entra signals and planned HSE work remain distinguishable.

Two new public routes appear at `/methodology/` and `/en/methodology/`. The homepage no longer duplicates progress through a statistics strip or recent-progress block. The global dark/light toggle is next to the NL/EN switch and stores only theme preference in the visitor's browser.

## Security and accessibility

- Existing strict self-only Content Security Policy is preserved; no inline scripts, external fonts, network requests, analytics or trackers were introduced.
- Framework documentation links are allowlisted as individual HTTPS URLs, open with `noopener noreferrer` and are not runtime dependencies.
- Dark remains the safe default; the explicit light theme is persistent on current portfolio pages.
- Current supporting JavaScript functions (mobile menu, status/project filters and language switching) are preserved.
- Actual browser and assistive-technology accessibility audits, live TLS and response headers should still be verified independently. Passing tests is not a compliance certificate.

## Validation and rollback

CI runs `scripts/validate.py`, `scripts/build.py`, `scripts/test_links.py`, `scripts/security_audit.py`, `scripts/check_release.py` and all `tests/test_*.py`. Only deploy a green reviewed commit.

Rollback should be a **new revert commit or a new review PR** restoring the original `main` state from `d1d1a23282d0a0a70d199ee0b6022204974afae6`, not a force push. Check the automatically triggered Pages deployment after any rollback.
