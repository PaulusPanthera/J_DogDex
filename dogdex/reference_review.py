"""Explicit EN/DE reference review; no inferred regional variants or price matches."""
import copy,hashlib,json
from pathlib import Path
from .special_import import add_printing,write_json
from .printing_model import physical_key,printing_label

ROOT=Path(__file__).resolve().parents[1]
FACTS=ROOT/'data/research/reference_1819/facts.json'

def apply(catalog):
    facts=json.loads(FACTS.read_text(encoding='utf-8'))
    by={e['id']:e for e in catalog['entries']};added=[];candidates=[]
    for row in facts['printings']:
        e=by[row['entry_id']]
        if (e['lang'],e['release'],e['number'])!=tuple(row['identity']):raise ValueError('Reviewed regional identity changed')
        review=[]
        p=add_printing(e,row['physical'],dict(kind='reference_review_1819',reviewed_on=facts['reviewed_on'],source_urls=row['source_urls'],evidence=row['evidence']),review)
        if p is None or p['id']!=row['printing_id']:raise ValueError('Reviewed physical identity changed: '+repr(review))
        p.update(label=printing_label(p),collection_status='documented',verification=dict(existence=dict(status='documented',source_urls=row['source_urls'],checked_on=facts['reviewed_on'],method='explicit_regional_printing_review'),specimen=dict(status='not_inspected')))
        if row.get('production_note'):p['production_note']=row['production_note']
        if row.get('canonical_url'):p['cardmarket_url']=row['canonical_url']
        added.append(p['id'])
    for row in facts['candidates']:
        e=by[row['entry_id']];p=next(p for p in e['printings'] if p['id']==row['printing_id'])
        if list(physical_key(e['id'],p))!=row['candidate']['physical_key']:raise ValueError('Candidate physical identity changed')
        if p.get('market_confirmed'):continue
        old=p.get('market_candidate')
        if old and old.get('product_id')!=row['candidate']['product_id']:raise ValueError('Conflicting provider reference requires review')
        p['market_candidate']=copy.deepcopy(row['candidate']);candidates.append(p['id'])
    for e in catalog['entries']:
        keys=[physical_key(e['id'],p) for p in e['printings']]
        if len(keys)!=len(set(keys)):raise ValueError('Duplicate physical printing: '+e['id'])
    catalog['reference_review_1819']=dict(reviewed_on=facts['reviewed_on'],facts_sha256=hashlib.sha256(FACTS.read_bytes()).hexdigest(),added_printing_ids=sorted(added),candidate_printing_ids=sorted(candidates),limits=facts['limits'])
    return catalog

def refresh(catalog):
    from .new_sets import refresh as refresh_statistics
    refresh_statistics(catalog)
    catalog.update(revision='1.8.19',catalog_date='2026-11-12')

def main():
    from .catalog_enrich import make_sqlite
    path=ROOT/'data/catalog.json';catalog=json.loads(path.read_text(encoding='utf-8'))
    apply(catalog);refresh(catalog);write_json(path,catalog);make_sqlite(catalog)
    print(json.dumps(dict(statistics=catalog['statistics'],review=catalog['reference_review_1819'])))

if __name__=='__main__':main()
