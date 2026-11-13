"""1.6 admission and upgrade behavior; factual checks are in the evidence audit."""
import base64,copy,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from dogdex.collector import Collection,ValidationError
from dogdex.special_import import add_printing
from catalog_history import catalog_at
def read(p):return json.loads(p.read_text(encoding='utf-8'))
class CompletionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.c=read(ROOT/'data/catalog.json');cls.old=read(ROOT/'data/research/completion_16/baseline_150.json');cls.by={e['id']:e for e in cls.c['entries']}
 def test_scope_secondary_ledgers_and_all_old_ids(self):
  self.assertEqual(self.c['roster'],self.old['roster']);self.assertEqual(len(self.c['roster']),41)
  for lang in('ja','ko'):self.assertEqual([e for e in read(ROOT/'data/research/asia_17/baseline_160.json')['entries']if e['lang']==lang],[e for e in self.old['entries']if e['lang']==lang])
  allby={e['id']:e for e in self.c['entries']+self.c['retired_entries']}
  for e in self.old['entries']+self.old['retired_entries']:
   self.assertIn(e['id'],allby);self.assertTrue({p['id']for p in e['printings']}<={p['id']for p in allby[e['id']]['printings']})
 def test_all_thirteen_native_candidates_exist_without_invented_finish(self):
  rows=read(ROOT/'data/research/reconciliation_15/german_candidate_decisions.json')['rows']
  for r in rows:
   if r['outcome']!='German_availability_unproven':continue
   es=[e for e in catalog_at('1.6')['entries']if e['lang']=='de'and e['release']==r['release']and e['number'].split('/')[0]==r['number'].split('/')[0]]
   self.assertEqual(len(es),1);self.assertEqual(es[0]['identity_status'],'provisional');self.assertFalse(es[0]['printings']);self.assertTrue(es[0]['evidence'])
 def test_unknown_rarity_does_not_block_an_explicit_printing(self):
  e=copy.deepcopy(next(e for e in self.c['entries']if e['lang']=='en'and e['release']=='base1'));e.update(id='fixture',rarity_code=None,rarity_state='unresolved',metadata_state='approved',identity_status='documented',printings=[]);review=[]
  p=add_printing(e,dict(finish='non_holo',edition='unlimited'),dict(source_url='https://example.org/exact-fixture'),review)
  self.assertTrue(p);self.assertFalse(review)
  e['identity_status']='provisional';self.assertIsNone(add_printing(e,dict(finish='holo',edition='unlimited'),{},review))
 def test_upgrade_keeps_disputed_copy_cost_wishlist_and_image(self):
  e=next(e for e in self.old['entries']if any(p.get('audit_status')=='needs_exact_native_product_proof'for p in e['printings']));pid=next(p['id']for p in e['printings']if p.get('audit_status')=='needs_exact_native_product_proof')
  with tempfile.TemporaryDirectory()as t:
   root=Path(t)/'app';(root/'data').mkdir(parents=True);catalog=root/'data/catalog.json';catalog.write_text(json.dumps(self.old),encoding='utf-8');user=Path(t)/'user';before=Collection(root,user)
   before.add_copies(dict(printing_id=pid,quantity=2,price='7.50',currency='EUR'));before.wish(dict(printing_id=pid,wanted=True));before.override(dict(entry_id=e['id'],values=dict(name='Personal name'),source_note='Collector correction preserved through upgrade'))
   before.catalog_image(dict(entry_id=e['id'],printing_id=pid,bytes=base64.b64encode(next((ROOT/'data/images').glob('*.webp')).read_bytes()).decode(),source_note='Collector picture preserved through upgrade'));saved=before.state();catalog.write_text(json.dumps(self.c),encoding='utf-8');after=Collection(root,user)
   for key in('copies','wishlist','entry_overrides','printing_image_overrides'):self.assertEqual(saved[key],after.state()[key])
   entry=after.entries()[e['id']];self.assertEqual(entry['name'],'Personal name');self.assertIn(pid,{p['id']for p in entry['printing_claims']});self.assertNotIn(pid,after.printing_map());self.assertEqual(sum(r['price_minor']for r in after.state()['copies']),1500)
   with self.assertRaises(ValidationError):after.add_copies(dict(printing_id=pid))
   held=next(p for p in entry['printing_claims']if p['id']==pid)
   with self.assertRaisesRegex(ValidationError,'already exists'):after.new_printing(dict(entry_id=e['id'],confirmed=True,finish=held['finish'],edition=held['edition'],size=held['size'],material=held['material'],layout=held['layout'],source_note='Same held physical claim must keep its original ID'))
   after.catalog_image(dict(entry_id=e['id'],printing_id=pid,bytes=base64.b64encode(next((ROOT/'data/images').glob('*.webp')).read_bytes()).decode(),source_note='Additional specimen on the same held printing ID'))
   self.assertNotIn(pid,after.printing_map())
   after.edit_copy(dict(id=saved['copies'][0]['id'],price='8.00',currency='EUR'));after.wish(dict(printing_id=pid,wanted=False));self.assertEqual(after.state()['wishlist'],[])
   # Confirming evidence promotes the same physical ID, including its picture override.
   p=next(p for p in entry['printing_claims']if p['id']==pid)
   after.save_printing(dict(entry_id=e['id'],printing_id=pid,confirmed=True,finish=p['finish'],edition=p['edition'],size=p['size'],material=p['material'],layout=p['layout'],pattern=p['pattern'],stamps=', '.join(json.loads(p['stamps_json'])),print_state=p['print_state'],source_note='Exact native product evidence supplied by collector'))
   self.assertIn(pid,after.printing_map());self.assertTrue(after.printing_map()[pid][1]['image'].startswith('/user-images/'))
   backup=after.backup();after.remove_copy(dict(id=saved['copies'][0]['id']));after.restore(backup);self.assertEqual(len(after.state()['copies']),2)
 def test_evidence_and_source_dispositions_are_separate_from_current_values(self):
  f=read(ROOT/'data/research/completion_16/field_verification_ledger.json');self.assertEqual(f['entry_count'],sum(e['lang']in('en','de')for e in catalog_at('1.6')['entries']));self.assertNotIn('accuracy_percentage',f)
  e=self.by['entry_ce03c376e52957e582345f59d7da67d2'];self.assertEqual(e['rarity_code'],'rare_holo');self.assertTrue(any(x['disposition']=='superseded'for x in e['evidence']))
  matrix=read(ROOT/'data/research/completion_16/species_language_matrix.json');self.assertEqual(len(matrix['rows']),82)
 def test_subset_numbers_cannot_match_an_unrelated_species(self):
  rows=read(ROOT/'data/research/completion_16/inventory_reconciliation.json')
  row=next(r for r in rows if r.get('source_url','').endswith('/30thcelebration/H26.shtml'))
  self.assertEqual(row['disposition'],'disputed_identifier');self.assertEqual(row['entry_id'],'entry_7505c0d299d857cca8a88eaa81a74542')
  self.assertIn(888,self.by[row['entry_id']]['subject_dex']);self.assertNotEqual(self.by[row['entry_id']]['release'],'30th')
 def test_legacy_manual_confirmation_and_unknown_fields_survive_upgrade(self):
  e=next(e for e in self.old['entries']if any(p.get('audit_status')=='needs_exact_native_product_proof'for p in e['printings']));p=next(p for p in e['printings']if p.get('audit_status')=='needs_exact_native_product_proof')
  with tempfile.TemporaryDirectory()as t:
   root=Path(t)/'app';(root/'data').mkdir(parents=True);path=root/'data/catalog.json';path.write_text(json.dumps(self.old),encoding='utf-8');user=Path(t)/'user';before=Collection(root,user)
   before.override(dict(entry_id=e['id'],values=dict(identity_verified=True),source_note='Collector supplied exact identity evidence in older editor'))
   before.save_printing(dict(entry_id=e['id'],printing_id=p['id'],confirmed=True,finish=p['finish'],edition=p['edition'],size=p['size'],material=p['material'],source_note='Collector supplied exact physical evidence in older editor'))
   # 1.5 saved these confirmations before the separate status fields existed.
   with before.connect()as db:
    for table,key,target,field in [('entry_overrides','entry_id',e['id'],'identity_status'),('printing_overrides','printing_id',p['id'],'collection_status')]:
     payload=json.loads(db.execute('SELECT payload_json FROM '+table+' WHERE '+key+'=?',(target,)).fetchone()[0]);payload.pop(field,None);db.execute('UPDATE '+table+' SET payload_json=? WHERE '+key+'=?',(json.dumps(payload),target))
   path.write_text(json.dumps(self.c),encoding='utf-8');after=Collection(root,user);self.assertIn(p['id'],after.printing_map());self.assertEqual(after.entries()[e['id']]['identity_status'],'documented')
  promo=next(e for e in self.c['entries']if e['lang']=='de'and e['release']=='smp'and e['number']=='SM54')
  self.assertIsNone(promo['release_date']);self.assertIsNone(promo['year']);self.assertEqual(promo['date_mode'],'card');self.assertTrue(promo['printings'])
if __name__=='__main__':unittest.main()
