"""Reviewed 1.5 reconciliation. No network, locale transfers or generated variants."""
import copy,json,re
from .special_import import ROOT,add_printing,date_fields,stable
from .rarities import normalize
from .printing_model import legacy_label as printing_label

FACTS=ROOT/'data/research/reconciliation_15/reviewed_facts.json'

def guard_alternate_dates(entries):
    """A lettered reprint cannot inherit the original expansion's release date."""
    held=[]
    for e in entries:
        if e['lang']not in('en','de')or not re.fullmatch(r'\d+[ab]',e['number']):continue
        if e.get('year_basis')in('card','product_source_claim','manual')or e.get('date_mode')=='card':continue
        e['superseded_inherited_date']=e.get('release_date')
        e.update(date_fields(None,'unresolved_product_date',None),date_note='Alternate-numbered product date requires its own regional evidence; original expansion date is not inherited.')
        held.append(e['id'])
    return held

def apply(catalog):
    facts=json.loads(FACTS.read_text(encoding='utf-8'))
    by={e['id']:e for e in catalog['entries']}
    releases={(r['lang'],r['release']):r for r in catalog['releases']}
    changes=[];new=[];added=[];retired=[];review=[]
    def checked(r):
        e=by[r['entry_id']]
        assert e['lang']in('en','de')
        assert (e['lang'],e['release'],e['number'])==tuple(r[k]for k in('lang','release','number'))
        return e
    def update(e,values,r,kind):
        before={k:copy.deepcopy(e.get(k))for k in values}
        e.update(copy.deepcopy(values))
        if before!=values:changes.append(dict(kind=kind,entry_id=e['id'],before=before,after=copy.deepcopy(values),source_urls=r.get('source_urls',[])))
    for r in facts.get('releases',[]):
        assert r['lang']in('en','de')and(r['lang'],r['release'])not in releases
        rec=copy.deepcopy(r);rec.update(date_precision={4:'year',7:'month',10:'day'}[len(r['date'])],date_state='sourced_regional')
        catalog['releases'].append(rec);releases[r['lang'],r['release']]=rec
    for r in facts.get('release_dates',[]):
        rel=releases[r['lang'],r['release']];rel['superseded_provider_date']=rel.get('date')
        rel.update(date=r['date'],reference_date=None,date_precision={4:'year',7:'month',10:'day'}[len(r['date'])],date_state='sourced_regional',source_url=r['source_urls'][0],evidence=r['evidence'])
        for e in by.values():
            if(e['lang'],e['release'])==(r['lang'],r['release'])and e.get('year_basis')not in('card','product_source_claim'):
                update(e,date_fields(r['date'],'sourced_regional',r['source_urls'][0])|dict(date_evidence=r,date_note=r['evidence']),r,'date_precision')
    for r in facts.get('card_dates',[]):
        e=checked(r)
        update(e,date_fields(r['date'],'sourced_card',r['source_urls'][0])|dict(year_basis='card',date_mode='card',date_evidence=r,date_note=r['evidence']),r,'card_date')
        if r.get('distribution_dates'):e['distribution_dates']=copy.deepcopy(r['distribution_dates'])
    for r in facts.get('entry_updates',[]):
        e=checked(r);update(e,r['values'],r,'entry_fields')
        e.setdefault('research_corrections',[]).append({k:copy.deepcopy(v)for k,v in r.items()if k!='values'})
    for r in facts.get('entries',[]):
        assert r['lang']=='de'and r['availability_basis']=='native_numbered_inventory_and_explicit_language_release'
        assert r['dex']in{sp['dex']for sp in catalog['roster']}
        assert not any((e['lang'],e['release'],e['number_key'])==(r['lang'],r['release'],r['number_key'])for e in by.values())
        rel=releases[r['lang'],r['release']]
        eid=stable('entry',['reconciliation_15',r['lang'],r['release'],r['number_key'],r['dex']])
        e=dict(id=eid,lang=r['lang'],release=r['release'],name=r['name'],english=r['english'],dex=r['dex'],subject_dex=[r['dex']],cameo_dex=[],number=r['number'],number_key=r['number_key'],identifier_namespace='collector',set_name=rel['name'],metadata_state='approved',category='standard',year_basis='set',rarity_code=None,rarity_state='not_printed',rarity_label='',rarity_namespace='de:trainer_kit:no_printed_symbol',rarity_family='other',art_style=None,art_style_state='unresolved',image=None,printings=[],sources=[dict(id='release:de:'+r['release'],name=rel['name'],state='catalog_release')],links=r['source_urls'],provenance=dict(kind='native_numbered_inventory',source_urls=r['source_urls'],evidence=r['evidence'],observed_on=facts['observed_on']),**date_fields(rel['date'],'sourced_regional',rel['source_url']))
        for raw in r['printings']:
            pr=add_printing(e,raw,dict(kind='native_numbered_deck',source_url=r['source_urls'][0],source_urls=r['source_urls'],evidence=r['evidence']),review)
            assert pr;added.append(pr['id'])
        normalize(e);catalog['entries'].append(e);by[eid]=e;new.append(eid)
    for r in facts.get('printing_updates',[]):
        e=checked(r);pr=next(p for p in e['printings']if p['id']==r['printing_id'])
        # Adding evidence never changes a saved physical target or adds a twin.
        if r.get('values'):
            before={k:copy.deepcopy(pr.get(k))for k in r['values']};pr.update(copy.deepcopy(r['values']))
            changes.append(dict(kind='printing_fields',entry_id=e['id'],printing_id=pr['id'],before=before,after=r['values'],source_urls=r['source_urls']))
        pr['audit_status']=r['status'];pr['audit_evidence']={k:copy.deepcopy(v)for k,v in r.items()if k!='values'}
        pr['label']=printing_label(pr)
    for r in facts.get('printings',[]):
        e=checked(r);before=len(e['printings'])
        pr=add_printing(e,r['printing'],dict(kind='reviewed_exact_product_variant',source_url=r['source_urls'][0],source_urls=r['source_urls'],evidence=r['evidence']),review)
        assert pr
        for source in pr.get('sources',[]):source.update(kind=r['printing'].get('product_kind','deck'),links=r['source_urls'],notes=r['evidence'],**date_fields(r['printing'].get('release_date'),'sourced_product',r['source_urls'][0]))
        if r['printing'].get('release_date'):pr['date_source']=r['source_urls'][0]
        if len(e['printings'])>before:added.append(pr['id'])
    for r in facts.get('retirements',[]):
        e=checked(r);e.update(retirement_reason=r['reason'],retirement_evidence=copy.deepcopy(r))
        catalog.setdefault('retired_entries',[]).append(e);retired.append(e['id'])
    catalog['entries']=[e for e in catalog['entries']if e['id']not in retired]
    for e in catalog['entries']:
        if e['lang']in('en','de'):normalize(e)
    date_holds=guard_alternate_dates(catalog['entries'])
    catalog['reconciliation_research']=dict(observed_on=facts['observed_on'],basis_revision='1.4.0',changes=changes,added_entry_ids=new,added_printing_ids=added,retired_entry_ids=retired,alternate_date_holds=date_holds,review=review,limits=facts['limits'])
    return catalog
