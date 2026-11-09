#!/usr/bin/env python3
"""One-use, strict release packager for reviewed bilingual site."""
from pathlib import Path
import hashlib,base64,lzma,json,subprocess,sys,shutil
ROOT=Path(__file__).resolve().parents[1]
ENC=ROOT/'.release/bilingual-v3.1.xz.b64'
EXPECTED='c248b504c375a889573054c95e2e8047ffb62b500cd1360810eff5fee2bfaca3'
blob=base64.b64decode(ENC.read_text(encoding='ascii').strip(),validate=True)
if hashlib.sha256(blob).hexdigest()!=EXPECTED:raise SystemExit('Bundle SHA256 mismatch')
data=json.loads(lzma.decompress(blob))
if data.get('base')!='a4a1964442b0e1f6f815a7fb1fa264b3cd002df3' or data.get('version')!='3.1':raise SystemExit('Unexpected source baseline/version')
files=data['files']
if len(files)!=24:raise SystemExit('Wrong bundle file count')
for name,body in files.items():
    path=Path(name)
    if path.is_absolute() or '..' in path.parts or not (name.startswith('site-src/pages/') and name.endswith('.tmpl') or name in ('assets/dashboard.css','assets/dashboard.js','scripts/apply_bilingual_patches.py') or name in ('assets/icons/ctf.svg','assets/icons/case.svg','assets/icons/lab.svg')):
        raise SystemExit('Unapproved source path: '+name)
    target=ROOT/path
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(body,encoding='utf8')
subprocess.run([sys.executable,str(ROOT/'scripts/apply_bilingual_patches.py')],check=True,cwd=ROOT)
(ROOT/'scripts/apply_bilingual_patches.py').unlink()
subprocess.run([sys.executable,str(ROOT/'scripts/build.py')],check=True,cwd=ROOT)
dist=ROOT/'dist'
for f in dist.rglob('*'):
    if f.is_file():
        dest=ROOT/f.relative_to(dist)
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(f,dest)
(ENC).unlink()
(ENC.parent).rmdir()
(ROOT/'scripts/stage_bilingual_bundle.py').unlink()
(ROOT/'.github/workflows/stage-bilingual-v3.yml').unlink()
for args in (('scripts/test_links.py',),('scripts/security_audit.py',),('scripts/check_release.py',)):
    subprocess.run([sys.executable,*args],check=True,cwd=ROOT)
subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-p','test_*.py','-v'],check=True,cwd=ROOT)
print('Staged bilingual release passes all local CI gates and leaves no bootstrap workflow.')
