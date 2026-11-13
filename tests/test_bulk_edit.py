"""Bulk classifications: exact selection, stale review protection, Undo and backup."""
import copy,io,json,sys,tempfile,unittest,zipfile
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from dogdex.collector import Collection
ROOT=Path(__file__).resolve().parents[1]

class BulkEditTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.store=Collection(ROOT,self.temp.name)
        self.entries=self.store.entries()
        self.cards=[e for e in self.entries.values() if e['lang']=='de' and not e.get('art_style') and e['printings']][:3]
        self.assertEqual(len(self.cards),3)
    def tearDown(self):self.temp.cleanup()
    def request(self,cards=None,**extra):return dict(entry_ids=[e['id'] for e in (cards or self.cards[:2])],lang='de',field='artwork',value='standard',only_unclassified=True)|extra
    def preview(self,request):return self.store.mutate('catalog/bulk/preview',request)
    def apply(self,request):
        reviewed=self.preview(request)
        return self.store.mutate('catalog/bulk/apply',request|dict(preview_key=reviewed['preview_key']))

    def test_exact_selected_cards_only_and_all_personal_data_survive_backup_and_undo(self):
        first=self.cards[0];pid=first['printings'][0]['id']
        self.store.add_copies(dict(printing_id=pid,quantity=2,condition='excellent',price='4.25',currency='EUR',notes='Original shop',misprint_notes='One misprint',purchased_on='2026-10-31'))
        self.store.wish(dict(printing_id=pid,wanted=True))
        before=self.store.state(True);raw_catalog=copy.deepcopy(self.store.catalog)
        originals={e['id']:copy.deepcopy(self.store.entry(e['id'])) for e in self.cards}
        request=self.request();reviewed=self.preview(request)
        self.assertEqual(self.store.state(True),before,'Review must not write any record')
        self.assertEqual(len(reviewed['changes']),2)
        result=self.store.mutate('catalog/bulk/apply',request|dict(preview_key=reviewed['preview_key']))
        for e in self.cards[:2]:
            updated=self.store.entry(e['id']);self.assertEqual(updated['art_style'],'standard')
            self.assertEqual(updated['printings'],originals[e['id']]['printings'])
            for key in ('identity_status','metadata_state','release_date','rarity_code','image','links','notes'):
                self.assertEqual(updated.get(key),originals[e['id']].get(key),key)
        self.assertEqual(self.store.entry(self.cards[2]['id']),originals[self.cards[2]['id']])
        for table in before:
            if table not in ('audit_log','entry_overrides'):self.assertEqual(self.store.state(True)[table],before[table],table)
        self.assertEqual(self.store.catalog,raw_catalog)
        backup=self.store.backup();restored=Collection(ROOT,Path(self.temp.name)/'restored');restored.restore(backup)
        self.assertEqual(restored.entry(first['id'])['art_style'],'standard')
        self.assertEqual(restored.state()['copies'],before['copies'])
        restored.mutate('catalog/bulk/undo',dict(batch_id=result['batch_id']))
        for e in self.cards:self.assertEqual(restored.entry(e['id']),originals[e['id']])
        self.assertEqual(restored.state()['copies'],before['copies'])
        with self.assertRaisesRegex(ValueError,'already been undone'):restored.mutate('catalog/bulk/undo',dict(batch_id=result['batch_id']))

    def test_existing_classifications_are_skipped_unless_explicitly_included(self):
        self.apply(self.request(self.cards[:1],value='full_art'))
        request=self.request();reviewed=self.preview(request)
        self.assertEqual(len(reviewed['changes']),1);self.assertEqual(len(reviewed['skipped']),1)
        self.apply(request);self.assertEqual(self.store.entry(self.cards[0]['id'])['art_style'],'full_art')
        reviewed=self.preview(self.request(only_unclassified=False));self.assertEqual(len(reviewed['changes']),1)

    def test_bad_or_cross_language_selection_and_hidden_targets_do_not_partially_write(self):
        en=next(e for e in self.entries.values() if e['lang']=='en')
        before=self.store.state(True)
        for request in [self.request(entry_ids=[self.cards[0]['id'],'unknown-card']),self.request(entry_ids=[self.cards[0]['id'],en['id']]),self.request(entry_ids=[self.cards[0]['id']]*2),self.request(value='non_holo'),self.request(field='identity_status',value='documented')]:
            with self.assertRaises(ValueError):self.preview(request)
            self.assertEqual(self.store.state(True),before)
        self.store.trash_item(dict(kind='entry',target_id=self.cards[1]['id']))
        with self.assertRaisesRegex(ValueError,'unavailable'):self.preview(self.request())

    def test_entire_batch_rejects_stale_review_and_database_failure_rolls_back(self):
        request=self.request();reviewed=self.preview(request)
        self.apply(self.request(self.cards[1:2],value='full_art'))
        before=self.store.state(True)
        with self.assertRaisesRegex(ValueError,'changed after review'):
            self.store.mutate('catalog/bulk/apply',request|dict(preview_key=reviewed['preview_key']))
        self.assertEqual(self.store.state(True),before)
        request=self.request(only_unclassified=False);reviewed=self.preview(request)
        with patch.object(self.store,'audit',side_effect=RuntimeError('Simulated failure')):
            with self.assertRaises(RuntimeError):self.store.mutate('catalog/bulk/apply',request|dict(preview_key=reviewed['preview_key']))
        self.assertEqual(self.store.state(True),before)

    def test_undo_restores_only_edited_fields_and_refuses_newer_classification(self):
        result=self.apply(self.request())
        eid=self.cards[0]['id']
        with self.store.connect() as db:
            row=db.execute('SELECT payload_json FROM entry_overrides WHERE entry_id=?',(eid,)).fetchone();values=json.loads(row[0]);values['notes']='New unrelated note'
            db.execute('UPDATE entry_overrides SET payload_json=? WHERE entry_id=?',(json.dumps(values),eid))
        self.store.mutate('catalog/bulk/undo',dict(batch_id=result['batch_id']))
        self.assertEqual(self.store.entry(eid)['notes'],'New unrelated note');self.assertIsNone(self.store.entry(eid).get('art_style'))
        original=self.apply(self.request());self.apply(self.request(self.cards[:1],value='full_art',only_unclassified=False))
        before=self.store.state(True)
        with self.assertRaisesRegex(ValueError,'newer change'):self.store.mutate('catalog/bulk/undo',dict(batch_id=original['batch_id']))
        self.assertEqual(self.store.state(True),before)

    def test_rarity_uses_separate_regional_codes_and_legacy_s_namespace(self):
        for lang in ('ja','ko'):
            e=next(e for e in self.entries.values() if e['lang']==lang)
            request=self.request([e],lang=lang,field='rarity',value='common',only_unclassified=False)
            with self.assertRaisesRegex(ValueError,'ledger'):self.preview(request)
            self.apply(request|dict(value='S_legacy_lvx'))
            old=self.store.entry(e['id']);self.assertEqual(old['rarity_key'],'S_legacy_lvx')
            self.apply(request|dict(value='S'))
            updated=self.store.entry(e['id']);self.assertEqual(updated['rarity_key'],'S');self.assertNotIn('legacy',updated['rarity_namespace'])
            for key in ('identity_status','metadata_state','art_style'):self.assertEqual(updated.get(key),e.get(key))

    def test_card_rarity_preserves_explicit_printing_rarity_and_unverified_identity(self):
        e=self.cards[0];p=e['printings'][0]
        self.store.save_printing(dict(entry_id=e['id'],printing_id=p['id'],printed_rarity_state='known',printed_rarity_code='uncommon',confirmed=True))
        before=self.store.entry(e['id']);self.apply(self.request([e],field='rarity',value='double_rare',only_unclassified=False))
        after=self.store.entry(e['id']);self.assertEqual(after['rarity_key'],'double_rare');self.assertEqual(after['printings'][0]['rarity_key'],'uncommon')
        for key in ('identity_status','metadata_state','art_style'):self.assertEqual(after.get(key),before.get(key))
        uncertain=next(e for e in self.entries.values() if e['lang']=='de' and e.get('identity_status')=='provisional')
        self.apply(self.request([uncertain],only_unclassified=False))
        updated=self.store.entry(uncertain['id']);self.assertEqual(updated['identity_status'],'provisional');self.assertEqual(updated['metadata_state'],uncertain['metadata_state']);self.assertFalse(updated['printings'])

if __name__=='__main__':unittest.main(verbosity=2)
