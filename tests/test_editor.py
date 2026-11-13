"""Catalog CRUD, scope changes and backward-compatible personal records."""
import copy,io,json,sqlite3,sys,tempfile,unittest,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from dogdex.collector import Collection,ValidationError,V2_TABLES
from dogdex.scope import EXCLUDED_DEX,in_scope,species
from dogdex.rarities import label,key
ROOT=Path(__file__).resolve().parents[1]

class EditorTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.store=Collection(ROOT,self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def source(self,**values):return self.store.save_source(dict(lang='en',name='Test collector source',kind='deck',release='QA-12',release_date='2020-05')|values)['source_id']
    def card(self,sid,**values):return self.store.save_card(dict(lang='en',source_id=sid,name='Test Vulpix',english='Test Vulpix',subject_dex=[37],cameo_dex=[],number='1',rarity_code='double_rare',identity_verified=True,art_style='standard',initial_printing=dict(finish='holo',confirmed=True))|values)['entry_id']
    def payload(self,raw):
        with zipfile.ZipFile(io.BytesIO(raw)) as z:return json.loads(z.read('collection.json'))
    def zipped(self,payload):
        out=io.BytesIO()
        with zipfile.ZipFile(out,'w') as z:z.writestr('collection.json',json.dumps(payload))
        return out.getvalue()
    def test_scope_removes_both_complete_families_without_removing_other_subjects(self):
        catalog=self.store.catalog;entries=list(self.store.entries().values())
        self.assertEqual({e['id'] for e in entries},{e['id'] for e in catalog['entries']})
        self.assertFalse(EXCLUDED_DEX & {r['dex'] for r in catalog['roster']})
        self.assertTrue(all(not (species(e)&EXCLUDED_DEX) for e in entries))
        self.assertEqual(len(catalog['retired_entries']),1839)
        self.assertEqual(sum(len(e['printings']) for e in catalog['retired_entries']),1881)
        self.assertFalse(in_scope(dict(subject_dex=[133],cameo_dex=[403])))
        self.assertTrue(in_scope(dict(subject_dex=[37],cameo_dex=[133])))
        self.assertEqual(catalog['scope']['research_priority'],['de','en'])
    def test_add_edit_card_and_source_with_complete_fields_and_initial_printing(self):
        sid=self.source(series='QA era',card_total=60,links=['https://example.com/source'],notes='Known source notes')
        eid=self.card(sid,cameo_dex=[58],notes='Known card notes',identifier_namespace='collector',number_key='001',links=['https://example.com/card'])
        entry=self.store.entry(eid);self.assertEqual(entry['release_date'],'2020-05');self.assertEqual(entry['rarity_key'],'double_rare');self.assertEqual(entry['cameo_dex'],[58]);self.assertEqual(len(entry['printings']),1)
        self.store.save_card(dict(entry_id=eid,lang='en',source_id=sid,name='Corrected name',english='Corrected name',subject_dex=[37],cameo_dex=[58],number='001',number_key='001',rarity_code='ultra_rare',identity_verified=True,art_style='full_art',date_mode='card',release_date='2020-05-22',cardmarket_search='Exact collector query',notes='Changed note',links=['https://example.com/corrected']))
        fixed=self.store.entry(eid);self.assertEqual((fixed['id'],fixed['rarity_key'],fixed['art_style']),(eid,'ultra_rare','full_art'));self.assertEqual(fixed['release_date'],'2020-05-22')
        self.assertEqual(self.store.sources()[sid]['card_total'],60)
        with self.assertRaises(ValueError):self.card(sid,number='001',number_key='001')
        with self.assertRaises(ValueError):self.store.save_source(dict(source_id=sid,lang='de',name='Wrong language',kind='deck'))
    def test_printing_edit_remove_restore_preserves_copy_wishlist_price_and_identity(self):
        sid=self.source();eid=self.card(sid);pid=self.store.entry(eid)['printings'][0]['id']
        cid=self.store.add_copies(dict(printing_id=pid,quantity=2,condition='near_mint',price='12.34',currency='EUR'))['ids'][0];self.store.wish(dict(printing_id=pid,wanted=True))
        self.store.save_printing(dict(entry_id=eid,printing_id=pid,finish='reverse_holo',edition='not_applicable',pattern='cosmos',layout='standard',size='oversized',material='paper',stamps='Collector stamp',print_state='documented_reissue',printed_rarity_state='known',printed_rarity_code='ultra_rare',release_date='2021-01',source_ids=[sid],confirmed=True))
        p=self.store.entry(eid)['printings'][0];self.assertEqual(p['id'],pid);self.assertEqual(p['rarity_key'],'ultra_rare');self.assertEqual(p['category'],'jumbo');self.assertIn('Collector stamp',p['label'])
        self.store.trash_item(dict(kind='printing',target_id=pid));self.assertNotIn(pid,self.store.printing_map());self.assertEqual(len(self.store.state()['copies']),2);self.assertEqual(len(self.store.state()['wishlist']),1)
        self.store.trash_item(dict(kind='printing',target_id=pid),True);self.assertIn(pid,self.store.printing_map())
        row=next(r for r in self.store.state()['copies'] if r['id']==cid);self.assertEqual((row['printing_id'],row['price_minor'],row['condition']),(pid,1234,'near_mint'))
        with self.assertRaises(ValueError):self.store.save_printing(dict(entry_id=eid,finish='reverse_holo',pattern='cosmos',edition='not_applicable',size='oversized',material='paper',stamps='Collector stamp',print_state='documented_reissue',confirmed=True))
    def test_source_removal_cascades_and_restore_keeps_individual_dates(self):
        sid=self.source();first=self.card(sid);second=self.card(sid,number='2',date_mode='card',release_date='2020-06-15')
        pid=self.store.entry(first)['printings'][0]['id'];self.store.add_copies(dict(printing_id=pid))
        self.store.save_source(dict(source_id=sid,lang='en',name='Renamed source',kind='box',release='QA-UPDATED',release_date='2021-03'))
        self.assertEqual(self.store.entry(first)['set_name'],'Renamed source');self.assertEqual(self.store.entry(first)['release'],'QA-UPDATED');self.assertEqual(self.store.entry(first)['release_date'],'2021-03');self.assertEqual(self.store.entry(second)['release_date'],'2020-06-15')
        self.store.trash_item(dict(kind='source',target_id=sid));self.assertNotIn(first,self.store.entries());self.assertNotIn(second,self.store.entries());self.assertEqual(len(self.store.state()['copies']),1)
        self.store.trash_item(dict(kind='source',target_id=sid),True);self.assertIn(first,self.store.entries());self.assertIn(second,self.store.entries())
    def test_remove_builtin_card_and_backup_roundtrip_keeps_all_editor_changes(self):
        e=next(e for e in self.store.entries().values() if e['lang']=='en' and e['printings']);pid=e['printings'][0]['id'];self.store.add_copies(dict(printing_id=pid,price='7',currency='EUR'))
        sid=self.source();eid=self.card(sid);self.store.trash_item(dict(kind='entry',target_id=e['id']));self.store.trash_item(dict(kind='source',target_id=sid))
        raw=self.store.backup();payload=self.payload(raw);self.assertEqual(payload['version'],4);before=self.store.state(True)
        self.store.restore(raw);after=self.store.state(True)
        for table in before:
            if table!='audit_log':self.assertEqual(before[table],after[table],table)
        self.assertNotIn(e['id'],self.store.entries());self.assertNotIn(eid,self.store.entries());self.assertEqual(len(self.store.state()['copies']),1)
        self.store.trash_item(dict(kind='entry',target_id=e['id']),True);self.assertIn(pid,self.store.printing_map())
    def test_old_backup_with_excluded_ownership_is_preserved_but_not_counted(self):
        retired=next(e for e in self.store.catalog['retired_entries'] if e['printings']);pid=retired['printings'][0]['id'];payload=self.payload(self.store.backup());payload['version']=2;payload['tables']={k:v for k,v in payload['tables'].items() if k in V2_TABLES}
        payload['tables']['copies'].append(dict(id='old-eevee-copy',printing_id=pid,condition='near_mint',price_minor=1234,currency='EUR',purchased_on='2025-01-01',notes='Original personal record',misprint_notes='',created_at='2025-01-01T00:00:00+00:00',updated_at='2025-01-01T00:00:00+00:00',deleted_at=None))
        payload['tables']['wishlist'].append(dict(printing_id=pid,created_at='2025-01-01T00:00:00+00:00'))
        self.store.restore(self.zipped(payload));self.assertEqual(self.store.state()['copies'][0]['price_minor'],1234);self.assertNotIn(pid,self.store.printing_map());self.assertNotIn(retired['id'],self.store.entries())
        self.assertEqual(self.payload(self.store.backup())['tables']['copies'][0]['id'],'old-eevee-copy')
        with self.assertRaises(ValueError):self.store.add_copies(dict(printing_id=pid))
    def test_failed_create_is_atomic_and_legacy_manual_sources_remain_editable(self):
        before=self.store.state(True)
        with self.assertRaises(ValueError):self.store.save_card(dict(lang='en',name='Incomplete card',number='1',subject_dex=[37],new_source=dict(lang='en',name='Should not be saved',kind='set'),rarity_code='unresolved',initial_printing=dict(finish='holo',confirmed=True)))
        self.assertEqual(self.store.state(True),before)
        eid=self.store.new_entry(dict(lang='en',dex=37,name='Legacy hand entry',number='Unnumbered',set_name='Old manual product',source_note='Original personal catalog record.'))['entry_id']
        entry=self.store.entry(eid);sid=entry['primary_source_id'];self.assertIn(sid,self.store.sources());self.assertTrue(entry['sources'])
        self.store.save_source(dict(source_id=sid,lang='en',name='Old source corrected',kind='deck',release_date='2001'))
        self.assertEqual(self.store.entry(eid)['set_name'],'Old source corrected')
    def test_corrupt_editor_backup_is_rejected_before_altering_personal_records(self):
        sid=self.source();eid=self.card(sid);pid=self.store.entry(eid)['printings'][0]['id']
        self.store.save_printing(dict(entry_id=eid,printing_id=pid,finish='reverse_holo',confirmed=True))
        before=self.store.state(True);payload=self.payload(self.store.backup())
        value=json.loads(payload['tables']['printing_overrides'][0]['payload_json']);value['id']='wrong-printing-id';payload['tables']['printing_overrides'][0]['payload_json']=json.dumps(value)
        with self.assertRaises(ValueError):self.store.restore(self.zipped(payload))
        self.assertEqual(self.store.state(True),before)

    def test_rarity_and_artwork_stay_distinct_and_language_specific(self):
        for lang in ('en','de'):
            doubles=[e for e in self.store.entries().values() if e['lang']==lang and e['rarity_code']=='double_rare'];self.assertTrue(doubles);self.assertTrue(all(e['art_style']=='standard' for e in doubles));self.assertTrue(all(e['rarity_key']=='double_rare' for e in doubles))
        self.assertEqual(label('double_rare','de'),'Doppelselten');self.assertEqual(label('double_rare','en'),'Double Rare')
        self.assertEqual(key(dict(rarity_state='known',rarity_code='S',rarity_namespace='ja_legacy_lvx')),'S_legacy_lvx')
        self.assertEqual(key(dict(rarity_state='known',rarity_code='S',rarity_namespace='ja_modern')),'S')
        self.assertEqual(label('SR','ja'),'SR · Super Rare')

if __name__=='__main__':unittest.main(verbosity=2)
