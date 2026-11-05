#!/usr/bin/env python3
"""Offline preflight for selected, public-safe portfolio content.

Not a replacement for source verification, image metadata inspection or human DLP.
"""
import datetime
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / 'content'


def load(name):
    return json.loads((CONTENT / name).read_text(encoding='utf-8'))


site, projects, log = load('site.json'), load('projects.json'), load('lab-log.json')
errors = []


def check_date(value, where):
    try:
        date = datetime.date.fromisoformat(value)
        if value != date.isoformat() or date > datetime.date.today():
            raise ValueError('non-canonical date or future date')
    except (ValueError, TypeError):
        errors.append(f'{where}: invalid/future ISO date')


def is_social_url(value, host, path_prefix):
    try:
        url = urlsplit(value)
        return (url.scheme == 'https' and url.hostname == host and
                url.username is None and url.password is None and url.port is None and
                url.path.rstrip('/').startswith(path_prefix) and
                not url.query and not url.fragment)
    except ValueError:
        return False


if site.get('display_name') != 'Jeroen':
    errors.append('site: display name must be Jeroen')
if site.get('role') != 'Security Engineer':
    errors.append('site: unexpected public role')
if not is_social_url(site.get('linkedin_url', ''), 'www.linkedin.com', '/in/jeroenvanderweijden'):
    errors.append('site: approved canonical LinkedIn profile required')
if site.get('github_profile') != 'https://github.com/jsec82':
    errors.append('site: GitHub link must be the public profile, not the private repository')
if site.get('public_email'):
    errors.append('site: public email address has not been approved')
if not isinstance(projects, list) or not projects:
    errors.append('projects: expected at least one reviewed project record')
if not isinstance(log, list) or not log:
    errors.append('lab log: expected reviewed events')
required = {'slug', 'title', 'eyebrow', 'status', 'date', 'discipline',
            'description', 'approach', 'validation', 'outcome', 'learned', 'tools', 'priority',
            'card_approach', 'card_validation', 'card_outcome', 'image', 'image_alt', 'visual_label'}
known_slugs = set()
priorities = set()
project_images = set()
for project in projects:
    slug = project.get('slug', '')
    if not isinstance(slug, str) or not re.fullmatch(r'[a-z0-9-]+', slug):
        errors.append(f'project slug invalid: {slug}')
    if slug in known_slugs:
        errors.append(f'project slug duplicate: {slug}')
    known_slugs.add(slug)
    missing = required - project.keys()
    if missing:
        errors.append(f'{slug}: missing keys {sorted(missing)}')
        continue
    if not isinstance(project['image'], str) or not re.fullmatch(r'[a-z0-9-]+\.svg', project['image']):
        errors.append(f'{slug}: image must be a local SVG filename')
    elif not (ROOT / 'assets' / project['image']).is_file():
        errors.append(f'{slug}: project image missing')
    else:
        project_images.add(project['image'])
    for field in ('image_alt', 'visual_label'):
        if not isinstance(project[field], str) or not project[field].strip():
            errors.append(f'{slug}: {field} missing')
    status = project['status']
    if status not in ('completed', 'in-progress', 'roadmap'):
        errors.append(f'{slug}: invalid status')
    if status == 'roadmap':
        if project['date'] is not None:
            errors.append(f'{slug}: roadmap item must have null date')
    else:
        check_date(project['date'], slug)
    if not isinstance(project['priority'], int) or project['priority'] in priorities:
        errors.append(f'{slug}: priority must be a unique integer')
    priorities.add(project['priority'])
    if not isinstance(project['tools'], list) or not project['tools'] or not all(isinstance(t, str) for t in project['tools']):
        errors.append(f'{slug}: tools must be a nonempty text array')
    for field in ('title', 'eyebrow', 'discipline', 'description', 'approach', 'validation', 'outcome', 'learned',
                  'card_approach', 'card_validation', 'card_outcome'):
        if not isinstance(project[field], str) or not project[field].strip():
            errors.append(f'{slug}: {field} is empty or not text')
        elif field.startswith('card_') and len(project[field]) > 185:
            errors.append(f'{slug}: {field} exceeds card summary limit')
for event in log:
    if event.get('project_slug') not in known_slugs:
        errors.append('lab log: unknown linked case')
    check_date(event.get('date'), 'lab log')
    for field in ('label', 'detail', 'category'):
        if not isinstance(event.get(field), str) or not event[field].strip():
            errors.append(f'lab log: missing {field}')
for name in project_images:
    try:
        root = ET.parse(ROOT / 'assets' / name).getroot()
        if root.tag != '{http://www.w3.org/2000/svg}svg' or not root.get('viewBox'):
            errors.append(f'{name}: invalid scalable SVG root')
    except (ET.ParseError, OSError):
        errors.append(f'{name}: SVG cannot be parsed')
# Block high-confidence leaks and URLs that would expose the private repo.
all_text = '\n'.join((CONTENT / n).read_text(encoding='utf-8') for n in
                     ('site.json', 'projects.json', 'lab-log.json'))
leaks = [
    (r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----', 'private key'),
    (r'(?i)(?:password|pwd|access[_ -]?token|client[_ -]?secret|api[_ -]?key)\s*[=:]\s*["\']?\S{6,}', 'possible credential'),
    (r'\b[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}\b', 'GUID or tenant identifier'),
    (r'\b[a-fA-F0-9]{32,}\b', 'long hex token or identifier'),
    (r'(?<![\w.@])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b', 'email address'),
    (r'\b(?:10|127|192\.168|172\.(?:1[6-9]|2[0-9]|3[01]))\.\d{1,3}\.\d{1,3}(?:\.\d{1,3})?\b', 'possible internal IP address'),
    (r'https?://github\.com/jsec82/(?!jsec82\.github\.io)[^\s"<>]+', 'unapproved GitHub repository URL'),
    (r'(?i)https?://', 'unexpected external URL'),
]
for pattern, label in leaks[:-1]:
    if re.search(pattern, all_text):
        errors.append(f'content: {label}; inspect the proposed public payload')
# Explicitly allow only the two approved external URLs in site.json.
for url in re.findall(r'https?://[^"\s]+', all_text):
    if url not in ('https://github.com/jsec82', 'https://www.linkedin.com/in/jeroenvanderweijden/'):
        errors.append(f'content: unapproved outbound URL {url[:70]}')
if errors:
    print('PUBLICATION PREFLIGHT FAILED:')
    for error in errors:
        print(' -', error)
    sys.exit(1)
print(f'Public content preflight passed: {len(projects)} reviewed cases, {len(log)} events.')
print('WARNING: human source/privacy/metadata review and explicit owner approval still required.')
