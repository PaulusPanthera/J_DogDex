"""Apply reviewed EN/DE facts; cached builds never accept provider defaults implicitly."""
import copy
from .special_import import ROOT,load,add_printing,date_fields

def apply(catalog):
    facts=load('western_reviewed_facts.json')
    byid={e['id']:e for e in catalog['entries']}
    identities={eid:(e['lang'],e['release'],e['number']) for eid,e in byid.items()}
    releases={(r['lang'],r['release']):r for r in catalog['releases']}
    date_changes=[];card_changes=[];printing_ids=[];review=[];image_ids=[]
    for record in facts.get('release_dates',[]):
        key=record['lang'],record['release'];r=releases[key]
        before=r.get('date')
        r.update(date=record['date'],date_precision={4:'year',7:'month',10:'day'}[len(record['date'])],date_state='sourced_regional',source_url=record['source_url'],evidence=record['evidence'],research_note=record.get('note',''))
        r.pop('unresolved_kind',None)
        if record.get('name'):r['name']=record['name']
        for e in byid.values():
            if (e['lang'],e['release'])!=key:continue
            if record.get('name'):
                e['set_name']=record['name']
                for source in e['sources']:
                    if source['id']=='release:'+e['lang']+':'+e['release']:source['name']=record['name']
            if e.get('year_basis') in ('card','product_source_claim'):continue
            e.update(date_fields(record['date'],'sourced_regional',record['source_url']),date_note=record.get('note',''),date_evidence=record['evidence'])
        if before!=record['date']:date_changes.append(dict(lang=key[0],release=key[1],before=before,after=record['date']))
    for record in facts.get('entry_updates',[]):
        e=byid[record['entry_id']]
        assert identities[e['id']]==tuple(record[k] for k in ('lang','release','number'))
        updates=copy.deepcopy(record['values']);before={k:e.get(k) for k in updates}
        e.update(updates);e.setdefault('research_corrections',[]).append({k:v for k,v in record.items() if k!='values'})
        if before!=updates:card_changes.append(dict(entry_id=e['id'],before=before,after=updates))
    for record in facts.get('card_dates',[]):
        e=byid[record['entry_id']]
        assert e['lang']==record['lang'] and e['number']==record['number']
        if e.get('release_date')!=record['date']:
            card_changes.append(dict(entry_id=e['id'],kind='individual_release_date',before=e.get('release_date'),after=record['date']))
        e.update(date_fields(record['date'],'sourced_card',record['source_url']),year_basis='card',date_mode='card',date_note=record['evidence'])
    for record in facts.get('printings',[]):
        e=byid[record['entry_id']]
        assert identities[e['id']]==tuple(record[k] for k in ('lang','release','number'))
        before=len(e['printings'])
        p=add_printing(e,record['printing'],dict(kind='reviewed_western_physical_printing',source_url=record['source_urls'][0],source_urls=record['source_urls'],evidence=record['evidence'],observed_on=facts['observed_on']),review)
        if p and len(e['printings'])>before:printing_ids.append(p['id'])
    aliases={}
    for record in facts.get('aliases',[]):
        old=byid[record['entry_id']];canonical=byid[record['canonical_id']]
        old.update(duplicate_of=canonical['id'],retirement_reason='duplicate_printed_card_identity',alias_evidence=record)
        canonical.setdefault('aliases',[]).append(old['id'])
        canonical['links']=list(dict.fromkeys(canonical['links']+old['links']))
        for source in old['sources']:
            if source['id'] not in {s['id'] for s in canonical['sources']}:canonical['sources'].append(source)
        aliases[old['id']]=canonical['id'];catalog.setdefault('retired_entries',[]).append(old)
    retired_forms=set()
    for record in facts.get('retirements',[]):
        old=byid[record['entry_id']]
        assert not old['printings']
        old.update(retirement_reason=record['reason'],retirement_evidence=record)
        catalog.setdefault('retired_entries',[]).append(old);retired_forms.add(old['id'])
    catalog['entries']=[e for e in catalog['entries'] if e['id'] not in aliases and e['id'] not in retired_forms]
    cache=load('western_image_cache.json')
    for e in catalog['entries']:
        record=cache.get(e['id'],{})
        if e.get('image') or not record.get('filename'):continue
        assert e['lang']==record['lang'] and e['number']==record['number']
        assert (ROOT/'data/images'/record['filename']).is_file()
        e.update(image=record['filename'],image_source=record['image_url'],image_evidence=record)
        for p in e['printings']:
            if not p.get('image'):p.update(image=e['image'],image_scope='entry')
        image_ids.append(e['id'])
    catalog['entry_aliases']=aliases
    catalog['western_research']=dict(observed_on=facts['observed_on'],release_date_changes=date_changes,entry_changes=card_changes,added_printing_ids=printing_ids,added_image_entry_ids=image_ids,duplicate_identities_removed=len(aliases),non_canine_forms_removed=len(retired_forms),review=review,holds=facts.get('holds',[]))
    return catalog
