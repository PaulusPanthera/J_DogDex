"""Mechanical evidence gates and collection migration, separate from factual sample review."""
import base64,copy,hashlib,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from dogdex.collector import Collection
from tools.audit_catalog import digest,number
from catalog_history import catalog_at
def read(path):return json.loads(path.read_text(encoding="utf-8"))
class SystematicTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.c=read(ROOT/'data/catalog.json');cls.by={e['id']:e for e in cls.c['entries']};cls.path=ROOT/'data/research/systematic';cls.f=read(cls.path/'reviewed_facts.json');cls.p=read(cls.path/'publisher_evidence.json')
 def test_all_original_targets_and_secondary_language_records_survive(self):
  b=read(self.path/'upgrade_baseline.json');self.assertEqual(len(self.c['roster']),41)
  preserved=self.by|{e['id']:e for e in self.c.get('retired_entries',[])}
  for eid,pids in b['entries'].items():self.assertIn(eid,preserved);self.assertTrue(set(pids)<={p['id']for p in preserved[eid]['printings']})
  for lang,expected in b['secondary_language_sha256'].items():self.assertEqual(digest([e for e in read(ROOT/'data/research/asia_17/baseline_160.json')['entries']if e['lang']==lang]),expected)
  self.assertEqual(self.c['systematic_research']['review'],[])
 def test_new_existing_card_pack_finishes_have_native_checkbox_proof(self):
  assertions={r['entry_id']:r for r in self.p['assertions']}
  for r in self.f['printings']:
   a=assertions[r['entry_id']];self.assertIn(r['printing']['finish'],a['pack_finishes']);self.assertEqual(r['source_sha256'],a['source_sha256']);self.assertTrue(r['checkbox_evidence']);self.assertEqual(r['lang'],a['lang'])
  docs={(d['lang'],d['release']):d for d in self.p['documents']}
  for r in self.f['entries']:
   if r['release']=='tk-dp-l':continue
   doc=docs[r['lang'],r['release']];row=next(x for x in doc['rows']if number(x['number'])==number(r['number']));self.assertEqual(row['name'],r['name']);self.assertTrue(set(p['finish']for p in r['printings'])<=set(row['pack_finishes']));self.assertEqual(hashlib.sha256((ROOT/'data/images'/r['image']).read_bytes()).hexdigest()+'.webp',r['image'])
 def test_rarity_artwork_and_marketplace_status_are_distinct(self):
  def card(l,r,n):return next(e for e in self.by.values()if(e['lang'],e['release'],e['number'])==(l,r,n))
  self.assertEqual(card('de','xy8','92')['rarity_code'],'rare_break');self.assertEqual(card('de','ex12','83')['rarity_code'],'rare_holo_ex_lowercase')
  for lang in('en','de'):
   e=card(lang,'sma','SV64');self.assertEqual((e['rarity_code'],e['art_style']),('shiny_rare_gx','full_art'));self.assertEqual(card(lang,'dpp','DP12')['name'],'Lucario LV.X');self.assertEqual(card(lang,'dpp','DP12')['rarity_code'],'promo')
  # These inference dispositions describe the frozen 1.4 audit boundary.
  # Later evidence may supersede them; do not retroactively rewrite the audit.
  for e in catalog_at('1.4')['entries']:
   if e['lang']not in('en','de'):continue
   source=e.get('art_style_source')or{}
   if isinstance(source,dict)and source.get('inference'):self.assertNotEqual(e['art_style_state'],'verified')
   for p in e['printings']:
    if p.get('market_candidate'):self.assertNotIn('market_product_id',p);self.assertEqual(p['market_candidate']['state'],'unverified_provider_candidate')
 def test_update_preserves_copies_prices_wishlist_manual_fields_and_picture(self):
  old=read(self.path/'upgrade_test_fixture.json');v=next(e for e in old['entries']if e['lang']=='en'and e['release']=='base1');d=next(e for e in old['entries']if e['lang']=='de');pid=v['printings'][0]['id'];dpid=d['printings'][0]['id']
  with tempfile.TemporaryDirectory()as temp:
   root=Path(temp)/'new app';(root/'data').mkdir(parents=True);target=root/'data/catalog.json';target.write_text(json.dumps(old),encoding='utf-8');user=Path(temp)/'existing collection';before=Collection(root,user)
   before.add_copies(dict(printing_id=pid,quantity=2,price='12.34',currency='EUR',condition='near_mint',notes='User copy notes'));before.add_copies(dict(printing_id=dpid,price='7.89',currency='EUR'));before.wish(dict(printing_id=dpid,wanted=True))
   before.override(dict(entry_id=d['id'],values=dict(name='My manually corrected title'),source_note='Existing deliberate manual catalog correction'))
   before.catalog_image(dict(entry_id=v['id'],printing_id=pid,bytes=base64.b64encode((ROOT/'data/images'/v['image']).read_bytes()).decode(),source_note='User replacement photograph before upgrade'))
   copies=before.state()['copies'];target.write_text(json.dumps(self.c),encoding='utf-8');after=Collection(root,user)
   self.assertEqual(after.state()['copies'],copies);self.assertEqual(sum(x['price_minor']for x in copies),3257);self.assertEqual({x['printing_id']for x in after.state()['wishlist']},{dpid});self.assertEqual(after.entry(d['id'])['name'],'My manually corrected title');self.assertTrue(after.printing_map()[pid][1]['image'].startswith('/user-images/'))
   backup=after.backup();after.remove_copy(dict(id=copies[0]['id']));after.restore(backup);self.assertEqual(after.state()['copies'],copies)
 def test_sample_is_frozen_and_not_reported_as_population_accuracy(self):
  s=read(self.path/'sample_audit.json');self.assertEqual(s['sample_size'],80);self.assertEqual(len({r['entry_id']for r in s['rows']}),80);self.assertEqual(s['visual_records_assessed'],76);self.assertEqual(s['records_with_observed_errors'],16)
  r=read(self.path/'inventory_reconciliation.json');self.assertEqual((r['species_compared'],r['reference_rows']),(41,957));self.assertFalse(any(x['status']=='missing_candidate'for x in r['rows']if x['lang']=='en'))
if __name__=='__main__':unittest.main()
