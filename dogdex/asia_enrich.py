"""Offline 1.7 JA/KO reconciliation; no network or inferred physical variants."""
import copy,json
from .special_import import ROOT,add_printing
from .printing_model import legacy_label as printing_label
from .rarities import normalize

def apply(catalog):
    frozen=json.loads((ROOT/'data/research/asia_17/reviewed_facts.json').read_text(encoding='utf-8'))
    protected={key:copy.deepcopy([r for r in catalog[key]if r['lang']in('en','de')])for key in('entries','releases')}
    old_ids={e['id']:{p['id']for p in e['printings']}for e in catalog['entries']}
    by={e['id']:e for e in catalog['entries']};changes=[];added=[];review=[];prepared={}
    for e in by.values():
        if e['lang']in('ja','ko'):e.setdefault('identity_status','documented'if e['metadata_state']=='approved'else'provisional')
    for e in frozen['entries']:
        assert e['lang']in('ja','ko')and e['id']not in by
        by[e['id']]=copy.deepcopy(e);catalog['entries'].append(by[e['id']])
    release_keys={(r['lang'],r['release'])for r in catalog['releases']}
    for r in frozen['releases']:
        assert r['lang']in('ja','ko')
        if(r['lang'],r['release'])not in release_keys:catalog['releases'].append(copy.deepcopy(r));release_keys.add((r['lang'],r['release']))
    for row in frozen.get('release_updates',[]):
        assert row['lang']in('ja','ko');r=next(r for r in catalog['releases']if(r['lang'],r['release'])==(row['lang'],row['release']));r.update(copy.deepcopy(row['values']))
    for r in frozen['updates']:
        e=by[r['entry_id']];assert e['lang']in('ja','ko')
        before={k:copy.deepcopy(e.get(k))for k in r['values']};e.update(copy.deepcopy(r['values']))
        if before!=r['values']:changes.append(dict(entry_id=e['id'],kind=r['kind'],before=before,after=r['values'],source_urls=r.get('source_urls',[])))
    for r in frozen['printing_updates']:
        e=by[r['entry_id']];assert e['lang']in('ja','ko');p=next(p for p in e['printings']if p['id']==r['printing_id'])
        before={k:copy.deepcopy(p.get(k))for k in r['values']};p.update(copy.deepcopy(r['values']));p['label']=printing_label(p)
        changes.append(dict(entry_id=e['id'],printing_id=p['id'],kind=r.get('kind','physical_detail_qualified'),before=before,after=r['values'],source_urls=r['source_urls']))
    for i,r in enumerate(frozen['printings'],1):
        e=by[r['entry_id']];assert e['lang']in('ja','ko');n=len(e['printings']);p=add_printing(e,r['printing'],r['provenance'],review)
        if not p:raise ValueError('Incomplete 1.7 physical tuple admitted: '+e['id'])
        prepared['prepared:'+str(i)]=p['id']
        if len(e['printings'])>n:added.append(p['id'])
        # A promo printing's individual product date is independent of the series launch.
        if not r['printing'].get('release_date')and('promo'in e['release'].lower()or e['release']in('SMP','XYP','BWP','LP','PCGP','DPP','DPtP','M-P','S-P','SV-P','P')):p.update(date_mode='product',date_state='unresolved_product_date')
    def durable(value):
        if isinstance(value,dict):return{k:durable(v)for k,v in value.items()}
        if isinstance(value,list):return[durable(v)for v in value]
        return prepared.get(value,value)if isinstance(value,str)else value
    for eid,items in frozen['evidence'].items():by[eid].setdefault('evidence',[]).extend(durable(copy.deepcopy(items)))
    for eid,items in frozen['claims'].items():by[eid].setdefault('variant_claims',[]).extend(copy.deepcopy(items))
    for e in by.values():
        if e['lang']in('ja','ko'):normalize(e)
    exclusions=[dict(lang=r['lang'],name=r['raw'].get('name'),release=r['raw'].get('release_code'),number=r['raw'].get('number'),disposition=r['disposition'],reason=r['reason'],source_urls=[r['source_url']])for r in json.loads((ROOT/'data/research/asia_17/reconciliation.json').read_text(encoding='utf-8'))if r.get('family')in('official_ja','official_ko')and r['disposition']=='excluded_form']
    catalog.setdefault('reference_exclusions',[]).extend(exclusions)
    catalog['asia_research']=dict(basis_revision='1.6.0',observed_on=frozen['observed_on'],changes=changes,added_entry_ids=[e['id']for e in frozen['entries']],added_printing_ids=added,limits=frozen['limits'])
    for key,before in protected.items():assert before==[r for r in catalog[key]if r['lang']in('en','de')],key+' EN/DE changed'
    for eid,pids in old_ids.items():assert pids<={p['id']for p in by[eid]['printings']},eid+' lost physical IDs'
    return catalog
