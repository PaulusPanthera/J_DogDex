"""Build the public Windows bundle; never includes personal or generated viewer files."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import argparse,datetime,hashlib,json,sqlite3,zipfile
from dogdex import __version__
ROOT=Path(__file__).resolve().parents[1]
BASELINE='e79d48ff8d056d88fa0d6b1f0771f220d79f62d82797c886183e20ada9c22da0'
def digest(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def managed_paths():
    c=json.loads((ROOT/'data/catalog.json').read_text(encoding='utf-8'))
    names=['app.py','START_DOGDEX.bat','CREATE_REVIEW_ZIP.bat','CHECK_DOGDEX.bat','DEVELOPMENT.md','.gitattributes','.github/workflows/checks.yml','README.txt','MOBILE_README.md','.gitignore','data/catalog.sqlite3','data/catalog-collector.sqlite3','data/catalog.json','data/runtime-receipt.json','data/SOURCE_IDENTIFIER_RECONCILIATION_REPORT.md'];paths=[ROOT/n for n in names]
    for folder in ('dogdex','tools','static','runtime','tests','data/research','project_notes'):
        paths.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and 'node_modules' not in p.parts and 'previous_layout' not in p.parts and not p.name.startswith('DogDex_Collection_Audit_') and p.suffix not in ('.pyc','.zip') and not (folder=='runtime' and p.name.startswith('.')))
    paths.extend(ROOT/'data/images'/name for name in c['used_images']);paths=sorted(set(paths))
    if not all(p.is_file() for p in paths):raise ValueError('Bundle file missing')
    if any(any(part in ('my_collection','docs','.git') for part in p.relative_to(ROOT).parts) for p in paths):raise ValueError('Private/generated folder in public bundle')
    return paths,c

def write_manifest():
    if digest(ROOT/'data/catalog.sqlite3')!=BASELINE:raise ValueError('Immutable catalogue changed')
    for name in ('catalog.sqlite3','catalog-collector.sqlite3'):
        with sqlite3.connect((ROOT/'data'/name).as_uri()+'?mode=ro',uri=True) as db:
            if db.execute('PRAGMA quick_check').fetchone()[0]!='ok' or db.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('Catalogue integrity failed')
    paths,c=managed_paths();manifest=dict(format='dogdex-local-collector-bundle',version=__version__,created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),platform='Windows x64',catalog_sha256=BASELINE,statistics=c['statistics'],image_files=len(c['used_images']),files={p.relative_to(ROOT).as_posix():dict(bytes=p.stat().st_size,sha256=digest(p)) for p in paths})
    (ROOT/'BUNDLE_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8');return paths+[ROOT/'BUNDLE_MANIFEST.json'],manifest

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT.parent/'DogDex_Local_Collector_Windows.zip');a=p.parse_args()
    if '..' not in (ROOT/'runtime/python314._pth').read_text(encoding='utf-8').splitlines():raise ValueError('Embedded runtime source path is missing')
    paths,manifest=write_manifest()
    with zipfile.ZipFile(a.output,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for f in paths:z.write(f,'DogDex/'+f.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(a.output) as z:
        if z.testzip():raise ValueError('ZIP CRC failed')
        for name,info in manifest['files'].items():
            with z.open('DogDex/'+name) as f:
                if hashlib.file_digest(f,'sha256').hexdigest()!=info['sha256']:raise ValueError('ZIP checksum failed: '+name)
    print(json.dumps(dict(path=str(a.output),bytes=a.output.stat().st_size,sha256=digest(a.output),files=len(paths))))
if __name__=='__main__':main()
