"""Reviewed EN/DE 1.8.17 inventory. No personal files or inferred variants."""
import copy,hashlib,json
from pathlib import Path
from .special_import import add_printing,date_fields,stable,write_json
from .printing_model import physical_key,printing_label
from .rarities import normalize
ROOT=Path(__file__).resolve().parents[1]
FACTS=ROOT/'data/research/new_sets_1817/facts.json'

def evidence(obj,field,value,urls,note):
    key='evidence' if isinstance(obj.get('evidence',[]),list) else 'new_sets_evidence'
    row=dict(field=field,value=copy.deepcopy(value),source_urls=list(urls),summary=note,
             source_family='new_sets_1817',disposition='documented',retrieved_on='2026-11-11')
    records=obj.setdefault(key,[])
    if row not in records:records.append(row)

def apply(catalog):
    facts=json.loads(FACTS.read_text(encoding='utf-8'));by={e['id']:e for e in catalog['entries']}
    releases={(r['lang'],r['release']):r for r in catalog['releases']};touched=[]
    for row in facts['releases']:
        key=row['lang'],row['release'];r=releases.get(key)
        if r is None:r=dict(lang=row['lang'],release=row['release']);catalog['releases'].append(r);releases[key]=r
        if r.get('date') and r['date']!=row['date']:
            evidence(r,'Superseded release date',{k:r.get(k) for k in ('date','date_state','source_url','research_note')},r.get('source_urls') or [],'A later retail product date does not define the subset booster release.')
        r.update(name=row['name'],date=row['date'],date_precision='day',date_state='sourced_regional',source_url=row['source_urls'][0],source_urls=row['source_urls'],abbreviation={'official':row['market_code']})
        r.pop('release_period',None)
        evidence(r,'Regional expansion release',row['date'],row['source_urls'],'Released regional inventory; independently numbered promos remain separate.')
        sid='release:'+row['lang']+':'+row['release'];meta=catalog.setdefault('source_metadata',{}).setdefault(sid,{})
        meta.update(canonical_set_id='western:'+row['release'])
        if row['release']=='30th-c':meta.update(source_role='subset',parent_source_id='release:'+row['lang']+':30th',subset_key='classic_collection',subset_name='Classic Collection',subset_order=10,numbering_namespace='original_printed_collector_number',aliases=['30th Classic Collection','30 Jahre Classic Collection'])
        else:meta.update(source_role='numbered_set',aliases=[row['market_code'],'Delta-Herrschaft' if row['release']=='me06' else '30 Jahre','Delta Reign' if row['release']=='me06' else '30th Celebration'])
    for row in facts['entries']:
        eid=row.get('entry_id') or stable('entry',['new_sets_1817',row['lang'],row['release'],row['number']]);e=by.get(eid)
        if e is None:
            if any((x['lang'],x['release'],x['number'])==(row['lang'],row['release'],row['number']) for x in catalog['entries']):raise ValueError('Unreviewed import identity collision')
            e=dict(id=eid,printings=[],sources=[],links=[],year_basis='set');catalog['entries'].append(e);by[eid]=e
        else:
            if (e['lang'],e['release'])!=(row['lang'],row['release']) or e['number'] not in (row['number'],row.get('previous_number')):raise ValueError('Reviewed identity changed: '+eid)
            if row.get('entry_id') and not any(v.get('source_family')=='new_sets_1817' and v.get('field')=='Previous assessment' for v in e.get('evidence',[])):
                evidence(e,'Previous assessment',{k:e.get(k) for k in ('number','rarity_code','rarity_state','identity_status','release_date','date_source','date_note','date_evidence','status_reason')},e.get('links',[]),'Historical selection retained; the released regional identity is now selected separately.')
        rel=releases[row['lang'],row['release']]
        e.update({k:copy.deepcopy(row[k]) for k in ('lang','release','number','name','english','dex','subject_dex','cameo_dex','category','art_style','rarity_code')})
        e.update(number_key=str(int(row['number'])),identifier_namespace='collector',set_name=rel['name'],metadata_state='approved',identity_status='documented',rarity_state='known',rarity_namespace=row['lang']+':'+row['release']+':reviewed_printed_rarity',rarity_family='common' if row['rarity_code']=='common' else 'rare',art_style_state='verified',art_style_source=dict(method='reviewed_card_face',source_urls=row['source_urls'],reviewed_on=facts['reviewed_on']),provider_identifiers=dict(tcgdex=row['provider_id']),date_evidence=dict(date=rel['date'],source_urls=rel['source_urls']),**date_fields(rel['date'],'sourced_regional',rel['source_url']))
        for key in ('status_reason','date_note','release_period'):e.pop(key,None)
        if row.get('printed_identifier'):e['printed_identifier']=row['printed_identifier']
        sid='release:'+e['lang']+':'+e['release']
        if not any(s['id']==sid for s in e['sources']):e['sources'].insert(0,dict(id=sid,name=e['set_name'],state='catalog_release'))
        for s in e['sources']:
            if s['id']==sid:s['name']=e['set_name']
        e['links']=list(dict.fromkeys(e.get('links',[])+row['source_urls']))
        if row.get('image') and not e.get('image'):
            im=row['image'];assert hashlib.sha256((ROOT/'data/images'/im['filename']).read_bytes()).hexdigest()+'.webp'==im['filename']
            e.update(image=im['filename'],image_source=im['source_url'],image_language=im['image_language'],image_review=dict(kind='representative',status='unverified',image=im['filename'],image_language=im['image_language']))
        if row.get('cameo_note'):e['cameo_source']=dict(method='native_face_review',source_urls=row['source_urls'],evidence=row['cameo_note'])
        normalize(e)
        evidence(e,'Reviewed regional identity',{k:row[k] for k in ('number','name','rarity_code','art_style')},row['source_urls'],row.get('number_note') or row.get('cameo_note') or 'Regional card identity; physical finishes specified separately.')
        if row.get('rarity_note'):evidence(e,'Original printed rarity',row['rarity_code'],row['source_urls'],row['rarity_note'])
        if e['release']=='30th' and e['printings']:
            if len(e['printings'])!=1 or e['printings'][0]['finish']!='holo':raise ValueError('Unexpected 30th tuple; manual review required')
            p=e['printings'][0]
            if json.loads(p.get('stamps_json','[]'))!=['30th_anniversary']:
                evidence(e,'Existing anniversary printing qualified',dict(printing_id=p['id'],previous_physical_key=list(physical_key(eid,p))),row['source_urls'],'Visible anniversary mark qualifies the existing target; stable ID retained.')
                p['stamps_json']='["30th_anniversary"]'
        review=[]
        for spec in row['printings']:
            p=add_printing(e,spec,dict(kind='new_sets_1817',source_url=row['source_urls'][0],source_urls=row['source_urls'],reviewed_on=facts['reviewed_on'],evidence=row.get('physical_note') or 'Manufacturer all-foil expansion; explicit anniversary face.'),review)
            if p is None:raise ValueError('Physical tuple rejected: '+repr(review))
            p.update(label=printing_label(p),collection_status='documented',verification=dict(existence=dict(status='documented',source_urls=row['source_urls'],checked_on=facts['reviewed_on'],method='explicit_regional_inventory'),specimen=dict(status='not_inspected')))
            if not p.get('image') and e.get('image'):p.update(image=e['image'],image_scope='entry')
            if row.get('market_candidate') and not p.get('market_confirmed'):p['market_candidate']=dict(product_id=row['market_candidate'],name=e['english'],source_url=row['provider_url'],state='unverified_provider_candidate',note='Check exact collector number; IR provider IDs may repeat ordinary cards.')
        keys=[physical_key(eid,p) for p in e['printings']]
        if len(keys)!=len(set(keys)):raise ValueError('Duplicate physical tuple: '+eid)
        touched.append(eid)
    catalog['new_sets_1817']=dict(version=facts['version'],reviewed_on=facts['reviewed_on'],facts_sha256=hashlib.sha256(FACTS.read_bytes()).hexdigest(),entry_ids=sorted(touched),added_entry_ids=sorted(set(touched)-set(facts['baseline_entry_ids'])),added_printing_ids=sorted({p['id'] for eid in touched for p in by[eid]['printings']}-set(facts['baseline_printing_ids'])),limits=facts['limits'],gallery_review=facts['gallery_review'])
    return catalog

def refresh(c):
    from .scope import is_cameo
    es=c['entries'];ps=[p for e in es for p in e['printings']];c.update(revision='1.8.17',catalog_date='2026-11-11')
    c['statistics']=dict(entries=len(es),printings=len(ps),without_printings=sum(not e['printings'] for e in es),missing_images=sum(not e.get('image') for e in es),full_art_entries=sum(e.get('art_style')=='full_art' for e in es),cameo_entries=sum(is_cameo(e) for e in es),jumbo_printings=sum(p['size']=='oversized' or p['material']=='metal' for p in ps),missing_release_dates=sum(not e.get('release_date') for e in es),reference_dates=sum(e.get('date_state')=='provider_reference' for e in es))
    c['language_stats']={lang:dict(entries=sum(e['lang']==lang for e in es),with_printings=sum(e['lang']==lang and bool(e['printings']) for e in es),printings=sum(len(e['printings']) for e in es if e['lang']==lang),full_art=sum(e['lang']==lang and e.get('art_style')=='full_art' for e in es),cameos=sum(e['lang']==lang and is_cameo(e) for e in es)) for lang in ('en','de','ja','ko')}
    c['used_images']=sorted({im for e in es for im in [e.get('image'),*(p.get('image') for p in e['printings'])] if im and (ROOT/'data/images'/im).is_file()})
    c.setdefault('research_summary',{}).update(accepted_set_dates=sum(bool(r.get('date')) for r in c['releases']),reference_only_set_dates=sum(not r.get('date') and bool(r.get('reference_date')) for r in c['releases']),unresolved_set_dates=sum(not r.get('date') and not r.get('reference_date') for r in c['releases']))
    c['release_research_summary']={lang:dict(total=len(rs),dated=sum(bool(r.get('date')) for r in rs),exact_day=sum(bool(r.get('date')) and len(r['date'])==10 for r in rs),month=sum(bool(r.get('date')) and len(r['date'])==7 for r in rs),year=sum(bool(r.get('date')) and len(r['date'])==4 for r in rs),reference_only=sum(not r.get('date') and bool(r.get('reference_date')) for r in rs),no_date=sum(not r.get('date') and not r.get('reference_date') for r in rs)) for lang in ('en','de','ja','ko') for rs in [[r for r in c['releases'] if r['lang']==lang]]}

def main():
    from .catalog_enrich import make_sqlite
    path=ROOT/'data/catalog.json';c=json.loads(path.read_text(encoding='utf-8'));apply(c);refresh(c);write_json(path,c);make_sqlite(c);print(json.dumps(c['statistics']))
if __name__=='__main__':main()
