"""Confirmed listing reuse is independent of language and physical-printing identity."""
import base64,copy,json,shutil,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from dogdex.collector import Collection,ValidationError,now
from dogdex.marketplace import search_products,confirm_product,canonical_product_url,price_state
from dogdex.mobile_export import build_snapshot

ROOT=Path(__file__).resolve().parents[1]
V1='https://www.cardmarket.com/en/Pokemon/Products/Singles/Base-Set/Growlithe-V1-BS28'
V2='https://www.cardmarket.com/en/Pokemon/Products/Singles/Base-Set/Growlithe-V2-BS28'
MODERN='https://www.cardmarket.com/en/Pokemon/Products/Singles/Sword-Shield/Vulpix-SSH022'

class SharedProductTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        c=json.loads((ROOT/'data/catalog.json').read_text(encoding='utf-8'))
        c['entries']=[e for e in c['entries'] if (e['lang'] in ('en','de') and ((e['release']=='base1' and e['number']=='28') or (e['release']=='swsh1' and e['number'].lstrip('0')=='22'))) or (e['lang']=='ja' and e['release']=='SV3' and e['number']=='115')]
        c['retired_entries']=[];c['retired_releases']=[];cls.catalog=c
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.root=Path(t.name);(self.root/'data').mkdir()
        (self.root/'data/catalog.json').write_text(json.dumps(self.catalog),encoding='utf-8');self.store=Collection(self.root)
        today=now();products={273723:('Growlithe',1),660200:('Growlithe',1),900001:('Vulpix',1800)}
        (self.store.user_dir/'market_products.json').write_text(json.dumps(dict(format='dogdex-cardmarket-products-1',source_created_at=today,fetched_at=today,products={str(k):dict(product_id=k,name=n,id_expansion=x) for k,(n,x) in products.items()})),encoding='utf-8')
        (self.store.user_dir/'market_prices.json').write_text(json.dumps(dict(format='dogdex-cardmarket-prices-1',source_created_at=today,fetched_at=today,products={'273723':dict(trend=1.17),'660200':dict(trend=14.39),'900001':dict(trend=0.12,**{'trend-holo':0.77})})),encoding='utf-8')
    def card(self,lang='de',release='base1'):
        return next(e for e in self.store.entries().values() if e['lang']==lang and e['release']==release)
    def select(self,pid,**data):return search_products(self.store,dict(printing_id=pid,cache_only=True,**data))
    def save(self,s,pid=273723,all_targets=False,**extra):
        candidate=next(p for p in s['products'] if p['product_id']==pid)
        data=dict(printing_id=s['printing_id'],context_key=s['context_key'],product_id=pid,price_series=s['default_series'],listing_url=candidate['listing_url'],confirmed=True)
        if all_targets:data['targets']=[{k:t[k] for k in ('printing_id','context_key')} for t in candidate['related_printings']]
        return confirm_product(self.store,data|extra)
    def test_saved_listing_prefills_and_reference_recovers_without_guessing_an_id_from_a_slug(self):
        de=self.card();first=next(p for p in de['printings'] if p['edition']=='first_edition')
        s=self.select(first['id']);self.assertEqual(s['query'],V1);self.assertEqual(s['existing_url'],V1)
        c=s['products'][0];self.assertEqual(c['product_id'],273723);self.assertEqual(c['listing_url'],V1)
        self.assertEqual(len(c['related_printings']),4)
        self.assertFalse(c['reusable']);self.assertFalse(price_state(self.store)['printings'])
        urls=['https://www.cardmarket.com/de/Pokemon/Products/Singles/Base-Set/Growlithe-V1-BS28?language=3&minCondition=4&isFirstEd=Y',V1+'?utm_source=test']
        for url in urls:self.assertEqual(canonical_product_url(url),V1)
        self.assertIsNone(canonical_product_url('https://cardmarket.com.evil.invalid/en/Pokemon/Products/Singles/Base-Set/Growlithe'))
    def test_new_collector_confirmation_is_reused_on_a_different_edition_and_language(self):
        de=self.card();unlimited=next(p for p in de['printings'] if p['edition']=='unlimited');first=next(p for p in de['printings'] if p['edition']=='first_edition')
        self.save(self.select(unlimited['id']))
        c=self.select(first['id'])['products'][0];self.assertTrue(c['reusable']);self.assertEqual(c['reused_from']['printing_id'],unlimited['id'])
        en=self.card('en');enp=next(p for p in en['printings'] if p['edition']=='unlimited')
        c=self.select(enp['id'])['products'][0];self.assertTrue(c['reusable']);self.assertEqual(c['reused_from']['lang'],'de')
    def test_batch_keeps_ids_collection_metadata_pictures_and_separate_shadowless_product(self):
        de=self.card();p=de['printings'][0]
        self.store.save_printing(dict(p,entry_id=de['id'],printing_id=p['id'],confirmed=True,notes='Keep printing correction'))
        self.store.add_copies(dict(printing_id=p['id'],quantity=2,condition='excellent',price='4.56',currency='EUR',notes='Keep purchase note',misprint_notes='Duplicate for misprint collection',purchased_on='2026-10-30'))
        self.store.wish(dict(printing_id=p['id'],wanted=True))
        self.store.mutate('catalog/image',dict(entry_id=de['id'],printing_id=p['id'],bytes=base64.b64encode(b'GIF89a'+b'\0'*150).decode(),image_kind='representative',source_note='Keep picture override'))
        before=self.store.state();ids={q['id'] for e in self.store.entries().values() for q in e['printings']}
        with patch('urllib.request.urlopen') as net:result=self.save(self.select(p['id']),all_targets=True);net.assert_not_called()
        self.assertEqual(result['linked_count'],4);after=self.store.state()
        for table in ('copies','wishlist','entry_overrides','printing_image_overrides','image_overrides','manual_printings'):self.assertEqual(before[table],after[table])
        self.assertEqual(ids,{q['id'] for e in self.store.entries().values() for q in e['printings']})
        self.assertEqual(self.store.entry(de['id'])['printings'][0]['notes'],'Keep printing correction')
        prices=price_state(self.store)['printings'];self.assertEqual(len(prices),4)
        for q in self.card('en')['printings']:
            self.assertEqual(q['id'] in prices,q['layout']!='shadowless')
        snapshot=build_snapshot(self.store)
        for e in snapshot['entries']:
            for q in e['printings']:
                if q['id'] in prices:self.assertEqual(q['market_match']['canonical_url'],V1)
        restored=Collection(self.root,self.root/'restored');restored.restore(self.store.backup())
        for table in ('copies','wishlist','printing_overrides','printing_image_overrides'):self.assertEqual(after[table],restored.state()[table])
        # Provider caches are deliberately outside the personal backup; a refreshed cache supplies prices.
        shutil.copyfile(self.store.user_dir/'market_prices.json',restored.user_dir/'market_prices.json')
        self.assertEqual(price_state(restored)['printings'],prices)
    def test_shadowless_first_and_unstamped_share_v2_and_never_v1(self):
        en=self.card('en');p=next(q for q in en['printings'] if q['edition']=='first_edition')
        s=self.select(p['id']);self.assertEqual(s['query'],V2);self.assertEqual(s['products'][0]['product_id'],660200)
        self.assertEqual(len(s['products'][0]['related_printings']),2)
        result=self.save(s,pid=660200,all_targets=True);self.assertEqual(result['linked_count'],2)
        self.assertTrue(all(q.get('price_product_id')==660200 for q in self.card('en')['printings'] if q['layout']=='shadowless'))
        self.assertFalse(any(q.get('market_confirmed') for q in self.card()['printings']))
    def test_related_printing_context_is_checked_atomically(self):
        de=self.card();s=self.select(de['printings'][0]['id']);c=s['products'][0]
        other=next(t for t in c['related_printings'] if not t['current']);oe,op=next((e,q) for e in self.store.entries().values() for q in e['printings'] if q['id']==other['printing_id'])
        self.store.override(dict(entry_id=oe['id'],values=dict(number='28-altered'),source_note='Concurrent identity edit'))
        before=self.store.state()
        with self.assertRaises(ValidationError):self.save(s,all_targets=True)
        self.assertEqual(before,self.store.state());self.assertFalse(price_state(self.store)['printings'])
    def test_injected_different_product_target_is_rejected_before_any_write(self):
        de=self.card();s=self.select(de['printings'][0]['id']);v2=next(q for q in self.card('en')['printings'] if q['layout']=='shadowless')
        target=dict(printing_id=v2['id'],context_key=self.select(v2['id'])['context_key']);current=dict(printing_id=s['printing_id'],context_key=s['context_key'])
        before=self.store.state()
        with self.assertRaises(ValidationError):self.save(s,targets=[current,target])
        self.assertEqual(before,self.store.state())
    def test_conflicting_existing_match_is_not_overwritten_by_batch(self):
        de=self.card();self.save(self.select(de['printings'][0]['id']),pid=273723)
        first=next(p for p in de['printings'] if p['edition']=='first_edition')
        self.save(self.select(first['id'],query='900001'),pid=900001)
        s=self.select(de['printings'][0]['id']);c=s['products'][0]
        self.assertNotIn(first['id'],{t['printing_id'] for t in c['related_printings']})
    def test_same_listing_reuses_product_but_assigns_reverse_series_independently(self):
        for lang in ('en','de'):
            e=self.card(lang,'swsh1');self.store.save_card(dict(e,entry_id=e['id'],source_id=e['primary_source_id'],cardmarket_url=MODERN,source_note='Reviewed shared listing fixture'))
        en=self.card('en','swsh1');p=next(p for p in en['printings'] if p['finish']=='non_holo')
        s=self.select(p['id'],query='900001');self.save(s,pid=900001,listing_url=MODERN)
        de=self.card('de','swsh1');p=next(p for p in de['printings'] if p['finish']=='non_holo')
        s=self.select(p['id']);self.assertTrue(s['products'][0]['reusable']);result=self.save(s,pid=900001,all_targets=True)
        self.assertEqual(result['linked_count'],4)
        for e in [self.card('en','swsh1'),self.card('de','swsh1')]:
            for p in e['printings']:
                self.assertEqual(p['price_series'],'reverse' if p['finish']=='reverse_holo' else 'standard')
                self.assertEqual(result['prices']['printings'][p['id']]['trend'],0.77 if p['finish']=='reverse_holo' else 0.12)

    def test_batch_preserves_an_existing_related_manual_series_choice(self):
        for lang in ('en','de'):
            e=self.card(lang,'swsh1');self.store.save_card(dict(e,entry_id=e['id'],source_id=e['primary_source_id'],cardmarket_url=MODERN,source_note='Shared listing fixture'))
        en=self.card('en','swsh1');reverse=next(p for p in en['printings'] if p['finish']=='reverse_holo')
        self.save(self.select(reverse['id'],query='900001'),pid=900001,listing_url=MODERN,price_series='standard')
        normal=next(p for p in self.card('de','swsh1')['printings'] if p['finish']=='non_holo')
        selection=self.select(normal['id']);candidate=next(p for p in selection['products'] if p['product_id']==900001)
        self.assertEqual(next(t for t in candidate['related_printings'] if t['printing_id']==reverse['id'])['price_series'],'standard')
        self.save(selection,pid=900001,all_targets=True)
        self.assertEqual(next(p for p in self.card('en','swsh1')['printings'] if p['id']==reverse['id'])['price_series'],'standard')
        self.assertEqual(next(p for p in self.card('de','swsh1')['printings'] if p['finish']=='reverse_holo')['price_series'],'reverse')

if __name__=='__main__':unittest.main()
