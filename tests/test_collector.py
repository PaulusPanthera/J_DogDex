"""Exercise real persistence, exact printing IDs, recovery and HTTP boundaries."""
import base64,hashlib,http.client,io,json,sqlite3,sys,tempfile,threading,unittest,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from dogdex.collector import Collection,ValidationError,money
from dogdex.app import make_server
from dogdex.scope import is_cameo

ROOT=Path(__file__).resolve().parents[1]
BASELINE='e79d48ff8d056d88fa0d6b1f0771f220d79f62d82797c886183e20ada9c22da0'

class CollectorTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='DogDex test with spaces ')
        self.store=Collection(ROOT,Path(self.temp.name)/'my collection')
        self.entry=next(e for e in self.store.catalog['entries'] if e['lang']=='en' and len(e['printings'])>1)
        self.pid=self.entry['printings'][0]['id']
    def tearDown(self):self.temp.cleanup()
    def add(self,**values):return self.store.add_copies(dict(printing_id=self.pid,condition='near_mint',price='12.34',currency='EUR',quantity=1,**values))
    def backup_payload(self,raw):
        with zipfile.ZipFile(io.BytesIO(raw)) as z:return json.loads(z.read('collection.json'))
    def zip_payload(self,payload):
        out=io.BytesIO()
        with zipfile.ZipFile(out,'w') as z:z.writestr('collection.json',json.dumps(payload))
        return out.getvalue()
    def test_catalog_identity_and_images(self):
        c=self.store.catalog
        self.assertEqual(c['statistics']['entries'],len(c['entries']));self.assertEqual(c['statistics']['printings'],sum(len(e['printings']) for e in c['entries']))
        self.assertEqual({e['lang'] for e in c['entries']},{'en','de','ja','ko'})
        self.assertEqual(len(self.store.printing_map()),sum(len(e['printings']) for e in self.store.entries().values()))
        self.assertNotIn('full_art',{e['rarity_family'] for e in c['entries']},'Do not infer artwork style from rarity alone.')
        self.assertTrue(all((ROOT/'data/images'/name).is_file() for name in c['used_images']))
        self.assertEqual(hashlib.sha256((ROOT/'data/catalog.sqlite3').read_bytes()).hexdigest(),BASELINE)
    def test_every_printing_but_not_every_copy_counts(self):
        result=self.store.add_copies(dict(printing_id=self.pid,quantity=2,condition='near_mint',price='12.34',currency='EUR'))
        state=self.store.state();self.assertEqual(len(result['ids']),2);self.assertEqual(len(state['copies']),2)
        self.assertEqual(len({c['printing_id'] for c in state['copies']}),1)
        other=self.entry['printings'][1]['id'];self.store.add_copies(dict(printing_id=other))
        self.assertEqual(len({c['printing_id'] for c in self.store.state()['copies']}),2)
        reopened=Collection(ROOT,self.store.user_dir);self.assertEqual(len(reopened.state()['copies']),3)
    def test_money_condition_date_and_rejected_printing(self):
        self.assertEqual(money('12,34','EUR'),(1234,'EUR'));self.assertEqual(money('0','EUR'),(0,'EUR'))
        self.assertEqual(money('100','JPY'),(100,'JPY'));self.assertEqual(money('','EUR'),(None,None))
        for amount,currency in [('NaN','EUR'),('-1','EUR'),('1.001','EUR'),('1.1','JPY'),('Infinity','EUR'),('1','XXX')]:
            with self.subTest(amount=amount,currency=currency),self.assertRaises(ValidationError):money(amount,currency)
        for invalid in [dict(printing_id='invented_finish'),dict(condition='fake'),dict(purchased_on='2026-02-30'),dict(quantity=0),dict(quantity=True)]:
            with self.subTest(invalid=invalid),self.assertRaises(ValidationError):self.store.add_copies(dict(printing_id=self.pid)|invalid)
        self.assertEqual(self.store.state()['copies'],[])
    def test_wishlist_removal_and_copy_edit_remove_undo(self):
        self.store.wish(dict(printing_id=self.pid,wanted=True))
        cid=self.add(remove_from_wishlist=True)['ids'][0];self.assertEqual(self.store.state()['wishlist'],[])
        self.store.edit_copy(dict(id=cid,condition='good',price='5',currency='USD',notes='<script>not executed</script>',misprint_notes='Off-centre'))
        row=self.store.state()['copies'][0];self.assertEqual((row['price_minor'],row['condition'],row['printing_id']),(500,'good',self.pid))
        self.store.remove_copy(dict(id=cid));self.assertEqual(self.store.state()['copies'],[])
        self.store.remove_copy(dict(id=cid),undo=True);self.assertEqual(self.store.state()['copies'][0]['misprint_notes'],'Off-centre')
    def test_language_ledgers_do_not_share_ownership(self):
        self.add();pids={r['printing_id'] for r in self.store.state()['copies']}
        by_language={lang:sum(p['id'] in pids for e in self.store.catalog['entries'] if e['lang']==lang for p in e['printings']) for lang in ('en','de','ja','ko')}
        self.assertEqual(by_language,dict(en=1,de=0,ja=0,ko=0))
    def test_manual_research_gate_and_special_categories(self):
        for category,size in [('cameo','standard'),('jumbo','oversized')]:
            eid=self.store.new_entry(dict(lang='en',dex=37,name='Research example '+category,number='Unnumbered',set_name='Documented source',category=category,source_note='Test evidence for a missing catalog card.'))['entry_id']
            request=dict(entry_id=eid,finish='holo',edition='not_applicable',size=size,source_note='Verified exact physical card in test evidence.',confirmed=True)
            with self.assertRaises(ValidationError):self.store.new_printing(request)
            self.store.override(dict(entry_id=eid,values=dict(identity_verified=True,rarity_state='not_printed'),source_note='Verified name and no printed rarity.'))
            pid=self.store.new_printing(request)['printing_id'];self.store.add_copies(dict(printing_id=pid))
            self.assertEqual(self.store.printing_map()[pid][1]['category'],category)
            with self.assertRaises(ValidationError):self.store.new_printing(request)
        self.assertEqual(len({c['printing_id'] for c in self.store.state()['copies']}),2)
    def test_no_unsupported_modern_edition_or_nonholo_pattern(self):
        entry=next(e for e in self.store.catalog['entries'] if e['lang']=='en' and e['release'].startswith('sv') and e['printings'] and e['metadata_state']=='approved' and e['rarity_state']=='known')
        request=dict(entry_id=entry['id'],finish='holo',edition='first_edition',confirmed=True,source_note='Unreliable assertion deliberately tested.')
        for invalid in [dict(edition='first_edition'),dict(edition='unlimited'),dict(edition='not_applicable',layout='shadowless'),dict(edition='not_applicable',layout='shadowed'),dict(edition='not_applicable',finish='non_holo',pattern='cosmos'),dict(confirmed=False)]:
            with self.subTest(invalid=invalid),self.assertRaises(ValidationError):self.store.new_printing(request|invalid)
    def test_corrections_preserve_original_catalog(self):
        original=self.store.base_entries[self.entry['id']]['name']
        self.store.override(dict(entry_id=self.entry['id'],values=dict(name='Local corrected label',year=2001),source_note='Test a documented local correction.'))
        self.assertEqual(self.store.entry(self.entry['id'])['name'],'Local corrected label')
        self.assertEqual(self.store.base_entries[self.entry['id']]['name'],original)
        self.assertEqual(hashlib.sha256((ROOT/'data/catalog.sqlite3').read_bytes()).hexdigest(),BASELINE)
    def test_backup_roundtrip_includes_images_research_soft_deletes(self):
        self.test_manual_research_gate_and_special_categories()
        self.store.wish(dict(printing_id=self.pid,wanted=True));cid=self.add()['ids'][0];self.store.remove_copy(dict(id=cid))
        sample=(ROOT/'data/images'/self.store.catalog['used_images'][0]).read_bytes()
        self.store.catalog_image(dict(entry_id=self.entry['id'],source_note='Test source for standard catalog image.',bytes=base64.b64encode(sample).decode()))
        backup=self.store.backup();expected=self.store.state(True);self.store.remove_copy(dict(id=cid),undo=True)
        self.store.restore(backup);actual=self.store.state(True)
        for table in expected:
            if table!='audit_log':self.assertEqual(actual[table],expected[table],table)
        self.assertEqual(len(list((self.store.user_dir/'backups').glob('before-restore-*.zip'))),1)
        image=actual['image_overrides'][0]['filename'];self.assertEqual((self.store.user_dir/'catalog_images'/image).read_bytes(),sample)
    def test_invalid_restore_preserves_current_records(self):
        self.add();before=self.store.state(True);payload=self.backup_payload(self.store.backup())
        payload['tables']['copies'][0]['printing_id']='unknown'
        with self.assertRaises(ValidationError):self.store.restore(self.zip_payload(payload))
        self.assertEqual(self.store.state(True),before)
        payload=self.backup_payload(self.store.backup());payload['tables']['copies'].append(payload['tables']['copies'][0])
        with self.assertRaises(ValidationError):self.store.restore(self.zip_payload(payload))
        self.assertEqual(self.store.state(True),before)
        for raw in [b'not a zip',self.zip_payload([]),self.zip_payload(dict(format='other'))]:
            with self.assertRaises(ValidationError):self.store.restore(raw)

    def test_source_ids_regional_dates_and_research_coverage(self):
        c=self.store.catalog
        with sqlite3.connect(ROOT/'data/catalog.sqlite3') as db:
            original_entries={r[0] for r in db.execute('SELECT id FROM published_entries')}
            original_printings={r[0] for r in db.execute('SELECT id FROM available_variants')}
        self.assertTrue(original_entries<=set(self.store.base_entries)|{e['id'] for e in c.get('retired_entries',[])})
        self.assertTrue(original_printings <= set(self.store.printing_map(include_removed=True,include_retired=True)))
        base=next(e for e in c['entries'] if e['lang']=='de' and e['release']=='base1')
        self.assertEqual((base['release_date'],base['date_precision']),('1999-12','month'))
        korean=next(e for e in c['entries'] if e['lang']=='ko' and e['release']=='SV1S')
        self.assertEqual(korean['release_date'],'2023-03-15')
        for lang in ('en','de','ja','ko'):
            self.assertTrue(any(e['lang']==lang and e.get('art_style')=='full_art' for e in c['entries']))
            self.assertEqual(sum(e['lang']==lang and is_cameo(e) for e in c['entries']),c['language_stats'][lang]['cameos'])
        self.assertEqual(c['printing_enrichment_summary']['japanese_added'],94)
        detective=next(e for e in c['entries']+c.get('retired_entries',[]) if e['lang']=='ja' and e['release']=='SV-P' and e['number']=='098')
        self.assertEqual({p['finish'] for p in detective['printings']},{'holo'})
        with sqlite3.connect(ROOT/'data/catalog-collector.sqlite3') as db:
            self.assertEqual(db.execute('PRAGMA quick_check').fetchone()[0],'ok')
            self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(),[])
            self.assertEqual(db.execute('SELECT COUNT(*) FROM entries').fetchone()[0],len(c['entries']))
            self.assertEqual(db.execute('SELECT COUNT(*) FROM printings').fetchone()[0],c['statistics']['printings'])
    def test_printing_picture_isolation_and_backup_versions(self):
        sample=(ROOT/'data/images'/self.store.catalog['used_images'][0]).read_bytes()
        eid=self.entry['id'];other=self.entry['printings'][1]['id'];original=self.store.printing_map()[other][1]['image']
        request=dict(entry_id=eid,printing_id=self.pid,source_note='Verified exact printing catalog reference.',bytes=base64.b64encode(sample).decode())
        self.store.catalog_image(request)
        pmap=self.store.printing_map();self.assertTrue(pmap[self.pid][1]['image'].startswith('/user-images/'))
        self.assertEqual(pmap[other][1]['image'],original)
        unrelated=next(p['id'] for e in self.store.catalog['entries'] if e['id']!=eid for p in e['printings'])
        with self.assertRaises(ValidationError):self.store.catalog_image(request|dict(printing_id=unrelated))
        backup=self.store.backup();self.store.remove_image(dict(entry_id=eid,printing_id=self.pid))
        self.store.restore(backup);self.assertEqual(len(self.store.state()['printing_image_overrides']),1)
        payload=self.backup_payload(backup);payload['version']=1
        from dogdex.collector import LEGACY_TABLES
        payload['tables']={k:v for k,v in payload['tables'].items() if k in LEGACY_TABLES}
        self.store.restore(self.zip_payload(payload));self.assertEqual(self.store.state()['printing_image_overrides'],[])
        self.assertEqual(self.store.printing_map()[other][1]['image'],original)
    def test_set_dates_keep_precision_and_card_override_precedence(self):
        eid=self.entry['id'];lang=self.entry['lang'];release=self.entry['release']
        data=dict(lang=lang,release=release,release_date='2000-04',source_note='Regional monthly chronology verified in test.')
        self.store.override_release(data)
        related=[e for e in self.store.entries().values() if e['lang']==lang and e['release']==release]
        self.assertTrue(all(e['release_date']=='2000-04' and e['date_precision']=='month' for e in related))
        self.store.override(dict(entry_id=eid,values=dict(release_date='2000-04-15'),source_note='Exact individual product launch verified.'))
        self.store.override_release(data|dict(release_date='2001'))
        self.assertEqual(self.store.entry(eid)['release_date'],'2000-04-15')
        for date in ('2026-02-30','2026-13','20','2026-01-99'):
            with self.assertRaises(ValidationError):self.store.override_release(data|dict(release_date=date))
        raw=self.store.backup();self.store.restore(raw)
        self.assertEqual(self.store.entry(eid)['release_date'],'2000-04-15')
    def test_new_card_reuses_set_and_blocks_duplicate_identity(self):
        data=dict(lang=self.entry['lang'],release=self.entry['release'],dex=37,name='Test missing card',english='Test missing card',number='Research-999',set_name='ignored source name',source_note='Exact missing card identity and printed number.')
        eid=self.store.new_entry(data)['entry_id'];created=self.store.entry(eid)
        self.assertEqual(created['release'],self.entry['release']);self.assertEqual(created['set_name'],self.entry['set_name'])
        self.assertEqual(created['printings'],[])
        with self.assertRaises(ValidationError):self.store.new_entry(data)
    def test_new_card_retains_inherited_date_evidence_and_promo_gaps(self):
        source=next(e for e in self.store.catalog['entries'] if e['lang']=='de' and e['date_state']=='provider_reference')
        request=dict(lang='de',release=source['release'],dex=37,name='Date inheritance check',number='Research-date-test',set_name=source['set_name'],source_note='Identity checked, regional date not established.')
        eid=self.store.new_entry(request)['entry_id'];entry=self.store.entry(eid)
        self.assertEqual(entry['date_state'],'provider_reference')
        self.assertEqual(entry['release_date'],source['release_date'])
        self.assertNotEqual(entry['date_source'],request['source_note'])
        # A dated individual promo must not date all other cards in that series.
        promo=next(e for e in self.store.catalog['entries'] if e['lang']=='ja' and e['release']=='S-P')
        self.store.override(dict(entry_id=promo['id'],values=dict(release_date='2021-04-01'),source_note='One specific promotional distribution date.'))
        eid=self.store.new_entry(request|dict(lang='ja',release='S-P',name='Undated promo check',set_name=promo['set_name']))['entry_id']
        self.assertIsNone(self.store.entry(eid)['release_date'])
        self.assertEqual(self.store.entry(eid)['date_state'],'unresolved')
    def test_manufacturer_archive_dates_and_source_names(self):
        catalog=self.store.catalog
        def find(key):return next(e for e in catalog['entries'] if e['lang']=='ja' and e['release']==key)
        for key,date in [('SVI','2024-03-08'),('SA','2019-11-29'),('SVD','2023-07-07'),('DPt-EPd','2008-10-10'),('WCP','2007-07-05'),('SMP1','2016-12-15'),('MP1','2025-12-19')]:
            entry=find(key);self.assertEqual(entry['release_date'],date)
            self.assertNotEqual(entry['set_name'],key)
            source=next(s for s in entry['sources'] if s['id']=='release:ja:'+key)
            self.assertEqual(source['name'],entry['set_name'])
        # One title occurs in different eras; the DPt product must be selected.
        self.assertIn('dpt',find('DPt-EPd')['date_evidence']['product_image'])
        self.assertTrue(all(int(e['number'])<=139 for e in catalog['entries'] if e['lang']=='ja' and e['release']=='SVD'))
        self.assertEqual(catalog['research_summary']['accepted_set_dates'],sum(bool(r.get('date')) for r in catalog['releases']))
        matches=json.loads((ROOT/'data/research/extra_product_date_matches.json').read_text(encoding='utf-8'))['matches']
        self.assertEqual(len(matches),41)
        for match in matches:
            evidence=match['evidence']
            if evidence.get('snapshot_file'):
                self.assertEqual(hashlib.sha256((ROOT/'data/research'/evidence['snapshot_file']).read_bytes()).hexdigest(),evidence['snapshot_sha256'])
    def test_existing_database_schema_migrates_without_changing_copies(self):
        cid=self.add()['ids'][0]
        with self.store.connect() as db:
            db.execute('DROP TABLE printing_image_overrides');db.execute('DROP TABLE release_overrides')
        reopened=Collection(ROOT,self.store.user_dir);row=reopened.state()['copies'][0]
        self.assertEqual((row['id'],row['printing_id'],row['price_minor']),(cid,self.pid,1234))
        self.assertEqual(reopened.state()['printing_image_overrides'],[])

class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.server=make_server(ROOT,port=0,user_dir=Path(cls.temp.name));cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join();cls.temp.cleanup()
    def request(self,method,path,body=None,headers=None):
        c=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=10)
        c.request(method,path,body=body,headers=headers or {});r=c.getresponse();result=(r.status,r.read(),dict(r.getheaders()));c.close();return result
    def test_static_catalog_and_request_guards(self):
        status,raw,headers=self.request('GET','/');self.assertEqual(status,200);self.assertIn(b'DogDex',raw);self.assertIn('Content-Security-Policy',headers);self.assertEqual(headers['Cache-Control'],'no-store')
        status,module,module_headers=self.request('GET','/catalog.mjs');self.assertEqual(status,200);self.assertIn('javascript',module_headers['Content-Type'])
        self.assertEqual(self.request('GET','/../data/catalog.sqlite3')[0],404)
        self.assertEqual(self.request('GET','/images/../../app.py')[0],404)
        self.assertEqual(self.request('GET','/api/state',headers={'Host':'external.example'})[0],403)
        self.assertEqual(self.request('POST','/api/copy/add','{}',{'Content-Type':'application/json'})[0],403)
    def test_real_http_mutation_and_backup(self):
        _,raw,_=self.request('GET','/api/state');token=json.loads(raw)['token'];pid=next(iter(self.server.store.printing_map()))
        headers={'Content-Type':'application/json','X-DogDex-Token':token}
        self.assertEqual(self.request('POST','/api/copy/add',json.dumps(dict(printing_id=pid)),headers|{'Origin':'https://external.example'})[0],403)
        status,raw,_=self.request('POST','/api/copy/add',json.dumps(dict(printing_id=pid,price='1.25',currency='EUR')),headers)
        self.assertEqual(status,200);self.assertEqual(json.loads(raw)['state']['copies'][0]['price_minor'],125)
        status,raw,_=self.request('GET','/api/backup');self.assertEqual(status,200)
        with zipfile.ZipFile(io.BytesIO(raw)) as z:self.assertIsNone(z.testzip());self.assertIn('collection.json',z.namelist())

if __name__=='__main__':unittest.main(verbosity=2)
