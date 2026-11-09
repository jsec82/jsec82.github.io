#!/usr/bin/env python3
"""Fail CI when committed GitHub Pages files diverge from the generated dist/.

This prevents an HTML change from bypassing curated-source validation and
prevents a later build from silently changing the site from what was reviewed.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT/'dist'
GENERATED_DIRS = ('assets','projects','about','activity','skills','focus','roadmap','contact')


def check(root=ROOT):
    dist = root/'dist'
    if not dist.is_dir():
        return ['run python scripts/build.py before checking release integrity']
    problems = []
    artifacts = {p.relative_to(dist) for p in dist.rglob('*') if p.is_file()}
    for rel in sorted(artifacts):
        deployed = root/rel
        if not deployed.is_file():
            problems.append(f'missing committed deployment file: {rel}')
        elif (dist/rel).read_bytes() != deployed.read_bytes():
            problems.append(f'generated/deployed content differs: {rel}')
    # Detect old project pages or assets omitted by the current generator.
    for folder in GENERATED_DIRS:
        directory = root/folder
        if directory.exists():
            for deployed in directory.rglob('*'):
                if deployed.is_file() and deployed.relative_to(root) not in artifacts:
                    problems.append(f'unexpected stale deployment file: {deployed.relative_to(root)}')
    return problems


if __name__ == '__main__':
    errors = check()
    if errors:
        sys.exit('RELEASE INTEGRITY FAILED:\n - '+'\n - '.join(errors))
    print('Release integrity passed: committed public site matches the deterministic build.')
