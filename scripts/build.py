#!/usr/bin/env python3
"""Build only reviewed public static pages; no network, npm, tenant or private repo access."""
from pathlib import Path
from xml.sax.saxutils import escape
import shutil, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist'
SOURCES=ROOT/'site-src/pages'
LEGACY=('about/index.html','skills/index.html','activity/index.html')
DOMAIN='https://weijdensecurity.nl'
def main():
    subprocess.run([sys.executable,str(ROOT/'scripts/validate.py')],check=True)
    if OUT.is_symlink():raise SystemExit('dist must not be a symlink')
    if OUT.exists():shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT/'assets',OUT/'assets')
    pages=[]
    for source in sorted(SOURCES.rglob('*.tmpl')):
        rel=source.relative_to(SOURCES).as_posix().removesuffix('.tmpl')
        if not rel.endswith('.html') or '..' in Path(rel).parts:raise SystemExit('invalid source path')
        target=OUT/rel
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,target)
        pages.append(rel)
    for rel in LEGACY:
        target=OUT/rel
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/rel,target)
        pages.append(rel)
    for name in ('CNAME','robots.txt','.nojekyll'):
        shutil.copyfile(ROOT/name,OUT/name)
    def uri(path):
        if path=='index.html':return DOMAIN+'/'
        if path.endswith('/index.html'):return DOMAIN+'/'+path.removesuffix('index.html')
        return DOMAIN+'/'+path
    rows=''.join('<url><loc>'+escape(uri(p))+'</loc></url>' for p in pages)
    (OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+rows+'</urlset>\n',encoding='utf-8')
    print('Generated:',len(pages),'public pages from individually editable source templates.')
if __name__=='__main__':main()
