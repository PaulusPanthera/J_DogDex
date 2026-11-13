import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
"""Offline inventory measurements; populated fields never imply factual verification."""
import collections,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/research/systematic'
def dump(path,value):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def digest(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def number(v):return re.sub(r'(^|[A-Z])0+(?=\d)',r'\1',str(v).split('/')[0].upper())
def measure(c):
 es=c['entries'];issues=[];groups=collections.defaultdict(list)
 for e in es:groups[e['lang'],e['release'],e['identifier_namespace'],e['number_key']if e['number']=='Unnumbered'else number(e['number'])].append(e)
 for k,v in groups.items():
  if len(v)>1:issues.append(dict(kind='duplicate_identity_candidate',identity=k,entry_ids=[e['id']for e in v]))
 for e in es:
  if e['lang']not in('en','de'):continue
  for field in ('id','name','english','release','number','identifier_namespace','sources'):
   if not e.get(field):issues.append(dict(kind='missing_core_field',entry_id=e['id'],field=field))
  if e.get('date_precision')=='day' and e.get('release_date','')>'2026-10-28':issues.append(dict(kind='release_after_scope_cutoff',entry_id=e['id'],value=e['release_date']))
  if not e.get('release_date'):issues.append(dict(kind='missing_numeric_date',entry_id=e['id'],period=e.get('release_period')))
  if e.get('date_state')=='provider_reference':issues.append(dict(kind='unqualified_date',entry_id=e['id'],value=e.get('release_date')))
  if e['release']in('basep','np','dpp','hgssp','bwp','xyp','smp','swshp','svp','mep')and e.get('year_basis')not in('card','product_source_claim'):issues.append(dict(kind='promo_series_date_candidate',entry_id=e['id'],value=e.get('release_date')))
  a=e.get('art_style_source')or{}
  if isinstance(a,dict)and a.get('inference')and e.get('art_style_state')=='verified':issues.append(dict(kind='inference_labeled_verified',entry_id=e['id']))
  if e['category']=='cameo'and e.get('subject_dex'):issues.append(dict(kind='primary_subject_marked_cameo',entry_id=e['id']))
  if not e['printings']:issues.append(dict(kind='no_accepted_printing',entry_id=e['id']))
  for p in e['printings']:
   if p['finish']=='non_holo'and e.get('rarity_code')in('rare_holo','rare_holo_gx','rare_holo_EX_uppercase','rare_holo_ex_lowercase','rare_holo_v','rare_holo_vmax','rare_holo_vstar','illustration_rare','special_illustration_rare','hyper_rare','ultra_rare','rainbow_rare')and not p.get('world_championship_year')and p.get('audit_status')!='documented_product_exception':issues.append(dict(kind='foil_rarity_nonholo_candidate',entry_id=e['id'],printing_id=p['id'],state='product_exception_requires_own_evidence'))
   if p['finish']=='non_holo'and p['pattern']!='none':issues.append(dict(kind='nonholo_with_foil_pattern',entry_id=e['id'],printing_id=p['id']))
   if p.get('market_product_id')and not p.get('market_reference_state')=='verified':issues.append(dict(kind='unverified_market_product_reference',entry_id=e['id'],printing_id=p['id']))
 for r in c.get('market_research_holds',[]):issues.append(dict(kind='rejected_market_reference',entry_id=r['entry_id'],printing_id=r['printing_id']))
 def stats(rows):return dict(records=len(rows),printings=sum(len(e['printings'])for e in rows),missing_date=sum(not e.get('release_date')for e in rows),known_date_period=sum(bool(e.get('release_period'))for e in rows),provisional_date=sum(e.get('date_state')=='provider_reference'for e in rows),unclassified_artwork=sum(not e.get('art_style')for e in rows),missing_image=sum(not e.get('image')for e in rows),unresolved_rarity=sum(e['rarity_state']=='unresolved'for e in rows),without_printings=sum(not e['printings']for e in rows),date_states=dict(collections.Counter(e.get('date_state')or'unresolved'for e in rows)))
 sources={}
 for e in es:
  for raw in e['sources']+[r for p in e['printings']for r in p.get('sources',[])]:
   key=e['lang'],raw['id'];g=sources.setdefault(key,dict(lang=e['lang'],source_id=raw['id'],name=raw['name'],entry_ids=set(),printing_ids=set()));g['entry_ids'].add(e['id'])
   for p in e['printings']:
    if raw in e['sources']or any(r['id']==raw['id']for r in p.get('sources',[])):g['printing_ids'].add(p['id'])
 source_rows=[{k:v for k,v in g.items()if k not in('entry_ids','printing_ids')}|dict(records=len(g['entry_ids']),printings=len(g['printing_ids']),entry_ids=sorted(g['entry_ids']),printing_ids=sorted(g['printing_ids']))for g in sources.values()]
 fields='id lang dex subject_dex cameo_dex release set_name name english number number_key identifier_namespace category release_date release_period date_precision date_state rarity_code rarity_state art_style art_style_state'.split()
 return dict(revision=c['revision'],sources=source_rows,inventory_notes='Species rows include every tracked primary/background appearance. Source rows use unique card and printing IDs within each source; cross-source/species sums need not equal unique language totals.',languages={lang:stats([e for e in es if e['lang']==lang])for lang in('en','de','ja','ko')},species=[dict(lang=lang,dex=r['dex'],name=r['name'],**stats([e for e in es if e['lang']==lang and r['dex']in(set(e.get('subject_dex')or[])|set(e.get('cameo_dex')or[])or{e['dex']})]))for lang in('en','de','ja','ko')for r in c['roster']],releases=[dict(lang=lang,release=rel,**stats([e for e in es if(e['lang'],e['release'])==(lang,rel)]))for lang,rel in sorted({(e['lang'],e['release'])for e in es})],issue_counts=dict(collections.Counter(i['kind']for i in issues)),issues=issues,inventory=[{k:e.get(k)for k in fields}|dict(printing_ids=[p['id']for p in e['printings']],source_urls=e['links'])for e in es])
def baseline(c):
 dump(OUT/'baseline_inventory.json',measure(c));dump(OUT/'upgrade_baseline.json',dict(revision=c['revision'],entries={e['id']:[p['id']for p in e['printings']]for e in c['entries']},secondary_language_sha256={lang:digest([e for e in c['entries']if e['lang']==lang])for lang in('ja','ko')}))
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--baseline',action='store_true');a=p.parse_args();c=json.load(open(ROOT/'data/catalog.json',encoding='utf-8'))
 if a.baseline:baseline(c)
 else:dump(OUT/'current_inventory.json',measure(c))
 print(json.dumps(measure(c)['languages'],ensure_ascii=False))
