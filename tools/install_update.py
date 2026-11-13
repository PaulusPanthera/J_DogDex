"""Atomic managed-file update, explicit old-layout archive, and personal-data check."""
import argparse,datetime,hashlib,json,os,re,shutil,socket,sqlite3,sys,tempfile,zipfile
from pathlib import Path
VERSION='1.8.19'
PROTECTED={'my_collection','runtime','docs','.git'}

def digest(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def safe(root,name):
    path=root/name
    if Path(name).is_absolute() or '..' in Path(name).parts or not path.resolve().is_relative_to(root.resolve()):raise ValueError('Unsafe managed path: '+name)
    if any(p.is_symlink() for p in [path,*path.parents] if p.is_relative_to(root)):raise ValueError('Symbolic link in managed path: '+name)
    return path

def rows(path):
    if not path.is_file():return {}
    with sqlite3.connect(path.as_uri()+'?mode=ro',uri=True) as db:
        if db.execute('PRAGMA quick_check').fetchone()[0]!='ok':raise ValueError('Personal database integrity check failed')
        names=[r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
        return {n:sorted(db.execute('SELECT * FROM "'+n.replace('"','""')+'"').fetchall(),key=repr) for n in names}

def copy_db(source,dest):
    with sqlite3.connect(source.as_uri()+'?mode=ro',uri=True) as src,sqlite3.connect(dest) as dst:src.backup(dst)

def install(target,staging,check_running=True):
    target=target.resolve();staging=staging.resolve();payload=staging/'payload'
    manifest=json.loads((staging/'UPDATE_MANIFEST.json').read_text(encoding='utf-8'));files=manifest['files']
    if manifest['version']!=VERSION:raise ValueError('Updater version mismatch')
    if not (target/'app.py').is_file() or not (target/'data/catalog.json').is_file():raise ValueError('Extract the update directly into the existing DogDex folder first.')
    version_file=target/'dogdex/__init__.py'
    match=re.search(r'__version__\s*=\s*[\x27\"]([^\x27\"]+)',version_file.read_text(encoding='utf-8')) if version_file.is_file() else None
    if not match or match[1] not in manifest['expected_app_versions']:raise ValueError('Install DogDex 1.8.18 before this update. An older application can share the same catalogue data but still require earlier code fixes.')
    if check_running:
        with socket.socket() as sock:
            sock.settimeout(.3)
            if sock.connect_ex(('127.0.0.1',8765))==0:raise ValueError('Close the DogDex server window before updating.')
    for name,info in files.items():
        if Path(name).parts[0] in PROTECTED:raise ValueError('Protected folder in update payload')
        source=safe(payload,name);safe(target,name)
        if not source.is_file() or source.stat().st_size!=info['bytes'] or digest(source)!=info['sha256']:raise ValueError('Damaged update payload: '+name)
    if digest(target/'data/catalog.json') not in (manifest['expected_catalog_sha256'],files['data/catalog.json']['sha256']):raise ValueError('The base catalogue differs from the version this update was prepared for. In-app personal edits are supported; a different base catalogue needs reconciliation first.')
    old=json.loads((target/'data/catalog.json').read_text(encoding='utf-8'));new=json.loads((payload/'data/catalog.json').read_text(encoding='utf-8'))
    if old['roster']!=new['roster']:raise ValueError('Species roster differs')
    if not {e['id'] for e in old['entries']}<={e['id'] for e in new['entries']}:raise ValueError('Existing card identity would be removed')
    if not {p['id'] for e in old['entries'] for p in e['printings']}<={p['id'] for e in new['entries'] for p in e['printings']}:raise ValueError('Existing printing ID would be removed')
    user=target/'my_collection';dbpath=user/'collection.sqlite3';before=rows(dbpath)
    stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f');backup=user/'backups'/('before-1.8.19-'+stamp);backup.mkdir(parents=True)
    if dbpath.is_file():copy_db(dbpath,backup/'collection.sqlite3')
    changes=[n for n,i in files.items() if not (target/n).is_file() or digest(target/n)!=i['sha256']]
    existed=[];installed=[];moved=[];archive=target/'project_notes/previous_layout'/stamp
    with zipfile.ZipFile(backup/'managed-files.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name in changes:
            path=target/name
            if path.is_file():z.write(path,name);existed.append(name)
    (backup/'restore.json').write_text(json.dumps(dict(version=VERSION,changed=changes,previously_present=existed),indent=2),encoding='utf-8')
    try:
        for name in changes:
            dest=target/name;dest.parent.mkdir(parents=True,exist_ok=True)
            fd,tmp=tempfile.mkstemp(prefix=dest.name+'.update-',dir=dest.parent);os.close(fd)
            try:shutil.copyfile(payload/name,tmp);os.replace(tmp,dest)
            finally:Path(tmp).unlink(missing_ok=True)
            installed.append(name)
        for item in manifest['old_layout']:
            name=item['from']
            if name=='app.py' or len(Path(name).parts)!=1:continue
            path=safe(target,name)
            if path.is_file():
                archive.mkdir(parents=True,exist_ok=True);shutil.move(str(path),archive/name);moved.append(name)
        cache=target/'__pycache__'
        if cache.is_dir() and not cache.is_symlink():archive.mkdir(parents=True,exist_ok=True);shutil.move(str(cache),archive/'__pycache__');moved.append('__pycache__')
        if rows(dbpath)!=before:raise ValueError('Personal records changed during installation')
        # Validate the installed package and owned IDs on a disposable database.
        sys.path.insert(0,str(target))
        from dogdex.collector import Collection
        with tempfile.TemporaryDirectory(prefix='dogdex-update-check-') as tmp:
            check=Path(tmp)/'collection';check.mkdir()
            if dbpath.is_file():copy_db(dbpath,check/'collection.sqlite3')
            store=Collection(target,check);view=store.editor_view();accepted={p['id'] for e in view['entries'] for p in e['printings']}
            if any(c['printing_id'] not in accepted for c in store.state()['copies']):raise ValueError('An owned printing cannot be resolved')
        if rows(dbpath)!=before:raise ValueError('Personal rows changed during validation')
        result=dict(version=VERSION,changed_files=len(changes),archived_root_files=len(moved),personal_tables_unchanged=True,backup=str(backup.relative_to(target)))
        (backup/'installation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        print('DogDex 1.8.19 installed. Collection records are unchanged.');print('Start with START_DOGDEX.bat. Export mobile view again when ready.');print('Backup: '+str(backup));return result
    except Exception:
        for name in reversed(moved):shutil.move(str(archive/name),target/name)
        with zipfile.ZipFile(backup/'managed-files.zip') as z:
            for name in reversed(installed):
                if name in existed:(target/name).write_bytes(z.read(name))
                else:(target/name).unlink(missing_ok=True)
        raise

def main():
    p=argparse.ArgumentParser();p.add_argument('--target',type=Path);p.add_argument('--staging',type=Path);p.add_argument('--skip-running-check',action='store_true');a=p.parse_args();staging=a.staging or Path(__file__).resolve().parent
    try:install(a.target or staging.parent,staging,not a.skip_running_check)
    except Exception as e:print('Update stopped: '+str(e));return 1
    return 0
if __name__=='__main__':raise SystemExit(main())
