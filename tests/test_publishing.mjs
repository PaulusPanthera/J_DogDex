import test from 'node:test';
import assert from 'node:assert/strict';
import {compareSources,sourceDateLabel,marketLink} from '../static/catalog.mjs';
import {priceMarkup,primaryPrice,pricePreview} from '../static/prices.mjs';
import {rarityAppearance,rarityMarkup,finishClass} from '../static/appearance.mjs';

test('source chronology uses regional dates and expansion sequence without adding precision',()=>{
 const exp={lang:'de',series:'Neo',era_order:1,name:'Expedition',release_date:'2003',sequence_hint:'2002-09-15'};
 const aqua={...exp,name:'Aquapolis',sequence_hint:'2003-01-15'};
 assert.ok(compareSources(exp,aqua)<0);assert.ok(compareSources(aqua,exp, -1)<0);
 assert.equal(sourceDateLabel(exp),'2003');
 assert.ok(compareSources({...exp,release_date:'2003-10-01'},{...aqua,release_date:'2003-02-01'})>0);
 assert.equal(sourceDateLabel({...exp,date_state:'provider_reference'}),'Regional date unconfirmed');
 assert.ok(compareSources(exp,{...exp,date_state:'provider_reference'})<0);
 assert.ok(compareSources({...aqua,sort_order:1},exp)<0);
});
test('market searches include set and meaningful collector numbering, while overrides win',()=>{
 const e={lang:'de',english:'Vulpix',market_name:'Vulpix',market_code:'SSH',market_number:'22',number:'22',set_name:'Schwert & Schild'};
 assert.equal(marketLink(e).query,'Vulpix (SSH 22)');
 assert.equal(marketLink({...e,market_code:'SIT',market_number:'017'}).query,'Vulpix (SIT 017)');
 const p={price_product_id:273763,market_confirmed:true};assert.equal(new URL(marketLink(e,p).url).searchParams.get('idProduct'),'273763');
 const manual='https://www.cardmarket.com/en/Pokemon/Products?idProduct=123';
 const manualLink=new URL(marketLink({...e,market_link_override:true,cardmarket_url:manual},p).url);assert.equal(manualLink.searchParams.get('idProduct'),'123');assert.equal(manualLink.searchParams.get('language'),'3');assert.equal(manualLink.searchParams.get('minCondition'),'3');
 assert.equal(new URL(marketLink({...e,market_link_override:true,cardmarket_url:manual},{...p,market_match:{method:'collector_product_search'}}).url).searchParams.get('idProduct'),'273763');
 assert.equal(marketLink(e,{market_candidate:{product_id:273763}}).exact,false);
});
test('compact guide retains context and selects one clearly labelled gallery price',()=>{
 const prices={updated_at:'2026-10-29T02:52:59+0100',printings:{one:{trend:1.25,avg30:2.4,series:'standard'}}};
 const html=priceMarkup(prices,'one',String);assert.match(html,/€1\.25/);assert.match(html,/30-day average/);assert.match(html,/2026-10-29/);assert.match(html,/languages, editions and conditions combined/);
 assert.equal(priceMarkup(prices,'missing',String),'');
 assert.equal(primaryPrice(prices,'one').key,'trend');assert.match(pricePreview(prices,'one',String),/€1\.25/);assert.doesNotMatch(pricePreview(prices,'one',String),/CM trend/);
 const p={printings:{zero:{trend:0,avg30:2},fallback:{trend:null,avg30:3,avg7:4},low:{low:0.99},invalid:{trend:NaN,avg30:-1}}};
 assert.equal(primaryPrice(p,'zero').value,0);assert.equal(primaryPrice(p,'fallback').key,'avg30');assert.equal(primaryPrice(p,'low').key,'low');assert.equal(primaryPrice(p,'invalid'),null);assert.match(pricePreview(p,'low',String),/from/);assert.equal(pricePreview(p,'unknown',String),'');
 assert.match(html,/<details class="market-guide"/);assert.doesNotMatch(html,/<details[^>]*\bopen\b/);assert.doesNotMatch(html,/Your purchase cost stays separate/);
});
test('rarity symbols respect regional codes, era and printing overrides',()=>{
 const modern={lang:'en',release:'sv03',rarity_code:'ultra_rare',rarity_state:'known',rarity_label:'Ultra Rare'};
 assert.equal(rarityAppearance({...modern,lang:'de',rarity_label:'Selten, ultraselten'}).label,'Ultra Rare');
 assert.equal(rarityAppearance(modern).count,2);assert.equal(rarityAppearance(modern).tone,'silver');
 assert.equal(rarityAppearance({...modern,release:'swsh12'}).symbol,'');
 assert.equal(rarityAppearance({...modern,rarity_code:'illustration_rare'}).tone,'gold');
 assert.equal(rarityAppearance({...modern,rarity_code:'special_illustration_rare'}).count,2);
 assert.equal(rarityAppearance({...modern,rarity_code:'hyper_rare'}).count,3);
 assert.equal(rarityAppearance({...modern,rarity_code:'double_rare'}).tone,'ink');
 assert.equal(rarityAppearance({lang:'ja',rarity_code:'SR',rarity_state:'known'}).short,'SR');assert.equal(rarityAppearance({lang:'ko',rarity_code:'RR',rarity_state:'known'}).symbol,'');
 assert.equal(rarityAppearance({e:modern,rarity_key:'not_printed',rarity_label:'No printed rarity'}).symbol,'');
 assert.match(rarityMarkup({...modern,rarity_code:'common'},String),/<circle/);assert.match(rarityMarkup({...modern,rarity_code:'uncommon'},String),/diamond|m8 1\.8/);
 assert.equal(finishClass({finish:'holo'}),'finish-holo');assert.equal(finishClass({finish:'reverse_holo'}),'finish-reverse');assert.equal(finishClass({finish:'non_holo'}),'finish-non-holo');
});
