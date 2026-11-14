"""Independent cameo coverage, bounded corrections and regional safety checks."""
import collections
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from catalog_history import catalog_at,read
from dogdex.cameo_review import apply,verify_coverage,require_coverage
from dogdex.collector import Collection
from dogdex.printing_model import physical_key

ROOT=Path(__file__).resolve().parents[1]
def digest(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

class CameoReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=read('data/catalog.json');cls.f=read('data/research/cameo_1820/facts.json');cls.base=read('data/research/cameo_1820/baseline_1819.json');cls.registry=read('data/research/cameo_1820/coverage_requirements.json')
        cls.by={e['id']:e for e in cls.c['entries']}

    def host(self,lang,release,num):
        return next(e for e in self.c['entries'] if (e['lang'],e['release'],e['number'].lstrip('0'))==(lang,release,num.lstrip('0')))

    def test_delta_preserves_every_original_id_and_printing_field(self):
        self.assertTrue(set(self.base['entry_hashes'])<=self.by.keys())
        expected_new={r['entry_id'] for r in self.f['records'] if r['action']=='new_entry'}
        self.assertEqual(set(self.by)-set(self.base['entry_hashes']),expected_new);self.assertEqual(len(expected_new),7)
        ps={p['id']:(e,p) for e in self.c['entries'] for p in e['printings']}
        self.assertEqual(set(ps)-set(self.base['physical_keys']),set(self.c['cameo_review_1820']['added_printing_ids']))
        self.assertEqual(len(set(ps)-set(self.base['physical_keys'])),12)
        for pid,key in self.base['physical_keys'].items():
            e,p=ps[pid];self.assertEqual(list(physical_key(e['id'],p)),key,pid);self.assertEqual(digest(p),self.base['printing_hashes'][pid],pid)
        allowed={r['entry_id'] for r in self.f['records']+self.f['link_updates']}
        actual={eid for eid,h in self.base['entry_hashes'].items() if digest(self.by[eid])!=h}
        self.assertEqual(actual,allowed&set(self.base['entry_hashes']))

    def test_historical_1819_fixture_matches_frozen_archive_hashes(self):
        old=catalog_at('1.8.19')
        self.assertEqual({e['id']:digest(e) for e in old['entries']},self.base['entry_hashes'])
        self.assertEqual(digest(old['roster']),self.base['roster_sha256'])

    def test_perrin_is_exact_localized_reflection_card(self):
        for lang,name in [('en','Perrin'),('de','Gemma')]:
            e=self.host(lang,'sv06','220');self.assertEqual(e['name'],name);self.assertEqual(e['category'],'cameo');self.assertEqual(e['cameo_dex'],[58]);self.assertEqual(e['subject_dex'],[])
            self.assertEqual(e['rarity_code'],'special_illustration_rare');self.assertEqual(e['art_style'],'full_art');self.assertEqual(e['release_date'],'2024-05-24');self.assertEqual([p['finish'] for p in e['printings']],['holo'])
            self.assertFalse(any(x['lang']==lang and x['release']=='sv06' and x['number'] in ('160','209') and 58 in x.get('cameo_dex',[]) for x in self.c['entries']))

    def test_species_repairs_do_not_add_duplicate_cards_or_printings(self):
        for lang in ('en','de'):self.assertEqual(self.host(lang,'30th','150')['cameo_dex'],[448,570,571,745])
        self.assertIn(263,self.host('de','mep','059')['cameo_dex']);self.assertIn(571,self.host('de','smp','SM83')['cameo_dex'])
        old={e['id']:e for e in catalog_at('1.8.19')['entries']}
        for row in self.f['link_updates']:self.assertEqual(self.by[row['entry_id']]['printings'],old[row['entry_id']]['printings'])

    def test_regional_stamps_and_products_remain_distinct(self):
        for lang in ('en','de'):
            for num in ('108','110'):
                e=self.host(lang,'mep',num);self.assertEqual(e['subject_dex'],[]);self.assertEqual(e['category'],'cameo');self.assertEqual(e['printings'][0]['stamps_json'],'["30th_anniversary"]')
        en=self.host('en','mep','092');de=self.host('de','mep','092')
        self.assertTrue(all(p['finish']=='non_holo' and p['pattern']=='none' for e in (en,de) for p in e['printings']))
        self.assertEqual({p['stamps_json'] for p in en['printings']},{'[]','["staff"]'});self.assertEqual([p['stamps_json'] for p in de['printings']],['[]'])
        self.assertEqual(len({physical_key(en['id'],p) for p in en['printings']}),2)
        with tempfile.TemporaryDirectory() as user:
            store=Collection(ROOT,user);es=store.entries();sources=store.sources()
            for row in self.f['records']:
                e=es[row['entry_id']];self.assertEqual(e['primary_source_id'],'release:'+e['lang']+':'+e['release'])
                for p in e['printings']:
                    for sid in p.get('distribution_source_ids',[]):self.assertEqual(sources[sid]['source_role'],'product')

    def test_replay_is_idempotent_and_preserves_regional_scope(self):
        c=copy.deepcopy(self.c);apply(c);self.assertEqual(c,self.c)
        self.assertEqual(digest(c['roster']),self.base['roster_sha256'])
        self.assertEqual(digest([e for e in c['entries'] if e['lang'] in ('ja','ko')]),self.base['asian_entries_sha256'])
        self.assertEqual(len(c['roster']),41)

    def test_positive_requirements_come_from_independent_discovery_sources(self):
        self.assertTrue(verify_coverage(self.c,self.registry)['ok']);self.assertEqual(len(self.registry['appearances']),153)
        comparison=read('data/research/cameo_1820/reference_comparison.json')
        self.assertEqual({r['source'] for r in comparison['cases']},{'cardcameos','pokecameos','elitefourum_master'})
        self.assertGreater(comparison['summary']['forum_claims'],0)
        self.assertTrue(all(r['source_urls'] for r in self.registry['appearances']))

    def test_coverage_rejects_dropped_host(self):
        c=copy.deepcopy(self.c);eid=self.host('de','sv06','220')['id'];c['entries']=[e for e in c['entries'] if e['id']!=eid]
        with self.assertRaisesRegex(ValueError,'Cameo coverage failed'):require_coverage(c,self.registry)

    def test_coverage_rejects_lost_species_link(self):
        c=copy.deepcopy(self.c);e=next(e for e in c['entries'] if e['id']==self.host('en','30th','150')['id']);e['cameo_dex'].remove(745)
        self.assertFalse(verify_coverage(c,self.registry)['ok'])

    def test_coverage_rejects_duplicate_canonical_host(self):
        c=copy.deepcopy(self.c);e=copy.deepcopy(self.host('en','sv06','220'));e['id']='unreconciled_import';c['entries'].append(e)
        self.assertFalse(verify_coverage(c,self.registry)['ok'])
        with self.assertRaisesRegex(ValueError,'already indexed'):
            old=catalog_at('1.8.19');old['entries'].append(e);apply(old)

    def test_coverage_rejects_lost_or_changed_staff_identity(self):
        c=copy.deepcopy(self.c);e=next(e for e in c['entries'] if e['id']==self.host('en','mep','092')['id']);p=next(p for p in e['printings'] if p['stamps_json']=='["staff"]');p['stamps_json']='[]'
        self.assertFalse(verify_coverage(c,self.registry)['ok'])
        e['printings']=[p for p in e['printings'] if p['stamps_json']!='[]'];self.assertFalse(verify_coverage(c,self.registry)['ok'])

    def test_unverified_variants_are_not_generated(self):
        for lang in ('en','de'):
            self.assertEqual([p['finish'] for p in self.host(lang,'me06','095')['printings']],['non_holo'])
        for e in self.c['entries']:
            if e['lang']=='de' and ((e['release']=='xy9' and e['number'] in ('98a','98b')) or (e['release']=='swshp' and e['number'] in ('SWSH116','SWSH244'))):self.assertEqual(e['printings'],[])
            if e['lang']=='en' and e['release']=='mep' and e['number']=='120':self.assertEqual(e['printings'],[])
        self.assertEqual(len(self.f['pending']),9)

    def test_cached_images_have_receipts_and_prices_are_unconfirmed(self):
        for row in self.f['records']:
            e=self.by[row['entry_id']]
            self.assertEqual(e['rarity_key'],e['rarity_code'])
            for info in [row['image']]+[p['image'] for p in row['physical'] if p.get('image')]:
                self.assertEqual(hashlib.sha256((ROOT/'data/images'/info['filename']).read_bytes()).hexdigest(),info['cached_sha256'])
            for p in e['printings']:
                self.assertFalse(p.get('market_confirmed'));self.assertFalse(p.get('price_product_id'))
                if p.get('market_candidate'):self.assertEqual(p['market_candidate']['physical_key'],list(physical_key(e['id'],p)))

    def test_historical_replay_drift_guard_rejects_unreviewed_changes(self):
        c=copy.deepcopy(self.c);pid=self.f['retained_provenance'][0]['printing_id']
        p=next(p for e in c['entries'] for p in e['printings'] if p['id']==pid)
        p['provenance']['evidence']='Unreviewed replacement'
        with self.assertRaisesRegex(ValueError,'Unreviewed historical provenance'):apply(c)

if __name__=='__main__':unittest.main()
