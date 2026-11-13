"""Keep real physical variants, regional dates and saved collection targets distinct."""
import base64,copy,hashlib,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from dogdex.collector import Collection
from dogdex.special_import import norm

class RegionalResearchTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.c=json.loads((ROOT/'data/catalog.json').read_text(encoding='utf-8'));cls.baseline=json.loads((ROOT/'data/research/regional_upgrade_baseline.json').read_text(encoding='utf-8'));cls.byid={e['id']:e for e in cls.c['entries']}
 def card(self,lang,release,number):return next(e for e in self.byid.values()if(e['lang'],e['release'],e['number'])==(lang,release,number))
 def test_upgrade_retains_every_target_and_secondary_ledgers(self):
  preserved=self.byid|{e['id']:e for e in self.c['retired_entries']}
  self.assertTrue(set(self.baseline['entries'])-set(self.byid)<=set(self.c['reconciliation_research']['retired_entry_ids']))
  for eid,pids in self.baseline['entries'].items():
   self.assertTrue(eid in preserved);self.assertTrue(set(pids)<={p['id']for p in preserved[eid]['printings']})
  for lang,expected in self.baseline['secondary_language_sha256'].items():
   actual=hashlib.sha256(json.dumps([e for e in json.loads((ROOT/'data/research/asia_17/baseline_160.json').read_text(encoding='utf-8'))['entries']if e['lang']==lang],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest();self.assertEqual(actual,expected)
  self.assertEqual(self.c['regional_research']['review'],[])
  self.assertEqual(len(self.c['regional_research']['added_printing_ids']),43)
 def test_exact_foil_promos_are_not_the_different_numbered_nonholo_deck_card(self):
  for lang in('en','de'):
   for no in('SM06','SM54','SM83','SM89','SM95','SM105','SM118','SM120','SM130'):
    e=self.card(lang,'smp',no);self.assertTrue(all(p['finish']=='holo'for p in e['printings']));self.assertEqual(e['art_style'],'standard')
    if no in('SM95','SM118','SM130'):
     self.assertTrue(all('set_logo'in json.loads(p['stamps_json'])for p in e['printings']))
     self.assertEqual(sum('staff'in json.loads(p['stamps_json'])for p in e['printings']),1 if lang=='en'else 0)
   self.assertEqual(self.card(lang,'smp','SM200')['printings'][0]['finish'],'non_holo')
   self.assertTrue(any(p['finish']=='non_holo'for p in self.card(lang,'smp','SM128')['printings']))
   self.assertEqual({p['size']for p in self.card(lang,'smp','SM230')['printings']},{'standard','oversized'})
   self.assertTrue(all(p['finish']=='holo'for p in self.card(lang,'smp','SM230')['printings']))
 def test_paper_patterns_and_stamps_do_not_leak_between_languages(self):
  for no in('011','024'):
   self.assertEqual({p['pattern']for p in self.card('en','svp',no)['printings']},{'cosmos_smooth','cosmos_pixel'})
   self.assertEqual(len(self.card('de','svp',no)['printings']),1)
  pixel=next(p for p in self.card('en','svp','024')['printings']if p['pattern']=='cosmos_pixel');self.assertEqual(pixel['date_state'],'provider_reference');self.assertIn('unresolved',pixel['date_note'])
  self.assertEqual({p['pattern']for p in self.card('en','smp','SM06')['printings']},{'cosmos','sequin'})
  seq=next(p for p in self.card('en','smp','SM06')['printings']if p['pattern']=='sequin');self.assertEqual(seq['release_date'],'2018-02')
  self.assertEqual(sum('pokemon_center'in json.loads(p['stamps_json'])for p in self.card('en','mep','010')['printings']),1)
  self.assertFalse(any('pokemon_center'in json.loads(p['stamps_json'])for p in self.card('de','mep','010')['printings']))
 def test_regional_product_dates_keep_real_precision_and_staff_exception(self):
  for lang in('en','de'):self.assertEqual(self.card(lang,'smp','SM192')['release_date'],'2019-09-06')
  for lang,date in [('en','2018-03-23'),('de','2018-03')]:self.assertEqual(self.card(lang,'smp','SM105')['release_date'],date)
  for lang,date in [('en','2025-09-26'),('de','2025-10-10')]:self.assertEqual(self.card(lang,'mep','010')['release_date'],date)
  self.assertEqual(self.card('de','svp','024')['release_date'],'2023-06')
  self.assertEqual(self.card('de','smp','SM230')['release_date'],'2019-11')
  self.assertEqual(self.card('de','swshp','SWSH186')['release_date'],'2022-02')
  luc=self.card('en','swshp','SWSH186');self.assertEqual(luc['release_date'],'2022-02-12');self.assertEqual(next(p for p in luc['printings']if'staff'in json.loads(p['stamps_json']))['release_date'],'2023')
 def test_retail_replica_targets_keep_player_year_back_and_product_date(self):
  replicas=[(e,p)for e in self.byid.values()for p in e['printings']if p.get('world_championship_year')]
  self.assertEqual(len(replicas),34);self.assertEqual({e['lang']for e,p in replicas},{'en'})
  for e,p in replicas:
   self.assertEqual((p['finish'],p['pattern'],p['size']),('non_holo','none','standard'));self.assertFalse(p['tournament_legal']);self.assertIn(p['player_signature'],p['label']);self.assertIn('different World Championships back',p['notes']);self.assertEqual(p['sources'][0]['kind'],'deck')
  n=self.card('en','xy10','105');signatures=[p['player_signature']for p in n['printings']if p.get('world_championship_year')==2016];self.assertEqual(len(set(signatures)),4)
  for e,p in replicas:
   if p['world_championship_year']==2018:self.assertEqual(p['release_date'],'2018-11-16')
   if p['world_championship_year']==2023:self.assertEqual(p['release_date'],'2024-03-01')
  undaunted=self.card('en','hgss3','8');cl=self.card('en','col1','21');self.assertEqual(len([p for p in undaunted['printings']if p.get('world_championship_year')==2012]),1);self.assertEqual(len([p for p in cl['printings']if p.get('world_championship_year')==2012]),2)
 def test_conflicting_marketplace_product_ids_do_not_relabel_a_card(self):
  holds=self.c['market_research_holds'];self.assertEqual(len(holds),41)
  for r in holds:
   e=self.byid[r['entry_id']];p=next(p for p in e['printings']if p['id']==r['printing_id']);self.assertNotIn('market_product_id',p);self.assertNotIn('market_name',p)
  for e in self.byid.values():
   if e['lang']not in('en','de'):continue
   for p in e['printings']:
    if p.get('market_name'):self.assertTrue(norm(e['english'])in norm(p['market_name'])or norm(p['market_name'])in norm(e['english']))
 def test_native_pictures_are_hash_checked_and_never_unreviewed_candidates(self):
  cache=json.loads((ROOT/'data/research/regional_image_cache.json').read_text(encoding='utf-8'));accepted=[r for r in cache.values()if r.get('filename')];self.assertEqual(len(accepted),7)
  for r in accepted:
   self.assertEqual((r['lang'],r['review_state']),('de','verified'));self.assertIn('Manually reviewed',r['identity_check']);self.assertEqual(hashlib.sha256((ROOT/'data/images'/r['filename']).read_bytes()).hexdigest()+'.webp',r['filename']);self.assertEqual(self.byid[r['entry_id']]['image'],r['filename'])
 def test_saved_ownership_stays_on_corrected_promo_and_regular_not_replica(self):
  old=copy.deepcopy(self.c);promo=copy.deepcopy(self.card('en','smp','SM95'));regular=copy.deepcopy(self.card('en','ex8','101'))
  original=set(self.baseline['entries'][promo['id']]);promo['printings']=[p for p in promo['printings']if p['id']in original];pid=promo['printings'][0]['id'];promo['printings'][0].update(finish='non_holo',pattern='none',stamps_json='[]')
  regular['printings']=[p for p in regular['printings']if not p.get('world_championship_year')];rid=regular['printings'][0]['id'];old['entries']=[promo,regular]
  with tempfile.TemporaryDirectory()as temp:
   root=Path(temp)/'app';(root/'data').mkdir(parents=True);path=root/'data/catalog.json';path.write_text(json.dumps(old),encoding='utf-8');user=Path(temp)/'my_collection';before=Collection(root,user)
   before.add_copies(dict(printing_id=pid,price='12.34',currency='EUR'));before.add_copies(dict(printing_id=rid,price='6.66',currency='EUR'));before.wish(dict(printing_id=pid,wanted=True))
   before.catalog_image(dict(entry_id=promo['id'],printing_id=pid,bytes=base64.b64encode((ROOT/'data/images'/promo['image']).read_bytes()).decode(),source_note='Exact user photo; must survive catalog correction.'))
   copies=before.state()['copies'];path.write_text(json.dumps(self.c),encoding='utf-8');after=Collection(root,user)
   self.assertEqual(after.state()['copies'],copies);self.assertEqual(sum(c['price_minor']for c in copies),1900);self.assertEqual(after.printing_map()[pid][1]['finish'],'holo');self.assertTrue(after.printing_map()[pid][1]['image'].startswith('/user-images/'))
   replica=next(p for p in self.card('en','ex8','101')['printings']if p.get('world_championship_year'));self.assertNotIn(replica['id'],{c['printing_id']for c in copies});self.assertEqual({r['printing_id']for r in after.state()['wishlist']},{pid})
   backup=after.backup();after.remove_copy(dict(id=copies[0]['id']));after.restore(backup);self.assertEqual(after.state()['copies'],copies)

if __name__=='__main__':unittest.main()
