"""Regional catalog corrections and preservation of existing owned targets."""
import base64
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from dogdex.collector import Collection


class ExpandedResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((ROOT/'data/catalog.json').read_text(encoding='utf-8'))
        cls.byid = {e['id']: e for e in cls.catalog['entries']}
        cls.baseline = json.loads((ROOT/'data/research/expanded_upgrade_baseline.json').read_text(encoding='utf-8'))

    def card(self, lang, release, number):
        return next(e for e in self.byid.values() if (e['lang'], e['release'], e['number']) == (lang, release, number))

    def test_all_previous_targets_survive_and_secondary_ledgers_are_unchanged(self):
        preserved=self.byid|{e['id']:e for e in self.catalog['retired_entries']}
        self.assertTrue(set(self.baseline['entries'])-set(self.byid)<=set(self.catalog['reconciliation_research']['retired_entry_ids']))
        for eid, pids in self.baseline['entries'].items():
            self.assertTrue(eid in preserved)
            self.assertTrue(set(pids) <= {p['id'] for p in preserved[eid]['printings']})
        for lang, expected in self.baseline['secondary_language_sha256'].items():
            # Historical western passes preserved JA/KO; 1.7 changes are authorized and tested separately.
            frozen = json.loads((ROOT/'data/research/asia_17/baseline_160.json').read_text(encoding='utf-8'))
            entries = [e for e in frozen['entries'] if e['lang'] == lang]
            actual = hashlib.sha256(json.dumps(entries, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
            self.assertEqual(actual, expected)
        self.assertEqual(self.catalog['expanded_research']['review'], [])
        zorua=self.card('de','2011bw','9')
        self.assertEqual((zorua['metadata_state'],zorua['release_date'],zorua['date_precision']),('approved','2012-03-09','day'))
        self.assertEqual([(p['finish'],p['pattern']) for p in zorua['printings']],[('holo','confetti')])

    def test_new_cards_keep_rarity_artwork_and_fixed_printings_distinct(self):
        self.assertEqual((self.card('de','sm2','21a')['rarity_key'], self.card('de','sm2','21a')['art_style']), ('common','standard'))
        self.assertEqual((self.card('de','sm3.5','77a')['rarity_key'], self.card('de','sm3.5','77a')['art_style']), ('ultra_rare','full_art'))
        for lang, release, number, finish in [('en','tk-ex-p','2','non_holo'), ('en','tk-dp-l','6','non_holo'), ('de','tk-dp-l','3','holo')]:
            entry = self.card(lang, release, number)
            self.assertEqual(entry['rarity_key'], 'not_printed')
            self.assertEqual([(p['finish'],p['size']) for p in entry['printings']], [(finish,'standard')])
        for lang in ('en','de'):
            for release, number in [('swsh11','173'), ('swsh12','173'), ('swsh12.5gg','GG54')]:
                self.assertEqual(self.card(lang,release,number)['art_style'], 'full_art')
        for number in ('13',):
            self.assertEqual(self.card('de','g1',number)['art_style'], 'standard')
        for number in ('6','32'):
            self.assertEqual(self.card('de','basep',number)['rarity_key'], 'promo')
        for release,number in [('xyp','XY180'),('swshp','SWSH304'),('bwp','BW09')]:
            e=self.card('de',release,number)
            self.assertEqual(e['identity_status'],'provisional');self.assertFalse(e['printings']);self.assertTrue(e['evidence'])

    def test_product_dates_preserve_regional_and_partial_precision(self):
        self.assertEqual((self.card('de','xyp','XY19')['release_date'], self.card('de','xyp','XY19')['date_precision']), ('2014-09','month'))
        self.assertEqual(self.card('de','xyp','XY02')['release_date'], '2013')
        self.assertEqual(self.card('de','mep','095')['release_date'], '2026-10')
        self.assertEqual(self.card('en','mep','095')['release_date'], '2026-09-16')
        for lang in ('en','de'):
            for number in ('SWSH018','SWSH019'):
                self.assertEqual(self.card(lang,'swshp',number)['release_date'], '2020-05-22')
        self.assertEqual(self.card('de','swshp','SWSH085')['release_date'], '2021-02-19')
        self.assertEqual(self.card('de','swshp','SWSH199')['release_date'], '2022-02-25')
        source = next(r for r in self.catalog['releases'] if (r['lang'],r['release']) == ('en','tk-dp-l'))
        self.assertEqual(source['date'], '2007-09-24')
        self.assertEqual(self.card('en','tk-dp-l','3')['release_date'], source['date'])
        self.assertEqual(self.card('en','tk-dp-l','6')['release_date'], source['date'])

    def test_owned_copies_costs_and_exact_picture_survive_catalog_upgrade_and_backup(self):
        # Reconstruct the two original owned records before the changed BW19 tuple.
        old = copy.deepcopy(self.catalog)
        old['entries'] = [copy.deepcopy(self.card('en','base1','68')), copy.deepcopy(self.card('en','bwp','BW19'))]
        bw = old['entries'][1]
        bw['printings'] = [p for p in bw['printings'] if p['size']=='standard']
        self.assertEqual(len(bw['printings']), 1)
        bw['printings'][0]['pattern'] = 'unspecified'
        vpid, bpid = old['entries'][0]['printings'][1]['id'], bw['printings'][0]['id']
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)/'app';(root/'data').mkdir(parents=True)
            catalog_path=root/'data/catalog.json';catalog_path.write_text(json.dumps(old),encoding='utf-8')
            user=Path(folder)/'my_collection';before=Collection(root,user)
            before.add_copies(dict(printing_id=vpid,condition='near_mint',price='12.34',currency='EUR'))
            before.add_copies(dict(printing_id=bpid,condition='excellent',price='6.66',currency='EUR'))
            before.wish(dict(printing_id=vpid,wanted=True))
            raw=(ROOT/'data/images'/self.card('en','base1','68')['image']).read_bytes()
            before.catalog_image(dict(entry_id=old['entries'][0]['id'],printing_id=vpid,bytes=base64.b64encode(raw).decode(),source_note='User selected exact first-edition picture.'))
            copies=before.state()['copies'];backup=before.backup()
            catalog_path.write_text(json.dumps(self.catalog),encoding='utf-8')
            after=Collection(root,user)
            self.assertEqual(after.state()['copies'], copies)
            self.assertEqual(sum(c['price_minor'] for c in copies),1900)
            self.assertEqual(after.printing_map()[bpid][1]['pattern'],'cosmos')
            self.assertEqual(len(after.state()['printing_image_overrides']),1)
            self.assertEqual({r['printing_id'] for r in after.state()['wishlist']},{vpid})
            self.assertTrue(after.printing_map()[vpid][1]['image'].startswith('/user-images/'))
            after.remove_copy(dict(id=copies[0]['id']));after.restore(backup)
            self.assertEqual(after.state()['copies'],copies)
            self.assertEqual(len(after.state()['printing_image_overrides']),1)
            self.assertEqual(len({p['id'] for p in after.entries()[bw['id']]['printings']}),2)


if __name__ == '__main__':
    unittest.main()
