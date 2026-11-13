"""Form-specific scope, native identity restoration and collection preservation."""
import base64, copy, json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from dogdex.collector import Collection, ValidationError
from dogdex.identity_corrections import apply, apply_form_review
from dogdex.mobile_export import build_snapshot

ROOT=Path(__file__).resolve().parents[1]
IMAGE=b'GIF89a'+b'\0'*150

class IdentityCorrectionsTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.catalog=json.loads((ROOT/'data/catalog.json').read_text(encoding='utf-8'))
  cls.changes=json.loads((ROOT/'data/research/identity_189/record_changes.json').read_text(encoding='utf-8'))
  cls.by={(e['lang'],e['release'],e['number']):e for e in cls.catalog['entries']}

 def test_native_restoration_and_form_review_are_idempotent(self):
  c=copy.deepcopy(self.catalog);apply(c);self.assertEqual(c,self.catalog);apply(c);self.assertEqual(c,self.catalog)
  e=self.by['de','me03','077'];self.assertEqual(e['id'],'research_entry_453f9e8eeb2552cab2739fb7116b1cce')
  self.assertEqual(e['cameo_dex'],[828]);self.assertEqual(e['subject_dex'],[]);self.assertEqual(e['art_style'],'standard')
  self.assertEqual({p['finish'] for p in e['printings']},{'non_holo','reverse_holo'});self.assertEqual(len(e['printings']),2)
  for lang in ('en','de'):
   a=self.by[lang,'me03','104'];b=self.by[lang,'me03','120']
   self.assertEqual(a['identity_status'],'excluded');self.assertEqual(a['scope_review']['cameo_forms'],['complete'])
   self.assertEqual(b['category'],'cameo');self.assertEqual(b['subject_dex'],[]);self.assertEqual(b['cameo_dex'],[718])
   self.assertEqual(b['scope_review']['included_cameo_forms'],['10_percent'])
   self.assertEqual(a['release_date'],'2026-03-27');self.assertEqual(b['release_date'],'2026-03-27')
  for lang in ('ja','ko'):
   x=next(e for e in c['entries'] if e['lang']==lang);old=copy.deepcopy(x);apply_form_review(x);self.assertEqual(x,old)

 def test_runtime_exact_match_does_not_infer_other_cards_or_languages(self):
  x={'lang':'de','release':'custom','canonical_set_id':'western:me03','number':'0104','dex':718,'subject_dex':[718],'printings':[{'id':'kept'}]}
  apply_form_review(x);self.assertEqual(x['identity_status'],'excluded');self.assertEqual(x['printings'][0]['id'],'kept')
  for lang,release,number in [('ja','me03','104'),('de','other','104'),('en','me03','047')]:
   x={'lang':lang,'release':release,'number':number,'dex':718,'subject_dex':[718],'printings':[]};old=copy.deepcopy(x);apply_form_review(x);self.assertEqual(x,old)

 def test_update_preserves_owned_excluded_copies_manual_printings_images_and_wishes(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);(root/'data').mkdir();old=copy.deepcopy(self.catalog)
   before_by={r['entry_id']:r['before'] for r in self.changes}
   old['entries']=[copy.deepcopy(before_by.get(e['id'],e)) for e in old['entries']];old.pop('identity_corrections_189',None)
   (root/'data/catalog.json').write_text(json.dumps(old),encoding='utf-8')
   with patch('dogdex.editor.apply_form_review',lambda e:e):
    s=Collection(root);e=self.by['de','me03','077'];e104=self.by['de','me03','104'];e120=self.by['de','me03','120']
    pid104=e104['printings'][0]['id'];pid120=e120['printings'][0]['id']
    pid=s.save_printing(dict(entry_id=e['id'],finish='non_holo',pattern='none',confirmed=True,notes='Existing manual normal'))['printing_id']
    for printing_id in (pid104,pid120,pid):
     s.add_copies(dict(printing_id=printing_id,quantity=2,price='12.34',currency='EUR',condition='excellent',notes='Keep this purchase',misprint_notes='One collected misprint',purchased_on='2026-10-30'))
     s.wish(dict(printing_id=printing_id,wanted=True))
    s.override(dict(entry_id=e104['id'],values={'english':'My manual display label'},source_note='Preserve my correction'))
    s.catalog_image(dict(entry_id=e['id'],printing_id=pid,bytes=base64.b64encode(IMAGE).decode(),source_note='My actual card'))
    s.catalog_image(dict(entry_id=e104['id'],printing_id=pid104,bytes=base64.b64encode(IMAGE).decode(),source_note='Keep excluded card photo'))
    before=s.state(True);images={p.name:p.read_bytes() for p in (s.user_dir/'catalog_images').iterdir()}
   (root/'data/catalog.json').write_text(json.dumps(self.catalog),encoding='utf-8');up=Collection(root)
   self.assertEqual(up.state(True),before)
   self.assertEqual({p.name:p.read_bytes() for p in (up.user_dir/'catalog_images').iterdir()},images)
   got=up.entry(e['id']);self.assertEqual(len(got['printings']),2);self.assertIn(pid,{p['id'] for p in got['printings']})
   self.assertEqual(sum(p['finish']=='non_holo' for p in got['printings']),1)
   alias=next(a for a,w in got['printing_aliases'].items() if w==pid);self.assertEqual(up.printing_map()[alias][1]['id'],pid)
   excluded=up.entry(e104['id']);self.assertEqual(excluded['identity_status'],'excluded');self.assertEqual(excluded['english'],'My manual display label')
   self.assertEqual(len(excluded['printings']),0);self.assertEqual(excluded['printing_claims'][0]['id'],pid104)
   self.assertTrue(excluded['printing_claims'][0]['image'].startswith('/user-images/'))
   self.assertNotIn(pid104,up.printing_map());self.assertIn(pid104,up.printing_map(include_removed=True))
   with self.assertRaises(ValidationError):up.add_copies(dict(printing_id=pid104,quantity=1,price='',currency='EUR',condition='unassessed'))
   snapshot=build_snapshot(up);self.assertEqual(snapshot['ownership'][pid104],2);self.assertIn(pid104,snapshot['wishlist'])
   public=next(e for e in snapshot['entries'] if e['id']==e104['id']);self.assertEqual(public['scope_review']['decision'],'excluded_form');self.assertEqual(public['printing_claims'][0]['id'],pid104)
   other=root/'restored';(other/'data').mkdir(parents=True);(other/'data/catalog.json').write_text(json.dumps(self.catalog),encoding='utf-8')
   restored=Collection(other);restored.restore(up.backup())
   after=restored.state(True)
   for table in before:
    if table!='audit_log':self.assertEqual(before[table],after[table],table)

if __name__=='__main__':unittest.main()
