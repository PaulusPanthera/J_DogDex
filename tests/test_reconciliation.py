"""Upgrade safety and recurring import failures; separate from factual validation."""
import base64,copy,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from dogdex.collector import Collection
from dogdex.reconciliation_enrich import guard_alternate_dates

def read(p):return json.loads(p.read_text(encoding='utf-8'))
class ReconciliationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.c=read(ROOT/'data/catalog.json');cls.path=ROOT/'data/research/reconciliation_15';cls.old=read(cls.path/'baseline_140.json');cls.all={e['id']:e for e in cls.c['entries']+cls.c['retired_entries']}
 def test_all_saved_targets_survive_and_secondary_ledgers_are_identical(self):
  for e in self.old['entries']:
   self.assertIn(e['id'],self.all);self.assertTrue({p['id']for p in e['printings']}<={p['id']for p in self.all[e['id']]['printings']})
  for lang in('ja','ko'):self.assertEqual([e for e in self.old['entries']if e['lang']==lang],[e for e in read(ROOT/'data/research/asia_17/baseline_160.json')['entries']if e['lang']==lang])
  self.assertEqual(self.c['roster'],self.old['roster']);self.assertEqual(self.c['reconciliation_research']['review'],[])
 def test_alternate_product_date_does_not_inherit_expansion(self):
  e=dict(id='alternate',lang='de',number='24a',year_basis='set',release_date='2014-11-05')
  self.assertEqual(guard_alternate_dates([e]),['alternate']);self.assertIsNone(e['release_date']);self.assertEqual(e['date_state'],'unresolved_product_date')
  for basis in('card','manual','product_source_claim'):
   e=dict(id='own',lang='en',number='98a',year_basis=basis,release_date='2018-09-21');self.assertEqual(guard_alternate_dates([e]),[]);self.assertEqual(e['release_date'],'2018-09-21')
 def test_withdrawal_preserves_user_copies_costs_edits_wishlist_picture_and_backup(self):
  ids=self.c['reconciliation_research']['retired_entry_ids'];e=next(e for e in self.old['entries']if e['id']==ids[0]);pid=e['printings'][0]['id']
  with tempfile.TemporaryDirectory()as t:
   root=Path(t)/'app';(root/'data').mkdir(parents=True);target=root/'data/catalog.json';target.write_text(json.dumps(self.old),encoding='utf-8');user=Path(t)/'user';before=Collection(root,user)
   before.add_copies(dict(printing_id=pid,quantity=2,price='12.34',currency='EUR',notes='Preserve even if native identity is withdrawn'));before.wish(dict(printing_id=pid,wanted=True))
   before.override(dict(entry_id=e['id'],values=dict(name='Personal correction retained'),source_note='Existing user correction before upgrade'))
   before.catalog_image(dict(entry_id=e['id'],printing_id=pid,bytes=base64.b64encode(next((ROOT/'data/images').glob('*.webp')).read_bytes()).decode(),source_note='User-owned replacement photograph before upgrade'))
   saved=before.state();target.write_text(json.dumps(self.c),encoding='utf-8');after=Collection(root,user)
   for table in('copies','wishlist','entry_overrides','printing_image_overrides'):self.assertEqual(saved[table],after.state()[table])
   recovered=after.catalog_entries(include_removed=True,include_retired=True)[e['id']];self.assertEqual(recovered['name'],'Personal correction retained');self.assertTrue(next(p for p in recovered['printings']if p['id']==pid)['image'].startswith('/user-images/'));self.assertEqual(sum(x['price_minor']for x in after.state()['copies']),2468)
   backup=after.backup();after.remove_copy(dict(id=saved['copies'][0]['id']));after.restore(backup);self.assertEqual(saved['copies'],after.state()['copies'])
 def test_fresh_sample_and_partial_evidence_are_not_population_accuracy(self):
  sample=read(self.path/'sample_audit.json');old=read(ROOT/'data/research/systematic/sample_audit.json');self.assertEqual(len(sample['rows']),80);self.assertFalse({r['entry_id']for r in sample['rows']}&{r['entry_id']for r in old['rows']});self.assertEqual(sample['images_reviewed'],78)
  led=read(self.path/'field_verification_ledger.json');self.assertEqual(led['entry_count'],sum(e['lang']in('en','de')for e in read(ROOT/'data/research/completion_16/baseline_150.json')['entries']));self.assertNotIn('accuracy_percentage',led)
  self.assertTrue(any(x['fields']['release_date']['state']=='provider_assertion'for x in led['entries']));self.assertTrue(any(x['fields']['art_style']['state']=='missing'for x in led['entries']))
if __name__=='__main__':unittest.main()
