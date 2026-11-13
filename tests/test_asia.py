"""1.7 scope/admission/migration checks, separate from factual specimen review."""
import base64,copy,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from dogdex.collector import Collection
from dogdex.scope import is_cameo
from catalog_history import catalog_at

def read(path):return json.loads(path.read_text(encoding='utf-8'))
class AsiaTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.c=read(ROOT/'data/catalog.json');cls.old=read(ROOT/'data/research/asia_17/baseline_160.json');cls.f=read(ROOT/'data/research/asia_17/reviewed_facts.json');cls.by={e['id']:e for e in cls.c['entries']}
 def test_protected_western_catalog_and_roster_are_identical(self):
  self.assertEqual(self.c['roster'],self.old['roster']);self.assertEqual(len(self.c['roster']),41)
  for key in('entries','releases'):
   current=[r for r in catalog_at('1.7')[key] if r['lang'] in ('en','de')]
   self.assertEqual([r for r in self.old[key]if r['lang']in('en','de')],current)
  for e in self.old['entries']+self.old['retired_entries']:
   after=next(x for x in self.c['entries']+self.c['retired_entries']if x['id']==e['id']);self.assertTrue({p['id']for p in e['printings']}<={p['id']for p in after['printings']})
 def test_claims_remain_visible_without_manufactured_targets(self):
  new=[self.by[e['id']]for e in self.f['entries']];research=[e for e in new if e['identity_status']=='provisional']
  self.assertEqual(len(new),107);self.assertEqual(len(research),88);self.assertTrue(all(not e['printings']and e['evidence']for e in research))
  self.assertEqual(sum(e['lang']=='ko'and e['identity_status']=='documented'for e in new),13)
  self.assertFalse(any(p.get('market_product_id')for e in new for p in e['printings']))
  for r in self.f['printings']:
   e=self.by[r['entry_id']];self.assertEqual(e['identity_status'],'documented');self.assertNotIn('normal',r['provenance']['kind'])
   if e['lang']=='ko':self.assertIn(r['provenance']['kind'],('exact_language_product_tuple','official_ko_exact_mirror'))
 def test_native_codes_do_not_override_printed_rarity_and_decorative_marks_are_kept(self):
  e=next(e for e in self.c['entries']if e['lang']=='ko'and e['release']=='S12a'and e['number']=='081');self.assertEqual(e['rarity_state'],'not_printed');self.assertIsNone(e['rarity_code'])
  changed=[r for r in self.c['asia_research']['changes']if r['kind']=='mega_mark_native_label'];self.assertEqual(len(changed),11)
  self.assertTrue(all(self.by[r['entry_id']]['name'].startswith('メガ')for r in changed))
  e=self.by['entry_f63c4b8fb0a556108e8c7564f8788ac7'];self.assertEqual(e['identity_status'],'excluded');self.assertFalse(e['printings']);self.assertEqual(e['number'],'104')
 def test_primary_hosts_are_not_duplicate_cameo_cards(self):
  es=[e for e in self.c['entries']if e['lang']=='ja'and e['release']=='M5'and e['number'].lstrip('0')in('55','98')]
  self.assertEqual(len(es),1);self.assertEqual(es[0]['subject_dex'],[942]);self.assertIn(943,es[0]['cameo_dex']);self.assertFalse(is_cameo(es[0]))
  e=next(e for e in self.c['entries']if e['lang']=='ja'and e['release']=='M-P'and e['number']=='59');self.assertEqual(e['subject_dex'],[653]);self.assertFalse(is_cameo(e))
  self.assertFalse(any(e['lang']=='ja'and any('korean_league'in p['stamps_json']for p in e['printings'])for e in self.c['entries']))
 def test_upgrade_keeps_costs_wishes_manual_source_printing_and_picture_overlays(self):
  change=next(r for r in self.c['asia_research']['changes']if r.get('printing_id')and r['kind']=='physical_detail_qualified');eid=change['entry_id'];pid=change['printing_id'];old=next(e for e in self.old['entries']if e['id']==eid);p=next(p for p in old['printings']if p['id']==pid)
  with tempfile.TemporaryDirectory()as t:
   root=Path(t)/'app';(root/'data').mkdir(parents=True);path=root/'data/catalog.json';path.write_text(json.dumps(self.old),encoding='utf-8');user=Path(t)/'user';before=Collection(root,user)
   before.add_copies(dict(printing_id=pid,quantity=2,price='6.25',currency='EUR'));before.wish(dict(printing_id=pid,wanted=True))
   before.override(dict(entry_id=eid,values=dict(name='Collector native name'),source_note='Existing manual identity correction'))
   before.save_printing(dict(entry_id=eid,printing_id=pid,finish=p['finish'],pattern=p['pattern'],edition=p['edition'],layout=p['layout'],size=p['size'],material=p['material'],confirmed=True,source_note='Collector supplied an exact regional specimen before this upgrade'))
   before.save_source(dict(source_id='release:ko:dppromo',lang='ko',name='My legacy source title',kind='promo',source_note='Existing local source correction'))
   before.catalog_image(dict(entry_id=eid,printing_id=pid,bytes=base64.b64encode(next((ROOT/'data/images').glob('*.webp')).read_bytes()).decode(),source_note='Collector printing image'))
   saved=before.state();path.write_text(json.dumps(self.c),encoding='utf-8');after=Collection(root,user)
   for key in('copies','wishlist','entry_overrides','printing_overrides','source_overrides','printing_image_overrides'):self.assertEqual(saved[key],after.state()[key])
   self.assertEqual(sum(c['price_minor']for c in after.state()['copies']),1250);self.assertEqual(after.entry(eid)['name'],'Collector native name');self.assertEqual(after.printing_map()[pid][1]['pattern'],p['pattern']);self.assertTrue(after.printing_map()[pid][1]['image'].startswith('/user-images/'));self.assertEqual(after.sources()['release:ko:dppromo']['name'],'My legacy source title')
 def test_provisional_identity_can_be_promoted_without_a_second_id(self):
  e=next(self.by[r['id']]for r in self.f['entries']if r['identity_status']=='provisional'and r['release']=='PCG1')
  with tempfile.TemporaryDirectory()as t:
   store=Collection(ROOT,t);n=len(store.entries());store.override(dict(entry_id=e['id'],values=dict(identity_verified=True),source_note='Collector supplies exact native identity evidence'))
   pid=store.new_printing(dict(entry_id=e['id'],confirmed=True,finish='non_holo',edition='unlimited',source_note='Exact historical physical edition supplied by collector'))['printing_id']
   self.assertEqual(len(store.entries()),n);self.assertEqual(store.printing_map()[pid][0]['id'],e['id'])

if __name__=='__main__':unittest.main()
