#!/usr/bin/env python3
"""Dependency-free internal link, anchor and domain checks for the public static site."""
from pathlib import Path
from urllib.parse import urlsplit,unquote
from html.parser import HTMLParser
import json,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
DIST=(ROOT/'dist').resolve()
class Parser(HTMLParser):
    def __init__(self):super().__init__();self.ids=set();self.links=[];self.h1=0
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if 'id' in d:self.ids.add(d['id'])
        if tag=='h1':self.h1+=1
        if tag=='a' and d.get('href'):self.links.append(d['href'])
        if tag in ('script','img','link') and d.get('src',d.get('href')):self.links.append(d.get('src',d.get('href')))
pages={}
for f in DIST.rglob('*.html'):
    p=Parser();p.feed(f.read_text(encoding='utf-8'));pages[f.resolve()]=p
errors=[]
for file,p in pages.items():
    if p.h1!=1:errors.append(f'{file}: expected exactly one H1')
    for raw in p.links:
        u=urlsplit(raw)
        if u.scheme or u.netloc:
            if not (u.scheme=='https' and (u.netloc=='weijdensecurity.nl' or raw in ('https://github.com/jsec82','https://www.linkedin.com/in/jeroenvanderweijden/','https://www.nist.gov/publications/workforce-framework-cybersecurity-nice-framework','https://www.nist.gov/itl/applied-cybersecurity/nice/nice-framework-resource-center/nice-framework-current-versions','https://www.nist.gov/cyberframework','https://learn.microsoft.com/en-us/security/zero-trust/zero-trust-overview','https://attack.mitre.org/resources/'))):
                errors.append(f'{file}: unapproved external url {raw}')
            continue
        target=(file.parent/unquote(u.path)).resolve() if u.path else file
        if not target.is_relative_to(DIST):errors.append(f'{file}: path escape {raw}');continue
        if not target.is_file():errors.append(f'{file}: broken link {raw}');continue
        if u.fragment and target in pages and unquote(u.fragment) not in pages[target].ids:errors.append(f'{file}: missing anchor {raw}')
required={'index.html','projects/index.html','focus/index.html','roadmap/index.html','contact/index.html','about/index.html','skills/index.html','activity/index.html'}
projects=json.loads((ROOT/'content/projects.json').read_text(encoding='utf-8'))
required|={'projects/'+p['slug']+'.html' for p in projects}
required|={'en/'+rel for rel in required if rel not in ('about/index.html','skills/index.html','activity/index.html')}
required|={prefix+'projects/engineering/'+route for prefix in ('','en/') for route in ('index.html','endpoint.html','identity.html','capstone.html')}
required|={'methodology/index.html','en/methodology/index.html'}
for rel in required:
    if (DIST/rel).resolve() not in pages:errors.append('missing route: '+rel)
if len(pages)!=len(required):errors.append('Unexpected HTML count')
if len(ET.parse(DIST/'sitemap.xml').getroot())!=len(required):errors.append('Incorrect sitemap count')
if (DIST/'CNAME').read_text().strip()!='weijdensecurity.nl':errors.append('Incorrect custom domain')
if 'Sitemap: https://weijdensecurity.nl/sitemap.xml' not in (DIST/'robots.txt').read_text():errors.append('Incorrect robots sitemap')
home=(DIST/'index.html').read_text()
for area in ('intune','entra','defender','sentinel'):
    if 'focus/index.html?area='+area not in home:errors.append('Missing homepage focus link '+area)
if errors:raise SystemExit('SITE LINK CHECK FAILED:\n - '+'\n - '.join(errors))
print('Passed: '+str(len(pages))+' public pages; links, anchors, sitemap and DNS metadata.')
