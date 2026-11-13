"""Read-only project diagnostics; private database validation uses a disposable copy."""
import argparse
from contextlib import closing
import datetime
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from dogdex import __version__
from dogdex.collector import Collection
from dogdex.printing_model import physical_key
ROOT=Path(__file__).resolve().parents[1]
BASELINE='e79d48ff8d056d88fa0d6b1f0771f220d79f62d82797c886183e20ada9c22da0'

def check(root=ROOT):
    root=Path(root).resolve()
    report=dict(app_version=__version__,checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),checks=[],summary={})
    def run(name,fn):
        try:
            detail=fn();report['checks'].append(dict(name=name,ok=True,detail=detail))
        except Exception as exc:report['checks'].append(dict(name=name,ok=False,detail=str(exc)))
    c=None
    def catalogue():
        nonlocal c
        c=json.loads((root/'data/catalog.json').read_text(encoding='utf-8'))
        entries=c['entries'];eids=[e['id'] for e in entries];pids=[p['id'] for e in entries for p in e['printings']]
        if len(eids)!=len(set(eids)) or len(pids)!=len(set(pids)):raise ValueError('Duplicate catalogue identity')
        if c['statistics']['entries']!=len(entries) or c['statistics']['printings']!=len(pids):raise ValueError('Catalogue statistics do not match its records')
        for e in entries:
            keys=[physical_key(e['id'],p) for p in e['printings']]
            if len(keys)!=len(set(keys)):raise ValueError('Duplicate physical tuple: '+e['id'])
        report['summary'].update(catalog_revision=c['revision'],entries=len(entries),raw_printings=len(pids))
        return 'Catalogue '+c['revision']+'; identities and physical tuples are unique'
    run('catalogue',catalogue)
    def original():
        with (root/'data/catalog.sqlite3').open('rb') as f:got=hashlib.file_digest(f,'sha256').hexdigest()
        if got!=BASELINE:raise ValueError('Original catalogue checkpoint checksum differs')
        return 'Original checkpoint unchanged'
    run('original_checkpoint',original)
    def index():
        p=root/'data/catalog-collector.sqlite3'
        if not p.is_file():raise ValueError('Derived index missing. Run python tools/build_index.py')
        with closing(sqlite3.connect(p.as_uri()+'?mode=ro',uri=True)) as db:
            if db.execute('PRAGMA quick_check').fetchone()[0]!='ok' or db.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('Derived index integrity failed')
            actual={r[0] for r in db.execute('SELECT id FROM printings')}
        if c is None:raise ValueError('Catalogue could not be loaded')
        expected={p['id'] for e in c['entries'] for p in e['printings']}
        if actual!=expected:raise ValueError('Derived index differs from JSON. Run python tools/build_index.py')
        return str(len(actual))+' indexed printings'
    run('derived_index',index)
    def images():
        if c is None:raise ValueError('Catalogue could not be loaded')
        missing=[n for n in c['used_images'] if not (root/'data/images'/n).is_file()]
        if missing:raise ValueError(str(len(missing))+' missing cached images')
        return str(len(c['used_images']))+' cached images present'
    run('cached_images',images)
    def personal():
        p=root/'my_collection/collection.sqlite3'
        with tempfile.TemporaryDirectory(prefix='dogdex-check-') as temp:
            user=Path(temp)/'collection';user.mkdir()
            if p.is_file():
                with closing(sqlite3.connect(p.as_uri()+'?mode=ro',uri=True)) as source,closing(sqlite3.connect(user/'collection.sqlite3')) as dest:
                    if source.execute('PRAGMA quick_check').fetchone()[0]!='ok':raise ValueError('Personal database integrity failed')
                    source.backup(dest)
            store=Collection(root,user);state=store.state();accepted=store.printing_map()
            unknown={r['printing_id'] for r in state['copies'] if r['printing_id'] not in accepted}
            report['summary'].update(active_copies=len(state['copies']),owned_printings=len({r['printing_id'] for r in state['copies']}),wishlist=len(state['wishlist']),accepted_printings=len(accepted))
            if unknown:raise ValueError(str(len(unknown))+' owned printing IDs need review; all personal records were left untouched')
        return 'Personal database and owned printing IDs resolve; checked on a temporary copy'
    run('personal_collection',personal)
    report['ok']=all(r['ok'] for r in report['checks'])
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path);a=p.parse_args()
    report=check()
    for r in report['checks']:print(('OK   ' if r['ok'] else 'FAIL ')+r['name']+': '+r['detail'])
    print(json.dumps(report['summary'],ensure_ascii=False))
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        print('Check report: '+str(a.output))
    return 0 if report['ok'] else 1
if __name__=='__main__':raise SystemExit(main())
