"""Focused 1.8.9 identity/forme review; collection rows are never rewritten.

Raw provider dex/cameo IDs do not distinguish Zygarde formes. The exact card
reviews below keep the canine cameo on 120 and hold the out-of-scope 104.
"""
import copy, hashlib, json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FACTS = ROOT / 'data/research/identity_189/facts.json'

@lru_cache(maxsize=1)
def reviewed_facts():
    return json.loads(FACTS.read_text(encoding='utf-8'))

def reviewed_key(entry):
    """An exact Western set/number match; never infer a regional counterpart."""
    if entry.get('lang') not in ('en','de'):
        return None
    if entry.get('release') != 'me03' and entry.get('canonical_set_id') != 'western:me03':
        return None
    if 718 not in set(entry.get('subject_dex') or []) | set(entry.get('cameo_dex') or []) | {entry.get('dex')}:
        return None
    number = str(entry.get('number','')).strip().lstrip('0')
    return number if number in ('104','120') else None

def apply_form_review(entry):
    """Also called after personal overlays, retaining every physical/owned ID."""
    number = reviewed_key(entry)
    if not number:
        return entry
    row = next(r for r in reviewed_facts()['forms'] if r['number'] == number)
    entry['scope_review'] = dict(version='1.8.9', reviewed_on='2026-10-31',
        decision=row['decision'], subject_forms=copy.deepcopy(row['subject_forms']),
        cameo_forms=copy.deepcopy(row['cameo_forms']),
        included_cameo_forms=copy.deepcopy(row['included_cameo_forms']),
        reason=row['reason'], source_urls=list(row['source_urls']))
    if row['decision'] == 'excluded_form':
        # Keep the documented card and all physical IDs in the editor and in
        # owned-copy history. Only its eligibility for completion is withdrawn.
        entry.update(identity_status='excluded', status_reason=row['reason'])
        for p in entry.get('printings',[]):
            p['collection_status'] = 'excluded'
    else:
        # These arrays describe the tracked roles, not every depicted forme.
        entry.update(subject_dex=[], cameo_dex=[718], dex=718, category='cameo')
        for p in entry.get('printings',[]):
            p['category'] = 'cameo'
    return entry

def append_evidence(entry, field, value, urls, summary, disposition='documented'):
    event=dict(field=field, value=copy.deepcopy(value), source_urls=list(urls),
        source_family='identity_corrections_189', disposition=disposition,
        retrieved_on='2026-10-31', summary=summary)
    history=entry.setdefault('evidence',[])
    if event not in history:
        history.append(event)

def apply(catalog):
    from .special_import import add_printing
    from .printing_model import physical_key
    facts=reviewed_facts();r=facts['restored_identity']
    e=next(e for e in catalog['entries'] if e['id']==r['entry_id'])
    if (e['lang'],e['release'],e['number']) != ('de','me03','077'):
        raise ValueError('Reviewed German 077 identity changed')
    image_path=ROOT/'data/images'/r['image']
    if not image_path.is_file() or hashlib.sha256(image_path.read_bytes()).hexdigest()+'.webp' != r['image']:
        raise ValueError('Reviewed native German image is unavailable or changed')
    e.update(image=r['image'], art_style='standard', art_style_state='visually_checked',
        art_style_source=dict(method='exact_native_card_image',source_urls=[facts['source_urls']['native_image']],inference=False),
        rarity_code='uncommon',rarity_state='known',rarity_family='uncommon',
        subject_dex=[],cameo_dex=[828],category='cameo',metadata_state='approved',identity_status='documented')
    e['status_reason']='Native German 077 artwork and explicit regional physical printings verified; Thievul on the shop billboard.'
    e['image_source']=dict(source_url=facts['source_urls']['native_image'],retrieved_on='2026-10-31',native_language='de',reference_scope='entry')
    append_evidence(e,'Native German artwork / cameo',{'image':r['image'],'cameo_dex':[828],'art_style':'standard'},
        [facts['source_urls']['user_checklist'],facts['source_urls']['native_image']],r['image_observation'])
    review=[];applied=[]
    for row in r['physical_printings']:
        raw=dict(finish=row['finish'],pattern=row['pattern'],edition='not_applicable',layout='standard',size='standard',material='paper',print_state='standard')
        p=add_printing(e,raw,dict(kind='reviewed_identity_189',source_url=row['source_urls'][0],source_urls=row['source_urls'],reviewed_on='2026-10-31',evidence=row['evidence']),review)
        if p is None:
            raise ValueError('Reviewed German printing could not be applied: '+repr(review))
        p.update(collection_status='documented',image=e['image'],image_scope='entry',category='cameo',
            verification=dict(existence=dict(status='documented',source_urls=row['source_urls'],checked_on='2026-10-31',method='native_checklist_or_direct_German_merchant'),specimen=dict(status='not_inspected')))
        p.setdefault('market_candidate',dict(product_id=877494,name='Lumiose City',source_url=facts['source_urls']['native_card'],state='unverified_provider_candidate'))
        applied.append(p['id'])
    append_evidence(e,'German physical printings',applied,list(dict.fromkeys(u for p in r['physical_printings'] for u in p['source_urls'])),
        'Non-holo from the native manufacturer checklist; reverse holo from an explicit German merchant listing. Neither finish is generated from rarity or an API generic Normal default.')
    form_ids=[]
    for entry in catalog['entries']:
        if not reviewed_key(entry):
            continue
        apply_form_review(entry);form_ids.append(entry['id'])
        append_evidence(entry,'Zygarde forme scope',entry['scope_review'],entry['scope_review']['source_urls'],entry['scope_review']['reason'],
            'excluded_collecting_scope' if entry['scope_review']['decision']=='excluded_form' else 'documented_cameo')
    keys=[physical_key(e['id'],p) for p in e['printings']]
    if len(keys)!=len(set(keys)):
        raise ValueError('Duplicate restored physical printing')
    catalog['identity_corrections_189']=dict(version='1.8.9',reviewed_on='2026-10-31',
        facts_sha256=hashlib.sha256(FACTS.read_bytes()).hexdigest(),restored_entry_id=e['id'],
        added_printing_ids=applied,form_reviewed_entry_ids=sorted(form_ids),limits=facts['limits'])
    return catalog

def main():
    from .catalog_enrich import make_sqlite
    from .scope import is_cameo
    path=ROOT/'data/catalog.json';catalog=json.loads(path.read_text(encoding='utf-8'))
    apply(catalog);catalog.update(revision='1.8.9',catalog_date='2026-10-31')
    es=catalog['entries'];ps=[p for e in es for p in e['printings']]
    catalog['statistics'].update(entries=len(es),printings=len(ps),without_printings=sum(not e['printings'] for e in es),missing_images=sum(not e.get('image') for e in es),
        full_art_entries=sum(e.get('art_style')=='full_art' for e in es),cameo_entries=sum(is_cameo(e) for e in es),
        missing_release_dates=sum(not e.get('release_date') for e in es))
    for lang in ('en','de'):
        catalog['language_stats'][lang].update(entries=sum(e['lang']==lang for e in es),with_printings=sum(e['lang']==lang and bool(e['printings']) for e in es),
            printings=sum(len(e['printings']) for e in es if e['lang']==lang),full_art=sum(e['lang']==lang and e.get('art_style')=='full_art' for e in es),cameos=sum(e['lang']==lang and is_cameo(e) for e in es))
    catalog['used_images']=sorted(set(catalog['used_images'])|{reviewed_facts()['restored_identity']['image']})
    path.write_text(json.dumps(catalog,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    make_sqlite(catalog)
    print(json.dumps(catalog['identity_corrections_189'],ensure_ascii=False))

if __name__=='__main__':
    main()
