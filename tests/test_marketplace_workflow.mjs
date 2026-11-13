import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {spawn} from 'node:child_process';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {filteredProductUrl,marketLink} from '../static/catalog.mjs';
const require=createRequire(import.meta.url),{JSDOM}=require(process.env.DOGDEX_QA_NODE_MODULES?path.join(process.env.DOGDEX_QA_NODE_MODULES,'jsdom'):'jsdom');
const root=fileURLToPath(new URL('../',import.meta.url));
const V1='https://www.cardmarket.com/en/Pokemon/Products/Singles/Base-Set/Growlithe-V1-BS28';
const V2='https://www.cardmarket.com/en/Pokemon/Products/Singles/Base-Set/Growlithe-V2-BS28';

test('offer links follow the printing and saved condition without claiming a filtered guide price',()=>{
 for(const [lang,language] of [['en','1'],['de','3'],['ja','7'],['ko','10']]){
  for(const edition of ['first_edition','unlimited','unstamped','not_applicable']){
   const url=new URL(filteredProductUrl(V1,{lang},{edition,finish:'non_holo'},'3'));
   assert.equal(url.searchParams.get('language'),language);assert.equal(url.searchParams.get('minCondition'),'3');
   assert.equal(url.searchParams.get('isFirstEd'),edition==='first_edition'?'Y':'N');assert.equal(url.searchParams.get('isReverseHolo'),'N');
  }
 }
 const reverse=new URL(filteredProductUrl(V1+'?language=1&minCondition=7&sellerCountry=7&isReverseHolo=N',{lang:'de'},{edition:'not_applicable',finish:'reverse_holo'},'2'));
 assert.equal(reverse.searchParams.get('language'),'3');assert.equal(reverse.searchParams.get('isReverseHolo'),'Y');assert.equal(reverse.searchParams.get('minCondition'),'2');assert.equal(reverse.searchParams.get('sellerCountry'),'7');
 assert.equal(new URL(filteredProductUrl(reverse.href,{lang:'en'},{finish:'holo'},'')).searchParams.has('minCondition'),false);
 for(const url of ['https://cardmarket.com.evil.invalid/en/Pokemon/Products?idProduct=1','https://www.cardmarket.com/en/Pokemon/Products/Search?searchString=Growlithe','javascript:alert(1)'])assert.equal(filteredProductUrl(url,{lang:'en'}),url);
 const linked=marketLink({lang:'en',name:'Growlithe',cardmarket_url:V1},{finish:'non_holo',edition:'first_edition',market_confirmed:true,price_product_id:660200,market_match:{method:'collector_product_search',canonical_url:V2}},{condition:'4'});
 assert.equal(new URL(linked.url).pathname,new URL(V2).pathname);assert.equal(new URL(linked.url).searchParams.get('isFirstEd'),'Y');assert.equal(linked.offers,true);
 const untrusted=marketLink({lang:'en',english:'Growlithe'},{market_confirmed:true,price_product_id:660200,market_match:{method:'collector_product_search',canonical_url:'javascript:alert(1)'}});assert.equal(new URL(untrusted.url).hostname,'www.cardmarket.com');assert.equal(new URL(untrusted.url).searchParams.get('idProduct'),'660200');
});

test('finder reuses a saved Growlithe product across selected EN/DE printings over real HTTP',{timeout:90000},async()=>{
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'dogdex-shared-market-')),app=path.join(temp,'app');fs.mkdirSync(path.join(app,'data'),{recursive:true});
 fs.cpSync(path.join(root,'static'),path.join(app,'static'),{recursive:true});
 const c=JSON.parse(fs.readFileSync(path.join(root,'data/catalog.json'),'utf8'));
 c.entries=c.entries.filter(e=>['en','de'].includes(e.lang)&&e.release==='base1'&&e.number==='28');c.retired_entries=[];c.retired_releases=[];
 fs.writeFileSync(path.join(app,'data/catalog.json'),JSON.stringify(c));
 const user=path.join(temp,'collection');fs.mkdirSync(user);
 const stamp=new Date().toISOString();fs.writeFileSync(path.join(user,'market_products.json'),JSON.stringify({format:'dogdex-cardmarket-products-1',source_created_at:stamp,fetched_at:stamp,products:{273723:{product_id:273723,name:'Growlithe',id_expansion:1},660200:{product_id:660200,name:'Growlithe',id_expansion:1},274198:{product_id:274198,name:"Blaine's Growlithe [Blaze]",id_expansion:6}}}));
 fs.writeFileSync(path.join(user,'market_prices.json'),JSON.stringify({format:'dogdex-cardmarket-prices-1',source_created_at:stamp,fetched_at:stamp,products:{273723:{trend:1.17,avg30:2.13},660200:{trend:14.39}}}));
 const bootstrap="import sys;sys.path.insert(0,sys.argv[1]);from app import make_server;s=make_server(sys.argv[2],port=0,user_dir=sys.argv[3]);print('http://127.0.0.1:'+str(s.server_port),flush=True);s.serve_forever()";
 const server=spawn('python3',['-c',bootstrap,root,app,user],{stdio:['ignore','pipe','pipe']});let dom,stderr='';server.stderr.on('data',b=>stderr+=b);
 try{
  const base=await new Promise((resolve,reject)=>{let out='';const timer=setTimeout(()=>reject(Error(stderr||'Server startup timeout')),10000);server.stdout.on('data',b=>{out+=b;const m=/http:\/\/127\.0\.0\.1:\d+/.exec(out);if(m){clearTimeout(timer);resolve(m[0]);}});server.once('error',reject);});
  dom=new JSDOM('<html><head><style>'+fs.readFileSync(path.join(root,'static/app.css'),'utf8')+'</style></head><body><div id="app"></div><dialog id="dialog"></dialog><div id="toast"></div></body></html>',{url:base,runScripts:'outside-only',pretendToBeVisual:true});const w=dom.window;
  w.scrollTo=()=>{};w.HTMLDialogElement.prototype.showModal=function(){this.open=true;};w.HTMLDialogElement.prototype.close=function(){this.open=false;};
  const requests=[];w.fetch=(url,options)=>{requests.push({url:String(url),body:options?.body&&JSON.parse(options.body)});return fetch(new URL(url,base),options);};
  const script=['set-symbols.mjs','source-ui.mjs','localization.mjs','catalog.mjs','prices.mjs','appearance.mjs','market-ui.mjs','editor-ui.mjs','app.js'].map(f=>fs.readFileSync(path.join(root,'static',f),'utf8').replace(/^import[^\n]*\n/gm,'').replace(/\bexport /g,'')).join('\n')+'\nwindow.qa={ui,render,detail,post,get entries(){return entries},get user(){return user}};';w.eval(script);
  const $=s=>w.document.querySelector(s),wait=async(fn,label)=>{for(let i=0;i<400;i++){if(fn())return;await new Promise(r=>setTimeout(r,10));}throw Error(label+' '+$('#dialog').textContent.slice(0,800));};
  const click=async s=>{assert.ok($(s),s);$(s).click();await new Promise(r=>setTimeout(r,20));};await wait(()=>w.qa.entries.length,'boot');
  let de=w.qa.entries.find(e=>e.lang==='de'),en=w.qa.entries.find(e=>e.lang==='en');const unlimited=de.printings.find(p=>p.edition==='unlimited'),first=de.printings.find(p=>p.edition==='first_edition'),shadowless=en.printings.find(p=>p.edition==='first_edition');
  await w.qa.post('copy/add',{printing_id:unlimited.id,quantity:2,condition:'excellent',price:'0',currency:'EUR',notes:'Gift kept',misprint_notes:'Collected duplicate',purchased_on:'2026-10-30'});await w.qa.post('wishlist',{printing_id:first.id,wanted:true});
  const copies=JSON.stringify(w.qa.user.copies),wishes=JSON.stringify(w.qa.user.wishlist),ids=w.qa.entries.flatMap(e=>e.printings.map(p=>p.id));
  const seed=await w.qa.post('market/search',{printing_id:unlimited.id,cache_only:true});const seedProduct=seed.products.find(p=>p.product_id===273723);
  await w.qa.post('market/confirm',{printing_id:unlimited.id,context_key:seed.context_key,product_id:273723,listing_url:seedProduct.listing_url,price_series:'standard',confirmed:true});
  w.qa.ui.lang='de';w.qa.render();w.qa.detail(first.id);
  let link=new URL($('.market-link').href);assert.equal(link.pathname,new URL(V1).pathname);assert.equal(link.searchParams.get('language'),'3');assert.equal(link.searchParams.get('isFirstEd'),'Y');assert.equal(link.searchParams.get('minCondition'),'3');
  const condition=$('#market-condition');condition.value='4';condition.dispatchEvent(new w.Event('change',{bubbles:true}));assert.equal(new URL($('.market-link').href).searchParams.get('minCondition'),'4');assert.equal(JSON.parse(w.localStorage.getItem('dogdex-view-v1')).marketCondition,'4');assert.equal(w.document.activeElement.id,'market-condition');
  await click('[data-action="market-find"]');await wait(()=>$('[data-action="market-select"][data-id="273723"]'),'reuse candidate');
  assert.equal($('#market-query').value,V1);assert.equal($('.market-candidate').querySelector('[data-action="market-select"]').dataset.id,'273723');assert.match($('.market-candidate').textContent,/Confirmed related printing/);assert.match($('.market-candidate button').textContent,/Reuse product/);
  assert.equal(new URL($('.finder-existing').href).searchParams.get('isFirstEd'),'Y');assert.ok($('.finder-other'));assert.equal($('.finder-other').open,false);
  await click('[data-action="market-select"][data-id="273723"]');let form=$('#market-confirm-form');assert.equal(form.querySelectorAll('[name="printing_target"]:checked').length,4);assert.doesNotMatch($('.market-related').textContent,/Shadowless/);
  form.elements.confirmed.checked=true;form.dispatchEvent(new w.Event('submit',{bubbles:true,cancelable:true}));await wait(()=>$('#dialog').dataset.kind==='detail'&&$('.market-primary')?.textContent.includes('1.17'),'shared save');
  const save=requests.filter(r=>r.url.endsWith('market/confirm')).at(-1).body;assert.equal(save.targets.length,4);assert.equal(JSON.stringify(w.qa.user.copies),copies);assert.equal(JSON.stringify(w.qa.user.wishlist),wishes);assert.deepEqual(w.qa.entries.flatMap(e=>e.printings.map(p=>p.id)),ids);
  assert.match($('.market-heading').textContent,/guide/);assert.match($('.market-guide').title,/editions/);
  const amount=$('.market-primary').textContent;$('#market-condition').value='2';$('#market-condition').dispatchEvent(new w.Event('change',{bubbles:true}));assert.equal($('.market-primary').textContent,amount);assert.equal(new URL($('.market-link').href).searchParams.get('minCondition'),'2');
  const firstTile=[...w.document.querySelectorAll('.card')].find(t=>t.querySelector('.card-visual')?.dataset.id===first.id);assert.equal(firstTile.querySelector('.card-price .price-scope'),null);assert.equal(firstTile.querySelector('.card-price').textContent,'€1.17');assert.match(firstTile.querySelector('.card-price').title,/editions and conditions combined/);
  w.qa.detail(shadowless.id);link=new URL($('.market-link').href);assert.equal(link.pathname,new URL(V2).pathname);assert.equal(link.searchParams.get('language'),'1');assert.equal(link.searchParams.get('isFirstEd'),'Y');
  await click('[data-action="market-find"]');await wait(()=>$('[data-action="market-select"][data-id="660200"]'),'V2 reference');assert.equal($('#market-query').value,V2);await click('[data-action="market-select"][data-id="660200"]');assert.equal($('#market-confirm-form').querySelectorAll('[name="printing_target"]:checked').length,2);assert.doesNotMatch($('.market-related').textContent,/German/);
  assert.equal(JSON.stringify(w.qa.user.copies),copies);
 }finally{dom?.window.close();server.kill('SIGTERM');await new Promise(resolve=>server.once('close',resolve));fs.rmSync(temp,{recursive:true,force:true});}
});
