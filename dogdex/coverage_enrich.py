"""Apply explicit western coverage additions without copying foreign printings.

Every new identity, finish and regional date has its own recorded evidence.
This stage is deliberately separate from provider import and never uses a
translated card name as proof that a physical language edition was released.
"""
import copy
import hashlib

from .printing_model import legacy_label as printing_label
from .scope import EXCLUDED_DEX
from .special_import import ROOT, add_printing, date_fields, load, stable


def apply(catalog, *, expanded=False, regional=False):
    assert not (expanded and regional)
    stage = 'regional' if regional else 'expanded' if expanded else 'coverage'
    facts = load(stage+'_reviewed_facts.json')
    followup = {} if expanded or regional else load('promo_reviewed_facts.json')
    for section in ('entries', 'entry_updates', 'card_dates', 'printings', 'printing_updates', 'holds'):
        facts.setdefault(section, []).extend(copy.deepcopy(followup.get(section, [])))
    byid = {entry['id']: entry for entry in catalog['entries']}
    releases = {(r['lang'], r['release']): r for r in catalog['releases']}
    added_entries, added_printings, dates, images, review = [], [], [], [], []

    for record in facts.get('releases', []):
        assert record['lang'] in ('en', 'de')
        key = record['lang'], record['release']
        assert key not in releases, 'A new source must not replace an existing source'
        release = copy.deepcopy(record)
        release.update(date_precision={4: 'year', 7: 'month', 10: 'day'}[len(record['date'])], date_state='sourced_regional')
        catalog['releases'].append(release)
        releases[key] = release
        catalog['retired_releases'] = [r for r in catalog.get('retired_releases', []) if (r['lang'], r['release']) != key]

    for record in facts.get('release_dates', []):
        assert record['lang'] in ('en', 'de')
        key = record['lang'], record['release']
        release = releases[key]
        release.update(date=record['date'], date_precision={4: 'year', 7: 'month', 10: 'day'}[len(record['date'])], date_state='sourced_regional', source_url=record['source_url'], evidence=record['evidence'])
        if record.get('name'):
            release['name'] = record['name']
        for entry in byid.values():
            if (entry['lang'], entry['release']) != key:
                continue
            if record.get('name'):
                entry['set_name'] = record['name']
                for source in entry['sources']:
                    if source['id'] == 'release:'+entry['lang']+':'+entry['release']:
                        source['name'] = record['name']
            if entry.get('year_basis') not in ('card', 'product_source_claim'):
                before = entry.get('release_date')
                entry.update(date_fields(record['date'], 'sourced_regional', record['source_url']), date_evidence=record['evidence'])
                if before != record['date']:
                    dates.append(dict(entry_id=entry['id'], before=before, after=record['date']))

    for record in facts.get('entries', []):
        assert record['lang'] in ('en', 'de') and record['dex'] not in EXCLUDED_DEX
        release = releases[record['lang'], record['release']]
        eid = stable('entry', ['western_coverage', record['lang'], record['release'], record['number_key'], record['dex']])
        assert eid not in byid
        assert not any((e['lang'], e['release'], e['number_key'], e['dex']) == (record['lang'], record['release'], record['number_key'], record['dex']) for e in byid.values()), 'Duplicate card identity'
        entry = dict(
            id=eid, lang=record['lang'], release=record['release'],
            name=record['name'], english=record['english'], dex=record['dex'],
            subject_dex=[record['dex']], cameo_dex=[],
            number=record['number'], number_key=record['number_key'],
            identifier_namespace=record.get('identifier_namespace', 'collector'),
            set_name=release['name'], year_basis='set',
            metadata_state='approved', category=record.get('category', 'standard'),
            rarity_code=record.get('rarity_code'), rarity_state='known' if record.get('rarity_code') else 'not_printed',
            rarity_namespace=record['lang']+':'+record['release']+':regional_taxonomy',
            rarity_label=record.get('rarity_label', 'No printed rarity'), rarity_family='other',
            art_style=record.get('art_style', 'standard'), art_style_state='verified',
            art_style_source=record.get('art_style_source') or dict(method='reviewed_exact_regional_card_reference' if expanded else 'regional_deck_card_reference', source_urls=record['source_urls']),
            image=None, printings=[],
            sources=[dict(id='release:'+record['lang']+':'+record['release'], name=release['name'], state='catalog_release')],
            links=record['source_urls'],
            provenance=dict(kind='reviewed_regional_identity', source_urls=record['source_urls'], evidence=record['evidence'], observed_on=facts['observed_on']),
            **date_fields(release.get('date') or release.get('reference_date'), 'sourced_regional', release.get('source_url') or release.get('reference_source_url')),
        )
        entry['date_evidence'] = release.get('evidence')
        if record.get('release_date'):
            entry.update(date_fields(record['release_date'], 'sourced_card', record['source_urls'][0]), year_basis='card', date_mode='card', date_evidence=record['evidence'])
        if record.get('notes'):
            entry['notes'] = record['notes']
        if record.get('component_entry_ids'):
            components = [byid[eid] for eid in record['component_entry_ids']]
            assert len(components) == 4 and all((e['lang'], e['dex'], e['rarity_code']) == (entry['lang'], entry['dex'], entry['rarity_code']) for e in components)
            assert entry['identifier_namespace'] == 'composite' and all(p.get('size') == 'oversized' for p in record['printings'])
            entry['component_entry_ids'] = record['component_entry_ids']
        for raw in record['printings']:
            printing = add_printing(entry, raw, dict(kind='reviewed_composite_oversized_card' if record.get('component_entry_ids') else 'reviewed_regional_physical_card' if expanded else 'reviewed_regional_deck_card', source_url=record['source_urls'][0], source_urls=record['source_urls'], evidence=record['evidence'], observed_on=facts['observed_on']), review)
            assert printing, 'Every new accepted identity needs an evidenced physical printing'
            for source in printing.get('sources', []):
                source.update(kind=raw.get('product_kind') or ('box' if printing['size'] == 'oversized' else 'deck'), links=record['source_urls'], notes=record['evidence'], **date_fields(raw.get('release_date'), 'sourced_product', record['source_urls'][0]))
            added_printings.append(printing['id'])
        assert entry['printings']
        catalog['entries'].append(entry)
        byid[eid] = entry
        added_entries.append(eid)

    def checked_entry(record):
        entry = byid[record['entry_id']]
        assert entry['lang'] in ('en', 'de')
        assert (entry['lang'], entry['release'], entry['number']) == tuple(record[k] for k in ('lang', 'release', 'number'))
        return entry

    for record in facts.get('entry_updates', []):
        entry = checked_entry(record)
        assert set(record['values']) <= {'art_style', 'art_style_state', 'art_style_source', 'sources', 'rarity_code', 'rarity_state', 'rarity_label', 'rarity_namespace', 'rarity_family', 'metadata_state'}
        entry.update(copy.deepcopy(record['values']))
        entry.setdefault('research_corrections', []).append({k: v for k, v in record.items() if k != 'values'})

    for record in facts.get('card_dates', []):
        entry = checked_entry(record)
        before = entry.get('release_date')
        entry.update(date_fields(record['date'], 'sourced_card', record['source_urls'][0]), year_basis='card', date_mode='card', date_note=record['evidence'], date_evidence=record)
        if before != record['date']:
            dates.append(dict(entry_id=entry['id'], before=before, after=record['date']))
        entry['links'] = list(dict.fromkeys(entry['links'] + record['source_urls']))

    for record in facts.get('printings', []):
        entry = checked_entry(record)
        before = len(entry['printings'])
        printing = add_printing(entry, record['printing'], dict(kind='reviewed_western_product', source_url=record['source_urls'][0], source_urls=record['source_urls'], evidence=record['evidence'], observed_on=facts['observed_on']), review)
        assert printing, 'Reviewed product failed the identity/rarity/physical tuple gate'
        for field in ('notes', 'date_state', 'date_note', 'world_championship_year', 'player_signature', 'tournament_legal', 'cardmarket_url', 'cardmarket_search'):
            if field in record['printing']:
                printing[field] = copy.deepcopy(record['printing'][field])
        if len(entry['printings']) > before:
            added_printings.append(printing['id'])
        for source in printing.get('sources', []):
            source.update(kind=record['printing'].get('product_kind') or ('box' if printing['size'] == 'oversized' else 'deck'), links=record['source_urls'], notes=record['evidence'], **date_fields(record['printing'].get('release_date'), record['printing'].get('date_state') or 'sourced_product', record['source_urls'][0]))
        entry['links'] = list(dict.fromkeys(entry['links'] + record['source_urls']))

    for record in facts.get('printing_updates', []):
        entry = checked_entry(record)
        printing = next(p for p in entry['printings'] if p['id'] == record['printing_id'])
        # Correct reviewed product details without changing a saved physical ID.
        printing.update(copy.deepcopy(record['values']))
        if 'release_date' in record['values']:
            for source in printing.get('sources', []):
                source.update(kind=source.get('kind') or ('box' if printing['size'] == 'oversized' else 'deck'), links=record['source_urls'], notes=record['evidence'], **date_fields(printing['release_date'], 'sourced_product', record['source_urls'][0]))
        printing['label'] = printing_label(printing)
        printing.setdefault('research_corrections', []).append({k: v for k, v in record.items() if k != 'values'})

    for eid, record in load(stage+'_image_cache.json').items():
        if not record.get('filename'):
            continue
        entry = byid[eid]
        assert entry['lang'] in ('en', 'de') and (entry['lang'], entry['release'], entry['number']) == (record['lang'], record['release'], record['number'])
        if entry.get('image'):
            continue
        path = ROOT / 'data/images' / record['filename']
        assert path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()+'.webp' == record['filename']
        entry.update(image=record['filename'], image_source=record['image_url'], image_evidence=record)
        for printing in entry['printings']:
            if not printing.get('image'):
                printing.update(image=entry['image'], image_scope='entry')
        images.append(eid)

    catalog[stage+'_research'] = dict(observed_on=facts['observed_on'], added_entry_ids=added_entries, added_printing_ids=added_printings, card_date_changes=dates, added_image_entry_ids=images, corrected_printing_ids=[r['printing_id'] for r in facts.get('printing_updates', [])], holds=facts.get('holds', []), review=review)
    if not expanded and not regional:
        catalog['promo_research'] = dict(observed_on=followup['observed_on'], card_date_entry_ids=[r['entry_id'] for r in followup.get('card_dates', [])], artwork_entry_ids=[r['entry_id'] for r in followup.get('entry_updates', []) if r['values'].get('art_style') == 'full_art'], composite_entry_ids=[stable('entry', ['western_coverage', r['lang'], r['release'], r['number_key'], r['dex']]) for r in followup.get('entries', [])])
    return catalog
