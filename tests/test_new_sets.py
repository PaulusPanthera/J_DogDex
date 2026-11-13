"""Bounded new-set identities/finishes, stable IDs and deterministic repeat checks."""
import copy,hashlib,json,unittest
from pathlib import Path
from dogdex.new_sets import apply,FACTS
from dogdex.printing_model import physical_key
ROOT=Path(__file__).resolve().parents[1]
class NewSetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=json.loads((ROOT/'data/catalog.json').read_text(encoding='utf-8'));cls.f=json.loads(FACTS.read_text(encoding='utf-8'));cls.by={e['id']:e for e in cls.c['entries']}
    def test_explicit_delta_inventory_and_price_holds(self):
        expected={'018':{'non_holo','reverse_holo'},'019':{'holo','reverse_holo'},'066':{'non_holo','reverse_holo'},'067':{'holo'},'106':{'holo'},'112':{'holo'}}
        for lang in ('en','de'):
            es=[e for e in self.c['entries'] if e['lang']==lang and e['release']=='me06'];self.assertEqual(len(es),6);self.assertEqual(sum(len(e['printings']) for e in es),9);self.assertEqual({e['number'] for e in es},set(expected))
            for e in es:
                self.assertEqual(e['release_date'],'2026-11-06');self.assertEqual({p['finish'] for p in e['printings']},expected[e['number']]);self.assertEqual(e['art_style'],'full_art' if e['number'] in ('106','112') else 'standard');self.assertTrue(all(not p.get('market_confirmed') and not p.get('price_product_id') for p in e['printings']))
    def test_classic_original_number_is_not_main_set_number(self):
        for r in self.f['entries']:
            if r['release']!='30th-c':continue
            e=self.by[r['entry_id']];self.assertEqual(e['number'],'138');self.assertEqual(e['printed_identifier'],'138/202');self.assertEqual(e['provider_identifiers']['tcgdex'],'30th-c-028');self.assertEqual(e['release_date'],'2026-09-16');self.assertEqual(len(e['printings']),1);self.assertNotIn('status_reason',e);self.assertNotIn('date_note',e)
            source=self.c['source_metadata']['release:'+e['lang']+':30th-c'];self.assertEqual(source['parent_source_id'],'release:'+e['lang']+':30th');self.assertEqual(source['subset_key'],'classic_collection');self.assertTrue(any(x['lang']==e['lang'] and x['release']=='30th' and x['number']=='138' and x['id']!=e['id'] for x in self.c['entries']))
    def test_stable_ids_unique_physical_tuples_and_checkpoint(self):
        self.assertEqual(len(self.c['roster']),41)
        self.assertTrue(set(self.f['baseline_entry_ids'])<=self.by.keys());self.assertTrue(set(self.f['baseline_printing_ids'])<={p['id'] for e in self.c['entries'] for p in e['printings']})
        for e in self.c['entries']:
            keys=[physical_key(e['id'],p) for p in e['printings']];self.assertEqual(len(keys),len(set(keys)))
        self.assertEqual(hashlib.sha256((ROOT/'data/catalog.sqlite3').read_bytes()).hexdigest(),'e79d48ff8d056d88fa0d6b1f0771f220d79f62d82797c886183e20ada9c22da0')
    def test_idempotence_and_image_receipts(self):
        c=copy.deepcopy(self.c);apply(c);self.assertTrue(c==self.c)
        for r in self.f['entries']:
            if r.get('image'):self.assertEqual(hashlib.sha256((ROOT/'data/images'/r['image']['filename']).read_bytes()).hexdigest()+'.webp',r['image']['filename'])
        for lang in ('en','de'):
            es=[e for e in c['entries'] if e['lang']==lang and e['release']=='30th'];self.assertEqual(len(es),14);self.assertTrue(all(len(e['printings'])==1 and e['printings'][0]['stamps_json']=='["30th_anniversary"]' for e in es))
if __name__=='__main__':unittest.main()
