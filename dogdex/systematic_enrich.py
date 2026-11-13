"""Apply reviewed regional facts reproducibly, retaining every existing user target.

This stage consumes offline evidence. It never invents finishes from rarity,
shared artwork or a different language's release. Runtime manual edits remain
an overlay owned by Collection/CatalogEditor and are never rebuilt here.
"""
import copy,json
from .special_import import ROOT,add_printing,date_fields,stable
from .rarities import normalize
from .printing_model import legacy_label as printing_label

FACTS=ROOT/'data/research/systematic/reviewed_facts.json'
def apply(catalog):
 facts=json.loads(FACTS.read_text(encoding='utf-8'));by={e['id']:e for e in catalog['entries']};releases={(r['lang'],r['release']):r for r in catalog['releases']};changes=[];review=[];added=[];new=[];inferred=[];candidates=[]
 def checked(record):
  e=by[record['entry_id']];assert e['lang']in('en','de');assert(e['lang'],e['release'],e['number'])==tuple(record[k]for k in('lang','release','number'));return e
 def change(e,values,record,kind):
  before={k:copy.deepcopy(e.get(k))for k in values};e.update(copy.deepcopy(values))
  if before!=values:changes.append(dict(kind=kind,entry_id=e['id'],before=before,after=copy.deepcopy(values),source_urls=record.get('source_urls',[])))
 for e in by.values():
  if e['lang']not in('en','de'):continue
  source=e.get('art_style_source')or{}
  if isinstance(source,dict)and source.get('inference')and e.get('art_style_state')=='verified':e['art_style_state']='inferred';inferred.append(e['id'])
  for p in e['printings']:
   if p.get('market_product_id'):
    candidate=dict(product_id=p.pop('market_product_id'),name=p.pop('market_name',None),source_url=p.pop('market_name_source',None),checks=dict(name='provider_name_screen_only',set='not_independently_checked',number='not_independently_checked',variant='not_independently_checked'),state='unverified_provider_candidate')
    p['market_candidate']=candidate;candidates.append(dict(entry_id=e['id'],printing_id=p['id'],**candidate))
  if not e.get('market_link_evidence'):e.pop('market_name',None)
 for r in facts.get('release_dates',[]):
  assert r['lang']in('en','de');release=releases[r['lang'],r['release']];old=release.get('date')or release.get('reference_date');release['superseded_provider_date']=old
  release.update(date=r.get('date'),reference_date=None,date_precision={4:'year',7:'month',10:'day'}.get(len(r.get('date')or'')),date_state='sourced_regional_period'if r.get('release_period')else r.get('evidence_kind','sourced_regional'),source_url=r['source_urls'][0],source_urls=r['source_urls'],evidence=r['evidence'])
  if r.get('release_period'):release['release_period']=r['release_period']
  for e in by.values():
   if(e['lang'],e['release'])!=(r['lang'],r['release'])or e.get('year_basis')in('card','product_source_claim'):continue
   values=date_fields(r.get('date'),release['date_state'],r['source_urls'][0]);values.update(date_evidence=r,date_note=r['evidence'])
   if r.get('release_period'):values['release_period']=r['release_period']
   change(e,values,r,'release_date')
 for r in facts.get('entry_updates',[]):
  e=checked(r);change(e,r['values'],r,'entry_fields');e.setdefault('research_corrections',[]).append({k:copy.deepcopy(v)for k,v in r.items()if k!='values'})
 for r in facts.get('card_dates',[]):
  e=checked(r);values=date_fields(r.get('date'),r.get('date_state','sourced_card'),r['source_urls'][0]);values.update(year_basis='card',date_mode='card',date_evidence=r,date_note=r['evidence']);change(e,values,r,'card_date')
 for r in facts.get('entries',[]):
  assert r['lang']in('en','de')and r['dex']in{sp['dex']for sp in catalog['roster']}
  rid=(r['lang'],r['release']);release=releases[rid];eid=stable('entry',['systematic_inventory',r['lang'],r['release'],r['number_key'],r['dex']])
  assert not any((e['lang'],e['release'],e['number_key'])==(r['lang'],r['release'],r['number_key'])for e in by.values())
  e=dict(id=eid,lang=r['lang'],release=r['release'],name=r['name'],english=r['english'],dex=r['dex'],subject_dex=r.get('subject_dex',[r['dex']]),cameo_dex=r.get('cameo_dex',[]),number=r['number'],number_key=r['number_key'],identifier_namespace='collector',set_name=release['name'],metadata_state='approved',category=r.get('category','standard'),year_basis='card'if r.get('release_date')else'set',rarity_code=r.get('rarity_code'),rarity_state='known'if r.get('rarity_code')else'not_printed',rarity_namespace=r['lang']+':'+r['release']+':reviewed_published_taxonomy',rarity_label='',rarity_family='other',art_style=r.get('art_style'),art_style_state='visually_checked'if r.get('image')else'sourced',art_style_source=dict(method='exact_regional_inventory',source_urls=r['source_urls'],inference=False),image=r.get('image'),image_source=r.get('image_source'),printings=[],sources=[dict(id='release:'+r['lang']+':'+r['release'],name=release['name'],state='catalog_release')],links=r['source_urls'],provenance=dict(kind='systematic_native_identity',evidence=r['evidence'],source_urls=r['source_urls']),**date_fields(r.get('release_date')or release.get('date'),'sourced_card'if r.get('release_date')else release.get('date_state','unresolved'),r['source_urls'][0]))
  if r.get('image'):
   assert(ROOT/'data/images'/r['image']).is_file();e['image_evidence']=r.get('image_evidence')
  if release.get('release_period')and not e['release_date']:e['release_period']=release['release_period']
  for raw in r['printings']:
   p=add_printing(e,raw,dict(kind='exact_native_identity_and_printing',source_url=r['source_urls'][0],source_urls=r['source_urls'],evidence=r['evidence']),review);assert p;added.append(p['id'])
  assert e['printings'];normalize(e);catalog['entries'].append(e);by[eid]=e;new.append(eid)
 for r in facts.get('printings',[]):
  e=checked(r);before=len(e['printings']);p=add_printing(e,r['printing'],dict(kind='manufacturer_native_pack_checkbox',source_url=r['source_urls'][0],source_urls=r['source_urls'],source_sha256=r.get('source_sha256'),page=r.get('page'),evidence=r['evidence'],checkbox_evidence=r.get('checkbox_evidence')),review);assert p
  if len(e['printings'])>before:added.append(p['id'])
 for r in facts.get('conflicts',[]):
  if r.get('printing_id'):
   e=by[r['entry_id']];p=next(p for p in e['printings']if p['id']==r['printing_id']);p['audit_status']=r['state'];p['audit_note']=r.get('next_action')
 for e in by.values():
  if e['lang']in('en','de'):
   normalize(e)
   # The gate also covers any future facts that add marketplace IDs after import.
   for p in e['printings']:
    if p.get('market_product_id'):
     candidate=dict(product_id=p.pop('market_product_id'),name=p.pop('market_name',None),source_url=p.pop('market_name_source',None),checks=dict(name='not_independently_checked',set='not_independently_checked',number='not_independently_checked',variant='not_independently_checked'),state='unverified_provider_candidate');p['market_candidate']=candidate;candidates.append(dict(entry_id=e['id'],printing_id=p['id'],**candidate))
   source=e.get('art_style_source')or{}
   assert not(isinstance(source,dict)and source.get('inference')and e.get('art_style_state')=='verified')
 catalog['systematic_research']=dict(observed_on=facts['observed_on'],baseline_revision=facts['basis_revision'],changes=changes,added_entry_ids=new,added_printing_ids=added,inference_status_entry_ids=inferred,marketplace_candidates=candidates,conflicts=facts.get('conflicts',[]),review=review)
 return catalog
