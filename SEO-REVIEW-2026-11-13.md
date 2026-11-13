# Technical SEO and AI Search Readiness Review
**Date:** 13 November 2026  
**Repository:** jsec82/jsec82.github.io  
**Baseline:** `2f7fbbd126fc50b3039e5d93e949613f15a4ba33`  
**Change scope:** Search metadata, invisible public structured data, robots.txt crawler clarification, tests and documentation only. **No homepage redesign.**

## Why these changes

The website already serves human-readable HTML, public crawlable pages, an XML sitemap, canonical URLs, bilingual hreflang links and a strict Content Security Policy. However, home, Projects, Focus, Roadmap and Contact reused generic descriptions, while six separate HSE project-detail pages shared one non-specific description. This made it harder to distinguish their purpose in indexed snippets and summaries.

## Applied changes

1. Unique Dutch/English descriptions for home, Projects, Core Focus, Roadmap, Contact, and all six HSE detail pages. The home titles now explicitly reflect Microsoft Security Engineering and the core Identity/Endpoint theme.
2. `WebSite` schema.org microdata at the root homepage, naming the actual site **Weijden Security**. Uses HTML microdata, not JSON-LD JavaScript, to preserve the current strict CSP and existing security audit rules.
3. `ProfilePage` + `Person` schema.org microdata on the two public Contact pages, using only already-public identifiers and approved professional links. No tenant names, device IDs, IP addresses, personal email addresses or unpublished evidence.
4. Explicit `OAI-SearchBot` allowance in robots.txt. The prior `User-agent: * Allow: /` already allowed it; this addition clarifies search-discovery intent without changing other crawler policies.
5. Search regression tests ensure metadata/OG agreement, CSP, valid canonical and hreflang tags, 29 advertised public pages and data-integrity status.
6. Fixed historical README text that inaccurately described the previously published Engineering section as an unmerged preview.

## Not done (intentionally)

- No keyword stuffing, bulk AI-written articles, fabricated certifications/results, fake endorsements or artificial content dates.
- No `llms.txt` promise; Google's AI Search guidelines state there is no special AI file or schema required to appear in AI results.
- No sitemap `lastmod` values were fabricated; the repository currently lacks reliable per-page source modification timestamps for historic content.
- No automatic Search Console submissions, indexing requests, crawler telemetry/analytics, or code injected into private Academy content.
- No changes to theme, page layout, profile picture, project stages, roadmap sequence or deployment workflows.

## Verification and publication limits

- Automated preflight: `scripts/validate.py`, `scripts/build.py`, `scripts/test_links.py`, `scripts/security_audit.py`, `scripts/check_release.py`, and full unittest discovery.
- Search metadata and structured data are validated as local HTML invariants. Google's live indexing and Rich Results Test were not accessible with an authenticated Search Console session.
- Public site indexing, snippet selection, AI answer citations and ranking positions are *not guaranteed*. You can request the sitemap in Google Search Console and Bing Webmaster Tools after deployment.
- Live HTTPS/HTTP-response-header controls from the previous security review remain separate and still require an actual hosting audit.

## Follow-up without changing the site

1. Verify ownership of the exact domain in Google Search Console and Bing Webmaster Tools; submit `https://weijdensecurity.nl/sitemap.xml`, inspect important NL/EN URLs and evaluate crawl/index coverage.
2. Use Google's Rich Results Test / Schema Markup Validator on the live Contact and home pages, correcting any parsing or eligibility warnings.
3. Check live robots and CDN allowances for Googlebot, Bingbot and OAI-SearchBot, including actual HTTP status, IP restrictions, blocking, HTTPS and WAF behavior.
4. Continue adding genuinely verified, sanitized engineering evidence as projects are performed; consistent content provenance and technical explanations are more valuable than generative-search gimmicks.

**Official references:**
- Google Search AI SEO guidance: https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
- Google site name microdata: https://developers.google.com/search/docs/appearance/site-names
- Google ProfilePage microdata: https://developers.google.com/search/docs/appearance/structured-data/profile-page
- Sitemap guidance: https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap
- OpenAI crawler guidance: https://developers.openai.com/api/docs/bots
