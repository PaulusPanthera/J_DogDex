"""Exact 1.8.5 -> 1.8.6 delta, preservation and persisted-collection checks."""
import base64, collections, copy, hashlib, json, sqlite3, tempfile, unittest
from pathlib import Path
from dogdex.collector import Collection
from dogdex.printing_corrections import apply
from dogdex.printing_model import physical_key, printing_label
from dogdex.printing_audit import recorded_claims, claim_matches
from catalog_history import catalog_at

ROOT=Path(__file__).resolve().parents[1]
def digest(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
IMAGE=b'GIF89a'+b'\0'*150
class PrintingCorrectionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.catalog=json.loads((ROOT/'data/catalog.json').read_text(encoding='utf-8'));cls.base=json.loads((ROOT/'data/research/printing_186/baseline_185.json').read_text(encoding='utf-8'));cls.facts=json.loads((ROOT/'data/research/printing_186/corrections.json').read_text(encoding='utf-8'))
  cls.temp=tempfile.TemporaryDirectory();cls.store=Collection(ROOT,cls.temp.name);cls.entries=cls.store.entries();cls.raw={(e['lang'],e['release'],e['number']):e for e in cls.catalog['entries']}
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def test_exact_delta_preserves_ids_physical_keys_references_and_asian_ledgers(self):
  c=catalog_at('1.8.9');ids={p['id'] for e in c['entries'] for p in e['printings']};added=set(c['printing_corrections_186']['new_printing_ids'])
  self.assertEqual(len(ids),4545);self.assertEqual(ids-set(self.base['raw_ids']),added|set(c['identity_corrections_189']['added_printing_ids']));self.assertEqual(len(added),26);self.assertTrue(set(self.base['raw_ids'])<=ids)
  self.assertEqual(sorted(e['id'] for e in c['entries']),self.base['entry_ids']);self.assertEqual(digest(c['roster']),self.base['roster_sha256']);self.assertEqual(len(c['roster']),41)
  self.assertEqual(digest([e for e in c['entries'] if e['lang'] in ('ja','ko')]),self.base['asian_entries_sha256'])
  for e in c['entries']:
   keys=[physical_key(e['id'],p) for p in e['printings']];self.assertEqual(len(keys),len(set(keys)),e['id'])
   for p in e['printings']:
    if p['id'] in self.base['physical_keys']:
     self.assertEqual(list(physical_key(e['id'],p)),self.base['physical_keys'][p['id']])
     self.assertEqual(digest({k:v for k,v in p.items() if 'market' in k or 'price' in k or 'image' in k}),self.base['reference_fields_sha256'][p['id']])
  # Changed existing records must be exactly the explicit correction scope.
  allowed={(r['lang'],r['release'],r['number']) for r in self.facts['printings']+self.facts['unresolved']}
  changed_pids={r['printing_id'] for r in self.facts['printing_metadata']}
  allowed.update((e['lang'],e['release'],e['number']) for e in c['entries'] if any(p['id'] in changed_pids for p in e['printings']))
  release_scope={(r['lang'],r['release']) for r in self.facts['release_metadata']}
  changed={e['id'] for e in c['entries'] if digest(e)!=self.base['entry_hashes'][e['id']]}
  expected={e['id'] for e in c['entries'] if (e['lang'],e['release'],e['number']) in allowed or (e['lang'],e['release']) in release_scope}
  identity_changed={r['entry_id'] for r in json.loads((ROOT/'data/research/identity_189/record_changes.json').read_text(encoding='utf-8'))}
  self.assertEqual(changed,expected|identity_changed);self.assertEqual(changed,set(json.loads((ROOT/'data/research/printing_186/changed_entry_ids.json').read_text(encoding='utf-8')))|identity_changed)
  self.assertEqual(hashlib.sha256((ROOT/'data/catalog.sqlite3').read_bytes()).hexdigest(),self.base['file_hashes']['data/catalog.sqlite3'])
 def test_white_flare_twenty_patterns_ordinary_reverse_and_logo(self):
  for lang,count in [('en',26),('de',25)]:
   es=[e for e in self.entries.values() if e['lang']==lang and e['release']=='sv10.5w'];self.assertEqual(len(es),10);self.assertEqual(sum(len(e['printings']) for e in es),count)
   for num in ('074','075','076','061','062'):
    e=self.raw[lang,'sv10.5w',num]
    for pattern in ('poke_ball','master_ball'):
     ps=[p for p in e['printings'] if p['pattern']==pattern];self.assertEqual(len(ps),1);p=ps[0];self.assertEqual(p['finish'],'reverse_holo');self.assertEqual(p['printed_rarity_state'],'inherit');self.assertEqual(p['stamps_json'],'[]');self.assertIn('Ball',printing_label(p))
    plain=[p for p in e['printings'] if p['finish']=='reverse_holo' and p['pattern']=='unspecified'];self.assertEqual(len(plain),1);self.assertIn(plain[0]['id'],self.base['raw_ids'])
   for num in ('154','155','156','142','143'):self.assertEqual(len(self.raw[lang,'sv10.5w',num]['printings']),1)
  logo=[p for p in self.raw['en','sv10.5w','062']['printings'] if json.loads(p['stamps_json'])==['white_flare']];self.assertEqual(len(logo),1);self.assertEqual(logo[0]['finish'],'holo');self.assertEqual(logo[0]['release_date'],'2025-11-20');self.assertIn('Costco',logo[0]['sources'][0]['name'])
 def test_specials_exact_tuple_dates_rarity_and_existing_nondoubles(self):
  for rel,num,en,de in [('swsh11','084',4,3),('sv04','136',3,2),('me02','045',4,2),('sv01','034',3,2),('sv04.5','038',3,2)]:
   self.assertEqual(len(self.raw['en',rel,num]['printings']),en);self.assertEqual(len(self.raw['de',rel,num]['printings']),de)
  pps=next(p for p in self.raw['de','swsh11','084']['printings'] if json.loads(p['stamps_json'])==['play_pokemon']);self.assertEqual(pps['finish'],'non_holo');self.assertEqual(self.raw['de','swsh11','084']['rarity_code'],'rare_holo');self.assertIn('Play! Pokémon',printing_label(pps))
  zac=self.raw['en','me02','045'];non=[p for p in zac['printings'] if p['finish']=='non_holo'];self.assertEqual(len(non),1);self.assertEqual(non[0]['id'],'variant_329df756e0de5185be7a6a5e90b28fe3');self.assertEqual(non[0]['release_date'],'2025-10-24');self.assertEqual(len(non[0]['sources']),2)
  cosmos=next(p for p in zac['printings'] if p['pattern']=='cosmos');self.assertIsNone(cosmos['release_date']);self.assertEqual(cosmos['date_state'],'unresolved_product_date')
  hound=next(p for p in self.raw['en','sv01','034']['printings'] if p['pattern']=='mirage');self.assertEqual(hound['finish'],'holo');self.assertEqual(json.loads(hound['stamps_json']),['pikachu_jack_o_lantern']);self.assertEqual(hound['release_date'],'2023-09-01')
  fid=next(p for p in self.raw['en','sv04.5','038']['printings'] if p['pattern']=='cosmos');self.assertEqual((fid['finish'],fid['release_date'],fid['date_precision']),('reverse_holo','2024-10','month'));self.assertEqual(self.raw['en','sv04.5','038']['rarity_code'],'common')
  for row in self.facts['printing_metadata']:
   p=next(p for e in self.catalog['entries'] for p in e['printings'] if p['id']==row['printing_id']);self.assertIn(p['id'],self.base['raw_ids']);self.assertEqual(p['release_date'],row['values']['release_date'])
 def test_unresolved_german_claims_are_visible_separate_from_confirmed_targets(self):
  self.assertEqual(len(self.facts['unresolved']),4)
  for row in self.facts['unresolved']:
   e=self.entries[self.raw[row['lang'],row['release'],row['number']]['id']];claims=[v for v in recorded_claims(e) if v['source_family']=='printing_corrections_186'];self.assertTrue(claims)
   for claim in claims:self.assertFalse(any(claim_matches(claim,p) for p in e['printings']),claim)
 def test_metadata_dates_aliases_idempotence_and_index_reload(self):
  sources=self.store.sources();self.assertEqual(sources['release:en:sv10.5w']['release_date'],'2025-07-18');self.assertEqual(sources['release:de:sv10.5w']['release_date'],'2025-07-18');self.assertEqual(sources['release:de:sv03']['name'],'Obsidianflammen');self.assertIn('Obsidian Flammen',sources['release:de:sv03']['aliases'])
  x=copy.deepcopy(self.catalog);result=apply(x);self.assertEqual(result['added'],[]);self.assertEqual(result['matched'],27);self.assertEqual(x,self.catalog)
  with sqlite3.connect(ROOT/'data/catalog-collector.sqlite3') as db:
   self.assertEqual(db.execute('SELECT COUNT(*) FROM printings').fetchone()[0],sum(len(e['printings']) for e in self.catalog['entries']));self.assertEqual(db.execute('PRAGMA quick_check').fetchone()[0],'ok');self.assertFalse(db.execute('PRAGMA foreign_key_check').fetchall())
  reopened=Collection(ROOT,self.temp.name);self.assertEqual(set(reopened.printing_map()),set(self.store.printing_map()));self.assertEqual(collections.Counter(e['lang'] for e in self.entries.values() for p in e['printings']),dict(en=1757,de=1471,ja=847,ko=530))
 def test_upgrade_preserves_manual_equivalents_costs_wishes_metadata_and_images(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);(root/'data').mkdir();old=copy.deepcopy(self.catalog);newids=set(old['printing_corrections_186']['new_printing_ids'])
   for e in old['entries']:e['printings']=[p for p in e['printings'] if p['id'] not in newids]
   (root/'data/catalog.json').write_text(json.dumps(old),encoding='utf-8');s=Collection(root);e=next(e for e in s.entries().values() if (e['lang'],e['release'],e['number'])==('en','sv10.5w','061'))
   pid=s.save_printing(dict(entry_id=e['id'],finish='reverse_holo',pattern='Poke Ball',confirmed=True,notes='My prior manual printing'))['printing_id']
   original=e['printings'][0]['id']
   for key in (pid,original):s.add_copies(dict(printing_id=key,quantity=2,price='7.25',currency='EUR',condition='mint',notes='Keep purchase'));s.wish(dict(printing_id=key,wanted=True))
   s.override(dict(entry_id=e['id'],values={'release_date':'2025-07','art_style':'unresolved'},source_note='My manual choice'))
   s.catalog_image(dict(entry_id=e['id'],printing_id=pid,bytes=base64.b64encode(IMAGE).decode(),source_note='My own picture'))
   s.save_source(dict(source_id='release:de:sv03',lang='de',name='My preferred Obsidian name',kind='set',release='sv03',release_date='2023-08'))
   with s.connect() as db:db.execute("DELETE FROM meta WHERE key='printing_corrections_version'")
   before=s.state(True);images={p.name:p.read_bytes() for p in (s.user_dir/'catalog_images').iterdir()}
   (root/'data/catalog.json').write_text(json.dumps(self.catalog),encoding='utf-8');up=Collection(root);self.assertEqual(up.state(True),before)
   got=up.entry(e['id']);self.assertEqual(len(got['printings']),4);self.assertEqual(sum(p['pattern']=='poke_ball' for p in got['printings']),1);self.assertIn(pid,{p['id'] for p in got['printings']});self.assertEqual(got['release_date'],'2025-07');self.assertEqual(up.sources()['release:de:sv03']['name'],'My preferred Obsidian name')
   self.assertEqual({p.name:p.read_bytes() for p in (up.user_dir/'catalog_images').iterdir()},images);self.assertEqual(len(list((up.user_dir/'backups').glob('before-printing-corrections-1.8.6-*.zip'))),1)
   alias=next(a for a,w in got['printing_aliases'].items() if w==pid);self.assertEqual(up.printing_map()[alias][1]['id'],pid);self.assertTrue(up.printing_map()[pid][1]['image'].startswith('/user-images/'))
   again=Collection(root);self.assertEqual(again.state(True),before);self.assertEqual(len(list((up.user_dir/'backups').glob('before-printing-corrections-1.8.6-*.zip'))),1)
 def test_distributed_equivalent_merges_provenance_only_without_rekeying(self):
  c=copy.deepcopy(self.catalog)
  e=next(e for e in c['entries'] if (e['lang'],e['release'],e['number'])==('en','me02','045'));p=next(p for p in e['printings'] if p['pattern']=='cosmos');newid=p['id'];p['id']='manual-existing-cosmos';p['provenance']={'kind':'collector_manual'}
  ids={p['id'] for e in c['entries'] for p in e['printings']};result=apply(c);self.assertEqual(result['added'],[]);self.assertEqual(ids,{p['id'] for e in c['entries'] for p in e['printings']});self.assertNotIn(newid,c['printing_corrections_186']['new_printing_ids']);self.assertEqual(len(p['sources']),1)

if __name__=='__main__':unittest.main()
