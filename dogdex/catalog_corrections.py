"""Apply reviewed English First Edition-era and German Skyridge facts reproducibly.

Personal collection files are never opened by this builder. New physical tuples
use the existing stable identity function. Conflicting dates stay in evidence.
"""
import copy, hashlib, json
from pathlib import Path
from .printing_model import physical_key
from .special_import import add_printing, date_fields, write_json

ROOT = Path(__file__).resolve().parents[1]
FACTS = ROOT / 'data/research/corrections_1812/corrections.json'

def event(obj, field, value, urls, summary, disposition='documented', family='corrections_1812'):
    record = dict(field=field, value=copy.deepcopy(value), source_urls=list(urls),
                  summary=summary, disposition=disposition, source_family=family,
                  retrieved_on='2026-10-31')
    key = 'evidence' if 'evidence' not in obj or isinstance(obj['evidence'], list) else 'correction_evidence'
    records = obj.setdefault(key, [])
    if record not in records:
        records.append(record)

def apply(catalog):
    facts = json.loads(FACTS.read_text(encoding='utf-8'))
    by = {(e['lang'], e['release'], e['number']): e for e in catalog['entries']}
    ids = []
    for row in facts['printings']:
        e = by[row['lang'], row['release'], row['number']]
        if e['id'] != row['entry_id']:
            raise ValueError('Reviewed English-era identity changed')
        review = []
        p = add_printing(e, row['printing'], dict(kind='reviewed_catalog_1812',
            source_url=row['source_urls'][0], source_urls=row['source_urls'],
            source_family=row['source_family'], reviewed_on=facts['reviewed_on'],
            evidence=row['evidence']), review)
        if p is None:
            raise ValueError('Reviewed Unlimited tuple cannot be applied: '+repr(review))
        p.update(collection_status='documented', verification=dict(
            existence=dict(status='documented', method='explicit_legacy_english_inventory_printing',
                source_urls=row['source_urls'], checked_on=facts['reviewed_on']),
            specimen=dict(status=row['specimen_status'], note=row['image_limit'])))
        event(e, 'Unlimited physical printing', dict(printing_id=p['id'], **row['printing']),
              row['source_urls'], row['evidence']+' '+row['image_limit'], family=row['source_family'])
        ids.append(p['id'])
        keys = [physical_key(e['id'], q) for q in e['printings']]
        if len(keys) != len(set(keys)):
            raise ValueError('Duplicate English-era physical identity')

    row = facts['release']
    release = next(r for r in catalog['releases'] if (r['lang'], r['release']) == (row['lang'], row['release']))
    urls = [row['source_url'], row['conflicting_claim']['source_url']]
    note = row['reason']
    selected = dict(date=row['selected_date'], source_url=row['source_url'],
                    source_family=row['source_family'], conflict=row['conflicting_claim'],
                    manufacturer_confirmation='not_located', reason=note)
    if release.get('date') != row['selected_date'] or release.get('date_state') != row['date_state']:
        prior = {k:copy.deepcopy(release.get(k)) for k in ('date','date_state','date_precision',
                 'source_url','source_urls','release_period','evidence','research_note','superseded_provider_date')}
        event(release, 'Previous selected German release date', prior, prior.get('source_urls') or [],
              'Earlier selection retained; it is no longer the displayed value.', 'superseded_selection')
    release.update(date=row['selected_date'], date_precision='day', date_state=row['date_state'],
        source_url=row['source_url'], source_urls=urls, evidence=selected, research_note=note,
        unresolved_kind='conflicting_regional_date_sources')
    release.pop('release_period', None)
    event(release, 'Selected German expansion date', selected, urls, note,
          'selected_with_unresolved_conflict', row['source_family'])
    affected = []
    for e in catalog['entries']:
        if (e['lang'], e['release']) != (row['lang'], row['release']):
            continue
        if e.get('year_basis') in ('manual', 'card', 'product_source_claim'):
            continue
        if e.get('release_date') != row['selected_date'] or e.get('date_state') != row['date_state']:
            previous = {k:copy.deepcopy(e.get(k)) for k in ('release_date','date_precision',
                        'date_state','date_source','date_evidence','release_period','year','date_note')}
            event(e, 'Previous selected German release date', previous,
                  [previous['date_source']] if previous['date_source'] else [],
                  'Earlier period retained as a conflicting historical source claim.', 'superseded_selection')
        e.update(date_fields(row['selected_date'], row['date_state'], row['source_url']),
                 date_evidence=copy.deepcopy(selected), date_note=note)
        e.pop('release_period', None)
        event(e, 'Selected German expansion date', selected, urls, note,
              'selected_with_unresolved_conflict', row['source_family'])
        affected.append(e['id'])
    catalog['catalog_corrections_1812'] = dict(version='1.8.12', reviewed_on=facts['reviewed_on'],
        facts_sha256=hashlib.sha256(FACTS.read_bytes()).hexdigest(),
        added_printing_ids=sorted(ids), date_entry_ids=sorted(affected),
        selected_german_skyridge_date=row['selected_date'], unresolved_conflicts=[selected],
        english_era_inventory=facts['english_era_inventory'], limits=facts['limits'])
    return catalog

def main():
    from .catalog_enrich import make_sqlite
    from .printing_enrich import refresh_statistics
    path = ROOT / 'data/catalog.json'
    catalog = json.loads(path.read_text(encoding='utf-8'))
    apply(catalog)
    catalog.update(revision='1.8.12', catalog_date='2026-10-31')
    refresh_statistics(catalog)
    catalog['statistics']['missing_release_dates'] = sum(not e.get('release_date') for e in catalog['entries'])
    catalog['research_summary'].update(
        accepted_set_dates=sum(bool(r.get('date')) for r in catalog['releases']),
        reference_only_set_dates=sum(not r.get('date') and bool(r.get('reference_date')) for r in catalog['releases']),
        unresolved_set_dates=sum(not r.get('date') and not r.get('reference_date') for r in catalog['releases']))
    write_json(path, catalog)
    make_sqlite(catalog)
    print(json.dumps(catalog['catalog_corrections_1812']))

if __name__ == '__main__':
    main()
