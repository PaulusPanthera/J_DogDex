"""Create a private review ZIP from current source, catalogue and personal files."""
import argparse,datetime,json,sqlite3,tempfile,zipfile
from contextlib import closing
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path);a=p.parse_args()
    output=(a.output or ROOT.parent/('DogDex_Review_'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.zip')).resolve()
    if output.exists():raise ValueError('Choose a new output filename; existing archives are not overwritten.')
    paths=[ROOT/n for n in ('app.py','START_DOGDEX.bat','CREATE_REVIEW_ZIP.bat','CHECK_DOGDEX.bat','DEVELOPMENT.md','README.txt','MOBILE_README.md','BUNDLE_MANIFEST.json','.gitignore','.gitattributes') if (ROOT/n).is_file()]
    for folder in ('dogdex','tools','static','tests','data','my_collection','project_notes','.github'):
        for f in (ROOT/folder).rglob('*'):
            rel=f.relative_to(ROOT)
            if not f.is_file() or f.is_symlink() or '__pycache__' in rel.parts or 'node_modules' in rel.parts or 'backups' in rel.parts or 'previous_layout' in rel.parts or f.suffix in ('.pyc','.zip') or f.name.endswith(('-wal','-shm')) or any(s.startswith(('mobile-export-','mobile-previous-')) for s in rel.parts):continue
            if f.resolve()!=output:paths.append(f)
    with tempfile.TemporaryDirectory(prefix='dogdex-review-') as tmp:
        db=ROOT/'my_collection/collection.sqlite3';snapshot=Path(tmp)/'collection.sqlite3'
        if db.is_file():
            with closing(sqlite3.connect(db.as_uri()+'?mode=ro',uri=True)) as src,closing(sqlite3.connect(snapshot)) as dest:
                if src.execute('PRAGMA quick_check').fetchone()[0]!='ok':raise ValueError('Personal database integrity check failed')
                src.backup(dest)
        with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for f in sorted(set(paths)):z.write(snapshot if f==db else f,'DogDex/'+f.relative_to(ROOT).as_posix())
            z.writestr('DogDex/REVIEW_ARCHIVE_INFO.txt','Private review archive: includes collection, purchase notes, prices, manual edits and custom images.\nRuntime, generated viewer, Git history, caches and old ZIP backups are omitted.\n')
        with zipfile.ZipFile(output) as z:
            if z.testzip():raise ValueError('Review ZIP validation failed')
    print('Review ZIP: '+str(output));print('Contains private collection information; share only for the intended review.')
if __name__=='__main__':main()
