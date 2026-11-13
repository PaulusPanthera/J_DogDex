"""Regional coverage regressions: actual identities, finishes, dates and evidence."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from dogdex.collector import Collection
from dogdex.scope import EXCLUDED_DEX


class CoverageResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((ROOT/'data/catalog.json').read_text(encoding='utf-8'))
        cls.facts = json.loads((ROOT/'data/research/coverage_reviewed_facts.json').read_text(encoding='utf-8'))
        cls.byid = {e['id']: e for e in cls.catalog['entries']}
        cls.summary = cls.catalog['coverage_research']

    def card(self, lang, release, number):
        return next(e for e in self.byid.values() if (e['lang'], e['release'], e['number']) == (lang, release, number))

    def test_new_regional_identities_have_real_sources_and_no_excluded_species(self):
        added = [self.byid[eid] for eid in self.summary['added_entry_ids'] if not self.byid[eid].get('component_entry_ids')]
        self.assertEqual(len(added), 26)
        self.assertEqual({e['lang'] for e in added}, {'de'})
        self.assertEqual(len({e['release'] for e in added}), 7)
        sources = {(r['lang'], r['release']) for r in self.catalog['releases']}
        for entry in added:
            self.assertIn((entry['lang'], entry['release']), sources)
            self.assertFalse(EXCLUDED_DEX & set(entry['subject_dex'] + entry['cameo_dex']))
            self.assertEqual(entry['rarity_state'], 'not_printed')
            self.assertEqual(len(entry['printings']), 1)
            self.assertTrue(entry['provenance']['source_urls'])
        self.assertEqual(self.summary['review'], [])

    def test_numbered_foil_face_cards_are_distinct_from_nonholo_inserts(self):
        for release, nonholo, holo in [('tk-bw-z', '17', '30'), ('tk-sm-l', '16', '30')]:
            first, second = self.card('de', release, nonholo), self.card('de', release, holo)
            self.assertNotEqual(first['id'], second['id'])
            self.assertEqual(first['printings'][0]['finish'], 'non_holo')
            self.assertEqual(second['printings'][0]['finish'], 'holo')
            self.assertEqual(first['date_precision'], 'year')
        for num in ('11', '28', '13', '22'):
            entry = self.card('de', 'tk-xy-p', num)
            self.assertEqual(entry['release_date'], '2016-04-27')
            self.assertEqual(entry['printings'][0]['finish'], 'non_holo')

    def test_beginner_cards_never_show_provider_indexes_as_printed_numbers(self):
        cards = [e for e in self.byid.values() if e['lang'] == 'de' and e['release'] == 'mfb']
        self.assertEqual({e['name'] for e in cards}, {'Vulpix', 'Vulnona', 'Fukano', 'Arkani'})
        self.assertEqual({e['number_key'] for e in cards}, {'11', '12', '13', '14'})
        for entry in cards:
            self.assertEqual((entry['number'], entry['identifier_namespace'], entry['release_date']), ('Unnumbered', 'provider_index', '2023'))
            self.assertEqual(json.loads(entry['printings'][0]['stamps_json']), ['charmander_deck'])

    def test_manufacturer_dates_override_card_index_dates_at_the_correct_language(self):
        for lang in ('en', 'de'):
            self.assertEqual(self.card(lang, 'smp', 'SM100')['release_date'], '2018-03-09')
        self.assertEqual(self.card('en', 'smp', 'SM84')['release_date'], '2017-11-03')
        self.assertEqual(self.card('de', 'smp', 'SM84')['release_date'], '2017-11')
        self.assertEqual(self.card('de', 'smp', 'SM84')['date_precision'], 'month')
        self.assertEqual(self.card('de', 'swshp', 'SWSH219')['release_date'], '2022-04-22')
        self.assertEqual(self.card('de', 'svp', '162')['release_date'], '2024')
        self.assertEqual(self.card('de', 'mep', '012')['release_date'], '2025-11-07')

    def test_real_product_sizes_and_lenticular_effect_have_collectible_variants(self):
        added = [p for e in self.byid.values() for p in e['printings'] if p['id'] in self.summary['added_printing_ids']]
        self.assertEqual(len(added), 41)
        jumbo = [p for p in added if p['size'] == 'oversized']
        self.assertEqual(len(jumbo), 13)
        self.assertEqual(sum(self.byid[p['entry_id']]['lang'] == 'de' for p in jumbo), 9)
        for lang in ('en', 'de'):
            entry = self.card(lang, 'mep', '012')
            oversized = next(p for p in entry['printings'] if p['size'] == 'oversized')
            self.assertEqual(oversized['print_state'], 'lenticular')
            self.assertIn('lenticular', oversized['label'])
            alolan = self.card(lang, 'smp', 'SM128')
            self.assertEqual({p['finish'] for p in alolan['printings']}, {'non_holo', 'holo'})
            self.assertEqual(alolan['number'], 'SM128')
        self.assertFalse(any(p['size'] == 'oversized' for p in self.card('de', 'svp', '162')['printings']))
        self.assertEqual(len(self.summary['holds']), 2)

    def test_regional_images_are_cached_individually_and_held_sources_never_publish(self):
        cache = json.loads((ROOT/'data/research/coverage_image_cache.json').read_text(encoding='utf-8'))
        for eid, record in cache.items():
            if record.get('filename'):
                entry = self.byid[eid]
                self.assertEqual((entry['lang'], entry['release'], entry['number']), (record['lang'], record['release'], record['number']))
                self.assertEqual(entry['image'], record['filename'])
                raw = (ROOT/'data/images'/record['filename']).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest()+'.webp', record['filename'])
                self.assertTrue(record['identity_check'])
                self.assertNotIn('held', record)
            else:
                self.assertNotIn(eid, self.summary['added_image_entry_ids'])
        mislabeled = next(r for r in cache.values() if r['lang'] == 'de' and r['release'] == 'mfb' and r['name'] == 'Vulpix')
        self.assertIn('English', mislabeled['held'])
        self.assertIsNone(self.byid[mislabeled['entry_id']]['image'])
        english = next(e for e in self.byid.values() if e['lang'] == 'en' and e['release'] == 'mfb' and e['dex'] == 37)
        self.assertIn('English', english['image_evidence']['identity_check'])

    def test_secondary_languages_are_unchanged_and_new_sources_can_be_edited(self):
        for lang, expected in self.facts['secondary_language_sha256'].items():
            # Preserve the historical no-change guard at the frozen 1.6 boundary.
            frozen = json.loads((ROOT/'data/research/asia_17/baseline_160.json').read_text(encoding='utf-8'))
            entries = [e for e in frozen['entries'] if e['lang'] == lang]
            digest = hashlib.sha256(json.dumps(entries, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
            self.assertEqual(digest, expected)
        with tempfile.TemporaryDirectory() as folder:
            store = Collection(ROOT, folder)
            eid = self.summary['added_entry_ids'][0]
            source_id = 'release:de:'+self.byid[eid]['release']
            self.assertIn(source_id, store.sources())
            source = store.sources()[source_id]
            self.assertEqual((source['kind'], source['series'], source['card_total']), ('deck', 'Schwarz & Weiß', 30))
            self.assertTrue(source['notes'])
            self.assertGreater(len(source['links']), 1)
            self.assertEqual(store.sources()['release:de:mfb']['kind'], 'deck')
            store.trash_item(dict(kind='source', target_id=source_id))
            self.assertNotIn(eid, store.entries())
            store.trash_item(dict(kind='source', target_id=source_id), True)
            self.assertIn(eid, store.entries())
            self.assertEqual(store.state()['copies'], [])
            jumbo = next(p for p in self.card('de', 'swshp', 'SWSH219')['printings'] if p['size'] == 'oversized')
            product_id = jumbo['sources'][0]['id']
            product = next(s for s in store.editor_view()['sources'] if s['id'] == product_id)
            self.assertEqual((product['card_count'], product['kind'], product['release_date']), (1, 'box', '2022-04-22'))
            self.assertTrue(product['links'])
            self.assertTrue(product['notes'])
            with self.assertRaises(ValueError):
                store.save_source(product | dict(source_id=product_id, lang='en'))

    def test_followup_dates_and_full_art_keep_native_rarity_and_precision(self):
        facts = json.loads((ROOT/'data/research/promo_reviewed_facts.json').read_text(encoding='utf-8'))
        self.assertEqual(len(facts['card_dates']), 22)
        for record in facts['card_dates']:
            entry = self.byid[record['entry_id']]
            self.assertEqual((entry['release_date'], entry['year_basis'], entry['date_state']), (record['date'], 'card', 'sourced_card'))
            if entry['lang'] == 'de':
                self.assertGreaterEqual(len(record['source_urls']), 2)
        self.assertEqual(self.card('de','swshp','SWSH213')['release_date'], '2022-04')
        self.assertEqual(next(p for p in self.card('de','swshp','SWSH214')['printings'] if p['size']=='oversized')['release_date'], '2022-04')
        self.assertEqual(self.card('en','mep','059')['release_date'], '2026-08-07')
        self.assertEqual((self.card('de','svp','198')['release_date'], self.card('de','svp','198')['date_precision']), ('2025-05-16', 'day'))
        for lang in ('en','de'):
            for release,number in [('mep','059'),('mep','080'),('mep','033'),*[('swshp','SWSH'+str(n)) for n in range(163,167)]]:
                entry = self.card(lang,release,number)
                self.assertEqual((entry['art_style'], entry['rarity_key']), ('full_art','promo'))
        self.assertEqual(len(self.catalog['promo_research']['artwork_entry_ids']), 14)

    def test_complete_v_union_is_one_independent_physical_card_with_backup_support(self):
        entries = [self.byid[eid] for eid in self.catalog['promo_research']['composite_entry_ids']]
        self.assertEqual({e['lang'] for e in entries}, {'en','de'})
        with tempfile.TemporaryDirectory() as folder:
            store = Collection(ROOT, folder)
            for entry in entries:
                self.assertEqual((entry['identifier_namespace'], entry['category'], entry['rarity_key']), ('composite','jumbo','promo'))
                self.assertEqual(len(entry['printings']), 1)
                self.assertEqual(entry['printings'][0]['print_state'], 'complete_v_union')
                self.assertEqual(entry['printings'][0]['size'], 'oversized')
                components = [self.byid[eid] for eid in entry['component_entry_ids']]
                self.assertEqual({e['number'] for e in components}, {'SWSH163','SWSH164','SWSH165','SWSH166'})
                self.assertTrue(entry['image'])
                product_id = entry['printings'][0]['sources'][0]['id']
                product = next(s for s in store.editor_view()['sources'] if s['id'] == product_id)
                self.assertEqual(product['card_count'], 5)
                store.add_copies(dict(printing_id=entry['printings'][0]['id'], price='12.34', currency='EUR'))
            owned = {c['printing_id'] for c in store.state()['copies']}
            self.assertEqual(len(owned), 2)
            self.assertFalse(owned & {p['id'] for entry in entries for eid in entry['component_entry_ids'] for p in self.byid[eid]['printings']})
            backup = store.backup()
            copy_id = store.state()['copies'][0]['id']
            store.remove_copy(dict(id=copy_id))
            store.restore(backup)
            self.assertEqual({c['printing_id'] for c in store.state()['copies']}, owned)
            self.assertTrue(all(c['price_minor'] == 1234 for c in store.state()['copies']))


if __name__ == '__main__':
    unittest.main()
