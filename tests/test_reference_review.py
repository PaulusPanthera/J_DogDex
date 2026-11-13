"""Bounded reference delta, regional safeguards and exact product suggestions."""
import collections,copy,hashlib,json,tempfile,unittest
from pathlib import Path
from dogdex.collector import Collection
from dogdex.marketplace import provider_products,provider_variant_matches,search_products
from dogdex.printing_model import physical_key
from dogdex.reference_review import apply

ROOT=Path(__file__).resolve().parents[1]
def digest(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

class ReferenceReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=json.loads((ROOT/'data/catalog.json').read_text(encoding='utf-8'))
        cls.f=json.loads((ROOT/'data/research/reference_1819/facts.json').read_text(encoding='utf-8'))
        cls.base=json.loads((ROOT/'data/research/reference_1819/baseline_1818.json').read_text(encoding='utf-8'))

    def test_exact_delta_preserves_all_existing_ids_tuples_and_non_candidate_fields(self):
        c=self.c;ps={p['id']:(e,p) for e in c['entries'] for p in e['printings']};old=self.base['physical_keys']
        self.assertEqual(set(ps)-set(old),set(c['reference_review_1819']['added_printing_ids']))
        self.assertEqual(len(set(ps)-set(old)),21)
        self.assertEqual(collections.Counter(ps[pid][0]['lang'] for pid in set(ps)-set(old)),dict(en=13,de=8))
        for pid,key in old.items():
            e,p=ps[pid];self.assertEqual(list(physical_key(e['id'],p)),key,pid)
            self.assertEqual(digest({k:v for k,v in p.items() if k!='market_candidate'}),self.base['printing_fields_sha256'][pid],pid)
        self.assertEqual(digest(c['roster']),self.base['roster_sha256'])
        self.assertEqual(digest([e for e in c['entries'] if e['lang'] in ('ja','ko')]),self.base['asian_entries_sha256'])
        allowed={r['entry_id'] for r in self.f['printings']+self.f['candidates']}
        self.assertEqual({e['id'] for e in c['entries'] if digest(e)!=self.base['entry_hashes'][e['id']]},allowed)

    def test_replay_is_idempotent_and_special_products_are_distribution_only(self):
        c=copy.deepcopy(self.c);apply(c);self.assertEqual(c,self.c)
        with tempfile.TemporaryDirectory() as user:
            store=Collection(ROOT,user);es=store.entries();sources=store.sources()
            for r in self.f['printings']:
                e=es[r['entry_id']];p=next(p for p in e['printings'] if p['id']==r['printing_id'])
                self.assertFalse(p.get('market_confirmed'));self.assertEqual(p['market_candidate']['physical_key'],list(physical_key(e['id'],p)))
                self.assertEqual(e['primary_source_id'],'release:'+e['lang']+':'+e['release'])
                for sid in p.get('distribution_source_ids',[]):self.assertEqual(sources[sid]['source_role'],'product')
            for e in es.values():
                if e['lang']=='de' and ((e['release']=='sv04.5' and e['number'] in ('042','062')) or (e['release']=='me04' and e['number']=='013')):
                    self.assertFalse(any(p.get('provenance',{}).get('kind')=='reference_review_1819' for p in e['printings']))

    def test_ball_and_energy_products_do_not_leak_between_patterns(self):
        e=next(e for e in self.c['entries'] if e['lang']=='de' and e['release']=='sv08.5' and e['number']=='050')
        variants=[dict(type='Reverse',foil='Pokéball',thirdParty=dict(cardmarket=806478)),dict(type='Reverse',foil='Meisterball',thirdParty=dict(cardmarket=806479)),dict(type='Reverse',thirdParty=dict(cardmarket=805439))]
        e=copy.deepcopy(e);e['evidence']=[dict(value=dict(variants=variants))]
        for p in e['printings']:
            if p['finish']!='reverse_holo':continue
            expected={'poke_ball':806478,'master_ball':806479,'none':805439,'unspecified':805439}[p['pattern']]
            self.assertEqual(set(provider_products(e,p)),{expected})
        p=copy.deepcopy(next(p for p in e['printings'] if p['pattern']=='poke_ball'));p['pattern']='friend_ball'
        self.assertEqual(provider_products(e,p),{})
        v=dict(type='Reverse',foil='Energie',size='Standard')
        p['pattern']='energy';self.assertTrue(provider_variant_matches(e,p,v))
        p['pattern']='friend_ball';self.assertFalse(provider_variant_matches(e,p,v))

    def test_stamps_size_and_shadowless_are_separate_product_identities(self):
        e=dict(id='qa',lang='en',release='sv03');p=dict(finish='non_holo',pattern='none',stamps_json='["pikachu_jack_o_lantern"]')
        self.assertFalse(provider_variant_matches(e,p,dict(type='normal')))
        v=dict(type='normal',stamp=['trick-or-trade']);self.assertTrue(provider_variant_matches(e,p,v))
        self.assertFalse(provider_variant_matches(e,p,v|dict(size='jumbo')))
        base=dict(id='base',lang='en',release='base1');plain=dict(finish='non_holo',pattern='none',layout='shadowed')
        v=dict(type='normal',subtype='shadowless',stamp=['1st-edition'])
        self.assertFalse(provider_variant_matches(base,plain,v));plain['layout']='shadowless'
        self.assertTrue(provider_variant_matches(base,plain,v));self.assertFalse(provider_variant_matches(base|dict(lang='de'),plain,v))

    def test_finder_surfaces_exact_new_candidate_without_confirming_a_price(self):
        with tempfile.TemporaryDirectory() as user:
            store=Collection(ROOT,user);e=next(e for e in store.entries().values() if e['lang']=='de' and e['release']=='sv08.5' and e['number']=='050')
            p=next(p for p in e['printings'] if p['pattern']=='master_ball')
            result=search_products(store,dict(printing_id=p['id'],cache_only=True))
            self.assertEqual({r['product_id'] for r in result['products']},{806479})
            self.assertIn('Riolu-V2-xPRE050',result['products'][0]['listing_url'])
            self.assertFalse(result['current_product_id']);self.assertFalse(store.state()['printing_overrides'])

if __name__=='__main__':unittest.main()
