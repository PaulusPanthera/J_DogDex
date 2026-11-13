"""Collection upgrade, public export and price-source separation checks."""
import base64, io, json, shutil, tempfile, unittest, zipfile
from pathlib import Path
from unittest.mock import patch
from dogdex.collector import Collection, ValidationError
from dogdex.marketplace import price_state, refresh_prices, PRICE_URL
from dogdex.mobile_export import build_snapshot, export_mobile

ROOT=Path(__file__).resolve().parents[1]
IMAGE=b'GIF89a'+b'\0'*150

class PublishingTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/'app';self.root.mkdir()
        shutil.copytree(ROOT/'static',self.root/'static')
        (self.root/'data').mkdir()
        # Full catalog identities, with no huge runtime/image copy required.
        shutil.copyfile(ROOT/'data/catalog.json',self.root/'data/catalog.json')
        self.store=Collection(self.root)
        self.e=next(e for e in self.store.editor_view()['entries'] if e['lang']=='en' and e['release']=='base1' and e['number']=='68')
        self.pid=self.e['printings'][0]['id'];self.sid=self.e['primary_source_id']

    def cover(self):
        self.store.mutate('catalog/source/image',dict(source_id=self.sid,bytes=base64.b64encode(IMAGE).decode(),source_note='Uploaded release cover specimen.'))

    def test_v4_roundtrip_keeps_source_cover_and_every_personal_record(self):
        self.store.add_copies(dict(printing_id=self.pid,condition='excellent',price='12.34',currency='EUR',quantity=2,notes='private note',misprint_notes='',purchased_on='2026-10-29'))
        self.store.wish(dict(printing_id=self.pid,wanted=True));self.cover()
        before=self.store.state(include_deleted=True);raw=self.store.backup()
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            data=json.loads(z.read('collection.json'));self.assertEqual(data['version'],4)
            self.assertEqual(z.read('catalog_images/'+before['source_image_overrides'][0]['filename']),IMAGE)
        other=Collection(self.root,self.root/'other_collection');other.restore(raw)
        after=other.state(include_deleted=True)
        for table in before:
            if table!='audit_log':self.assertEqual(before[table],after[table],table)
        self.assertEqual(other.sources()[self.sid]['image'],self.store.sources()[self.sid]['image'])

    def test_old_v3_backup_upgrades_without_rekeying(self):
        self.store.add_copies(dict(printing_id=self.pid,condition='unassessed',price='',currency='EUR',quantity=1,notes='',misprint_notes='',purchased_on=''))
        with zipfile.ZipFile(io.BytesIO(self.store.backup())) as z:old=json.loads(z.read('collection.json'))
        old['version']=3;del old['tables']['source_image_overrides']
        out=io.BytesIO()
        with zipfile.ZipFile(out,'w') as z:z.writestr('collection.json',json.dumps(old))
        target=Collection(self.root,self.root/'upgrade');target.restore(out.getvalue())
        self.assertEqual(target.state()['copies'],self.store.state()['copies'])

    def test_public_snapshot_uses_merged_data_and_only_public_ownership(self):
        self.store.add_copies(dict(printing_id=self.pid,condition='good',price='9876.54',currency='EUR',quantity=2,notes='SECRET-COPY-NOTE',misprint_notes='',purchased_on='2026-10-29'))
        self.cover();self.store.wish(dict(printing_id=self.pid,wanted=True))
        snapshot=build_snapshot(self.store);serialized=json.dumps(snapshot)
        self.assertNotIn('SECRET-COPY-NOTE',serialized);self.assertNotIn('price_minor',serialized)
        self.assertNotIn('source_note',serialized);self.assertNotIn('audit_log',serialized)
        self.assertEqual(snapshot['ownership'][self.pid],2)
        result=export_mobile(self.store);self.assertEqual(result['directory'],'docs')
        exported=self.root/'docs';html=(exported/'index.html').read_text(encoding='utf-8')
        self.assertIn('data-readonly="true"',html);self.assertIn('./app.js',html)
        from dogdex import __version__
        self.assertEqual(snapshot['app_version'],__version__)
        self.assertEqual((exported/'set-symbols.mjs').read_bytes(),(self.root/'static/set-symbols.mjs').read_bytes())
        self.assertEqual((exported/'brand/growlithe.svg').read_bytes(),(self.root/'static/brand/growlithe.svg').read_bytes())
        for symbol in (self.root/'static/set-symbols').iterdir():
            self.assertEqual((exported/'set-symbols'/symbol.name).read_bytes(),symbol.read_bytes())
        self.assertEqual((exported/'user-images'/Path(self.store.sources()[self.sid]['image']).name).read_bytes(),IMAGE)
        self.assertFalse(list(exported.rglob('*.sqlite3')))
        self.assertFalse((exported/'api').exists())
        self.assertNotIn('catalog/source/save',(exported/'editor-ui.mjs').read_text(encoding='utf-8'))
        self.assertEqual(self.store.state()['copies'][0]['price_minor'],987654)
        export_mobile(self.store) # repeat the managed export

    def test_export_refuses_unrelated_docs_and_leaves_collection_untouched(self):
        (self.root/'docs').mkdir();(self.root/'docs/important.txt').write_text('keep me',encoding='utf-8')
        before=self.store.state()
        with self.assertRaises(ValidationError):export_mobile(self.store)
        self.assertEqual((self.root/'docs/important.txt').read_text(encoding='utf-8'),'keep me')
        self.assertEqual(before,self.store.state())

    def test_provider_candidates_never_turn_into_prices_and_bad_feed_keeps_cache(self):
        target=self.store.user_dir/'market_prices.json'
        cache=dict(format='dogdex-cardmarket-prices-1',source_created_at='2026-10-29T02:52:59+0100',products={'273763':{'trend':12.5,'trend-holo':90}})
        target.write_text(json.dumps(cache),encoding='utf-8');before=target.read_bytes()
        view=self.store.editor_view();p=next(e for e in view['entries'] if e['id']==self.e['id'])['printings'][0]
        p['market_candidate']={'product_id':273763}
        self.assertNotIn(p['id'],price_state(self.store,view)['printings'])
        from dogdex.marketplace import identity_key
        p.update(price_product_id=273763,price_series='standard',market_confirmed=True,market_identity=identity_key(self.e))
        self.assertEqual(price_state(self.store,view)['printings'][p['id']]['trend'],12.5)
        p['price_series']='reverse';self.assertEqual(price_state(self.store,view)['printings'][p['id']]['trend'],90)
        response=io.BytesIO(b'{"version":99,"priceGuides":[]}')
        with patch('urllib.request.urlopen',return_value=response),self.assertRaises(ValidationError):refresh_prices(self.store,True)
        self.assertEqual(target.read_bytes(),before)

    def test_source_metadata_fixes_english_names_and_preserves_regional_precision(self):
        view=self.store.editor_view();sources={s['id']:s for s in view['sources']}
        self.assertEqual(sources['release:de:ecard1']['release_date'],'2003')
        self.assertLess(sources['release:de:ecard1']['sequence_hint'],sources['release:de:ecard2']['sequence_hint'])
        self.assertIn('Generation',sources[self.sid]['series'])
        vulpix=next(e for e in view['entries'] if e['lang']=='de' and e['release']=='swsh1' and e['number']=='22')
        self.assertEqual(vulpix['market_code'],'SSH');self.assertEqual(vulpix['market_number'],'22')
        alolan=next(e for e in view['entries'] if e['lang']=='de' and e['release']=='sm2' and e['number']=='21')
        self.assertIn('Alolan',alolan['market_name'])

    def test_confirmed_price_mapping_is_preserved_but_a_changed_identity_invalidates_it(self):
        printing=self.e['printings'][0]
        data=dict(printing,entry_id=self.e['id'],printing_id=self.pid,confirmed=True,
                  stamps=json.loads(printing['stamps_json']),price_product_id='273763',
                  price_series='standard',market_confirmed=True)
        self.store.save_printing(data)
        cache=dict(format='dogdex-cardmarket-prices-1',source_created_at='2026-10-29T02:52:59+0100',products={'273763':{'trend':12.5}})
        (self.store.user_dir/'market_prices.json').write_text(json.dumps(cache),encoding='utf-8')
        self.assertEqual(price_state(self.store)['printings'][self.pid]['trend'],12.5)
        self.store.save_card(dict(self.e,entry_id=self.e['id'],source_id=self.sid,name='Vulpix · corrected identity'))
        self.assertNotIn(self.pid,price_state(self.store)['printings'])
        self.assertFalse(next(p for p in self.store.entry(self.e['id'])['printings'] if p['id']==self.pid)['market_confirmed'])

if __name__=='__main__':unittest.main()
