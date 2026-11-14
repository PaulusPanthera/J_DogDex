"""Explicit EN/DE cameo corrections and an external-reference coverage guard.

Facts are language-specific. A provider translation, rarity or artwork match never
creates physical variants. Existing physical records and saved user overrides are
outside this stage's mutation boundary.
"""
import copy
import hashlib
import json
import re
from pathlib import Path
from .special_import import add_printing, date_fields, write_json
from .printing_model import physical_key, printing_label
from .prepare import rarity_family
from .rarities import normalize as normalize_rarity

ROOT=Path(__file__).resolve().parents[1]
FACTS=ROOT/'data/research/cameo_1820/facts.json'
REQUIREMENTS=ROOT/'data/research/cameo_1820/coverage_requirements.json'

def _number(value):
    value=str(value).split('/')[0].strip().casefold()
    return re.sub(r'(?<!\d)0+(?=\d)','',value)

def _identity(e):
    return e['lang'],e['release'],e.get('identifier_namespace','collector'),_number(e['number'])

def verify_coverage(catalog,requirements=None):
    """Check frozen positive source claims, independently of importer output.

    This checks known requirements, not the unprovable absence of unseen cameos.
    Operates on the base catalogue; personal exclusions remain user decisions.
    """
    if requirements is None:
        requirements=json.loads(REQUIREMENTS.read_text(encoding='utf-8'))
    index={};by={e['id']:e for e in catalog['entries']};errors=[]
    for e in catalog['entries']:index.setdefault(_identity(e),[]).append(e)
    for r in requirements['appearances']:
        ident=tuple(r['identity'][:3])+(_number(r['identity'][3]),)
        matches=index.get(ident,[]);e=by.get(r['entry_id'])
        prefix=r['entry_id']+' / '+str(r['dex'])
        if len(matches)!=1:
            errors.append(prefix+': expected one canonical host, found '+str(len(matches)));continue
        if e is None or matches[0]['id']!=r['entry_id']:
            errors.append(prefix+': stable host identity changed');continue
        if r['dex'] not in e.get(r['role']+'_dex',[]):errors.append(prefix+': species appearance missing')
        if e.get('metadata_state')!='approved' or e.get('identity_status') in ('provisional','disputed','excluded','announced'):
            errors.append(prefix+': confirmed host was demoted')
        if not e.get('printings'):errors.append(prefix+': no physical printing retained')
    for r in requirements.get('physical_printings',[]):
        e=by.get(r['entry_id']);p=next((p for p in (e or {}).get('printings',[]) if p['id']==r['printing_id']),None)
        if p is None:errors.append(r['printing_id']+': confirmed printing missing')
        elif list(physical_key(e['id'],p))!=r['physical_key']:errors.append(p['id']+': physical identity changed')
    return dict(ok=not errors,appearances_checked=len(requirements['appearances']),physical_printings_checked=len(requirements.get('physical_printings',[])),errors=errors)

def require_coverage(catalog,requirements=None):
    result=verify_coverage(catalog,requirements)
    if not result['ok']:raise ValueError('Cameo coverage failed: '+'; '.join(result['errors'][:10]))
    return result

def apply(catalog,verify=True):
    facts=json.loads(FACTS.read_text(encoding='utf-8'))
    by={e['id']:e for e in catalog['entries']};added=[];updated=[]
    for row in facts['records']:
        lang,release,num=row['identity'];e=by.get(row['entry_id'])
        if lang not in ('en','de'):raise ValueError('Cameo review cannot change this language')
        if e is None:
            if row['action']!='new_entry':raise ValueError('Existing research identity disappeared')
            # A separately imported host must be reconciled, never duplicated.
            ident=(lang,release,'collector',_number(num))
            if any(_identity(other)==ident for other in catalog['entries']):raise ValueError('Cameo host already indexed under another identity')
            e=dict(id=row['entry_id'],lang=lang,release=release,number=num,number_key=num,identifier_namespace='collector',printings=[],sources=[dict(id='release:'+lang+':'+release,name=row['set_name'],state='catalog_release')],links=[])
            catalog['entries'].append(e);by[e['id']]=e
        elif (e['lang'],e['release'],e['number'])!=tuple(row['identity']):raise ValueError('Reviewed cameo identity changed')
        elif row['action']=='promote_existing_research' and e.get('identity_status')=='provisional':
            e.setdefault('research_history',[]).append(dict(kind='before_cameo_review_1820',assessment={k:copy.deepcopy(e[k]) for k in ('metadata_state','identity_status','status_reason','release_date','rarity_code','rarity_state') if k in e}))
        e.update(name=row['name'],english=row['english'],set_name=row['set_name'],subject_dex=sorted(row['subject_dex']),cameo_dex=sorted(row['cameo_dex']),dex=(row['subject_dex'] or row['cameo_dex'])[0],category='standard' if row['subject_dex'] else 'cameo',metadata_state='approved',identity_status='documented',rarity_code=row['rarity_code'],rarity_state='known',rarity_namespace='western',rarity_label=row['rarity_code'].replace('_',' ').title(),rarity_family=rarity_family(row['rarity_code']),art_style=row['art_style'],art_style_state='verified',art_style_source=dict(method='reviewed_localized_card_face',source_urls=row['source_urls'],checked_on=facts['reviewed_on']),year_basis='card' if release in ('mep','smp') else 'set')
        e.update(date_fields(row['release_date'],'sourced_card',row['source_urls'][0]))
        e.pop('status_reason',None)
        normalize_rarity(e)
        # These are new hosts or previously image-less research records.
        if not e.get('image'):
            e.update(image=row['image']['filename'],image_source=row['image']['url'],image_language=lang)
        e['links']=list(dict.fromkeys(e.get('links',[])+row['source_urls']))
        e['cameo_review_1820']=dict(method='localized_face_and_release_review',evidence=row['cameo_evidence'],source_urls=row['source_urls'],reviewed_on=facts['reviewed_on'])
        for item in row['physical']:
            review=[]
            p=add_printing(e,item['physical'],dict(kind='cameo_review_1820',reviewed_on=facts['reviewed_on'],source_urls=item['source_urls'],evidence=item['evidence']),review)
            if p is None or p['id']!=item['printing_id']:raise ValueError('Reviewed printing identity changed: '+repr(review))
            p.update(label=printing_label(p),collection_status='documented',verification=dict(existence=dict(status='documented',source_urls=item['source_urls'],checked_on=facts['reviewed_on'],method='explicit_regional_cameo_review'),specimen=dict(status='not_inspected')))
            if item.get('image'):p.update(image=item['image']['filename'],image_scope='printing',image_source=item['image']['url'],image_language=lang)
            if item.get('candidate_product_id') and not p.get('market_confirmed'):
                candidate=dict(product_id=item['candidate_product_id'],name=row['english'],source_url=item['candidate_source_url'],provider_language=item['candidate_provider_language'],state='unverified_provider_candidate',physical_key=list(physical_key(e['id'],p)),checked_on=facts['reviewed_on'],note='Identity suggestion only; confirm the marketplace product and price series.')
                if p.get('market_candidate') and p['market_candidate']['product_id']!=candidate['product_id']:raise ValueError('Existing marketplace suggestion needs reconciliation')
                p['market_candidate']=candidate
            added.append(p['id'])
    for row in facts['link_updates']:
        e=by[row['entry_id']]
        if (e['lang'],e['release'],e['number'])!=tuple(row['identity']):raise ValueError('Species-link identity changed')
        e['cameo_dex']=sorted(set(e.get('cameo_dex',[]))|set(row['add_cameo_dex']))
        e['cameo_review_1820']=dict(method='localized_card_face',evidence=row['evidence'],source_urls=row['source_urls'],reviewed_on=facts['reviewed_on'])
        updated.append(e['id'])
    # One historical build fact gained an extra citation after 1.8.19 was
    # packaged. Keep the published provenance verbatim, with a narrow guard
    # against silently accepting any other prior-stage drift.
    ps={p['id']:(e,p) for e in catalog['entries'] for p in e['printings']}
    for row in facts.get('retained_provenance',[]):
        e,p=ps[row['printing_id']]
        if list(physical_key(e['id'],p))!=row['physical_key']:raise ValueError('Historical replay physical identity changed')
        if p.get('provenance')!=row['published_value']:
            actual=hashlib.sha256(json.dumps(p.get('provenance'),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
            if actual!=row['regenerated_value_sha256']:raise ValueError('Unreviewed historical provenance drift')
            p['provenance']=copy.deepcopy(row['published_value'])
    for e in catalog['entries']:
        keys=[physical_key(e['id'],p) for p in e['printings']]
        if len(keys)!=len(set(keys)):raise ValueError('Duplicate physical tuple: '+e['id'])
    catalog['cameo_review_1820']=dict(reviewed_on=facts['reviewed_on'],facts_sha256=hashlib.sha256(FACTS.read_bytes()).hexdigest(),added_entry_ids=sorted(r['entry_id'] for r in facts['records'] if r['action']=='new_entry'),promoted_entry_ids=sorted(r['entry_id'] for r in facts['records'] if r['action']=='promote_existing_research'),added_printing_ids=sorted(added),species_link_entry_ids=sorted(updated),pending=copy.deepcopy(facts['pending']),limits=facts['limits'])
    if verify:catalog['cameo_review_1820']['coverage']=require_coverage(catalog)
    return catalog

def refresh(catalog):
    from .new_sets import refresh as refresh_statistics
    refresh_statistics(catalog)
    catalog.update(revision='1.8.20',catalog_date='2026-11-13')

def main():
    from .catalog_enrich import make_sqlite
    path=ROOT/'data/catalog.json';catalog=json.loads(path.read_text(encoding='utf-8'))
    apply(catalog);refresh(catalog);write_json(path,catalog);make_sqlite(catalog)
    print(json.dumps(dict(statistics=catalog['statistics'],language_stats=catalog['language_stats'],coverage=catalog['cameo_review_1820']['coverage'])))

if __name__=='__main__':main()
