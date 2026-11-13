"""Product discovery is not confirmation; exact printing links preserve collections."""
import copy,io,json,tempfile,unittest,urllib.error
from pathlib import Path
from unittest.mock import patch
from dogdex.collector import Collection,ValidationError,now
from dogdex.marketplace import (PRODUCT_URL,search_products,confirm_product,provider_products,
                         refresh_products,read_products,product_id_from_url,price_state)

ROOT=Path(__file__).resolve().parents[1]
HOUNDOUR_URL='https://www.cardmarket.com/en/Pokemon/Products/Singles/Ruler-of-the-Black-Flame/Houndour-V2-sv3115'

class ProductFinderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        catalog=json.loads((ROOT/'data/catalog.json').read_text(encoding='utf-8'))
        wanted={('en','base1','68'),('en','swsh12tg','TG07'),('de','swsh12tg','TG07'),('ja','SV3','115')}
        catalog['entries']=[e for e in catalog['entries'] if (e['lang'],e['release'],e['number']) in wanted]
        catalog['retired_entries']=[];catalog['retired_releases']=[]
        releases={(e['lang'],e['release']) for e in catalog['entries']}
        catalog['releases']=[r for r in catalog['releases'] if (r['lang'],r['release']) in releases]
        cls.catalog=catalog

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);(self.root/'data').mkdir()
        (self.root/'data/catalog.json').write_text(json.dumps(self.catalog),encoding='utf-8')
        self.store=Collection(self.root)
        self.ja=next(e for e in self.store.entries().values() if e['lang']=='ja')
        self.pid=self.ja['printings'][0]['id']

    def cache_products(self):
        rows={724971:dict(name='Houndour [Coordinated Pack | Focus Fangs]',id_expansion=5409),682271:dict(name='Rockruff [Crunch]',id_expansion=5142),273763:dict(name='Vulpix',id_expansion=1),987654:dict(name='<b>Houndour</b> [Other printing]',id_expansion=9000)}
        value=dict(format='dogdex-cardmarket-products-1',source_created_at='2026-10-29T14:18:13+0100',fetched_at=now(),products={str(pid):dict(product_id=pid,**row) for pid,row in rows.items()})
        (self.store.user_dir/'market_products.json').write_text(json.dumps(value),encoding='utf-8');return value

    def cache_prices(self):
        (self.store.user_dir/'market_prices.json').write_text(json.dumps(dict(format='dogdex-cardmarket-prices-1',source_created_at='2026-10-29T02:52:59+0100',fetched_at=now(),products={'724971':dict(trend=2.76,avg30=2.84),'682271':dict(trend=4.03)})),encoding='utf-8')

    def selection(self):
        return search_products(self.store,dict(printing_id=self.pid,cache_only=True))

    def confirm(self,selection=None,**values):
        selection=selection or self.selection()
        data=dict(printing_id=self.pid,context_key=selection['context_key'],product_id=724971,price_series='standard',confirmed=True)
        data.update(values);return confirm_product(self.store,data)

    def test_native_evidence_is_visible_without_network_or_promotion(self):
        before=self.store.state()
        with patch('urllib.request.urlopen') as network:result=self.selection();network.assert_not_called()
        self.assertEqual(result['context']['lang'],'ja');self.assertEqual(result['context']['number'],'115')
        self.assertEqual(result['products'][0]['product_id'],724971)
        self.assertEqual(result['products'][0]['name'],'Houndour')
        self.assertFalse(result['products'][0]['catalogue_present']);self.assertTrue(result['products'][0]['suggested'])
        self.assertEqual(before,self.store.state());self.assertFalse(price_state(self.store)['printings'])
        wrong=copy.deepcopy(self.ja['printings'][0]);wrong['finish']='non_holo'
        self.assertNotIn(724971,provider_products(self.ja,wrong))

    def test_german_identity_reuses_a_compatible_western_reference_as_unconfirmed(self):
        de=next(e for e in self.store.entries().values() if e['lang']=='de')
        result=search_products(self.store,dict(printing_id=de['printings'][0]['id'],cache_only=True))
        hint=next(p for p in result['products'] if p['product_id']==682271)
        self.assertTrue(any('unchecked' in origin['label'] for origin in hint['origins']));self.assertFalse(hint['current'])
        self.assertEqual(result['context']['lang'],'de');self.assertFalse(price_state(self.store)['printings'])

    def test_pretty_urls_do_not_turn_card_numbers_into_product_ids(self):
        self.cache_products()
        self.assertIsNone(product_id_from_url(HOUNDOUR_URL))
        self.assertEqual(product_id_from_url('https://www.cardmarket.com/en/Pokemon/Products?idProduct=724971'),724971)
        self.assertIsNone(product_id_from_url('https://cardmarket.com.evil.invalid/?idProduct=724971'))
        result=search_products(self.store,dict(printing_id=self.pid,query=HOUNDOUR_URL,cache_only=True))
        self.assertEqual(result['products'][0]['product_id'],724971)
        self.assertNotIn(115,{p['product_id'] for p in result['products']})
        result=search_products(self.store,dict(printing_id=self.pid,query='https://www.cardmarket.com/en/Pokemon/Products?idProduct=724971',cache_only=True))
        self.assertEqual([p['product_id'] for p in result['products']],[724971])
        with self.assertRaises(ValidationError):search_products(self.store,dict(printing_id=self.pid,query='https://example.com/idProduct=724971'))

    def test_catalogue_enriches_candidates_but_does_not_change_catalog_or_copy_state(self):
        self.cache_products();before=self.store.state()
        result=self.selection();row=result['products'][0]
        self.assertEqual(row['name'],'Houndour [Coordinated Pack | Focus Fangs]');self.assertEqual(row['id_expansion'],5409)
        self.assertTrue(row['catalogue_present']);self.assertGreater(result['total'],1)
        self.assertEqual(before,self.store.state())

    def test_code_card_products_are_not_physical_card_candidates(self):
        cache=self.cache_products();cache['products']['362883']=dict(product_id=362883,name='Online Code Card (Rockruff Blister)')
        (self.store.user_dir/'market_products.json').write_text(json.dumps(cache),encoding='utf-8')
        de=next(e for e in self.store.entries().values() if e['lang']=='de')
        result=search_products(self.store,dict(printing_id=de['printings'][0]['id'],query='Rockruff',cache_only=True))
        self.assertNotIn(362883,{p['product_id'] for p in result['products']})
        typed=search_products(self.store,dict(printing_id=self.pid,query='362883',cache_only=True))
        self.assertTrue(typed['products'][0]['code_product'])
        with self.assertRaisesRegex(ValidationError,'online code card'):self.confirm(typed,product_id=362883)
        self.assertFalse(price_state(self.store)['printings'])

    def test_confirmation_requires_explicit_check_and_a_fresh_identity(self):
        self.cache_products();self.cache_prices();selection=self.selection()
        with self.assertRaises(ValidationError):self.confirm(selection,confirmed=False)
        with self.assertRaises(ValidationError):self.confirm(selection,price_series='reverse')
        with self.assertRaises(ValidationError):self.confirm(selection,product_id=0)
        self.store.override(dict(entry_id=self.ja['id'],values=dict(number='115-alt'),source_note='A separately reviewed collector-number correction.'))
        with self.assertRaisesRegex(ValidationError,'changed'):self.confirm(selection)
        self.assertFalse(price_state(self.store)['printings'])

    def test_save_and_backup_preserve_copies_costs_wishes_overrides_and_printing_ids(self):
        self.cache_products();self.cache_prices()
        # A pre-existing catalog correction must survive the dedicated match save.
        original=self.store.entry(self.ja['id'])['printings'][0]
        self.store.save_printing(dict(original,printing_id=self.pid,entry_id=self.ja['id'],notes='Keep my printing note',confirmed=True))
        self.store.add_copies(dict(printing_id=self.pid,quantity=2,condition='near_mint',price='9.50',currency='EUR',notes='Storage drawer 2',purchased_on='2026-10-22'))
        self.store.wish(dict(printing_id=self.pid,wanted=True));before=self.store.state()
        with patch('urllib.request.urlopen') as network:result=self.confirm();network.assert_not_called()
        self.assertTrue(result['saved']);self.assertEqual(result['prices']['printings'][self.pid]['trend'],2.76)
        after=self.store.state();self.assertEqual(before['copies'],after['copies']);self.assertEqual(before['wishlist'],after['wishlist'])
        printing=self.store.entry(self.ja['id'])['printings'][0]
        self.assertEqual(printing['id'],self.pid);self.assertEqual(printing['notes'],'Keep my printing note')
        self.assertTrue(printing['market_confirmed']);self.assertEqual(printing['market_match']['method'],'collector_product_search')
        restored=Collection(self.root,self.root/'restored');restored.restore(self.store.backup())
        self.assertEqual(restored.state()['copies'],after['copies']);self.assertEqual(restored.state()['wishlist'],after['wishlist'])
        self.assertEqual(restored.entry(self.ja['id'])['printings'][0]['price_product_id'],724971)
        self.assertEqual(len(restored.entry(self.ja['id'])['printings']),1)

    def test_a_new_price_only_match_also_roundtrips_in_existing_backup_format(self):
        self.cache_products();self.cache_prices();self.confirm()
        target=Collection(self.root,self.root/'restore-new-match');target.restore(self.store.backup())
        self.assertEqual(target.entry(self.ja['id'])['printings'][0]['price_product_id'],724971)

    def test_offline_price_refresh_reports_a_saved_link_and_unlink_keeps_ownership(self):
        self.cache_products();self.store.add_copies(dict(printing_id=self.pid,condition='good',price='4',currency='EUR'))
        with patch('dogdex.marketplace.refresh_prices',side_effect=ValidationError('Offline')):result=self.confirm()
        self.assertTrue(result['saved']);self.assertIn('Offline',result['price_warning'])
        self.assertTrue(self.store.entry(self.ja['id'])['printings'][0]['market_confirmed'])
        before=self.store.state()['copies'];selection=self.selection()
        result=confirm_product(self.store,dict(printing_id=self.pid,context_key=selection['context_key']),unlink=True)
        self.assertTrue(result['saved']);self.assertEqual(before,self.store.state()['copies']);self.assertFalse(price_state(self.store)['printings'])

    def test_cache_download_is_validated_reused_and_failed_refresh_keeps_previous_bytes(self):
        feed=dict(createdAt='2026-10-29T14:18:13+0100',products=[dict(idProduct=724971,name='Houndour',idExpansion=5409,idMetacard=422301)])
        with patch('urllib.request.urlopen',return_value=io.BytesIO(json.dumps(feed).encode())) as network:
            value=refresh_products(self.store);self.assertEqual(value['products']['724971']['name'],'Houndour');network.assert_called_once()
        before=(self.store.user_dir/'market_products.json').read_bytes()
        with patch('urllib.request.urlopen') as network:refresh_products(self.store);network.assert_not_called()
        with patch('urllib.request.urlopen',return_value=io.BytesIO(b'{"products":[],"createdAt":"bad"}')),self.assertRaises(ValidationError):refresh_products(self.store,True)
        self.assertEqual((self.store.user_dir/'market_products.json').read_bytes(),before)
        self.assertEqual(read_products(self.store)['products']['724971']['name'],'Houndour')

    def test_search_can_fall_back_to_recovered_hints_when_download_fails(self):
        with patch('urllib.request.urlopen',side_effect=urllib.error.URLError('Offline')):result=search_products(self.store,dict(printing_id=self.pid))
        self.assertEqual(result['products'][0]['product_id'],724971);self.assertIn('Offline',result['warning'])
        self.assertFalse(self.store.entry(self.ja['id'])['printings'][0].get('market_confirmed'))

if __name__=='__main__':unittest.main()
