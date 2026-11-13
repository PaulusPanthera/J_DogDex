"""Run against a previous full project ZIP and this release's update ZIP.

python tests/integration_installer.py BEFORE.zip UPDATE.zip OUTPUT_DIRECTORY
No input archive is modified. The temporary copy contains private user records.
"""
import hashlib,json,os,shutil,sqlite3,subprocess,sys,tempfile,zipfile
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def personal(root):
    database=root/'my_collection/collection.sqlite3'
    with sqlite3.connect(database.as_uri()+'?mode=ro',uri=True) as db:
        tables=[r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
        values={n:sorted(db.execute('SELECT * FROM "'+n.replace('"','""')+'"').fetchall(),key=repr) for n in tables}
    files={p.relative_to(root/'my_collection').as_posix():sha(p) for p in (root/'my_collection').rglob('*') if p.is_file() and 'backups' not in p.parts and not p.name.endswith(('-wal','-shm'))}
    return values,files

def main():
    before_zip,update_zip,output=map(lambda x:Path(x).resolve(),sys.argv[1:]);output.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='dogdex-installer-',dir=output) as tmp:
        temp=Path(tmp);base=temp/'baseline';base.mkdir()
        with zipfile.ZipFile(before_zip) as z:
            assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist());z.extractall(base)
        if not (base/'data/catalog.json').exists():base=base/'DogDex'
        before_personal=personal(base);summary={}
        def clone(name):
            target=temp/name
            def copy(src,dst):
                if 'my_collection' in Path(src).relative_to(base).parts:return shutil.copy2(src,dst)
                return os.link(src,dst)
            shutil.copytree(base,target,copy_function=copy)
            for n in ('.git','runtime','docs'):(target/n).mkdir(exist_ok=True);(target/n/'KEEP').write_text('unmanaged sentinel',encoding='utf-8')
            (target/'manual_notes.py').write_text('keep unknown root file',encoding='utf-8')
            with zipfile.ZipFile(update_zip) as z:z.extractall(target)
            return target
        def run(target):
            stage=target/'_dogdex_update_1_8_19';env=os.environ|{'PYTHONDONTWRITEBYTECODE':'1'}
            return subprocess.run([sys.executable,str(stage/'install_update.py'),'--target',str(target),'--skip-running-check'],capture_output=True,text=True,env=env,timeout=180)
        target=clone('normal');docs={p.relative_to(target/'docs').as_posix():sha(p) for p in (target/'docs').rglob('*') if p.is_file()}
        first=run(target);assert first.returncode==0,first.stdout+first.stderr;assert personal(target)==before_personal;assert (target/'collector.py').exists()==(base/'collector.py').exists();assert (target/'dogdex/collector.py').exists();assert (target/'manual_notes.py').read_text(encoding='utf-8')=='keep unknown root file';assert (target/'.git/KEEP').is_file();assert (target/'runtime/KEEP').is_file();assert docs=={p.relative_to(target/'docs').as_posix():sha(p) for p in (target/'docs').rglob('*') if p.is_file()}
        installed=json.loads((target/'data/catalog.json').read_text(encoding='utf-8'));assert installed['revision']=='1.8.19';record=max((target/'my_collection/backups').glob('before-1.8.19-*/installation.json'));summary['normal']=json.loads(record.read_text(encoding='utf-8'))
        again=run(target);assert again.returncode==0,again.stdout+again.stderr;assert personal(target)==before_personal;record=max((target/'my_collection/backups').glob('before-1.8.19-*/installation.json'));summary['repeat']=json.loads(record.read_text(encoding='utf-8'));assert summary['repeat']['changed_files']==0
        good=(target/'data/catalog.json').read_bytes();modified=json.loads(good);modified['unreviewed_manual_base_change']=True;(target/'data/catalog.json').write_text(json.dumps(modified),encoding='utf-8');custom=sha(target/'data/catalog.json');badbase=run(target);assert badbase.returncode==1;assert sha(target/'data/catalog.json')==custom;assert personal(target)==before_personal;(target/'data/catalog.json').write_bytes(good);summary['different_base_rejected']=True
        version_file=target/'dogdex/__init__.py';good_version=version_file.read_bytes();version_file.write_text('__version__ = "1.8.17"\n',encoding='utf-8');wrong_app=run(target);assert wrong_app.returncode==1;assert '1.8.18 before this update' in wrong_app.stdout;assert personal(target)==before_personal;assert (target/'data/catalog.json').read_bytes()==good;version_file.write_bytes(good_version);summary['older_app_with_same_catalogue_rejected']=True
        corrupt=clone('corrupt');payload=corrupt/'_dogdex_update_1_8_19/payload';(payload/'README.txt').write_text('corrupt payload',encoding='utf-8');rejected=run(corrupt);assert rejected.returncode==1;assert sha(corrupt/'data/catalog.json')==sha(base/'data/catalog.json');assert (corrupt/'collector.py').exists()==(base/'collector.py').exists();assert personal(corrupt)==before_personal;summary['corrupt_payload_rejected_before_mutation']=True
        rollback=clone('rollback');stage=rollback/'_dogdex_update_1_8_19';f=stage/'payload/dogdex/collector.py';f.write_text('raise RuntimeError("Injected post-install validation failure")\n',encoding='utf-8');manifest=json.loads((stage/'UPDATE_MANIFEST.json').read_text(encoding='utf-8'));manifest['files']['dogdex/collector.py']={'bytes':f.stat().st_size,'sha256':sha(f)};(stage/'UPDATE_MANIFEST.json').write_text(json.dumps(manifest),encoding='utf-8');failed=run(rollback);assert failed.returncode==1;assert 'Injected post-install' in failed.stdout;assert sha(rollback/'data/catalog.json')==sha(base/'data/catalog.json');assert sha(rollback/'app.py')==sha(base/'app.py');assert sha(rollback/'dogdex/collector.py')==sha(base/'dogdex/collector.py');assert personal(rollback)==before_personal;assert (rollback/'manual_notes.py').is_file();summary['post_install_failure_rolls_back_managed_files']=True
        summary.update(personal_tables_and_files_unchanged=True,generated_viewer_and_runtime_and_git_preserved=True,root_unknown_files_preserved=True)
        (output/'installer_integration.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary))
if __name__=='__main__':main()
