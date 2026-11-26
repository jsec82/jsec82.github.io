# Controlled GitHub Pages deployment

Pages source: GitHub Actions. Environment github-pages permits main only; protected main requires PR and GitHub Actions validate, strict up-to-date branch, no bypass, no force push or deletion. Zero independent approvals is an explicit owner trade-off. Never change these controls to unblock a release without owner authorization.

## Release
Create a feature branch, review the diff, open PR, wait for validate success on current head, merge through GitHub. Push to main runs deploy-pages.yml. Build repeats metadata validation, deterministic build, links, security/privacy audit, release integrity and regression tests before uploading dist; deployment needs successful build. Only deploy job has pages:write and id-token:write. Verify Actions deployment conclusion and SHA, then HTTPS NL/EN pages and intended content. Manual fallback: Actions > Publish approved portfolio > Run workflow on main with exact current reviewed 40-character main SHA. Never publish an unreviewed SHA.

## Rollback
Identify last successful deployment SHA in Actions. Revert offending merge(s) on a new branch (for squash merges, git revert <merge-sha>); inspect diff, open PR and pass validate before merging. Automatic deployment rebuilds the reverted content. Verify successful deployment and live pages; do not reset main, force-push, or bypass checks. If reverting the automation itself, the original manual workflow returns; manually dispatch it with the new reviewed main SHA. If compromised, owner may disable deployment workflow or environment access while investigating. Failed build must not deploy; previous successful release normally remains served. Never place secrets or private evidence in this public repo.
