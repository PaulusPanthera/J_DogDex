import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
"""Bounded EN/DE release evidence, inventory matrix and resumable queue."""
import collections,copy,json,re,unicodedata
from pathlib import Path
from tools.audit_catalog import measure,digest,dump
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data/research/completion_16'
def accepted(e,p):return e.get('identity_status','documented')=='documented'and e['metadata_state']=='approved'and p.get('collection_status','documented')=='documented'
def printed_name(v):
 # The checklist omits the SP owner marker and prints delta-species separately.
 v=re.sub(r'\s+(GL|C|G|E4|δ)$','',str(v))
 return ''.join(c for c in unicodedata.normalize('NFKD',v).casefold()if c.isalnum())
def printed_number(v,release=None):
 v=str(v).split('/')[0].upper();prefix={'xyp':'XY','smp':'SM','bwp':'BW','dpp':'DP','swshp':'SWSH'}.get(release)
 if prefix and v.isdigit():v=prefix+v
 return re.sub(r'(^|[A-Z])0+(?=\d)',r'\1',v)
def inventory(c):
 d=measure(c);d['inventory_notes']+=' Printing counts and without_printings are raw retained records; confirmed_printings and without_confirmed_printing apply the evidence/identity admission rule.'
 for issue in d['issues']:
  if issue['kind']=='no_accepted_printing':issue['kind']='no_recorded_printing'
 for e in c['entries']:
  if e['lang']in('en','de')and e['printings']and not any(accepted(e,p)for p in e['printings']):d['issues'].append(dict(kind='only_held_printings',entry_id=e['id'],identity_status=e.get('identity_status'),printing_ids=[p['id']for p in e['printings']]))
 d['issue_counts']=dict(collections.Counter(r['kind']for r in d['issues']))
 for lang,st in d['languages'].items():
  es=[e for e in c['entries']if e['lang']==lang];st['confirmed_printings']=sum(accepted(e,p)for e in es for p in e['printings']);st['without_confirmed_printing']=sum(not any(accepted(e,p)for p in e['printings'])for e in es)
 return d
def main():
 c=json.loads((ROOT/'data/catalog.json').read_text(encoding='utf-8'));old=json.loads((OUT/'baseline_150.json').read_text(encoding='utf-8'));facts=json.loads((OUT/'reviewed_facts.json').read_text(encoding='utf-8'));rows=json.loads((OUT/'inventory_reconciliation.json').read_text(encoding='utf-8'));products=json.loads((OUT/'product_reconciliation.json').read_text(encoding='utf-8'));docs=json.loads((OUT/'source_acquisition.json').read_text(encoding='utf-8'));by={e['id']:e for e in c['entries']};baseby={e['id']:e for e in old['entries']}
 dump(OUT/'baseline_inventory.json',inventory(old));dump(OUT/'current_inventory.json',inventory(c))
 old_printings={p['id']:(e,p)for e in old['entries']+old.get('retired_entries',[])for p in e['printings']};physical_changes=[]
 for e in c['entries']:
  if e['lang']not in('en','de'):continue
  for p in e['printings']:
   if p['id']not in old_printings:continue
   previous=old_printings[p['id']][1];fields={key:dict(before=previous.get(key),after=p.get(key))for key in('pattern','collection_status','release_date','date_state','date_mode','sources')if previous.get(key)!=p.get(key)}
   if fields:physical_changes.append(dict(entry_id=e['id'],printing_id=p['id'],lang=e['lang'],fields=fields,source_urls=sorted({u for src in p.get('sources',[])for u in src.get('links',[])})))
 dump(OUT/'physical_field_changes.json',dict(rows=physical_changes,limits='Changes include additional provenance and qualified precision, not just demonstrated errors. Stable printing IDs are unchanged.'))
 # Update the prior named denominator without presenting a translated row as native proof.
 wiki=json.loads((ROOT/'data/research/reconciliation_15/inventory_reconciliation.json').read_text(encoding='utf-8'))
 for r in wiki['rows']:
  hits=[e for e in c['entries']if e['lang']==r['lang']and e['release']==r.get('release')and printed_number(e['number'],e['release'])==printed_number(r.get('canonical_number',''),e['release'])]
  if hits and r['status']in('German_availability_unproven','matched'):
   r['entry_ids']=[e['id']for e in hits];r['status']='provisional_visible'if any(e.get('identity_status')=='provisional'for e in hits)else'matched_documented_identity'
 dump(OUT/'pokewiki_reconciliation.json',wiki)
 matrix=[]
 families={s['family']for s in docs}
 for sp in c['roster']:
  for lang in('en','de'):
   es=[e for e in c['entries']if e['lang']==lang and sp['dex']in(set(e.get('subject_dex',[]))|set(e.get('cameo_dex',[])))];rs=[r for r in rows if r['lang']==lang and sp['dex']in r['species_dex']];pr=[r for r in products if r.get('lang')==lang and sp['dex']in r.get('species_dex',[])];wr=[r for r in wiki['rows']if r['lang']==lang and r['dex']==sp['dex']]
   src={family:dict(rows=len(xs),dispositions=dict(collections.Counter(x['disposition']for x in xs)),entry_ids=sorted({x['entry_id']for x in xs if x.get('entry_id')}))for family in sorted({r['family']for r in rs})if(xs:=[r for r in rs if r['family']==family])}
   src['pokewiki_primary']=dict(rows=len(wr),dispositions=dict(collections.Counter(r['status']for r in wr)))
   src['pokumon_products']=dict(rows=len(pr),dispositions=dict(collections.Counter(r['disposition']for r in pr)))
   examined=[d for d in docs if d.get('dex')==sp['dex']];access={d['family']:d['state']for d in examined}
   special=[p for e in es for p in e['printings']if p['size']=='oversized'or p['material']=='metal'or p.get('world_championship_year')]
   matrix.append(dict(lang=lang,dex=sp['dex'],species=sp['name'],identity_count=len(es),identity_states=dict(collections.Counter(e.get('identity_status','documented')for e in es)),confirmed_printings=sum(accepted(e,p)for e in es for p in e['printings']),sources=src,source_access=access,sets=sorted({e['release']for e in es}),existing_records_absent_from_new_reference=sorted({e['id']for e in es}-{r['entry_id']for r in rs if r.get('entry_id')}),families_reviewed=dict(main_expansions='PokeWiki + Serebii + PokemonTCG API; manufacturer checks reused; native Carddex checks reused for DE',promos_and_regional_products='Dedicated Pokumon language/species filter; native prior facts; unresolved German claims visible',deck_and_alternate_identities='Pokumon exact products + prior trainer-kit and alternate inventories',cameos_and_items='Two additional cameo inventories, previous appearance pool and native provider candidates; primary subjects stay primary',jumbo_and_special='Pokumon jumbo products and prior manufacturer evidence; lenticular detail retained',championship_replicas='Prior individually documented replicas preserved and reindexed; no new comprehensive replica inventory located',physical_variants='Explicit source tuples reconciled; generic Normal and rarity never create printings'),special_printing_ids=[p['id']for p in special],pass_status='reconciled_discovered_claims',limits=['Source-specific denominators below are bounded inventories, not worldwide completeness.','Unindexed obscure paper, regional event and replica variants may remain.']+(['Native product coverage is narrower than English. No automatic EN-to-DE physical transfer.']if lang=='de'else[])))
 dump(OUT/'species_language_matrix.json',dict(rows=matrix,species=41,language_cells=82,scope='EN/DE pass through 2026-10-29; all discovered claims receive a disposition, with unresolved limits explicitly retained.'))
 checks=[];checks_by=collections.defaultdict(list)
 for r in rows:
  if r.get('disposition')not in('matched','newly_documented')or r.get('entry_id')not in by:continue
  e=by[r['entry_id']];name=e['english']if r['lang']=='en'else e['name'];same=printed_name(name)==printed_name(r['name'].replace('Deliquent','Delinquent'))and printed_number(e['number'],e['release'])==printed_number(r['number'],e['release'])
  check=dict(entry_id=e['id'],lang=e['lang'],family=r['family'],source_url=r['source_url'],fields=['name','number'],outcome='agrees_after_explicit_label_normalization'if same else'label_or_identity_conflict',selected=dict(name=name,number=e['number']),reference=dict(name=r['name'],number=r['number']),existing_in_15=e['id']in baseby,limits='This checks the inventory identity tuple, not dates, localized specimens or physical variants. Multiple upstream families are not assumed independent.')
  checks.append(check);checks_by[e['id']].append(check)
 dump(OUT/'field_comparisons.json',dict(rows=checks,by_family={family:dict(rows=len(rs),outcomes=dict(collections.Counter(r['outcome']for r in rs)),existing_records=len({r['entry_id']for r in rs if r['existing_in_15']}))for family in sorted({r['family']for r in checks})if(rs:=[r for r in checks if r['family']==family])},existing_records_with_identity_agreement=len({r['entry_id']for r in checks if r['existing_in_15']and r['outcome'].startswith('agrees')}),limits='Source-specific identity comparison coverage only. No total accuracy or worldwide completeness percentage.'))
 # Full evidence ledger: selected current fields are distinct from source claim history.
 native_checks=json.loads((OUT/'bisafans_native_reconciliation.json').read_text(encoding='utf-8'));native_rarity={r['entry_id']:r for r in native_checks['assertions']if r.get('expected_rarity')}
 led=[];queue=[]
 for e in c['entries']:
  if e['lang']not in('en','de'):continue
  ev=e.get('evidence',[]);fields={}
  for key in('name','number','release_date','rarity_code','art_style','identity_status'):
   state='missing'if e.get(key)is None else'not_printed'if key=='rarity_code'and e['rarity_state']=='not_printed'else'current_selected_value'
   if key=='art_style'and e.get('art_style_state')=='visually_assessed_16':state='new_visual_assessment_16'
   if key=='rarity_code'and any(r['entry_id']==e['id']and r['kind']=='rarity_value_corrected'for r in facts['updates']):state='newly_checked_16'
   if key=='rarity_code'and e['id']in native_rarity and e.get(key)==native_rarity[e['id']]['expected_rarity']:state='new_native_inventory_agreement_16'
   if key in('name','number')and any(r['outcome'].startswith('agrees')for r in checks_by[e['id']]):state='inventory_tuple_agreement_16'
   fields[key]=dict(value=e.get(key),state=state,claim_indices=[i for i,v in enumerate(ev)if v['field']==key])
  led.append(dict(entry_id=e['id'],lang=e['lang'],fields=fields,identity_comparisons=checks_by[e['id']],native_rarity_comparison=native_rarity.get(e['id']),evidence=ev,printing_claims=e.get('variant_claims',[]),printings={p['id']:dict(collection_status=p.get('collection_status','documented'),eligible_for_confirmed_completion=accepted(e,p),provenance=p.get('provenance'),audit_status=p.get('audit_status'))for p in e['printings']}))
  for r in checks_by[e['id']]:
   if r['outcome']=='label_or_identity_conflict':queue.append(dict(kind='inventory_label_conflict',entry_id=e['id'],priority=1,status='unresolved',evidence=r,next_action='Resolve the original printed label and source abbreviation before changing the selected value.'))
  if e.get('identity_status')in('provisional','disputed','announced'):queue.append(dict(kind='identity_or_availability',entry_id=e['id'],status=e['identity_status'],priority=1,reason=e.get('status_reason'),source_urls=e.get('links',[]),next_action='Add exact native/product evidence and promote this same ID; do not create a duplicate.'))
  for x in e.get('variant_claims',[]):queue.append(dict(kind='printing_claim',entry_id=e['id'],claim_id=x['id'],status=x['disposition'],priority=2,source_urls=x['source_urls'],next_action='Resolve the incomplete physical tuple against exact product evidence.'))
  for p in e['printings']:
   if not accepted(e,p):queue.append(dict(kind='held_physical_target',entry_id=e['id'],printing_id=p['id'],status=p.get('collection_status',e['identity_status']),priority=1,next_action='Resolve recorded conflict; ownership and target ID remain preserved.'))
  if not e.get('art_style'):queue.append(dict(kind='artwork',entry_id=e['id'],status='missing_picture_or_layout_ambiguous',priority=3,next_action='Use exact card face; do not infer Standard from rarity or an absent Full Art list.'))
 dump(OUT/'field_verification_ledger.json',dict(revision='1.6.0',entry_count=len(led),entries=led,limits=['Evidence is field-specific; an inventory match does not verify every selected value.','Recovered history is labelled separately from new source reconciliation and visual checks. No population accuracy percentage.']))
 # Re-screen all held Cardmarket IDs against the current primary catalog; no product match is promoted without missing set/number/variant proof.
 cmfile=next((d for d in docs if d['family']=='cardmarket_catalog'and d['state']=='cached'),None);cm=[]
 if cmfile:
  work=ROOT.parent/'work/completion_16';raw=json.loads((work/cmfile['cache_file']).read_text(encoding='utf-8'));lookup={p['idProduct']:p for p in raw['products']}
  for r in old['systematic_research']['marketplace_candidates']:
   p=lookup.get(r['product_id']);cm.append(r|dict(current_primary_product=p,state='still_quarantined_missing_exact_fields',checked_on='2026-10-29',source_sha256=cmfile['sha256'],checks=dict(name='current_primary_catalog_available'if p else'not_in_current_catalog',set='idExpansion_present_but_not_independently_resolved'if p else'unresolved',number='not_supplied_by_primary_bulk_catalog',variant='not_supplied_by_primary_bulk_catalog')))
 dump(OUT/'marketplace_reconciliation.json',dict(candidates=cm,denominator=len(cm),source=cmfile,limit='Current bulk catalog exposes product ID, English name/moves and expansion ID; it does not establish exact collector number, language or physical variant. No quarantined ID is promoted.'))
 queue.append(dict(kind='marketplace_batch',priority=2,status='blocked_missing_exact_metadata',candidate_count=len(cm),evidence='marketplace_reconciliation.json',next_action='Use exact marketplace listings/expansion metadata when accessible; do not repeat name-only checks.'))
 # Retain earlier blocked source and precision tasks, avoiding rediscovery loops.
 prev=json.loads((ROOT/'data/research/reconciliation_15/work_queue.json').read_text(encoding='utf-8'))
 for r in prev['items']:
  if r.get('kind')in('source_access','german_launch_precision','promo_product_date','launch_month_dispute','publisher_name_conflict'):queue.append(r|dict(carried_from='reconciliation_15',next_action=r.get('next_action','Resolve existing source conflict.')))
 for issue in measure(c)['issues']:
  if issue['kind']in('missing_numeric_date','unqualified_date','promo_series_date_candidate','foil_rarity_nonholo_candidate'):
   queue.append(issue|dict(priority=2,status='unresolved_field_or_diagnostic_flag',next_action='Inspect the field-specific evidence already attached to this identity. A diagnostic flag alone is not a demonstrated factual error.'))
 dump(OUT/'work_queue.json',dict(revision='1.6.0',items=queue,limits=['Queue is scoped by real remaining uncertainty. Counters and image growth are not completeness measures.'],resume_order=['Exact language/identity conflicts','Known physical claims with unresolved tuples','Marketplace exact metadata','Remaining images/artwork ambiguity']))
 sample=json.loads((OUT/'sample_plan.json').read_text(encoding='utf-8'));pub=json.loads((ROOT/'data/research/systematic/publisher_evidence.json').read_text(encoding='utf-8'));native=json.loads((ROOT/'data/research/reconciliation_15/carddex_reconciliation.json').read_text(encoding='utf-8'));px={r['entry_id']:r for r in pub['assertions']};nx={r['entry_id']:r for r in native['assertions']};sx={r['entry_id']:r for r in rows if r.get('entry_id')and r['family']=='serebii'and r['disposition']=='matched'};audit=[]
 for r in sample['rows']:
  e=baseby[r['entry_id']];proof=px.get(e['id'])or(nx.get(e['id'])if e['lang']=='de'else sx.get(e['id']));new=by[e['id']];errors=[]
  if proof:
   for field,normalize in(('name',printed_name),('number',lambda v:printed_number(v,e['release']))):
    if normalize(e[field])!=normalize(proof[field]):errors.append(dict(field=field,before=e[field],reference=proof[field],state='needs_conflict_review'))
  for u in facts['updates']:
   if u['entry_id']==e['id']and u['kind']=='rarity_value_corrected':errors.append(dict(field='rarity_code',before=e['rarity_code'],after=new['rarity_code']))
  audit.append(r|dict(assessed_fields=['name','number']if proof else[],unassessed_fields=['release_date','all_physical_variants','marketplace_identity']+([]if proof else['name','number']),independent_reference=proof,observed_errors=errors,comparison_rule='Compare native printed name and collector number; SP owner marker GL/C and separate delta symbol are retained as catalogue aliases, not identity errors.',artwork_assessment='See numbered artwork_review.json; not a date/finish verification.'))
 visual=json.loads((OUT/'sample_visual_review.json').read_text(encoding='utf-8'))
 for r in audit:r['shared_image_assessment']=dict(state='visually_assessed'if r.get('image')else'unassessed_missing_picture',observed_identity_error=False if r.get('image')else None,scope='Shared face name/number; not every edition, foil or regional product.')
 dump(OUT/'sample_audit.json',dict(seed=sample['seed'],sample_size=len(audit),rows=audit,records_with_observed_errors=sum(bool(r['observed_errors'])for r in audit),name_number_assessed=sum(bool(r['assessed_fields'])for r in audit),visual_review=visual,limits=['A diagnostic sample with field-specific assessment, not an accuracy estimate.','Unknown-year records excluded; seven remaining early German records were all selected.','Existing publisher/Carddex evidence is explicitly reused, not newly retrieved.','Dates, every physical variant and marketplace identities were not assessed by this sample.']))
 summary=dict(version='1.6.0',before=measure(old)['languages'],after=measure(c)['languages'],new_identity_states=dict(collections.Counter(e.get('identity_status')for e in facts['entries'])),new_identities_by_language=dict(collections.Counter(e['lang']for e in facts['entries'])),restored_ids=c['completion_research']['restored_entry_ids'],new_printings=len(c['completion_research']['added_printing_ids']),pattern_refinements=sum('pattern'in r['values']for r in facts['printing_updates']),rarity_corrections=[r for r in facts['updates']if r['kind']=='rarity_value_corrected'],confirmed_printings={lang:sum(accepted(e,p)for e in c['entries']if e['lang']==lang for p in e['printings'])for lang in('en','de','ja','ko')},new_reference_rows=dict(collections.Counter(r['family']for r in rows)),inventory_dispositions={f:dict(collections.Counter(r['disposition']for r in rows if r['family']==f))for f in sorted({r['family']for r in rows})},product_dispositions=dict(collections.Counter(r['disposition']for r in products)),artwork_missing_old_existing=sum(not by[e['id']].get('art_style')for e in old['entries']if e['lang']in('en','de')),consolidated_evidence_claims=sum(len(e.get('evidence',[]))for e in c['entries']),queue_items=len(queue),source_access=dict(collections.Counter(d['state']for d in docs)))
 dump(OUT/'audit_summary.json',summary);print(json.dumps({k:v for k,v in summary.items()if k not in('before','after','rarity_corrections')},ensure_ascii=False))
 md=['# DogDex 1.6 species/language reconciliation matrix','', 'Each row records a completed pass over the named evidence pools. It does not claim every worldwide printing is known. Detailed source denominators and unresolved dispositions are in species_language_matrix.json.','', '| Language | Species | Identities | Confirmed printings | Visible provisional / disputed | New source rows |','|---|---|---:|---:|---:|---:|']
 for r in matrix:md.append(f"| {r['lang'].upper()} | {r['species']} | {r['identity_count']} | {r['confirmed_printings']} | {sum(r['identity_states'].get(s,0)for s in('provisional','disputed'))} | {sum(v['rows']for k,v in r['sources'].items()if k not in('pokewiki_primary','pokumon_products'))} |")
 (ROOT/'SPECIES_MATRIX_1_6.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
if __name__=='__main__':
 import argparse
 argparse.ArgumentParser(description=__doc__).parse_args()
 main()
