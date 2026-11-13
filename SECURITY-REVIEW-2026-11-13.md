# Security & Release Review — Hands-on Security Engineering Preview

**Date:** 13 November 2026  
**Target:** public static portfolio repository and bilingual Hands-on Security Engineering preview  
**Scope:** repository source and generated build on the preview branch; existing public case data and branch deployment process  
**Baseline main commit:** `bb8029fe2f4cfaa668582e392b8f2fbec922753c`  
**Publication status:** **NOT APPROVED / NOT DEPLOYED**. Draft PR #4 remains open. No changes to main or live GitHub Pages were made as part of this review.

> **Assessment boundary:** A successful repository security preflight does **not** establish full compliance with OWASP, NCSC, WCAG, or any external standard, and is not an external penetration test. The current environment could not retrieve the live site over the public web or inspect TLS and HTTP response headers. Such controls are explicitly unverified, not marked compliant.

## 1. Scope and threat model

This is a statically generated, public-facing portfolio. It has no login, forms, client accounts, cookies, server API, analytics or third-party JavaScript at runtime. Main risks are:
- Unauthorized/mistaken content publication through GitHub Pages and unreviewed `main` updates.
- Exposure of personal identifiers, tenant/account/device data or private Academy evidence in public pages or static source assets.
- Unsafe active SVG, third-party scripts, browser DOM injection, malicious links or CSS asset references.
- Broken URLs, language-switch divergence, mismatched build output, misleading security/proficiency claims.
- Hosting configuration issues (TLS, custom domain verification and response headers) outside the HTML repository.

## 2. Evidence-based results

| Control / security requirement | Assessment | Evidence / limitation |
| --- | --- | --- |
| Correctly scoped public portfolio content | **PASS — static source** | Exactly three planned flagships HSE-01, HSE-02+05, HSE-11. Existing CTF/Case/Lab categories and historical evidence remain unchanged. All HSE cases marked planned; no fabricated outcome. |
| Bilingual navigation, internal anchors and sitemap | **PASS — automated** | All 29 pages generated, link and anchor checker successful, NL/EN direct counterpart test and sitemap/build-integrity checks passed. |
| HTML/DOM protections | **PASS — static checks** | Strict same-origin meta CSP, no inline event handlers/styles, no unapproved outbound resource or executable scripts; approved JS uses DOM textContent rather than unsafe HTML insertion. |
| Nested SVG and CSS asset handling | **PASS — newly hardened** | Security audit walks nested assets; rejects active SVG tags, XML DTD/entities, event handlers, external SVG references, malicious CSS imports/URLs. Negative tests for the new rules included. |
| Privacy and secret exposure | **PASS — rule-based preflight; human review still required** | Scans curated data, markup, image metadata and dangerous paths. Does not independently certify the absence of all private information, especially contextual identifiers or images. |
| Workflow supply chain | **PASS — code configuration** | GitHub Actions jobs use SHA-pinned actions and least-required `contents: read` permissions; checkout disables persisted credentials. Manual release workflow requires exact commit SHA, but is **not itself an effective deployment gate** while Pages still responds to pushes on main. |
| Source/generated release integrity | **PASS — automated** | Generated files, reviewed sources and committed output match; all 27 unit/regression tests passed in GitHub Actions run `43376593429`. |
| Python build artifact hygiene | **PASS — branch cleanup** | Four tracked `.pyc` cache files removed from the candidate branch and `.gitignore` introduced. No original cases, lab logs or progress records were deleted. |
| GitHub Pages publication source/gate | **NEEDS ACTION — release blocker** | GitHub Actions history shows `pages build and deployment` successful on repeated pushes to `main`. Current Pages Settings > Source is **not readable through this connector**. A `main` merge may publish automatically. |
| Live TLS, enforced HTTPS, DNS/domain ownership | **NOT VERIFIED** | No successful independent live HTTP/TLS connection from this environment. Check Pages Enforce HTTPS, valid certificate, domain verification and redirects in the hosting settings. |
| HTTP response headers and clickjacking defense | **NOT VERIFIED** | Meta-delivered CSP cannot enforce `frame-ancestors` (W3C CSP); this requires an HTTP header. Verify live HSTS, CSP/X-Frame-Options, X-Content-Type-Options, Referrer-Policy and Permissions-Policy at the hosting layer; do not assume GitHub Pages supports custom headers. |
| Real browser, accessibility, visual regressions | **PARTIAL** | Responsive CSS and links tested, accessible project-specific link names and non-gradient text fallback added; no independent complete screen-reader, keyboard, WCAG 2.2 AA or cross-browser audit. |

**CI result:** <https://github.com/jsec82/jsec82.github.io/actions/runs/43376593429> — 29 pages, 27 tests, link checks, security preflight, build-integrity check all successful.

## 3. Changes made after second review

1. Updated the existing security audit to recursively scan assets, including nested SVG icons.
2. Added SVG- and CSS-safety negative regression tests, plus explicit NL/EN counterpart and unique project link-name checks.
3. Improved accessibility of three visually similar project links (individual `aria-label`) and added a legible color fallback when text-gradient rendering is unavailable.
4. Removed generated Python bytecode from version control in the preview branch and introduced ignore rules.
5. Preserved the approved design, the previous site and private Academy progress. No production change, tenant access, telemetry ingestion or publishing workflow was initiated.

## 4. Release blockers and owner verification checklist

**Before any merge that can publish:**

- [ ] In repository **Settings → Pages → Build and deployment**, independently read the **Source**. If it is **Deploy from a branch → main**, every merge/push can publish even if the `workflow_dispatch` release workflow is present. Do **not** merge under the assumption that the workflow alone prevents deployment.
- [ ] Decide on deployment model. Prefer **GitHub Actions** as Pages publishing source with the existing manually triggered exact-SHA workflow; confirm no push-triggered deploy workflow remains, and protect the `github-pages` environment as appropriate.
- [ ] Review current `main` and the diff against the baseline SHA, require a green latest GitHub Actions validation, and preserve a documented rollback commit/tag.
- [ ] Complete the owner's content/visual/privacy review; then obtain **separate explicit owner approval** to publish/merge to the live website.
- [ ] Check live `https://weijdensecurity.nl/` and `https://weijdensecurity.nl/en/` in a normal browser, verify custom domain, enforce HTTPS, redirects, certificate and DNS ownership.
- [ ] Obtain the **actual HTTP response headers** from live site and document whether header-only controls such as `frame-ancestors`, HSTS and clickjacking defenses are provided by the hosting/CDN layer.
- [ ] Perform mobile + desktop browser review (keyboard focus order, 200% zoom, contrast, language switch, titles and readable status), plus a quick human DLP review.
- [ ] After separately authorized publication: verify the eight new routes, navigation from homepage and roadmap, HTTP status, cache, translated pages, and ability to restore the earlier main version.

Suggested read-only local checks for the site owner once network access is available:

```bash
curl -I --max-time 10 https://weijdensecurity.nl/
curl -I --max-time 10 https://weijdensecurity.nl/en/
curl -I --max-time 10 https://weijdensecurity.nl/projects/engineering/
curl -I --max-time 10 http://weijdensecurity.nl/
```

**Interpretation:** A `404` on the *new* engineering route is expected before publication; do not mistake it for a failed current live release.

## 5. Final audit disposition

**Repository preview:** **PASS WITH RESTRICTED SCOPE** — automated security and integrity checks green; no evidence of a high-impact application-layer defect found within this limited review.  

**Hosting and deployment safety:** **NOT CLEARED** — GitHub Pages source configuration, automatic publication gate, HTTPS security headers and live behavior require separate verification.  

**Publishing decision:** **HOLD**. Keep the draft PR unmerged and never infer publication approval from design acceptance or successful CI.
