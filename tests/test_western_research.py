"""Regression checks for reviewed western catalog corrections, not provider defaults."""
import contextlib,hashlib,io,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from dogdex.scope import EXCLUDED_DEX

class WesternResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog=json.loads((ROOT/'data/catalog.json').read_text(encoding='utf-8'))
        cls.entries=cls.catalog['entries']
        cls.facts=json.loads((ROOT/'data/research/western_reviewed_facts.json').read_text(encoding='utf-8'))
        cls.previous_ids={e['id']for e in json.loads((ROOT/'data/research/completion_16/baseline_150.json').read_text(encoding='utf-8'))['entries']}
    def card(self,lang,release,number):
        return next(e for e in self.entries if e['lang']==lang and e['release']==release and e['number']==number)
    def test_regional_dates_keep_real_precision_and_country(self):
        releases={(r['lang'],r['release']):r for r in self.catalog['releases']}
        for key,year in [('ecard1','2003'),('ecard2','2003'),('ex8','2005'),('ex11','2006'),('ex15','2007')]:
            r=releases['de',key];self.assertEqual((r['date'],r['date_precision']),(year,'year'));self.assertIn('Germany',str(r['evidence']))
        self.assertEqual(releases['de','2021swsh']['date'],'2021-03-11')
        self.assertEqual(releases['de','2022swsh']['date'],'2022-08-18')
        self.assertEqual(releases['de','xy0']['date'],'2013-11-08')
        # 1.8.17 superseded the old November estimate with regional evidence.
        self.assertEqual(releases['en','30th-c']['date'],'2026-09-16')
        self.assertEqual(self.card('en','bwp','BW66')['release_date'],'2013-02-06')
        self.assertEqual(self.card('en','bwp','BW52')['release_date'],'2012-09')
        self.assertEqual(self.card('de','mep','074')['release_date'],'2026-05-09')
        self.assertEqual(self.card('en','mep','074')['release_date'],'2026-05-09')
        self.assertEqual(self.card('de','mep','015')['release_date'],'2025')
        self.assertEqual(self.card('en','xy4','24a')['release_date'],'2017-05-19')
    def test_foil_evidence_overrides_bad_normal_flags_without_changing_rarity(self):
        for e in self.entries:
            if e['id']in self.previous_ids and e['lang'] in ('en','de') and e['release']=='30th':self.assertTrue(e['printings']);self.assertTrue(all(p['finish']=='holo' for p in e['printings']))
        self.assertEqual({p['finish'] for p in self.card('en','det1','15')['printings']},{'holo'})
        self.assertEqual(self.card('en','det1','15')['rarity_code'],'common')
        self.assertEqual({p['finish'] for p in self.card('en','bwp','BW52')['printings']},{'reverse_holo'})
        self.assertEqual({p['finish'] for p in self.card('en','smp','SM230')['printings']},{'holo'})
        rare=self.card('en','xy9','98b');self.assertEqual((rare['rarity_code'],rare['art_style']),('uncommon','full_art'))
        unresolved=self.card('de','xy6','77a');self.assertEqual(unresolved['identity_status'],'provisional');self.assertEqual(unresolved['metadata_state'],'review');self.assertTrue(unresolved['evidence'])
    def test_beginner_deck_indexes_are_not_printed_collector_numbers(self):
        cards=[e for e in self.entries if e['lang']=='en' and e['release']=='mfb']
        self.assertEqual(len(cards),4)
        self.assertEqual({e['number_key'] for e in cards},{'11','12','13','14'})
        for e in cards:
            self.assertEqual((e['number'],e['identifier_namespace'],e['metadata_state']),('Unnumbered','provider_index','approved'))
            self.assertEqual(len(e['printings']),1);p=e['printings'][0]
            self.assertEqual((p['finish'],json.loads(p['stamps_json'])),('non_holo',['charmander_deck']))
    def test_duplicate_and_wrong_form_records_are_outside_active_targets(self):
        active={e['id']:e for e in self.entries};retired={e['id']:e for e in self.catalog['retired_entries']}
        for old,new in self.catalog['entry_aliases'].items():
            self.assertNotIn(old,active);self.assertIn(new,active);self.assertEqual(retired[old]['duplicate_of'],new)
        for r in self.facts['retirements']:
            self.assertNotIn(r['entry_id'],active);self.assertEqual(retired[r['entry_id']]['retirement_reason'],'outside_10_percent_form_scope')
        self.assertTrue(any(e['dex']==718 and e['release']=='xy10' and e['number']=='52' for e in self.entries))
        self.assertFalse(any(EXCLUDED_DEX & set(e['subject_dex']+e['cameo_dex']) for e in self.entries))
    def test_images_and_remaining_holds_are_explicit_and_region_bound(self):
        w=self.catalog['western_research'];self.assertEqual(len(w['added_printing_ids']),152);self.assertEqual(len(w['added_image_entry_ids']),112)
        images={e['id']:e for e in self.entries if e['id'] in w['added_image_entry_ids']}
        for e in images.values():
            r=e['image_evidence'];self.assertEqual(r['lang'],e['lang']);self.assertEqual(r['number'],e['number']);self.assertNotIn('error',r);self.assertNotIn('held',r)
            self.assertTrue((ROOT/'data/images'/r['filename']).is_file())
        self.assertEqual(sum(e['lang']=='de' for e in images.values()),79)
        pending=[e for e in self.entries if e['id']in self.previous_ids and e['lang'] in ('en','de') and not e['printings']]
        resolved={r['entry_id'] for r in json.loads((ROOT/'data/research/expanded_reviewed_facts.json').read_text(encoding='utf-8'))['entry_updates'] if r['values'].get('metadata_state')=='approved'}
        resolved.update(self.catalog['new_sets_1817']['entry_ids'])
        self.assertEqual({e['id'] for e in pending},{r['entry_id'] for r in self.facts['holds']}-resolved)
        zorua=self.card('de','2011bw','9');self.assertEqual(zorua['metadata_state'],'approved')
        self.assertEqual(hashlib.sha256((ROOT/'data/catalog.sqlite3').read_bytes()).hexdigest(),'e79d48ff8d056d88fa0d6b1f0771f220d79f62d82797c886183e20ada9c22da0')
    def test_preparation_does_not_publish_an_intermediate_unscoped_index(self):
        from dogdex.prepare import build
        path=ROOT/'data/catalog.json';before=hashlib.sha256(path.read_bytes()).hexdigest()
        with contextlib.redirect_stdout(io.StringIO()):raw=build(write=False)
        self.assertGreater(len(raw['entries']),len(self.entries))
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),before)
    def test_staff_release_and_printed_card_suffix_are_preserved(self):
        for lang in ('en','de'):self.assertEqual(self.card(lang,'swshp','SWSH135')['name'],'Zacian LV.X')
        staff=[p for p in self.card('en','swshp','SWSH186')['printings'] if 'staff' in json.loads(p['stamps_json'])]
        self.assertEqual(len(staff),1);self.assertEqual((staff[0]['release_date'],staff[0]['date_precision']),('2023','year'))
        self.assertFalse(any('staff' in json.loads(p['stamps_json']) for p in self.card('de','swshp','SWSH186')['printings']))

if __name__=='__main__':unittest.main()
