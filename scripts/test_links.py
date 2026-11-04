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
# Every page must link to the dedicated navigation destinations, not just homepage anchors.
required_nav = {'index.html', 'projects/index.html', 'skills/index.html', 'about/index.html', 'activity/index.html'}
for name in required_nav:
    if not (root / name).is_file():
        errors.append(f'missing required navigation page: {name}')
for file, page in pages.items():
    destinations = set()
    for link in page.links:
        parsed = urlsplit(link)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        destinations.add((file.parent / unquote(parsed.path)).resolve())
    for path in required_nav:
        if (root / path).resolve() not in destinations:
            errors.append(f'{file.name}: missing navigation link to {path}')

# Custom-domain regression checks: prevent an old GitHub Pages host on future builds.
domain = 'https://weijdensecurity.nl'
for file in pages:
    source = file.read_text(encoding='utf-8')
    if 'https://jsec82.github.io/' in source:
        errors.append(f'{file.name}: old GitHub Pages URL in generated HTML')
    if f'<link rel="canonical" href="{domain}/' not in source:
        errors.append(f'{file.name}: custom-domain canonical link missing')
    if f'<meta property="og:url" content="{domain}/' not in source:
        errors.append(f'{file.name}: custom-domain Open Graph URL missing')
    if f'<meta property="og:image" content="{domain}/assets/hero-globe.webp"' not in source:
        errors.append(f'{file.name}: custom-domain Open Graph image missing')
cname = root / 'CNAME'
if not cname.is_file() or cname.read_text(encoding='utf-8').strip() != 'weijdensecurity.nl':
    errors.append('generated CNAME missing or incorrect')
robots = root / 'robots.txt'
if not robots.is_file() or 'Sitemap: https://weijdensecurity.nl/sitemap.xml' not in robots.read_text(encoding='utf-8'):
    errors.append('generated robots.txt points to the wrong sitemap')
sitemap = root / 'sitemap.xml'
if not sitemap.is_file():
    errors.append('generated sitemap.xml missing')
else:
    sitemap_text = sitemap.read_text(encoding='utf-8')
    if '<loc>https://weijdensecurity.nl/</loc>' not in sitemap_text or 'https://jsec82.github.io/' in sitemap_text:
        errors.append('generated sitemap.xml points to the wrong host')

# V2.3: all four homepage focus links must target the generated focus catalogue.
focus_page = root / 'focus' / 'index.html'
if not focus_page.is_file():
    errors.append('missing focus-area overview')
home_source = (root / 'index.html').read_text(encoding='utf-8')
for area in ('intune', 'entra', 'defender', 'sentinel'):
    if f'href="focus/index.html?area={area}"' not in home_source:
        errors.append(f'missing homepage focus link for {area}')

if errors:
    raise SystemExit('SITE LINK CHECK FAILED:\n - ' + '\n - '.join(errors))
print(f'Internal links, anchors and external URL allowlist passed for {len(pages)} pages.')
