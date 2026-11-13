"""Bounded data-delta, physical identity, preservation and independent evidence checks."""
import base64,copy,hashlib,io,json,sqlite3,tempfile,unittest,zipfile
from pathlib import Path
from dogdex.collector import Collection
from dogdex.mobile_export import build_snapshot
from dogdex.printing_model import physical_key,normalized
from dogdex.printing_enrich import apply
from dogdex.printing_audit import audit
from catalog_history import catalog_at
ROOT=Path(__file__).resolve().parents[1]
def digest(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
IMAGE=b'GIF89a'+b'\0'*150
class PrintingSystemTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.catalog=json.loads((ROOT/'data/catalog.json').read_text(encoding='utf-8'));cls.base=json.loads((ROOT/'data/research/printing_184/baseline_183.json').read_text(encoding='utf-8'));cls.facts=json.loads((ROOT/'data/research/printing_184/approved_variants.json').read_text(encoding='utf-8'))
 def store(self,catalog=None):
  temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);root=Path(temp.name);(root/'data').mkdir();(root/'data/catalog.json').write_text(json.dumps(catalog or self.catalog),encoding='utf-8');return Collection(root)
 def entry(self,store,number='122',lang='de'):return next(e for e in store.entries().values() if e['lang']==lang and e['release']=='me02.5' and e['number']==number)
 def save(self,s,e,**data):return s.save_printing(dict(entry_id=e['id'],confirmed=True,finish='reverse_holo',pattern='energy')|data)['printing_id']
 def legacy(self):
  c=copy.deepcopy(self.catalog);added=set(c['printing_reconciliation']['added_printing_ids'])
  for e in c['entries']:
   e.pop('printing_specification',None);e['printings']=[p for p in e['printings'] if p['id'] not in added]
   if 'evidence' in e:e['evidence']=[v for v in e['evidence'] if v.get('source_family')!='printing_reconciliation_184']
  c.pop('printing_reconciliation');return c
 def test_delta_is_bounded_idempotent_and_existing_facts_preserved(self):
  c=catalog_at('1.8.4');reviewed=set(c['printing_reconciliation']['reviewed_entries']);ids={p['id'] for e in c['entries'] for p in e['printings']};self.assertEqual(len(reviewed),20);self.assertEqual(len(ids),4517);self.assertTrue(set(self.base['existing_printing_ids'])<=ids);self.assertEqual(digest(c['roster']),self.base['roster_sha256'])
  for e in c['entries']:
   prior=copy.deepcopy(e)
   if e['id'] in reviewed:
    prior.pop('printing_specification');prior['printings']=[p for p in prior['printings'] if p['id'] not in c['printing_reconciliation']['added_printing_ids']];prior['evidence']=[v for v in prior['evidence'] if v.get('source_family')!='printing_reconciliation_184']
   self.assertEqual(digest(prior),self.base['entry_hashes'][e['id']],e['id'])
  after=copy.deepcopy(c);self.assertEqual(apply(after),[]);self.assertEqual(after,c)
  for lang in ('en','de'):
   es=[e for e in c['entries'] if e['lang']==lang and e['release']=='me02.5'];self.assertEqual(sum(len(e['printings']) for e in es),22)
   self.assertTrue(all(len(e['printings'])==1 for e in es if e['number'] in ('113','137','243','286')))
   okidogi=next(e for e in es if e['number']=='122');self.assertEqual(okidogi['rarity_code'],'rare');self.assertEqual({p['finish'] for p in okidogi['printings']},{'holo','reverse_holo'})
 def test_normalized_synonyms_cannot_create_duplicate_targets(self):
  s=self.store();e=self.entry(s);p=next(p for p in e['printings'] if p['pattern']=='energy');friend=next(p for p in e['printings'] if p['pattern']=='friend_ball');self.assertNotEqual(p['id'],friend['id'])
  for pattern in ('Energy','energy-symbol-pattern','Energie'):
   with self.assertRaisesRegex(ValueError,'already exists'):self.save(s,e,pattern=pattern)
  for pattern in ('Friendball','Freundesball','Friend Ball'):
   with self.assertRaisesRegex(ValueError,'already exists'):self.save(s,e,pattern=pattern)
  self.assertEqual(physical_key(e['id'],p),physical_key(e['id'],p|dict(pattern='Energy Symbol Pattern',edition='Standard')))
  self.assertNotEqual(physical_key(e['id'],p|dict(stamps_json='["ポケモン"]')),physical_key(e['id'],p|dict(stamps_json='["포켓몬"]')))
  self.assertNotEqual(physical_key(e['id'],p|dict(stamps_json='["ガ"]')),physical_key(e['id'],p|dict(stamps_json='["カ"]')))
 def test_evidence_states_are_independent(self):
  s=self.store();e=self.entry(s);p=next(p for p in e['printings'] if p['pattern']=='energy');self.assertEqual(p['verification']['existence']['status'],'documented');self.assertEqual(p['verification']['specimen']['status'],'not_inspected');self.assertNotEqual(p['image_review']['status'],'verified');self.assertFalse(p.get('market_confirmed'))
  s.catalog_image(dict(entry_id=e['id'],printing_id=p['id'],bytes=base64.b64encode(IMAGE).decode(),source_note='Exact photo supplied in isolated test',image_kind='physical_photo',image_exact=True,image_source_urls=['https://example.com/specimen']))
  got=s.printing_map()[p['id']][1];self.assertEqual(got['image_review']['status'],'verified');self.assertEqual(got['verification'],p['verification']);self.assertFalse(got.get('market_confirmed'))
  with self.assertRaises(ValueError):s.catalog_image(dict(entry_id=e['id'],bytes=base64.b64encode(IMAGE).decode(),source_note='Shared image is not a specimen',image_kind='representative',image_exact=True))
 def test_existing_id_copies_wishes_and_picture_survive_physical_edit_and_restore(self):
  s=self.store();e=self.entry(s);pid=e['printings'][0]['id'];cid=s.add_copies(dict(printing_id=pid,quantity=2,price='7.25',currency='EUR',notes='Keep private note'))['ids'][0];s.wish(dict(printing_id=pid,wanted=True));s.catalog_image(dict(entry_id=e['id'],printing_id=pid,bytes=base64.b64encode(IMAGE).decode(),source_note='Test exact physical image',image_kind='physical_photo',image_exact=True));before=s.state()
  self.save(s,e,printing_id=pid,pattern='cosmos');got=s.printing_map()[pid][1];self.assertTrue(got['image'].startswith('/user-images/'));self.assertEqual(got['image_review']['status'],'unverified');self.assertEqual(s.state()['copies'],before['copies']);self.assertEqual(s.state()['wishlist'],before['wishlist']);self.assertEqual(s.state()['copies'][0]['id'],cid)
  raw=s.backup();other=Collection(s.root,s.root/'restored');other.restore(raw);self.assertEqual(other.state()['copies'],s.state()['copies']);self.assertEqual(other.printing_map()[pid][1]['image'],got['image'])
 def test_upgrade_coalesces_manual_equivalent_without_rekeying_and_takes_backup(self):
  s=self.store(self.legacy());e=self.entry(s);pid=self.save(s,e,pattern='Friend Ball');s.add_copies(dict(printing_id=pid,price='4',currency='EUR'));s.wish(dict(printing_id=pid,wanted=True));s.catalog_image(dict(entry_id=e['id'],printing_id=pid,bytes=base64.b64encode(IMAGE).decode(),source_note='Existing private printing picture'))
  with s.connect() as db:db.execute("DELETE FROM meta WHERE key='printing_model_version'")
  before=s.state(True);(s.root/'data/catalog.json').write_text(json.dumps(self.catalog),encoding='utf-8');up=Collection(s.root);after=up.state(True)
  for table in before:self.assertEqual(before[table],after[table],table)
  merged=self.entry(up);self.assertEqual(len(merged['printings']),3);self.assertTrue(any(p['id']==pid for p in merged['printings']));alias=next(a for a,w in merged['printing_aliases'].items() if w==pid);self.assertEqual(up.printing_map()[alias][1]['id'],pid)
  self.assertEqual(len(list((up.user_dir/'backups').glob('before-printing-1.8.4-*.zip'))),1)
  up.add_copies(dict(printing_id=alias));self.assertEqual([c['printing_id'] for c in up.state()['copies']],[pid,pid]);snap=build_snapshot(up);self.assertEqual(snap['ownership'][pid],2);self.assertEqual(snap['wishlist'],[pid])
  backups=list((up.user_dir/'backups').glob('before-printing-1.8.4-*.zip'));up.restore(backups[0].read_bytes());self.assertEqual(up.state()['copies'],before['copies'])
 def test_physical_change_invalidates_market_and_exact_photo_verification(self):
  s=self.store();e=self.entry(s);p=e['printings'][0];pid=p['id'];self.save(s,e,printing_id=pid,finish='holo',pattern='unspecified',price_product_id=870327,price_series='standard',market_confirmed=True,cardmarket_url='https://www.cardmarket.com/en/Pokemon/Products?idProduct=870327')
  self.assertTrue(s.printing_map()[pid][1]['market_confirmed']);self.save(s,e,printing_id=pid,pattern='cosmos');got=s.printing_map()[pid][1];self.assertFalse(got['market_confirmed']);self.assertIsNone(got['price_product_id']);self.assertIsNone(got['cardmarket_url'])
 def test_audit_separates_verified_missing_from_unmatched_claims_and_info(self):
  s=self.store();e=self.entry(s);pid=next(p['id'] for p in e['printings'] if p['pattern']=='energy');s.trash_item(dict(kind='printing',target_id=pid));r=audit(s);row=next(v for v in r['rows'] if v['entry_id']==e['id']);self.assertEqual(len(row['missing_verified']),1);self.assertTrue(any(i['severity']=='confirmed' and i['kind']=='missing' for i in row['issues']));self.assertFalse(any(i['kind']=='classification' for i in row['issues']));self.assertGreater(r['summary']['unresolved_source_claims'],0);self.assertEqual(r['summary']['species'],41);self.assertTrue(any(i['severity']=='information' and i['kind']=='images' for i in row['issues']))
 def test_invalid_modern_edition_layout_and_nonholo_pattern_are_rejected(self):
  s=self.store();e=self.entry(s)
  for values in (dict(edition='first_edition'),dict(edition='unlimited'),dict(layout='shadowless'),dict(finish='non_holo',pattern='cosmos'),dict(pattern='random misspelling')):
   with self.assertRaises(ValueError):self.save(s,e,**values)
  base=next(e for e in s.entries().values() if e['lang']=='en' and e['release']=='base1' and e['number']=='68');p=base['printings'][0]
  with self.assertRaisesRegex(ValueError,'already exists'):s.save_printing(dict(entry_id=base['id'],confirmed=True,**{k:v for k,v in p.items() if k in ('finish','pattern','edition','layout','size','material','stamps_json','print_state')}))
 def test_canonical_groups_link_western_sources_but_keep_ids_and_asian_regions_separate(self):
  s=self.store();sources=s.sources();a=sources['release:en:me02.5'];b=sources['release:de:me02.5'];self.assertNotEqual(a['id'],b['id']);self.assertEqual(a['canonical_set_id'],b['canonical_set_id']);self.assertEqual(a['canonical_set_id'],'western:me02.5');self.assertTrue(all(v['canonical_set_id'].startswith('regional:'+v['lang']+':') or v['canonical_set_id'].startswith('source:') for v in sources.values() if v['lang'] in ('ja','ko')))
if __name__=='__main__':unittest.main(verbosity=2)
