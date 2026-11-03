#!/usr/bin/env python3
"""Validate local links, referenced fragments and approved external link destinations."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

root = (Path(__file__).resolve().parents[1] / 'dist').resolve()


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.ids.add(a['id'])
        if tag == 'a' and a.get('href'):
            self.links.append(a['href'])
        elif (tag in ('img', 'script') or (tag == 'link' and a.get('rel') in ('stylesheet', 'icon'))) and a.get('src', a.get('href')):
            self.links.append(a.get('src', a.get('href')))


pages = {}
for file in root.rglob('*.html'):
    p = Page()
    p.feed(file.read_text(encoding='utf-8'))
    pages[file.resolve()] = p

errors = []
for file, page in pages.items():
    for link in page.links:
        parsed = urlsplit(link)
        if parsed.scheme or parsed.netloc:
            if link not in ('https://github.com/jsec82', 'https://www.linkedin.com/in/jeroenvanderweijden/'):
                errors.append(f'{file.name}: unapproved external link {link}')
            continue
        dest = (file.parent / unquote(parsed.path)).resolve() if parsed.path else file
        if not dest.is_relative_to(root):
            errors.append(f'{file.name}: path escapes website root: {link}')
            continue
        if not dest.is_file():
            errors.append(f'{file.name}: missing local target: {link}')
        elif parsed.fragment and dest in pages and unquote(parsed.fragment) not in pages[dest].ids:
            errors.append(f'{file.name}: missing anchor: {link}')
if errors:
    raise SystemExit('SITE LINK CHECK FAILED:\n - ' + '\n - '.join(errors))
print(f'Internal links, anchors and external URL allowlist passed for {len(pages)} pages.')
