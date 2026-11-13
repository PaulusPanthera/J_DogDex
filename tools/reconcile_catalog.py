import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
"""Offline reconciliation and audit outputs. Run after catalog_enrich.py.

Cached inventories are bounded reference denominators, not a claim that every
physical card or printing has been catalogued. Native availability is separate
from an international row translated into German.
"""
import collections,json,re,unicodedata
from pathlib import Path
from tools.audit_catalog import dump,measure,number
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/research/systematic'
def norm(v):return re.sub('[^a-z0-9]','',unicodedata.normalize('NFKD',str(v)).encode('ascii','ignore').decode().lower())
EXPLICIT={'EX Hidden Legends':'ex5','EX Team Rocket Returns':'ex7','HeartGold & SoulSilver':'hgss1','HGSS Black Star Promos':'hgssp','Nintendo Black Star Promos':'np','Diamond & Pearl':'dp1','Black & White':'bw1','BW Black Star Promos':'bwp','DP Black Star Promos':'dpp','XY Black Star Promos':'xyp','SM Black Star Promos':'smp','SWSH Black Star Promos':'swshp','SV Black Star Promos':'svp','ME Black Star Promos':'mep',"McDonald's Collection":'2011bw','McDonald’s Kollektion 2011':'2011bw','McDonald’s Kollektion 2014':'2014xy','McDonald’s Kollektion 2015':'2015xy','McDonald’s Kollektion 2016':'2016xy','McDonald’s Kollektion 2021':'2021swsh','Expresskampf':'2022swsh','Legendäre Schätze':'bw11','Doppeltes Dilemma':'dc1','Shining Legends':'sm3.5','Sonne & Mond':'sm1','Schwarz & Weiß':'bw1','Grundset':'base1','30 Jahre':'30th','30th Celebration':'30th','Celebrations':'cel25','Hidden Fates':'sma','Verborgenes Schicksal':'sma','Minun-Deck':'tk-ex-m','Plusle-Deck':'tk-ex-p','Latios-Deck':'tk-ex-latio','Lucario-Deck':'tk-dp-l','Feelinara-Deck':'tk-xy-sy','UHaFnir-Deck':'tk-xy-n','Wrestler-Pikachu-Deck':'tk-xy-p','Wolwerock-Deck':'tk-sm-l','Stalobor-Deck':'tk-bw-e','Zoroark-Deck':'tk-bw-z','POP Serie 6':'pop6','POP Serie 8':'pop8','Majestät der Drachen':'sm7.5','Dragon Majesty':'sm7.5'}
NOT_GERMAN={'base4':'https://www.bisafans.de/sammelkarten/sets/klassisch/base-set-2.php','lc':'https://www.bisafans.de/sammelkarten/sets/neo/legendary-collection.php','gym1':'https://www.bisafans.de/sammelkarten/sets/klassisch/gym-heroes.php','gym2':'https://www.bisafans.de/sammelkarten/sets/klassisch/gym-challenge.php','ex5':'https://www.bisafans.de/sammelkarten/sets/ex/ex-hidden-legends.php','ex7':'https://www.bisafans.de/sammelkarten/sets/ex/ex-team-rocket-returns.php','bw11':'https://www.pokewiki.de/Legend%C3%A4re_Sch%C3%A4tze_(TCG)','dc1':'https://www.card-corner.de/Double-Crisis-Kartenliste'}
NON_CANINE_ZYGARDE={('xy10','53'),('xy10','54'),('xy10','54A'),('xyp','XY129'),('xyp','XY151'),('xyp','XY152'),('smp','SM15'),('smp','SM48'),('smp','SM122'),('sm3','100'),('sm6','72'),('sm6','73'),('sm6','123'),('sm6','136'),('sma','SV65'),('sm7.5','49'),('swsh3.5','28'),('swsh4','93'),('swsh7','118'),('me03','47'),('me03','124'),('mep','71')}

def reconcile(c,baseline):
 doc=json.load(open(ROOT/'data/research/expanded_species_index.json'));al={};rows=[]
 for r in c['releases']+c.get('retired_releases',[]):
  if r['lang']not in('en','de'):continue
  for name in(r['name'],r['name'].replace('EX ','')):
   k=norm(name)
   if k not in al or not r['release'].endswith(('tg','gg','sv')):al[k]=r['release']
 for k,v in EXPLICIT.items():al[norm(k)]=v
 def lookup(cat):
  ix=collections.defaultdict(list)
  for e in cat['entries']:ix[e['lang'],e['release'],number(e['number'])].append(e)
  return ix
 ix=lookup(c);old=lookup(baseline)
 for sp in doc['species']:
  for raw in sp['rows']:
   rid=al.get(norm(raw['release_name']));no=number(raw['number'])
   if rid=='swsh4.5'and no.startswith('SV'):rid='swsh4.5sv'
   if rid and no.startswith('TG'):rid+='tg'if rid+'tg'in{e['release']for e in c['entries']}else''
   if rid=='swsh12.5'and no.startswith('GG'):rid+='gg'
   for lang in('en','de'):
    matches=[e for e in ix[lang,rid,no]if raw['dex']in(e.get('subject_dex')or[])];prior=[e for e in old[lang,rid,no]if raw['dex']in(e.get('subject_dex')or[])]
    status='matched'if len(matches)==1 else'duplicate_candidate'if len(matches)>1 else'outside_form_scope'if raw['dex']==718 and(rid,no)in NON_CANINE_ZYGARDE else'foreign_language_only'if raw['release_name']in('Collection McDonald’s 2018','McDonald’s Kollektion 2013')else'announced_future_unreleased'if raw['release_name']=='FLO'else'not_released_in_German'if lang=='de'and rid in NOT_GERMAN else'unmapped_reference'if not rid else'missing_candidate'if lang=='en'else'German_availability_unproven'
    rows.append(dict(source='PokéWiki species card inventories',source_family='community_encyclopedia',lang=lang,dex=raw['dex'],name=raw['name'],reference_release=raw['release_name'],release=rid,number=raw['number'],canonical_number=no,status=status,baseline_matched=bool(prior),entry_ids=[e['id']for e in matches],source_url=sp['source_url'],source_sha256=sp['source_sha256'],card_url=raw.get('card_url'),release_url=raw.get('release_url'),availability_source=NOT_GERMAN.get(rid)if status=='not_released_in_German'else None))
 matched={eid for r in rows for eid in r['entry_ids']};extras=[dict(entry_id=e['id'],lang=e['lang'],release=e['release'],number=e['number'],name=e['name'],category=e['category'],state='outside_primary_species_inventory_denominator',source_urls=e['links'])for e in c['entries']if e['lang']in('en','de')and e['id']not in matched]
 result=dict(observed_on='2026-10-29',scope_cutoff='2026-10-28',reference_name='Cached PokéWiki primary-species international card inventories',species_compared=len(doc['species']),reference_rows=sum(len(s['rows'])for s in doc['species']),limitations=['International rows and translated German names do not prove German physical availability.','These inventories are not a complete cameo, product-reprint or printing-variant census.','Community inventories may share upstream sources; manufacturer checklists are a distinct evidence family.'],summary={l:dict(collections.Counter(r['status']for r in rows if r['lang']==l))for l in('en','de')},alias_rules=EXPLICIT,rows=rows,catalog_records_outside_reference=extras)
 dump(OUT/'inventory_reconciliation.json',result);return result

def report(c):
 baseline=json.load(open(OUT/'baseline_inventory.json'));by={e['id']:e for e in c['entries']};old={e['id']:e for e in baseline['inventory']};facts=json.load(open(OUT/'reviewed_facts.json'));pub=json.load(open(OUT/'publisher_evidence.json'));plan=json.load(open(OUT/'sample_plan.json'));current=measure(c);dump(OUT/'current_inventory.json',current)
 # Build a minimum baseline-compatible snapshot for identity comparisons, not a rebuilt older catalog.
 base=dict(entries=baseline['inventory']);recon=reconcile(c,base)
 rarity_changes=[dict(entry_id=eid,lang=by[eid]['lang'],before=r['rarity_code'],after=by[eid]['rarity_code'])for eid,r in old.items()if r['rarity_code']!=by[eid]['rarity_code']];date_changes=[dict(entry_id=eid,lang=by[eid]['lang'],before=r['release_date'],after=by[eid].get('release_date'),period=by[eid].get('release_period'))for eid,r in old.items()if r['release_date']!=by[eid].get('release_date')];name_changes=[dict(entry_id=eid,before=r['name'],after=by[eid]['name'])for eid,r in old.items()if r['name']!=by[eid]['name']]
 added=c['systematic_research']['added_entry_ids'];addedps=set(c['systematic_research']['added_printing_ids']);artfills=[eid for eid,r in old.items()if not r.get('art_style')and by[eid].get('art_style')];sample=[]
 for row in plan['rows']:
  eid=row['entry_id'];e=by[eid];before=old[eid];a=next((r for r in pub['assertions']if r['entry_id']==eid),None);errors=[]
  if before['rarity_code']!=e['rarity_code']:errors.append('rarity')
  if before['release_date']!=e.get('release_date')and before['date_state']!='provider_reference':errors.append('date_or_unsupported_precision')
  if any(p['id']in addedps for p in e['printings']):errors.append('missing_established_pack_finish')
  sample.append(row|dict(errors_observed=errors,after_rarity=e['rarity_code'],after_date=e.get('release_date'),publisher_identity='agrees'if a else'unassessed',publisher_rarity='symbol_decoded'if a and a['rarity_code']else'unassessed',foil_paper_and_all_editions='unassessed_shared_reference_image',date_check='changed_with_explicit_evidence'if'date_or_unsupported_precision'in errors else'provisional_or_not_independently_checked_in_this_sample',resolution='corrected'if errors else'no_error_found_in_assessed_fields'))
 sample_result=dict(seed=plan['seed'],sample_size=80,visual_records_assessed=sum(r['visual_identity']=='agrees'for r in sample),records_with_observed_errors=sum(bool(r['errors_observed'])for r in sample),observed_error_categories=dict(collections.Counter(t for r in sample for t in r['errors_observed'])),limitations=plan['limitations'],rows=sample);dump(OUT/'sample_audit.json',sample_result)
 # Unresolved work is explicit and resumable, with candidates kept out of accepted data.
 queue=[]
 for i,r in enumerate(recon['rows']):
  if r['status']in('missing_candidate','German_availability_unproven','unmapped_reference','duplicate_candidate'):queue.append(dict(id=f'inventory:{r["lang"]}:{r["dex"]}:{r["reference_release"]}:{r["number"]}',priority=1,kind='identity_reconciliation',status=r['status'],lang=r['lang'],release=r['release'],number=r['number'],name=r['name'],source_urls=[u for u in[r['source_url'],r.get('card_url'),r.get('release_url')]if u],next_action='Find exact native edition/specimen and product identity. Do not translate a listing into physical availability.'))
 for i,r in enumerate(facts.get('conflicts',[])):queue.append(dict(id='field-conflict:'+str(i),priority=1 if r['kind']=='unsupported_printing'else 2,**r))
 for i,r in enumerate(pub['conflicts']):
  if r['kind']=='publisher_name_conflict':queue.append(dict(id='publisher-font:'+r['entry_id'],priority=2,status='unresolved_extraction_symbol',**r,next_action='SP/LV.X symbols may be vector artwork omitted by text extraction; review exact printed card before changing its identity.'))
 for ref in json.load(open(OUT/'manufacturer_checklists.json'))['references']:
  if not ref.get('error') and not ref.get('rows'):queue.append(dict(id='publisher-outline:'+ref['lang']+':'+ref['release'],priority=2,kind='source_readability',status='vector_outlines_without_machine_readable_rows',source_urls=[ref['source_url']],next_action='Read the native publisher PDF visually for needed rows; populated catalog fields are not evidence of correctness.'))
  if ref.get('error'):queue.append(dict(id='publisher-access:'+ref['lang']+':'+ref['release'],priority=2,kind='source_access',status='blocked_or_unavailable',lang=ref['lang'],release=ref['release'],source_urls=[ref['source_url']],blocker=ref['error'],next_action='Find a published successor checklist URL or contemporary primary product page. Do not retry an access wall.'))
 de_lookup={(e['release'],number(e['number'])):e for e in c['entries']if e['lang']=='de'};cameos=[]
 for e in c['entries']:
  if e['lang']!='en' or e.get('subject_dex') or e['category']!='cameo':continue
  de=de_lookup.get((e['release'],number(e['number'])));status='matched_native_identity'if de else'not_released_in_German'if e['release']in NOT_GERMAN else'needs_native_identity_and_printing_proof'
  row=dict(english_entry_id=e['id'],german_entry_id=de['id']if de else None,release=e['release'],number=e['number'],name=e['name'],cameo_dex=e['cameo_dex'],status=status,source_urls=e['links']);cameos.append(row)
  if status=='needs_native_identity_and_printing_proof':queue.append(dict(id='cameo-native:'+e['id'],priority=1,kind='native_cameo_identity',**row,next_action='Confirm exact German artwork and language; obtain native physical finish evidence before accepting the card.'))
 dump(OUT/'cameo_reconciliation.json',dict(basis='Existing EN cameo source pool; this is a candidate comparison, not a complete external cameo denominator.',rows=cameos,summary=dict(collections.Counter(r['status']for r in cameos))))
 for issue in current['issues']:
  if issue['kind']=='foil_rarity_nonholo_candidate':queue.append(dict(id='printing-exception:'+issue['printing_id'],priority=2,**issue,next_action='Check exact native deck/product evidence. A non-holo version of a foil rarity can be a valid documented exception; do not change finish from rarity or another language.'))
 queue.append(dict(id='marketplace-field-checks',priority=2,kind='unverified_product_candidates',status='unresolved',candidate_count=len(c['systematic_research']['marketplace_candidates']),evidence_path='catalog.json/systematic_research/marketplace_candidates',next_action='Verify marketplace expansion, number and variant against each candidate before restoring an active product reference. Keep existing manually reviewed listing URLs.'))
 for lang in('en','de'):
  un=[e['id']for e in c['entries']if e['lang']==lang and not e.get('art_style')];queue.append(dict(id='artwork:'+lang,priority=3,kind='missing_artwork_classification',status='unassessed',entry_ids=un,next_action='Review existing exact native images in batches; do not fill Standard by default.'))
 dump(OUT/'work_queue.json',dict(updated_on='2026-10-29',next_priorities=['Resolve native-language missing candidates and currently unsupported printings.','Complete modern publisher rows, regional promo dates and marketplace number/variant checks.','Audit remaining artwork classifications, then obscure paper patterns and missing images.'],items=queue))
 log=[]
 for kind in('entry_updates','release_dates','card_dates','entries','printings'):
  for i,r in enumerate(facts.get(kind,[])):log.append(dict(id=kind+':'+str(i),kind=kind,subject=r.get('entry_id')or r.get('lang','')+':'+r.get('release','')+':'+r.get('number',''),source_urls=r.get('source_urls',[]),source_sha256=r.get('source_sha256'),evidence=r.get('evidence'),retrieval_family='manufacturer_pdf'if r.get('source_sha256')else'native_specimen_or_explicit_reviewed_reference'))
 dump(OUT/'evidence_log.json',dict(observed_on='2026-10-29',notes=['Source-family labels do not count sites copying the same upstream dataset as independent confirmations.','PDF and native image hashes identify cached evidence; web-source facts without a downloaded response never receive an invented source-body hash.'],facts=log))
 result=dict(baseline_revision='1.3.2',revision=c['revision'],reference_reconciliation=recon['summary'],reference_species=recon['species_compared'],reference_rows=recon['reference_rows'],publisher_documents=len(pub['documents']),publisher_identity_records_checked=len({r['entry_id']for r in pub['assertions']}),publisher_rarity_records_decoded=len({r['entry_id']for r in pub['assertions']if r['rarity_code']}),rarity_corrections=rarity_changes,date_corrections=date_changes,name_corrections=name_changes,added_entry_ids=added,added_printing_ids=sorted(addedps),verified_artwork_fields_filled=artfills,inference_status_corrections=len(c['systematic_research']['inference_status_entry_ids']),quarantined_marketplace_candidates=len(c['systematic_research']['marketplace_candidates']),sample={k:v for k,v in sample_result.items()if k!='rows'},queue_items=len(queue),limitations=['No overall catalog completeness or accuracy percentage is claimed.','Publisher rows verify bounded fields; card identity checks do not prove release date, all finishes, product-only variants or marketplace offers.','Native Windows executable not run in this Linux environment.'])
 dump(OUT/'audit_summary.json',result);return result
if __name__=='__main__':
 import argparse
 argparse.ArgumentParser(description=__doc__).parse_args()
 c=json.load(open(ROOT/'data/catalog.json',encoding='utf-8'));s=report(c);print(json.dumps({k:v for k,v in s.items()if not isinstance(v,list)},ensure_ascii=False))
