"""Idempotent, bounded physical-printing delta from reviewed evidence."""
import json,uuid
from pathlib import Path
from .printing_model import physical_key,printing_label
ROOT=Path(__file__).resolve().parents[1]
FACTS=ROOT/'data/research/printing_184/approved_variants.json'
def apply(catalog):
 facts=json.loads(FACTS.read_text(encoding='utf-8'));by={e['id']:e for e in catalog['entries']};added=[]
 for row in facts['rows']:
  e=by.get(row['entry_id'])
  if not e or (e['lang'],e['release'],e['number'])!=(row['lang'],row['release'],row['number']) or e['lang'] not in ('en','de'):raise ValueError('Reviewed physical identity changed')
  specs=[]
  for raw in row['expected']:
   spec=dict(finish=raw['finish'],pattern=raw['pattern'],edition='not_applicable',layout='standard',size='standard',material='paper',stamps_json='[]',print_state='standard');urls=[facts['sources'][k]['url'] for k in raw['evidence']]
   specs.append(spec|dict(status='documented',source_urls=urls,scope='regular_set'))
   if any(physical_key(e['id'],p)==physical_key(e['id'],spec) for p in e['printings']):continue
   pid='research_printing_'+uuid.uuid5(uuid.NAMESPACE_URL,'dogdex-reviewed-184:'+json.dumps(physical_key(e['id'],spec),ensure_ascii=False,separators=(',',':'))).hex
   p=spec|dict(id=pid,entry_id=e['id'],collection_status='documented',printed_rarity_state='inherit',printed_rarity_code=None,category=e['category'],image=e.get('image'),image_scope='entry',image_review=dict(kind='representative',status='unverified',image=e.get('image')),verification=dict(existence=dict(status='documented',source_urls=urls,checked_on=facts['reviewed_on'],method='card_specific_sources_and_native_inventory'),specimen=dict(status='not_inspected')),provenance=dict(method='printing_reconciliation_184',source_url=urls[0],source_urls=urls,reviewed_on=facts['reviewed_on'],provider_claim_locator=raw.get('provider_claim_locator')))
   p['label']=printing_label(p)
   if raw.get('provider_candidate_id'):p['market_candidate']=dict(product_id=raw['provider_candidate_id'],name=e.get('english'),source_url=raw.get('provider_url'),pattern=raw['pattern'],finish=raw['finish'],state='unverified_provider_candidate')
   e['printings'].append(p);added.append(pid)
  e['printing_specification']=dict(status='reviewed_regular_set',reviewed_on=facts['reviewed_on'],expected=specs,limits='Regular set printings only; product exclusives remain separate claims.')
  fact=dict(field='Regular-set physical printing specification',value=[dict(finish=p['finish'],pattern=p['pattern']) for p in specs],source_urls=list(dict.fromkeys(u for p in specs for u in p['source_urls'])),source_family='printing_reconciliation_184',disposition='documented',retrieved_on=facts['reviewed_on'],summary='Physical patterns corroborated separately from rarity, artwork, specimen/image inspection and marketplace mappings.')
  if not any(f.get('source_family')=='printing_reconciliation_184' for f in e.get('evidence',[])):e.setdefault('evidence',[]).append(fact)
 catalog['printing_reconciliation']=dict(revision='1.8.4',reviewed_entries=[r['entry_id'] for r in facts['rows']],added_printing_ids=[p['id'] for e in catalog['entries'] for p in e['printings'] if p.get('provenance',{}).get('method')=='printing_reconciliation_184'],expected_regular_set={lang:sum(len(r['expected']) for r in facts['rows'] if r['lang']==lang) for lang in ('en','de')},limits=facts['limits'])
 return added

def refresh_statistics(catalog):
 es=catalog['entries'];catalog['statistics'].update(printings=sum(len(e['printings']) for e in es),without_printings=sum(not e['printings'] for e in es))
 for lang in ('en','de','ja','ko'):catalog['language_stats'][lang].update(printings=sum(len(e['printings']) for e in es if e['lang']==lang),with_printings=sum(e['lang']==lang and bool(e['printings']) for e in es))
if __name__=='__main__':
 from .catalog_enrich import make_sqlite
 path=ROOT/'data/catalog.json';c=json.loads(path.read_text(encoding='utf-8'));added=apply(c);c.update(revision='1.8.4',catalog_date='2026-10-30');refresh_statistics(c);path.write_text(json.dumps(c,ensure_ascii=False,separators=(',',':')),encoding='utf-8');make_sqlite(c);print(json.dumps(dict(added=len(added),printings=c['statistics']['printings'])))
