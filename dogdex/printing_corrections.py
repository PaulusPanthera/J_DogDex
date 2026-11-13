"""Bounded 1.8.6 corrections from the completed manual audit, retaining IDs.

No cross-language variants, finish inference or new card identities are made.
The reviewed fact file is the reproducible input; personal data is never edited.
"""
import copy, hashlib, json
from pathlib import Path
from .special_import import add_printing, date_fields, write_json
from .printing_model import physical_key, printing_label
from .printing_enrich import refresh_statistics

ROOT = Path(__file__).resolve().parents[1]
FACTS = ROOT / 'data/research/printing_186/corrections.json'

def evidence(obj, event):
    # Older release evidence can be a dict/string. Retain it without coercion.
    key = 'evidence' if isinstance(obj.get('evidence'), list) else 'correction_evidence'
    events = obj.setdefault(key, [])
    if event not in events:
        events.append(copy.deepcopy(event))

def apply(catalog):
    facts = json.loads(FACTS.read_text(encoding='utf-8'))
    by = {(e['lang'], e['release'], e['number']): e for e in catalog['entries']}
    by_pid = {p['id']: p for e in catalog['entries'] for p in e['printings']}
    added, applied, review = [], [], []
    def event(field, value, urls, summary):
        return dict(field=field, value=copy.deepcopy(value), source_urls=urls,
                    source_family='printing_corrections_186', disposition='documented',
                    retrieved_on=facts['reviewed_on'], summary=summary)
    for row in facts['printings']:
        key = row['lang'], row['release'], row['number']
        if key[0] not in ('en', 'de') or key not in by:
            raise ValueError('Reviewed card identity changed: '+repr(key))
        e = by[key]
        raw = dict(finish=row['finish'], pattern=row['pattern'], edition='not_applicable',
                   layout='standard', size='standard', material='paper', stamps=row.get('stamps', []),
                   print_state='standard', printed_rarity_state='inherit', printed_rarity_code=None)
        if row.get('release_date'):
            raw.update(release_date=row['release_date'], source_url=row['source_urls'][0])
        old_ids = {p['id'] for p in e['printings']}
        provenance = dict(kind='reviewed_manual_audit_186', source_url=row['source_urls'][0],
                          source_urls=row['source_urls'], reviewed_on=facts['reviewed_on'],
                          original_terms=row.get('original_terms'), evidence=row['evidence'],
                          evidence_origin=row['evidence_origin'])
        p = add_printing(e, raw, provenance, review)
        if p is None:
            raise ValueError('Reviewed printing could not be applied: '+repr(review))
        is_new = p['id'] not in old_ids
        if is_new:
            p.update(collection_status='documented',
                     verification=dict(existence=dict(status='documented', source_urls=row['source_urls'],
                         checked_on=facts['reviewed_on'], method=row['evidence_origin']),
                         specimen=dict(status='not_inspected')))
            added.append(p['id'])
        if row.get('date_state'):
            p.update(date_fields(row.get('release_date'), row['date_state'], row['source_urls'][0]))
        for product in row.get('products', []):
            add_printing(e, raw | dict(product_name=product), provenance, review)
        p['label'] = printing_label(p)
        evidence(e, event('Physical printing', dict(printing_id=p['id'], **{
            k:p[k] for k in ('finish','pattern','edition','layout','size','material','stamps_json','print_state')}),
            row['source_urls'], row['evidence']))
        applied.append(p['id'])
    for row in facts['printing_metadata']:
        p = by_pid[row['printing_id']]
        p.update(copy.deepcopy(row['values']))
        p['label'] = printing_label(p)
        evidence(p, event('Printing-specific metadata', row['values'], row['source_urls'], row['reason']))
    for row in facts['release_metadata']:
        r = next(r for r in catalog['releases'] if (r['lang'],r['release'])==(row['lang'],row['release']))
        r.update(copy.deepcopy(row['values']))
        evidence(r, event('Selected release metadata', row['values'], row['source_urls'], row['reason']))
        for e in catalog['entries']:
            if (e['lang'],e['release']) != (row['lang'],row['release']):
                continue
            if 'name' in row['values']:
                e['set_name'] = row['values']['name']
            if 'date' in row['values'] and e.get('year_basis') not in ('manual','card','product_source_claim'):
                e.update(date_fields(row['values']['date'], row['values']['date_state'], row['source_urls'][0]))
    for sid, values in facts['source_metadata'].items():
        catalog.setdefault('source_metadata', {}).setdefault(sid, {}).update(copy.deepcopy(values))
    for row in facts['unresolved']:
        e = by[row['lang'],row['release'],row['number']]
        ev = event('variant_claims', row['claim'], row['source_urls'], row['blocker'])
        ev['disposition'] = 'unresolved_language_specific_printing'
        evidence(e, ev)
    # This bounded specification covers regular-set cards only, not product variants.
    for lang in ('en','de'):
        for number in ('074','075','076','061','062'):
            e = by[lang,'sv10.5w',number]
            specs = [dict(finish=p['finish'], pattern=p['pattern'], edition=p['edition'],
                          layout=p['layout'], size=p['size'], material=p['material'],
                          stamps_json=p['stamps_json'], print_state=p['print_state'],
                          status='documented', scope='regular_set', source_urls=facts['white_flare_sources'])
                     for p in e['printings'] if not json.loads(p['stamps_json'])]
            e['printing_specification'] = dict(status='reviewed_regular_set', reviewed_on=facts['reviewed_on'],
                expected=specs, limits='Only the five reviewed White Flare regular-set identities; no patterned Illustration Rares or inferred regional exclusives.')
    catalog['printing_corrections_186'] = dict(version='1.8.6', reviewed_on=facts['reviewed_on'],
        facts_sha256=hashlib.sha256(FACTS.read_bytes()).hexdigest(), applied_printing_ids=sorted(set(applied)),
        new_printing_ids=sorted(p['id'] for e in catalog['entries'] for p in e['printings']
                              if p.get('provenance',{}).get('kind')=='reviewed_manual_audit_186'),
        unresolved=facts['unresolved'])
    return dict(added=added, matched=len(applied)-len(added))

def main():
    catalog = json.loads((ROOT/'data/catalog.json').read_text(encoding='utf-8'))
    result = apply(catalog)
    catalog.update(revision='1.8.6', catalog_date='2026-10-30')
    refresh_statistics(catalog)
    write_json(ROOT/'data/catalog.json', catalog)
    from .catalog_enrich import make_sqlite
    make_sqlite(catalog)
    print(json.dumps(dict(added=len(result['added']), matched=result['matched'],
                         printings=catalog['statistics']['printings'])))

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', required=True)
    parser.parse_args()
    main()
