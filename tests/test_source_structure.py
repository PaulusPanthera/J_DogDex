"""Source-only regression checks; no new physical-printing factual audit."""
import base64,collections,copy,hashlib,json,sqlite3,tempfile,unittest,zipfile
from pathlib import Path
from dogdex.collector import Collection
from dogdex.source_structure import facts
from dogdex.printing_model import physical_key
from dogdex.source_inventory import inventory_rows,product_mapping,REQUIRED
from dogdex.special_import import add_printing

ROOT=Path(__file__).resolve().parents[1]
class SourceStructureTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory();cls.store=Collection(ROOT,cls.temp.name);cls.view=cls.store.editor_view();cls.sources={s['id']:s for s in cls.view['sources']};cls.entries=cls.view['entries'];cls.baseline=json.loads((ROOT/'data/research/sources_185/baseline_184.json').read_text(encoding='utf-8'))
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def test_original_checkpoint_and_source_layer_ids_survive_printing_delta(self):
  self.assertEqual(hashlib.sha256((ROOT/'data/catalog.sqlite3').read_bytes()).hexdigest(),self.baseline['catalog_hashes']['catalog.sqlite3'])
  ids={p['id'] for e in self.entries for p in e['printings']};old=set(self.baseline['accepted_printing_ids'])
  held={p['id'] for e in self.entries for p in e.get('printing_claims',[]) if e.get('scope_review',{}).get('decision')=='excluded_form'}
  self.assertTrue(old<=ids|held);self.assertEqual(old-ids,old&held)
  self.assertEqual(ids-old,set(self.store.catalog['printing_corrections_186']['new_printing_ids'])|set(self.store.catalog['identity_corrections_189']['added_printing_ids'])|set(self.store.catalog['catalog_corrections_1812']['added_printing_ids'])|set(self.store.catalog['new_sets_1817']['added_printing_ids'])|set(self.store.catalog['reference_review_1819']['added_printing_ids']))
  self.assertEqual(collections.Counter(e['lang'] for e in self.entries for p in e['printings']),dict(en=1757,de=1471,ja=847,ko=530))
 def test_unified_expansions_and_original_subset_numbers(self):
  for lang in ('en','de'):
   for code,child,counts in [('swsh12.5','swsh12.5gg',(16,6)),('swsh4.5','swsh4.5sv',(10,5))]:
    parent='release:'+lang+':'+code;es=[e for e in self.entries if e['expansion_source_id']==parent];self.assertEqual(sum(len(e['printings']) for e in es),sum(counts));self.assertEqual(sum(len(e['printings']) for e in es if e['subset_key']=='main'),counts[0]);self.assertEqual(self.sources['release:'+lang+':'+child]['navigation_source_id'],parent)
    for e in es:
     if e['subset_key']!='main':self.assertTrue(e['number'].startswith('GG' if code=='swsh12.5' else 'SV'))
   for code in ('swsh9','swsh10','swsh11','swsh12'):self.assertEqual(self.sources[f'release:{lang}:{code}tg']['navigation_source_id'],f'release:{lang}:{code}')
   self.assertEqual(self.sources[f'release:{lang}:sma']['navigation_source_id'],f'release:{lang}:sm115')
   self.assertEqual(self.sources[f'release:{lang}:cel25cc']['navigation_source_id'],f'release:{lang}:cel25')
 def test_regional_and_independent_series_do_not_merge(self):
  self.assertEqual(self.sources['release:ko:sma']['navigation_source_id'],'release:ko:sma')
  for lang in ('en','de'):
   for code in ('swshp','2021swsh','sv10.5b','sv10.5w'):
    sid=f'release:{lang}:{code}'
    if sid in self.sources:self.assertEqual(self.sources[sid]['navigation_source_id'],sid)
  for s in self.sources.values():
   if s['lang'] in ('ja','ko'):self.assertNotEqual(s.get('subset_key'),'galarian_gallery')
  prize=[s for s in self.sources.values() if s['source_role']=='numbered_series'];self.assertEqual(len(prize),4);self.assertEqual(len({s['navigation_source_id'] for s in prize}),4)
 def test_product_ledger_contains_all_named_contexts_without_new_collectibles(self):
  mapping=product_mapping(self.store)
  for label,needle in REQUIRED:self.assertTrue(any(needle.casefold() in r['old_source'].casefold() for r in mapping),label)
  for label,number in [('Legends of Galar Tins','SWSH018'),('Crown Zenith Elite Trainer Box','SWSH291'),('Shiny Zacian','SWSH292'),('Shiny Zamazenta','SWSH293')]:
   rows=[r for r in mapping if label.casefold() in r['old_source'].casefold()];self.assertTrue(any(r['collector_number']==number and r['canonical_set_id']=='release:en:swshp' for r in rows),label)
  for label in ('Boltund V Box','Lucario VSTAR Premium Collection','Hisuian Zoroark VSTAR Premium Collection'):
   rows=[r for r in mapping if r['active_entry'] and label.casefold() in r['old_source'].casefold()];self.assertTrue(any(r['physical_printing'].get('size')=='oversized' for r in rows),label);self.assertTrue(any(r['physical_printing'].get('size')=='standard' for r in rows),label)
  for e in self.entries:
   if e['number'] in ('SWSH076','SWSH077') and e['lang']=='en':
    ids=set(e['printings'][0]['distribution_source_ids']);self.assertIn('distribution:en:ss_upc',ids);self.assertIn('distribution:en:ss_etb_plus_'+('zacian' if e['number']=='SWSH076' else 'zamazenta'),ids);self.assertEqual(len(ids),2)
 def test_exhaustive_inventory_includes_zero_retired_and_original_sources(self):
  rows=inventory_rows(self.store);ids={r['source_id'] for r in rows};self.assertGreaterEqual(len(rows),1015);self.assertTrue({s['id'] for s in self.baseline['sources']}<=ids);self.assertTrue(any(not r['card_identities'] for r in rows));self.assertTrue(any(r['retired_card_identities'] for r in rows));self.assertTrue(any(not r['active_source'] for r in rows))
 def test_duplicate_import_adds_provenance_without_rekeying(self):
  e=copy.deepcopy(next(e for e in self.store.catalog['entries'] if e['lang']=='en' and e['release']=='swsh5' and e['number']=='96'));p=e['printings'][0];request={k:p[k] for k in ('finish','pattern','edition','layout','size','material','stamps_json','print_state')};request['product_name']='QA second distribution of same printing';before=[v['id'] for v in e['printings']];review=[]
  add_printing(e,request,dict(kind='source_only_test'),review);add_printing(e,request,dict(kind='source_only_test'),review)
  self.assertEqual(before,[v['id'] for v in e['printings']]);self.assertEqual(sum(s['name']==request['product_name'] for s in e['printings'][0].get('sources',[])),1);self.assertEqual(review,[])
 def test_manual_parent_validation_inventory_and_collection_upgrade(self):
  with tempfile.TemporaryDirectory() as temp:
   s=Collection(ROOT,temp);entry=next(e for e in self.entries if e['lang']=='en' and e['release']=='swsh12.5gg');pid=entry['printings'][0]['id'];s.add_copies(dict(printing_id=pid,quantity=2,price='12.34',currency='EUR',condition='mint',notes='keep'));s.wish(dict(printing_id=pid,wanted=True))
   manual=s.save_source(dict(lang='en',name='QA subset',kind='set',release='qa-subset',source_role='subset',parent_source_id='release:en:swsh12.5',subset_name='QA section',subset_key='qa_section',release_date='2023'))
   sid=manual['source_id'];self.assertEqual(s.sources()[sid]['navigation_source_id'],'release:en:swsh12.5')
   for parent in ('release:de:swsh12.5',sid,'distribution:en:ss_upc'):
    with self.assertRaises(ValueError):s.save_source(dict(lang='en',name='invalid',kind='set',source_role='subset',parent_source_id=parent,subset_name='invalid',subset_key='invalid'))
   with self.assertRaises(ValueError):s.save_source(dict(lang='en',name='duplicate key',kind='set',source_role='subset',parent_source_id='release:en:swsh12.5',subset_name='Duplicate GG',subset_key='galarian_gallery'))
   s.save_source(dict(source_id=sid,lang='en',name='QA independent',kind='set',release='qa-subset',source_role='numbered_set'));self.assertEqual(s.sources()[sid]['navigation_source_id'],sid)
   before=s.state(True);image_files={p.name:p.read_bytes() for p in Path(temp).rglob('*') if p.is_file() and p.suffix in ('.png','.jpg','.gif')}
   with s.connect() as db:db.execute("DELETE FROM meta WHERE key='source_structure_version'")
   reopened=Collection(ROOT,temp);after=reopened.state(True)
   for key in before:self.assertEqual(after[key],before[key],key)
   self.assertEqual(len(list((Path(temp)/'backups').glob('before-sources-1.8.5-*.zip'))),1)
   self.assertTrue(any(r['source_id']==sid and r['manual'] for r in inventory_rows(reopened)));self.assertEqual(len(after['copies']),2);self.assertEqual(after['copies'][0]['price_minor'],1234)
   again=Collection(ROOT,temp);self.assertEqual(again.state(True),after);self.assertEqual(len(list((Path(temp)/'backups').glob('before-sources-1.8.5-*.zip'))),1)

if __name__=='__main__':unittest.main()
