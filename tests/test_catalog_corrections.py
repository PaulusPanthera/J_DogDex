"""Bounded English-era additions, date conflict and real saved-collection upgrade."""
import base64, copy, hashlib, json, tempfile, unittest
from pathlib import Path
from dogdex.catalog_corrections import apply
from dogdex.collector import Collection
from dogdex.mobile_export import build_snapshot
from dogdex.printing_model import physical_key

ROOT = Path(__file__).resolve().parents[1]
IMAGE = b'GIF89a' + b'\0' * 150

class CatalogCorrectionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.current = json.loads((ROOT/'data/catalog.json').read_text(encoding='utf-8'))
        cls.before = json.loads((ROOT/'data/research/corrections_1812/before_records.json').read_text(encoding='utf-8'))
        cls.facts = json.loads((ROOT/'data/research/corrections_1812/corrections.json').read_text(encoding='utf-8'))

    def old_catalog(self):
        c = copy.deepcopy(self.current)
        old = {e['id']: e for e in self.before['entries']}
        c['entries'] = [copy.deepcopy(old.get(e['id'], e)) for e in c['entries']]
        c['releases'] = [copy.deepcopy(self.before['release']) if (r['lang'], r['release']) == ('de','ecard3') else r for r in c['releases']]
        for k in ('statistics','language_stats','research_summary'):
            c[k] = copy.deepcopy(self.before[k])
        c.pop('catalog_corrections_1812', None)
        c['revision'] = '1.8.9'
        return c

    def test_exact_delta_is_idempotent_and_keeps_asian_records_and_existing_ids(self):
        old = self.old_catalog()
        old_ids = {p['id'] for e in old['entries'] for p in e['printings']}
        original = {e['id']: e for e in old['entries']}
        updated = apply(copy.deepcopy(old))
        additions = set(updated['catalog_corrections_1812']['added_printing_ids'])
        self.assertEqual(len(additions), 27)
        self.assertEqual({p['id'] for e in updated['entries'] for p in e['printings']}, old_ids | additions)
        affected = {r['entry_id'] for r in self.facts['printings']} | set(updated['catalog_corrections_1812']['date_entry_ids'])
        for e in updated['entries']:
            if e['id'] not in affected:
                self.assertEqual(e, original[e['id']], e['id'])
        self.assertEqual(apply(copy.deepcopy(updated)), updated)
        self.assertEqual(hashlib.sha256((ROOT/'data/catalog.sqlite3').read_bytes()).hexdigest(), 'e79d48ff8d056d88fa0d6b1f0771f220d79f62d82797c886183e20ada9c22da0')

    def test_all_32_reference_identities_have_the_documented_unlimited_finish(self):
        matrix=json.loads((ROOT/'data/research/corrections_1812/english_edition_matrix.json').read_text(encoding='utf-8'))
        self.assertEqual(len(matrix['rows']),32)
        by={e['id']:e for e in self.current['entries']}
        self.assertEqual(sum(r['disposition']=='newly_documented' for r in matrix['rows']),27)
        for row in matrix['rows']:
            e=by[row['entry_id']]
            self.assertEqual(e['lang'],'en')
            self.assertEqual(sum(p['edition']=='unlimited' and p['finish']==row['selected_finish'] for p in e['printings']),1)
            self.assertEqual(hashlib.sha256((ROOT/'data/research/corrections_1812'/row['source_file']).read_bytes()).hexdigest(),row['source_sha256'])
            self.assertIn(row['selected_variant_label'],row['original_variant_labels'])
        vulpix={(r['release'],r['number']) for r in self.facts['printings'] if by[r['entry_id']]['dex']==37}
        self.assertEqual(vulpix,{('gym1','65'),('gym1','73'),('gym2','37'),('gym2','66'),('neo4','91')})

    def test_selected_date_and_conflicting_period_are_both_retained(self):
        with tempfile.TemporaryDirectory() as t:
            store = Collection(ROOT, t)
            source = store.sources()['release:de:ecard3']
            self.assertEqual(source['release_date'], '2003-08-15')
            self.assertEqual(source['date_state'], 'sourced_regional_date_conflict')
            entries = [e for e in store.entries().values() if e['lang']=='de' and e['release']=='ecard3']
            self.assertEqual(len(entries), 8)
            for e in entries:
                self.assertEqual(e['release_date'], '2003-08-15')
                self.assertEqual(e['date_precision'], 'day')
                self.assertNotIn('release_period', e)
                self.assertIn('Winter 2003/2004', json.dumps(e['evidence']))
                self.assertEqual(e['date_evidence']['manufacturer_confirmation'], 'not_located')
            snapshot = build_snapshot(store)
            self.assertTrue(all(e['release_date']=='2003-08-15' for e in snapshot['entries'] if e['lang']=='de' and e['release']=='ecard3'))

    def test_manual_unlimited_records_costs_wishes_overrides_and_images_survive_upgrade(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t);(root/'data').mkdir()
            (root/'data/catalog.json').write_text(json.dumps(self.old_catalog()),encoding='utf-8')
            store = Collection(root)
            manual = {}
            selected = {('neo1','74'),('neo4','91'),('gym2','3')}
            for row in [r for r in self.facts['printings'] if (r['release'],r['number']) in selected]:
                eid = row['entry_id']
                pid = store.save_printing(dict(entry_id=eid,finish=row['printing']['finish'],pattern='none',edition='unlimited',confirmed=True,notes='My existing Unlimited card'))['printing_id']
                manual[eid] = pid
                store.add_copies(dict(printing_id=pid,quantity=2,price='4.56',currency='EUR',condition='near_mint',notes='Retain purchase',misprint_notes='Collected misprint',purchased_on='2026-10-30'))
                store.wish(dict(printing_id=pid,wanted=True))
                store.catalog_image(dict(entry_id=eid,printing_id=pid,bytes=base64.b64encode(IMAGE).decode(),source_note='My physical card'))
            store.override(dict(entry_id=self.facts['printings'][0]['entry_id'],values={'english':'My Snubbull label'},source_note='Keep manual correction'))
            before = store.state(True)
            images = {p.name:p.read_bytes() for p in (store.user_dir/'catalog_images').iterdir()}
            (root/'data/catalog.json').write_text(json.dumps(self.current),encoding='utf-8')
            upgraded = Collection(root)
            self.assertEqual(upgraded.state(True), before)
            self.assertEqual({p.name:p.read_bytes() for p in (upgraded.user_dir/'catalog_images').iterdir()}, images)
            for eid, pid in manual.items():
                entry = upgraded.entry(eid)
                self.assertEqual(len(entry['printings']), 2)
                unlimited = [p for p in entry['printings'] if p['edition']=='unlimited']
                self.assertEqual([p['id'] for p in unlimited], [pid])
                keys = [physical_key(eid,p) for p in entry['printings']]
                self.assertEqual(len(keys), len(set(keys)))
                self.assertTrue(unlimited[0]['image'].startswith('/user-images/'))
            self.assertEqual(upgraded.entry(self.facts['printings'][0]['entry_id'])['english'], 'My Snubbull label')
            snapshot = build_snapshot(upgraded)
            for pid in manual.values():
                self.assertEqual(snapshot['ownership'][pid], 2)
                self.assertIn(pid, snapshot['wishlist'])
            other = root/'restored';(other/'data').mkdir(parents=True)
            (other/'data/catalog.json').write_text(json.dumps(self.current),encoding='utf-8')
            restored = Collection(other);restored.restore(upgraded.backup())
            for table, rows in before.items():
                if table != 'audit_log':
                    self.assertEqual(restored.state(True)[table], rows, table)

if __name__ == '__main__':
    unittest.main()
