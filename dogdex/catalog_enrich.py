"""Reproduce DogDex from the immutable original catalog and sourced facts.

Run with --images when preparing a release (Pillow is a build dependency only).
The packaged app and Windows launcher need only the bundled Python standard library.
"""
import argparse,collections,datetime,hashlib,json,re,sqlite3
from pathlib import Path
from . import prepare
from .scope import apply_scope,is_cameo
from .rarities import apply as apply_rarities
from .western_enrich import apply as apply_western
from .coverage_enrich import apply as apply_coverage
from .collector import physical_key
from .systematic_enrich import apply as apply_systematic
from .reconciliation_enrich import apply as apply_reconciliation
from .completion_enrich import apply as apply_completion
from .asia_enrich import apply as apply_asia
from .printing_enrich import apply as apply_printing_review
from .printing_corrections import apply as apply_printing_corrections
from .identity_corrections import apply as apply_identity_corrections
from .catalog_corrections import apply as apply_catalog_corrections
from .new_sets import apply as apply_new_sets, refresh as refresh_new_sets
from .reference_review import apply as apply_reference_review, refresh as refresh_reference_review
from .special_import import ROOT,FACTS,load,stable,norm,number,date_fields,add_printing,import_special,acquire_images,write_json

ART_RULE_SOURCE='https://www.pokemon.com/uk/news/pokemon-tcg-scarlet-and-violet-revamps-pokemon-tcg-card-aesthetic'
def dates(catalog):
 data=load('release_dates.json');lookup={(r['lang'],r['release']):r for r in data['releases']}
 for e in catalog['entries']:
  if e.get('year_basis')=='card':continue
  record=lookup.get((e['lang'],e['release']))
  if record:
   # Display the sourced regional product name instead of an importer set code.
   # Keep source identifiers stable so saved source views and collections survive.
   if e['set_name']==e['release'] and record.get('name') and record['name']!=e['release']:
    names=list(dict.fromkeys(part.strip() for part in record['name'].split(' / ') if 'ポケモンセンターオンライン' not in part))
    e['set_name']=' / '.join(names)
    for product in e['sources']:
     if product['id']=='release:'+e['lang']+':'+e['release'] or product.get('state')=='catalog_release':product['name']=e['set_name']
   value=record.get('date') or record.get('reference_date');state=record.get('date_state') if record.get('date') else 'provider_reference' if value else 'unresolved';source=record.get('source_url') if record.get('date') else record.get('reference_source_url')
   # An individual product year claim is a distinct source from a broad series.
   if e.get('year_basis')=='product_source_claim' and e.get('release_date') and (not value or e['release_date'][:4]>value[:4]):continue
   e.update(date_fields(value,state,source));e['date_evidence']=record.get('evidence');e['date_note']=record.get('research_note') or record.get('unresolved_kind')
 catalog['releases']=data['releases'];catalog['release_research_summary']=data['statistics']

def artwork_and_printings(catalog):
 data=load('artwork_printings.json');byid={e['id']:e for e in catalog['entries']};review=[];added=[]
 for record in data['printing_additions']:
  e=byid.get(record['entry_id'])
  if not e or (e['lang'],e['release'],e['number'])!=(record['lang'],record['release'],record['number']):raise ValueError('Japanese tuple identity changed: '+record['entry_id'])
  before=len(e['printings']);p=add_printing(e,record['printing'],dict(kind='dedicated_regional_source_tuple',source_url=record['source_url'],source_sha256=record['source_sha256'],identity_basis=record['identity_basis'],edition_basis=record['edition_basis'],raw_tuple=record['raw_tuple']),review)
  if p and len(e['printings'])>before:added.append(p['id'])
 for record in data['artwork']:
  e=byid.get(record['entry_id'])
  if not e or (e['lang'],e['release'],e['number'])!=(record['lang'],record['release'],record['number']):raise ValueError('Artwork identity changed')
  e.update(art_style='full_art',art_style_state='verified',art_style_source=record)
 # Additional cameo cards can have explicit full-art checklist evidence too.
 extracted=load('full_art_extracted_rows.json');index={}
 for r in extracted:
  if r['region']=='en':index[norm(r['set_name']),number(r['number']),norm(r['card_name'])]=r
 for e in catalog['entries']:
  if e.get('art_style')=='full_art' or e['lang']!='en':continue
  row=index.get((norm(e['set_name']),number(e['number']),norm(e['english'])))
  if row:e.update(art_style='full_art',art_style_state='verified',art_style_source=dict(method='exact_curated_full_art_list',evidence=row,inference=False))
  elif re.match(r'^sv\d',e['release']) and e['rarity_state']=='known' and e['rarity_code'] in ('ultra_rare','illustration_rare','special_illustration_rare','hyper_rare'):
   e.update(art_style='full_art',art_style_state='verified',art_style_source=dict(method='official_scarlet_violet_rarity_artwork_definition',source_url=ART_RULE_SOURCE,inference=True,rarity_code=e['rarity_code']))
 english={(e['release'],e['number_key'],tuple(e.get('subject_dex',[])),norm(e['english'])):e for e in catalog['entries'] if e['lang']=='en' and e.get('art_style')=='full_art'}
 for e in catalog['entries']:
  if e['lang']!='de' or e.get('art_style')=='full_art':continue
  en=english.get((e['release'],e['number_key'],tuple(e.get('subject_dex',[])),norm(e['english'])))
  if en:e.update(art_style='full_art',art_style_state='verified',art_style_source=dict(method='identical_localized_card_identity_transfer',english_entry_id=en['id'],source=en['art_style_source'],inference=True))
 catalog['printing_enrichment_summary']=dict(japanese_added=len(added),review=review,identity_holds=data.get('printing_review',[]))

def market(catalog):
 connection=sqlite3.connect((ROOT/'data/catalog.sqlite3').as_uri()+'?mode=ro',uri=True);ids=collections.defaultdict(set)
 for pid,raw in connection.execute("SELECT variant_id,raw_tuple_json FROM variant_claims WHERE review_state='approved' AND variant_id IS NOT NULL AND generated=0"):
  value=json.loads(raw).get('thirdParty',{}).get('cardmarket')
  if type(value) is int:ids[pid].add(value)
 connection.close()
 product_facts=load('market_names.json');product_names=product_facts['products']
 examples={('base1','28'):('Growlithe','BS','Base-Set','Growlithe-V1-BS28','Growlithe-V2-BS28'),('base1','68'):('Vulpix','BS','Base-Set','Vulpix-V1-BS68','Vulpix-V2-BS68'),('base4','42'):('Growlithe','B2','Base-Set-2','Growlithe-B242','Growlithe-B242')}
 market_holds=[]
 for e in catalog['entries']:
  for p in e['printings']:
   if len(ids[p['id']])==1:p['market_product_id']=next(iter(ids[p['id']]))
  for p in e['printings']:
   name=product_names.get(str(p.get('market_product_id')))
   if name and e['lang'] in ('en','de') and norm(e['english']) not in norm(name['name']) and norm(name['name']) not in norm(e['english']):
    market_holds.append(dict(entry_id=e['id'],printing_id=p['id'],rejected_product_id=p.pop('market_product_id'),expected_name=e['english'],rejected_name=name['name'],source_url=product_facts['source_url'],reason='Official marketplace product name conflicts with the accepted card identity.'))
    p.pop('market_name',None);p.pop('market_name_source',None)
    continue
   if name:p['market_name']=name['name'];p['market_name_source']=product_facts['source_url']
  names={p['market_name'] for p in e['printings'] if p.get('market_name')}
  if len(names)==1:e['market_name']=next(iter(names))
  known=examples.get((e['release'],number(e['number']))) if e['lang'] in ('en','de') else None
  if known:
   name,code,series,normal,shadowless=known;e.update(market_name=name,cardmarket_code=code,cardmarket_search=f'{name} ({number(e["number"])} {code})',cardmarket_url='https://www.cardmarket.com/en/Pokemon/Products/Singles/'+series+'/'+normal)
   for p in e['printings']:
    p['cardmarket_url']='https://www.cardmarket.com/en/Pokemon/Products/Singles/'+series+'/'+(shadowless if p['layout']=='shadowless' else normal)
   e['market_link_evidence']=dict(method='researched_marketplace_identity',note='Listing page; choose language and edition among offers. No live price or offer availability implied.',source_url=e['cardmarket_url'])
 catalog['market_research_holds']=market_holds

SCHEMA='''
PRAGMA foreign_keys=ON;
CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL);
CREATE TABLE entries(id TEXT PRIMARY KEY,lang TEXT NOT NULL,release_key TEXT NOT NULL,printed_identifier TEXT NOT NULL,card_name TEXT NOT NULL,release_date TEXT,date_precision TEXT,date_state TEXT,rarity_code TEXT,rarity_state TEXT,art_style TEXT,subject_dex_json TEXT,cameo_dex_json TEXT,record_json TEXT NOT NULL);
CREATE TABLE printings(id TEXT PRIMARY KEY,entry_id TEXT NOT NULL REFERENCES entries(id),finish TEXT,pattern TEXT,edition TEXT,layout TEXT,size TEXT,material TEXT,stamps_json TEXT,print_state TEXT,release_date TEXT,image TEXT,record_json TEXT NOT NULL);
CREATE TABLE releases(id TEXT PRIMARY KEY,lang TEXT,release_key TEXT,name TEXT,release_date TEXT,date_precision TEXT,date_state TEXT,source_url TEXT);
CREATE TABLE facts(kind TEXT,subject_id TEXT,payload_json TEXT,source_url TEXT);
CREATE INDEX printing_entry ON printings(entry_id);
CREATE INDEX entries_language_release ON entries(lang,release_key);
'''
def make_sqlite(catalog):
 path=ROOT/'data/catalog-collector.sqlite3';tmp=path.with_suffix('.sqlite3.tmp');tmp.unlink(missing_ok=True);c=sqlite3.connect(tmp);c.executescript(SCHEMA)
 dump=lambda v:json.dumps(v,ensure_ascii=False,separators=(',',':'))
 c.execute('INSERT INTO metadata VALUES(?,?)',('revision',catalog['revision']));c.execute('INSERT INTO metadata VALUES(?,?)',('original_catalog_sha256',catalog['catalog_sha256']))
 for e in catalog['entries']:
  c.execute('INSERT INTO entries VALUES('+','.join('?'*14)+')',(e['id'],e['lang'],e['release'],e['number'],e['name'],e.get('release_date'),e.get('date_precision'),e.get('date_state'),e['rarity_code'],e['rarity_state'],e.get('art_style'),dump(e.get('subject_dex',[])),dump(e.get('cameo_dex',[])),dump(e)))
  for p in e['printings']:c.execute('INSERT INTO printings VALUES('+','.join('?'*13)+')',(p['id'],e['id'],p['finish'],p['pattern'],p['edition'],p['layout'],p['size'],p['material'],p['stamps_json'],p['print_state'],p.get('release_date'),p.get('image'),dump(p)))
  for key in ('art_style_source','cameo_source','market_link_evidence'):
   if e.get(key):c.execute('INSERT INTO facts VALUES(?,?,?,?)',(key,e['id'],dump(e[key]),e[key].get('source_url')))
  for p in e['printings']:
   if p.get('market_candidate'):c.execute('INSERT INTO facts VALUES(?,?,?,?)',('unverified_marketplace_candidate',p['id'],dump(p['market_candidate']),p['market_candidate'].get('source_url')))
   if p.get('market_name'):c.execute('INSERT INTO facts VALUES(?,?,?,?)',('marketplace_identity',p['id'],dump({k:p[k] for k in ('market_product_id','market_name','market_name_source')}),p['market_name_source']))
   if p.get('provenance'):c.execute('INSERT INTO facts VALUES(?,?,?,?)',('physical_printing',p['id'],dump(p['provenance']),p['provenance'].get('source_url')))
 for r in catalog['releases']:
  c.execute('INSERT INTO releases VALUES(?,?,?,?,?,?,?,?)',(r['lang']+':'+r['release'],r['lang'],r['release'],r['name'],r.get('date') or r.get('reference_date'),r.get('date_precision') or {4:'year',7:'month',10:'day'}.get(len(r.get('reference_date') or '')),r['date_state'] if r.get('date') or r.get('release_period') else 'provider_reference' if r.get('reference_date') else 'unresolved',r.get('source_url') or r.get('reference_source_url')))
  c.execute('INSERT INTO facts VALUES(?,?,?,?)',('release_date',r['lang']+':'+r['release'],dump(r),r.get('source_url') or r.get('reference_source_url')))
 c.commit();assert c.execute('PRAGMA quick_check').fetchone()[0]=='ok';assert not c.execute('PRAGMA foreign_key_check').fetchall();c.close();tmp.replace(path)

def main(download=False):
 catalog=prepare.build(write=False);original_ids={e['id'] for e in catalog['entries']};original_printings={p['id'] for e in catalog['entries'] for p in e['printings']}
 # Baseline German translations share a regional collector identity with EN.
 en={(e['release'],e['number_key'],e['dex']):e['name'] for e in catalog['entries'] if e['lang']=='en'}
 for e in catalog['entries']:
  if e['lang']=='de' and (e['release'],e['number_key'],e['dex']) in en:e['english']=en[e['release'],e['number_key'],e['dex']]
 jobs=import_special(catalog);dates(catalog);artwork_and_printings(catalog);market(catalog);acquired=acquire_images(catalog,jobs,download)
 apply_scope(catalog);apply_western(catalog);apply_coverage(catalog);apply_coverage(catalog,expanded=True);apply_coverage(catalog,regional=True);apply_rarities(catalog);apply_systematic(catalog);apply_reconciliation(catalog);apply_completion(catalog);apply_asia(catalog);apply_printing_review(catalog)
 apply_printing_corrections(catalog)
 apply_identity_corrections(catalog)
 apply_catalog_corrections(catalog)
 apply_new_sets(catalog)
 apply_reference_review(catalog)
 catalog.update(format=3,revision='1.8.12',catalog_date='2026-10-31')
 entries=catalog['entries'];ps=[p for e in entries for p in e['printings']]
 assert {(e['lang'],e['release']) for e in entries}<={(r['lang'],r['release']) for r in catalog['releases']}
 assert original_ids<={e['id'] for e in entries+catalog['retired_entries']};assert original_printings<={p['id'] for e in entries+catalog['retired_entries'] for p in e['printings']}
 assert len({p['id'] for p in ps})==len(ps)
 for e in entries:
  keys=[physical_key(e['id'],p) for p in e['printings']]
  assert len(keys)==len(set(keys)),e['id']
 catalog['statistics']=dict(entries=len(entries),printings=len(ps),without_printings=sum(not e['printings'] for e in entries),missing_images=sum(not e.get('image') for e in entries),full_art_entries=sum(e.get('art_style')=='full_art' for e in entries),cameo_entries=sum(is_cameo(e) for e in entries),jumbo_printings=sum(p['size']=='oversized' or p['material']=='metal' for p in ps),missing_release_dates=sum(not e.get('release_date') for e in entries),reference_dates=sum(e.get('date_state')=='provider_reference' for e in entries))
 catalog['language_stats']={lang:dict(entries=sum(e['lang']==lang for e in entries),with_printings=sum(e['lang']==lang and bool(e['printings']) for e in entries),printings=sum(len(e['printings']) for e in entries if e['lang']==lang),full_art=sum(e['lang']==lang and e.get('art_style')=='full_art' for e in entries),cameos=sum(e['lang']==lang and is_cameo(e) for e in entries)) for lang in ('en','de','ja','ko')}
 catalog['used_images']=sorted({image for e in entries for image in [e.get('image'),*(p.get('image') for p in e['printings'])] if image and (ROOT/'data/images'/image).is_file()})
 catalog['research_summary']=dict(accepted_set_dates=sum(bool(r.get('date')) for r in catalog['releases']),reference_only_set_dates=sum(not r.get('date') and bool(r.get('reference_date')) for r in catalog['releases']),unresolved_set_dates=sum(not r.get('date') and not r.get('reference_date') for r in catalog['releases']),japanese_printing_additions=catalog['printing_enrichment_summary']['japanese_added'],available_cached_reference_images=acquired,pending_special_candidates=len(catalog['special_research']),limits=['Printing totals count catalog targets. Provider assertions and independently checked facts are measured separately in the audit.','Shared catalog images may show a different edition; exact printing replacements can be saved locally.','Cardmarket links do not provide live raw prices.'])
 refresh_reference_review(catalog)
 write_json(ROOT/'data/catalog.json',catalog);make_sqlite(catalog)
 print(json.dumps(dict(statistics=catalog['statistics'],language_stats=catalog['language_stats'],research=catalog['research_summary']),ensure_ascii=False),flush=True)
 return catalog
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--images',action='store_true');args=parser.parse_args();main(args.images)
