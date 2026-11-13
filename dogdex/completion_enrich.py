"""Offline 1.6 evidence admission; stable identities and physical claims are separate."""
import copy,json
from .special_import import ROOT,add_printing
from .rarities import normalize
from .printing_model import legacy_label as printing_label
def apply(catalog):
 f=json.loads((ROOT/'data/research/completion_16/reviewed_facts.json').read_text(encoding='utf-8'));by={e['id']:e for e in catalog['entries']};ret={e['id']:e for e in catalog.get('retired_entries',[])}
 for e in by.values():
  if e['lang']in('en','de'):e['identity_status']='documented'if e['metadata_state']=='approved'else'provisional'
 for r in f['restorations']:
  e=ret.pop(r['entry_id']);e.update(copy.deepcopy(r['values']));by[e['id']]=e;catalog['entries'].append(e)
 catalog['retired_entries']=list(ret.values());changes=[]
 for e in f['entries']:
  assert e['id']not in by and e['lang']in('en','de');by[e['id']]=copy.deepcopy(e);catalog['entries'].append(by[e['id']])
 existing={(r['lang'],r['release'])for r in catalog['releases']}
 for r in f['releases']:
  if (r['lang'],r['release'])not in existing:catalog['releases'].append(copy.deepcopy(r));existing.add((r['lang'],r['release']))
 for r in f['updates']:
  e=by[r['entry_id']];assert e['lang']in('en','de')and(e['lang'],e['release'],e['number'])==tuple(r[k]for k in('lang','release','number'))
  before={k:copy.deepcopy(e.get(k))for k in r['values']};e.update(copy.deepcopy(r['values']))
  if before!=r['values']:changes.append(dict(entry_id=e['id'],kind=r['kind'],before=before,after=r['values'],source_urls=r.get('source_urls',[])))
 review=[];added=[]
 for r in f['printings']:
  e=by[r['entry_id']];n=len(e['printings']);p=add_printing(e,r['printing'],r['provenance'],review)
  if not p:raise ValueError('Reviewed printing failed admission: '+r['entry_id'])
  if len(e['printings'])>n:
   added.append(p['id'])
   if not r['printing'].get('release_date')and r.get('source_product'):p.update(date_mode='product',date_state='unresolved_product_date')
  if r.get('source_product')and not any(s['id']==r['source_product']['id']for s in p.get('sources',[])):p.setdefault('sources',[]).append(copy.deepcopy(r['source_product']))
  if p['finish']=='non_holo'and r['provenance'].get('kind')=='explicit_language_product_physical_tuple':
   p.update(audit_status='documented_product_exception',audit_evidence=copy.deepcopy(r['provenance']))
 for r in f['printing_updates']:
  e=by[r['entry_id']];p=next(p for p in e['printings']if p['id']==r['printing_id']);p.update(copy.deepcopy(r['values']));p['label']=printing_label(p)
 for eid,items in f['evidence'].items():
  if eid in by:by[eid]['evidence']=copy.deepcopy(items)
 for eid,claims in f['variant_claims'].items():
  if eid in by:by[eid]['variant_claims']=copy.deepcopy(claims)
 for e in by.values():
  if e['lang']in('en','de'):normalize(e)
 wiki=json.loads((ROOT/'data/research/reconciliation_15/inventory_reconciliation.json').read_text(encoding='utf-8'))
 catalog['reference_exclusions']=[dict(lang=r['lang'],name=r['name'],release=r.get('reference_release'),number=r['number'],disposition=r['status'],source_urls=[u for u in(r.get('source_url'),r.get('availability_source'))if u],reason='Documented language exclusion'if r['status']=='not_released_in_German'else'Excluded form or other-language reference; retained scope decision')for r in wiki['rows']if r['status']in('not_released_in_German','outside_form_scope','foreign_language_only')]
 catalog['completion_research']=dict(basis_revision='1.5.0',observed_on=f['observed_on'],changes=changes,added_entry_ids=[e['id']for e in f['entries']],restored_entry_ids=[r['entry_id']for r in f['restorations']],added_printing_ids=added,printing_updates=len(f['printing_updates']),limits=f['limits'])
 catalog['scope'].update(retired_entries=len(catalog['retired_entries']),retired_printings=sum(len(e['printings'])for e in catalog['retired_entries']))
 return catalog
