import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
"""Field-level evidence ledger and resumable 1.5 delta, separate from 1.4 history."""
import collections,copy,json
from pathlib import Path
from urllib.parse import urlparse
from tools.audit_catalog import dump,digest,measure,number
ROOT=Path(__file__).resolve().parents[1];RESEARCH=ROOT/'data/research';OUT=RESEARCH/'reconciliation_15'

def urls(r):
    if not isinstance(r,dict):return []
    return list(dict.fromkeys([u for u in [r.get('source_url'),r.get('date_source'),r.get('image_source'),*r.get('source_urls',[])]if isinstance(u,str)and u.startswith('http')]))

def lineage(u):
    host=urlparse(u).netloc.lower()
    if 'tcgdex'in host:return 'TCGdex_provider'
    if 'pokemontcg'in u or 'pokemon-tcg-data'in u:return 'PokemonTCG_API_upstream'
    if host.endswith('pokemon.com')or host=='pokemon.com':return 'manufacturer'
    if 'carddex.net'in host:return 'Carddex_editorial'
    if 'bisafans.de'in host:return 'Bisafans_editorial'
    if 'pokewiki.de'in host:return 'PokeWiki_encyclopedia'
    if 'bulbagarden.net'in host:return 'Bulbapedia_encyclopedia'
    if 'cardmarket'in host:return 'Cardmarket'
    return host

def ledger(c,facts):
    """Index prior provenance as prior claims, never promote it to new validation."""
    by={e['id']:e for e in c['entries']};rows={};retired={e['id']for e in c.get('retired_entries',[])}
    for e in c['entries']:
        if e['lang']not in('en','de'):continue
        fields={k:dict(value=copy.deepcopy(e.get(k)),claims=[])for k in ('name','number','release_date','rarity_code','art_style')}
        for k in fields:fields[k]['state']='missing'if fields[k]['value']is None else'populated_unchecked'
        fields['release_date']['claims'].append(dict(state='provider_assertion'if e.get('date_state','').startswith('provider')else'prior_source_claim',path='catalog.json/date_evidence',source_urls=[e['date_source']]if e.get('date_source')else[],scope=e.get('date_state')))
        a=e.get('art_style_source')or{}
        if a:
            fields['art_style']['claims'].append(dict(state='inference'if isinstance(a,dict)and a.get('inference')else'prior_review_claim',path='catalog.json/art_style_source',source_urls=urls(a)))
        rows[e['id']]=dict(entry_id=e['id'],lang=e['lang'],release=e['release'],number=e['number'],fields=fields,printings={p['id']:dict(state='provider_assertion'if(p.get('provenance')or{}).get('kind')in('cameo_physical_tuple','provider')else'prior_review_claim'if p.get('provenance')else'populated_unchecked',provenance=copy.deepcopy(p.get('provenance')),audit_status=p.get('audit_status'),marketplace_state='unverified_candidate'if p.get('market_candidate')else'explicit_link'if p.get('cardmarket_url')else'no_product_reference')for p in e['printings']})
    def add(eid,field,state,path,r):
        if eid not in rows:return
        rows[eid]['fields'][field]['claims'].append(dict(state=state,path=path,source_urls=urls(r),source_lineages=sorted({lineage(u)for u in urls(r)})))
    for filename in [s+'_reviewed_facts.json'for s in('western','coverage','promo','expanded','regional')]+['systematic/reviewed_facts.json']:
        doc=json.load(open(RESEARCH/filename))
        for section in ('entry_updates','card_dates','entries','printings','printing_updates'):
            for i,r in enumerate(doc.get(section,[])):
                eid=r.get('entry_id')
                if not eid and section=='entries':
                    matches=[e for e in by.values()if(e['lang'],e['release'],e['number_key'])==(r['lang'],r['release'],r['number_key'])];eid=matches[0]['id']if len(matches)==1 else None
                path=filename+'/'+section+'/'+str(i)
                for key in r.get('values',{}):
                    if key in('name','number','rarity_code','art_style'):add(eid,key,'prior_review_claim',path,r)
                if section=='card_dates':add(eid,'release_date','prior_review_claim',path,r)
                if section=='entries':
                    for key in('name','number'):add(eid,key,'prior_review_claim',path,r)
    pub=json.load(open(RESEARCH/'systematic/publisher_evidence.json'))
    for i,r in enumerate(pub['assertions']):
        for key in ('name','number'):add(r['entry_id'],key,'publisher_identity_checked_14','systematic/publisher_evidence.json/assertions/'+str(i),r)
        if r.get('rarity_code')==by.get(r['entry_id'],{}).get('rarity_code'):add(r['entry_id'],'rarity_code','publisher_symbol_checked_14','systematic/publisher_evidence.json/assertions/'+str(i),r)
    carddex=json.load(open(OUT/'carddex_reconciliation.json'))
    for i,r in enumerate(carddex['assertions']):
        for key in ('name','number'):add(r['entry_id'],key,'native_inventory_checked_15','reconciliation_15/carddex_reconciliation.json/assertions/'+str(i),r)
        if r.get('expected_rarity')==by.get(r['entry_id'],{}).get('rarity_code'):add(r['entry_id'],'rarity_code','native_rarity_checked_15','reconciliation_15/carddex_reconciliation.json/assertions/'+str(i),r)
    for section in ('entry_updates','card_dates'):
        for i,r in enumerate(facts[section]):
            for key in (['release_date']if section=='card_dates'else r['values'].keys()):
                if key in('name','number','rarity_code','release_date','art_style'):add(r['entry_id'],key,'field_checked_15','reconciliation_15/reviewed_facts.json/'+section+'/'+str(i),r)
    for i,r in enumerate(facts['entries']):
        e=next(e for e in by.values()if(e['lang'],e['release'],e['number_key'])==(r['lang'],r['release'],r['number_key']))
        for key in('name','number','rarity_code'):add(e['id'],key,'field_checked_15','reconciliation_15/reviewed_facts.json/entries/'+str(i),r)
    for i,r in enumerate(facts['release_dates']):
        for e in by.values():
            if(e['lang'],e['release'],e.get('release_date'))==(r['lang'],r['release'],r['date']):add(e['id'],'release_date','field_checked_15','reconciliation_15/reviewed_facts.json/release_dates/'+str(i),r)
    for r in json.load(open(OUT/'sample_plan.json'))['rows']:
        if not r.get('image')or r['entry_id']in retired:continue
        for key in ('name','number','art_style'):add(r['entry_id'],key,'visual_sample_checked_15','reconciliation_15/sample_audit.json/position/'+str(r['position']),dict(source_urls=[r.get('image_source')or r['links'][0]]))
    counts=collections.defaultdict(collections.Counter)
    for r in rows.values():
        for name,f in r['fields'].items():
            states={q['state']for q in f['claims']}
            f['state']='missing'if f['value']is None else'checked_in_15'if any(s.endswith('_15')for s in states)else'checked_in_14'if any(s.endswith('_14')for s in states)else'inferred'if'inference'in states else'prior_review_claim'if'prior_review_claim'in states else'provider_assertion'if'provider_assertion'in states else'prior_source_claim'if'prior_source_claim'in states else'populated_unchecked'
            if name=='rarity_code'and by[r['entry_id']]['rarity_state']=='not_printed':f['state']='not_printed_checked_15'if'field_checked_15'in states else'not_printed_prior_claim'
            if name=='release_date'and by[r['entry_id']].get('release_period'):f.update(state='known_period_without_numeric_date',release_period=by[r['entry_id']]['release_period'])
            counts[name][f['state']]+=1
    result=dict(basis_revision=c['revision'],entry_count=len(rows),notes=['A check applies only to the named field, not the entire record.','Prior accepted review claims are indexed separately and are not retroactively certified.','A provider assertion is not independent confirmation; each claim retains source lineage.','No single overall correctness or completeness percentage is computed.'],field_state_counts={k:dict(v)for k,v in counts.items()},entries=list(rows.values()))
    dump(OUT/'field_verification_ledger.json',result);return result

def main():
    c=json.load(open(ROOT/'data/catalog.json',encoding='utf-8'));baseline=json.load(open(OUT/'baseline_140.json'));facts=json.load(open(OUT/'reviewed_facts.json'));old={e['id']:e for e in baseline['entries']};by={e['id']:e for e in c['entries']};allby=by|{e['id']:e for e in c.get('retired_entries',[])}
    for eid in old:assert eid in allby and {p['id']for p in old[eid]['printings']}<={p['id']for p in allby[eid]['printings']}
    for lang in('ja','ko'):assert [e for e in baseline['entries']if e['lang']==lang]==[e for e in c['entries']if e['lang']==lang]
    dump(OUT/'baseline_inventory.json',measure(baseline));dump(OUT/'current_inventory.json',measure(c))
    from tools import reconcile_catalog as recon
    original_out=recon.OUT;recon.OUT=OUT
    try:r=recon.reconcile(c,baseline)
    finally:recon.OUT=original_out
    # Explicit product-language evidence is bounded by release or exact alternate.
    unavailable={'2014xy':"https://bulbapedia.bulbagarden.net/wiki/McDonald%27s_Collection_2014_(TCG)",'2015xy':"https://bulbapedia.bulbagarden.net/wiki/McDonald%27s_Collection_2015_(TCG)",'ru1':'https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_Rumble_(TCG)'}
    for row in r['rows']:
        if row['lang']!='de':continue
        if row['release']in unavailable:
            row.update(status='not_released_in_German',availability_source=unavailable[row['release']],decision='Explicit release language inventory, not absence from provider')
        if(row['release'],row['canonical_number'])in(('xy4','24A'),('xy3','55A')):
            row.update(status='not_released_in_German',availability_source=facts['retirements'][0]['source_urls'][0],decision='English-only alternate product; ordinary German original remains separate')
    r['summary']={l:dict(collections.Counter(x['status']for x in r['rows']if x['lang']==l))for l in('en','de')};dump(OUT/'inventory_reconciliation.json',r)
    native_cards={(e['release'],number(e['number'])):e for e in by.values()if e['lang']=='de'};cameos=[]
    for e in by.values():
        if e['lang']!='en'or e['category']!='cameo'or e.get('subject_dex'):continue
        de=native_cards.get((e['release'],number(e['number'])));state='matched_native_identity'if de else'not_released_in_German'if e['release']in set(recon.NOT_GERMAN)|set(unavailable)else'held_previous_regional_claim'if(e['release'],e['number'])==('xy6','77a')else'needs_native_identity_and_printing_proof'
        cameos.append(dict(english_entry_id=e['id'],german_entry_id=de['id']if de else None,release=e['release'],number=e['number'],name=e['name'],status=state,source_urls=e['links']))
    dump(OUT/'cameo_reconciliation.json',dict(basis='Existing 65-card EN cameo source pool; not a complete external cameo inventory.',summary=dict(collections.Counter(x['status']for x in cameos)),rows=cameos))
    plan=json.load(open(OUT/'sample_plan.json'));sample=[]
    pub={x['entry_id']:x for x in json.load(open(RESEARCH/'systematic/publisher_evidence.json'))['assertions']};native={x['entry_id']:x for x in json.load(open(OUT/'carddex_reconciliation.json'))['assertions']}
    for row in plan['rows']:
        eid=row['entry_id'];e=allby[eid];errors=[]
        if row['position']==19:errors=['unsupported_exact_promo_date']
        if row['position']==61:errors=['unsupported_German_alternate_identity','image_is_ordinary_original_not_alternate']
        a=native.get(eid)or pub.get(eid);sample.append(row|dict(visual_identity='wrong_alternate_reference'if row['position']==61 else'agrees'if row['image']else'unassessed_missing_image',visual_artwork='unassessed_wrong_identity'if row['position']==61 else e.get('art_style')if row['image']else'unassessed_missing_image',rarity='checked_native_inventory'if a and(a.get('expected_rarity')or a.get('rarity_code'))==e.get('rarity_code')else'unassessed',date_check='primary_product_month_checked'if row['position']==19 else'unassessed_in_fresh_sample',errors_observed=errors,missing_artwork_at_baseline=not bool(row['art_style']),resolution='withdrawn_ID_preserved'if eid not in by else'corrected'if errors else'no_error_found_in_assessed_fields',all_variants_and_marketplace='unassessed_shared_card_reference'))
    result=dict(seed=plan['seed'],sample_size=len(sample),images_reviewed=sum(bool(x['image'])for x in sample),visual_identity_agreements=sum(x['visual_identity']=='agrees'for x in sample),records_with_observed_errors=sum(bool(x['errors_observed'])for x in sample),errors= dict(collections.Counter(k for x in sample for k in x['errors_observed'])),limitations=plan['design']+' Identity agreement with a cached face is not proof of physical availability, all variants or image provenance. Dates and many rarity fields remain unassessed. The previous sample is retained as a regression only.',rows=sample);dump(OUT/'sample_audit.json',result)
    led=ledger(c,facts)
    previous=json.load(open(RESEARCH/'systematic/work_queue.json'));queue=[];resolved=[];supported={q['printing_id']for q in facts['printing_updates']if q['status']=='documented_product_exception'}
    for item in previous['items']:
        item=copy.deepcopy(item)
        if item['kind']=='identity_reconciliation':
            rel=item['release'];no=number(item['number']);matched=[e for e in by.values()if(e['lang'],e['release'],number(e['number']))==('de',rel,no)]
            if rel in unavailable or matched:
                resolved.append(item|dict(resolution='excluded_language_release'if rel in unavailable else'added_native_deck_identity'));continue
            if rel in('2016xy','2018sm'):item.update(status='language_release_asserted_native_specimen_unresolved',blocker='International reference lists German, but no exact native specimen was obtained. Translated marketplace prices do not suffice.',next_action='Seek exact German numbered specimen or native contemporary checklist; keep out of accepted catalog meanwhile.')
        if item.get('printing_id')in supported:resolved.append(item|dict(resolution='documented_product_exception'));continue
        if item.get('entry_id')in c['reconciliation_research']['retired_entry_ids']:resolved.append(item|dict(resolution='unsupported_regional_target_withdrawn'));continue
        if item.get('kind')=='native_cameo_identity'and(item.get('release'),item.get('number'))in(('xy6','77a'),):
            item['next_action']='English-only product reference and wrong provider German image. Native specimen required before creating a German alternate. Preserve held prior claim.'
        queue.append(item)
    for doc in json.load(open(OUT/'carddex_reconciliation.json'))['documents']:
        if doc['status']!='cached':queue.append(dict(id='carddex-access:'+doc['release'],kind='source_access',priority=2,lang='de',release=doc['release'],source_urls=[doc['source_url']],blocker=doc['blocker'],next_action='Use existing publisher evidence; revisit native inventory only when a usable published source is available.'))
    queue +=[dict(id='regional-withdrawn:'+q['entry_id'],kind='withdrawn_regional_claim',priority=2,status='inactive_ID_preserved',**q,next_action='Only restore an exact native physical specimen; translated metadata and ordinary-card image are insufficient.')for q in facts['retirements']if q['reason']=='unsubstantiated_regional_identity']
    # Keep artwork work lists current after the sample fills.
    for q in queue:
        if q['kind']=='missing_artwork_classification':q['entry_ids']=[e['id']for e in by.values()if e['lang']==q['id'].split(':')[-1]and not e.get('art_style')]
    dump(OUT/'work_queue.json',dict(updated_on='2026-10-29',basis_revision='1.4.0',next_priorities=['Remaining 13 German primary candidates: ten promos and three McDonald’s native-specimen conflicts.','English-only product contamination and unsupported native finish claims.','Modern manufacturer PDF access and marketplace exact variant checks.'],resolved=resolved,items=queue))
    changes=[];filled=[]
    for eid,e in by.items():
        if eid not in old:continue
        before=old[eid]
        for key in('release_date','date_precision','rarity_code','name','art_style'):
            if before.get(key)==e.get(key):continue
            target=filled if before.get(key)is None else changes
            target.append(dict(entry_id=eid,lang=e['lang'],release=e['release'],number=e['number'],field=key,before=before.get(key),after=e.get(key)))
    summary=dict(baseline_revision='1.4.0',revision=c['revision'],baseline_counts=baseline['language_stats'],current_counts=c['language_stats'],corrected_existing_fields=changes,corrected_existing_record_count=len({q['entry_id']for q in changes}|set(c['reconciliation_research']['retired_entry_ids'])),filled_missing_fields=filled,withdrawn_regional_ids=c['reconciliation_research']['retired_entry_ids'],added_entry_ids=c['reconciliation_research']['added_entry_ids'],added_printing_ids=c['reconciliation_research']['added_printing_ids'],documented_existing_printing_exceptions=len(supported),reference_reconciliation=r['summary'],field_ledger_counts=led['field_state_counts'],sample={k:v for k,v in result.items()if k!='rows'},remaining_queue_items=len(queue),resolved_queue_items=len(resolved),limits=facts['limits'])
    dump(OUT/'audit_summary.json',summary);dump(OUT/'evidence_log.json',dict(observed_on='2026-10-29',reviewed_facts_path='reviewed_facts.json',cached_native_inventory='carddex_reconciliation.json',persistent_field_history='field_verification_ledger.json',source_lineages={u:lineage(u)for section in facts.values()if isinstance(section,list)for q in section if isinstance(q,dict)for u in urls(q)},acquisition_blockers='source_acquisition.json',note='Original source bytes and acquisition scripts are included in the separate 1.5 research evidence archive. No fake hashes for web snippets.'))
    print(json.dumps(dict(revision=c['revision'],corrected_records=summary['corrected_existing_record_count'],filled_fields=len(filled),added_entries=len(summary['added_entry_ids']),added_printings=len(summary['added_printing_ids']),withdrawn=len(summary['withdrawn_regional_ids']),queue=len(queue),resolved=len(resolved),sample_errors=result['records_with_observed_errors']),ensure_ascii=False))
    return summary
if __name__=='__main__':
 import argparse
 argparse.ArgumentParser(description=__doc__).parse_args()
 main()
