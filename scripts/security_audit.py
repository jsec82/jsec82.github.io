#!/usr/bin/env python3
"""Offline security and accessibility-baseline audit of generated public Pages.

Intentionally dependency-free. This is not a pentest, TLS/header audit or a
replacement for review of original lab evidence before public publication.
"""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
DOMAIN = 'https://weijdensecurity.nl'
ALLOWED_OUTBOUND = {
    'https://github.com/jsec82',
    'https://www.linkedin.com/in/jeroenvanderweijden/',
}
CSP = (
    "default-src 'none'; script-src 'self'; style-src 'self'; "
    "img-src 'self'; font-src 'self'; connect-src 'none'; "
    "object-src 'none'; base-uri 'none'; form-action 'none'; frame-src 'none'"
)
# Match actual credentials, not legitimate labels such as "password protection".
PRIVATE_PATTERN = re.compile(
    r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|'
    r'(?i:password|access[_ -]?token|client[_ -]?secret|api[_ -]?key)\s*[=:]\s*["\']?\S{6,}|'
    r'(?<![\w.@])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|'
    r'\b[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}\b',
    re.IGNORECASE,
)


class PageInspector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.errors = []
        self.title_count = 0
        self.h1_count = 0
        self.has_lang = False
        self.has_viewport = False
        self.canonical = []
        self.og_url = []
        self.og_image = []
        self.csp = []
        self.ids = set()
        self.references = []

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag == 'html':
            self.has_lang = data.get('lang') in ('en', 'nl')
        if tag == 'title':
            self.title_count += 1
        if tag == 'h1':
            self.h1_count += 1
        if data.get('id'):
            if data['id'] in self.ids:
                self.errors.append('duplicate element id: '+data['id'])
            self.ids.add(data['id'])
        for key, value in attrs:
            if key.lower().startswith('on') and len(key) > 2:
                self.errors.append('inline event handler: '+key)
            if key in ('src', 'href', 'poster', 'action', 'data') and value is not None:
                self.references.append((tag, key, value))
        if tag in ('iframe', 'frame', 'object', 'embed', 'form', 'base'):
            self.errors.append('unexpected element: '+tag)
        if tag == 'script':
            src = data.get('src', '')
            if not src or not src.endswith(('assets/site.js', 'assets/dashboard.js')):
                self.errors.append('inline/unapproved JavaScript')
        if tag == 'style' or data.get('style'):
            self.errors.append('inline styles prohibited by CSP')
        if tag == 'img' and 'alt' not in data:
            self.errors.append('image missing alt attribute')
        if tag == 'a' and data.get('target') == '_blank':
            rel = set((data.get('rel') or '').split())
            if not {'noopener', 'noreferrer'}.issubset(rel):
                self.errors.append('target=_blank missing noopener/noreferrer')
        if tag == 'meta':
            if data.get('name') == 'viewport':
                self.has_viewport = True
            if (data.get('http-equiv') or '').lower() == 'refresh':
                self.errors.append('meta refresh is prohibited')
            if (data.get('http-equiv') or '').lower() == 'content-security-policy':
                self.csp.append(data.get('content'))
            if data.get('property') == 'og:url':
                self.og_url.append(data.get('content'))
            if data.get('property') == 'og:image':
                self.og_image.append(data.get('content'))
        if tag == 'link' and 'canonical' in (data.get('rel') or '').split():
            self.canonical.append(data.get('href'))

    handle_startendtag = handle_starttag


def expected_url(relative):
    value = relative.as_posix()
    if value == 'index.html':
        return DOMAIN+'/'
    if value.endswith('/index.html'):
        return DOMAIN+'/'+value[:-len('index.html')]
    return DOMAIN+'/'+value


def audit_markup(source, relative):
    inspector = PageInspector()
    inspector.feed(source)
    errors = list(inspector.errors)
    page = expected_url(relative)
    if inspector.title_count != 1:
        errors.append('page must contain exactly one title')
    if inspector.h1_count != 1:
        errors.append('page must contain exactly one h1')
    if not inspector.has_lang or not inspector.has_viewport:
        errors.append('missing valid page language or responsive viewport')
    if inspector.canonical != [page]:
        errors.append('unexpected canonical URL')
    if inspector.og_url != [page]:
        errors.append('unexpected Open Graph URL')
    if inspector.og_image != [DOMAIN+'/assets/hero-globe.webp']:
        errors.append('unexpected Open Graph image')
    if inspector.csp != [CSP]:
        errors.append('missing/modified strict Content Security Policy')
    if 'http://' in source or 'https://jsec82.github.io' in source:
        errors.append('insecure or obsolete site URL')
    if PRIVATE_PATTERN.search(source):
        errors.append('potential personal information/credential in published HTML')
    for tag, key, value in inspector.references:
        parsed = urlsplit(value)
        if parsed.scheme and parsed.scheme not in ('https',):
            errors.append('dangerous or insecure URL scheme in '+tag+'/'+key)
        elif parsed.netloc:
            allowed = value in ALLOWED_OUTBOUND
            if tag == 'link' and value.startswith(DOMAIN+'/'):
                allowed = True
            if not allowed:
                errors.append('unapproved external URL or resource: '+tag+'/'+key)
        elif value.startswith('//'):
            errors.append('scheme-relative resource forbidden: '+tag+'/'+key)
    return errors



def scan_svg(path, data):
    """Block active SVG features and external references, including nested icons."""
    errors = []
    if len(data) > 250_000:
        errors.append('SVG exceeds 250 KB size budget: '+path.name)
    if re.search(rb'<!DOCTYPE|<!ENTITY|<\?xml-stylesheet', data, re.IGNORECASE):
        errors.append('SVG contains DTD, entity, or XML stylesheet: '+path.name)
        return errors
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        errors.append('SVG is not well-formed XML: '+path.name)
        return errors
    if root.tag != '{http://www.w3.org/2000/svg}svg':
        errors.append('SVG root is not SVG namespace: '+path.name)
    forbidden = {'script', 'foreignobject', 'image', 'feimage', 'a', 'audio',
                 'video', 'iframe', 'animate', 'animatetransform',
                 'animatemotion', 'set', 'style'}
    for element in root.iter():
        tag = element.tag.rsplit('}', 1)[-1].lower()
        if tag in forbidden:
            errors.append('SVG active/external element prohibited: '+tag+' in '+path.name)
        for raw_name, value in element.attrib.items():
            name = raw_name.rsplit('}', 1)[-1].lower()
            if name.startswith('on') and len(name) > 2:
                errors.append('SVG inline event prohibited: '+name+' in '+path.name)
            if name in ('href', 'src'):
                errors.append('SVG link or remote reference prohibited: '+name+' in '+path.name)
            if re.search(r'url\(\s*["\']?(?:https?:|//|data:|javascript:)|@import|expression\s*\(', value, re.IGNORECASE):
                errors.append('SVG unsafe URL or style expression: '+path.name)
    return errors


def scan_asset(path):
    data = path.read_bytes()
    errors = []
    if path.suffix == '.svg':
        errors.extend(scan_svg(path, data))
    if path.suffix == '.webp':
        if len(data) > 500_000:
            errors.append('graphic exceeds 500 KB size budget: '+path.name)
        if b'EXIF' in data or b'XMP ' in data:
            errors.append('image contains metadata chunk requiring review: '+path.name)
    if path.suffix == '.css':
        source = data.decode('utf-8')
        if re.search(r"@import\b|url\s*\(\s*['\"]?(?:https?:|//|data:|javascript:)|expression\s*\(", source, re.IGNORECASE):
            errors.append('unsafe CSS import, remote reference or expression: '+path.name)
    if path.suffix == '.js':
        source = data.decode('utf-8')
        if re.search(r'\b(?:eval|Function)\s*\(', source):
            errors.append('dynamic JS execution forbidden: '+path.name)
        if re.search(r'https?://|\bfetch\s*\(', source):
            errors.append('unexpected network access in JS: '+path.name)
    return errors


def audit(dist=DIST):
    errors = []
    if not dist.is_dir():
        return ['generated dist/ directory is missing']
    pages = sorted(dist.rglob('*.html'))
    if not pages:
        return ['no generated pages to inspect']
    for path in pages:
        for err in audit_markup(path.read_text(encoding='utf-8'), path.relative_to(dist)):
            errors.append(f'{path.relative_to(dist)}: {err}')
    assets = dist / 'assets'
    if not assets.is_dir():
        errors.append('assets directory missing')
    else:
        for path in assets.rglob('*'):
            if path.is_file():
                errors.extend(f'{path.relative_to(dist)}: {error}' for error in scan_asset(path))
    cname = dist/'CNAME'
    if not cname.is_file() or cname.read_text(encoding='utf-8').strip() != 'weijdensecurity.nl':
        errors.append('missing/incorrect CNAME')
    return errors


if __name__ == '__main__':
    found = audit()
    if found:
        sys.exit('SECURITY PREFLIGHT FAILED:\n - '+'\n - '.join(found))
    print('Security preflight passed: CSP, safe navigation, nested SVG/asset policy, metadata and privacy checks.')
    print('LIMITATION: verify live HTTPS, response headers, accessibility and original source privacy separately.')
