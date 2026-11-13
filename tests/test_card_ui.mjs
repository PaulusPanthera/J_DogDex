import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
const require=createRequire(import.meta.url);
const {JSDOM}=require(process.env.DOGDEX_QA_NODE_MODULES?path.join(process.env.DOGDEX_QA_NODE_MODULES,'jsdom'):'jsdom');
const root=fileURLToPath(new URL('../',import.meta.url));

test('compact captions preserve exact printing selection, colour, copies and indexed search',{timeout:30000},async()=>{
 const code="import sys,json,tempfile;from pathlib import Path;sys.path.insert(0,sys.argv[1]);from dogdex.collector import Collection;t=tempfile.TemporaryDirectory();s=Collection(Path(sys.argv[1]),t.name);print(json.dumps(dict(catalog=s.catalog,view=s.editor_view(),state=s.state())))";
 const fixture=JSON.parse(execFileSync('python3',['-c',code,root],{maxBuffer:150000000}));
 const base=fixture.view.entries.find(e=>e.lang==='en'&&e.release==='base1'&&e.number==='68');
 const unlimited=base.printings.find(p=>p.edition==='unlimited'&&p.print_state==='standard');
 const first=base.printings.find(p=>p.edition==='first_edition');assert.ok(unlimited&&first);
 fixture.prices={updated_at:'2026-10-30T00:00:00Z',printings:{[unlimited.id]:{trend:4.03,avg30:3.81,series:'standard'},[first.id]:{trend:null,avg30:12.50,series:'standard'}}};
 fixture.state.copies.push({id:'retained-copy-1',printing_id:unlimited.id,condition:'near_mint',price_minor:1999,currency:'EUR',notes:'Preserved note',purchased_on:'2026-10-29'}, {id:'retained-copy-2',printing_id:unlimited.id,condition:'good',price_minor:123,currency:'EUR',notes:''});
 const html='<html><head><style>'+fs.readFileSync(path.join(root,'static/app.css'),'utf8')+'</style></head><body><div id="app"></div><dialog id="dialog"></dialog><div id="toast"></div></body></html>';
 const dom=new JSDOM(html,{url:'http://localhost/',runScripts:'outside-only',pretendToBeVisual:true});const w=dom.window;
 w.scrollTo=()=>{};w.HTMLDialogElement.prototype.showModal=function(){this.open=true;};w.HTMLDialogElement.prototype.close=function(){this.open=false;};
 let mutations=0;const wishlistRequests=[];w.fetch=async(url,options)=>{if(options?.method==='POST'){mutations++;if(url==='/api/wishlist'){const data=JSON.parse(options.body);wishlistRequests.push(data);fixture.state.wishlist=fixture.state.wishlist.filter(w=>w.printing_id!==data.printing_id);if(data.wanted)fixture.state.wishlist.push({printing_id:data.printing_id});}}return {ok:true,json:async()=>String(url).includes('catalog.json')?fixture.catalog:{state:fixture.state,view:fixture.view,prices:fixture.prices,token:'qa'}};};
 const script=['set-symbols.mjs','source-ui.mjs','localization.mjs','catalog.mjs','prices.mjs','appearance.mjs','market-ui.mjs','editor-ui.mjs','app.js'].map(f=>fs.readFileSync(path.join(root,'static',f),'utf8').replace(/^import[^\n]*\n/gm,'').replace(/\bexport /g,'')).join('\n')+'\nwindow.qa={ui,render,detail,rebuild,queryMatches,get rows(){return rows},get entries(){return entries}};';w.eval(script);
 for(let i=0;i<100&&!w.document.querySelector('.card');i++)await new Promise(r=>setTimeout(r,10));
 const cameoCredit=w.document.querySelector('.artwork-credit');assert.ok(cameoCredit);assert.equal(cameoCredit.parentElement.className,'card-meta');assert.equal(w.document.querySelector('.card-bottom'),null);assert.equal(w.document.querySelector('.wish-btn'),null);assert.equal(w.document.querySelector('.count-badge'),null);
 const neo=fixture.view.entries.find(e=>e.lang==='de'&&e.release==='neo4'&&e.number==='91');assert.ok(neo);
 w.qa.ui.lang='de';w.qa.ui.pokemon='37';w.qa.ui.q='Neo Destiny';w.qa.render();
 // The German set title can be localized; directly test the actual existing row.
 w.qa.ui.q='91';w.qa.render();const tiles=[...w.document.querySelectorAll('.card')];
 const neoTile=tiles.find(el=>el.querySelector('.card-visual')?.getAttribute('data-id')===neo.printings[0].id);assert.ok(neoTile);
 assert.equal(neoTile.querySelector('.card-name').textContent,'Vulpix');assert.equal(neoTile.querySelector('.collector-number').textContent,'#91');assert.equal(neoTile.querySelector('.card-date').textContent,'2002');assert.match(neoTile.querySelector('.card-date').title,/Jul 2002/);assert.ok(neoTile.querySelector('.card-source .set-symbol'));assert.equal(neoTile.querySelector('.card-date').previousElementSibling.className,'card-set');assert.ok(neoTile.querySelector('.card-classification>.add'));assert.equal(neoTile.querySelector('.card-title .set-symbol'),null);
 assert.ok(neoTile.querySelector('.printing-chip'));assert.ok(neoTile.querySelector('.rarity-symbols svg'));assert.equal(neoTile.querySelector('.rarity-badge').dataset.rarity,'common');assert.equal(w.getComputedStyle(neoTile.querySelector('.card-visual img')).filter,'grayscale(1)');
 w.qa.ui.lang='en';w.qa.ui.q='';w.qa.render();const ownedTile=[...w.document.querySelectorAll('.card')].find(el=>el.querySelector('.card-visual')?.dataset.id===unlimited.id);assert.ok(ownedTile);
 assert.ok(ownedTile.querySelector('.card-heading>.card-price'));assert.match(ownedTile.getAttribute('aria-label'),/2 copies collected/);assert.equal(ownedTile.querySelector('.count-badge'),null);assert.equal(ownedTile.querySelector('.wish-btn'),null);assert.notEqual(w.getComputedStyle(ownedTile).backgroundColor,w.getComputedStyle(neoTile).backgroundColor);assert.equal(ownedTile.querySelector('.card-price strong').textContent,'€4.03');assert.equal(ownedTile.querySelector('.card-price').dataset.priceKind,'trend');assert.ok(ownedTile.querySelector('.finish-non-holo'));assert.equal(w.getComputedStyle(ownedTile.querySelector('.card-visual img')).filter,'');
 w.qa.detail(first.id);const dialog=w.document.querySelector('#dialog');assert.equal(dialog.querySelector('.printing-option').dataset.id,first.id);assert.equal(dialog.querySelector('.printing-option[aria-pressed="true"]').dataset.id,first.id);
 assert.match(dialog.querySelector('#dialog-title').textContent,/Vulpix #68/);assert.equal(dialog.querySelector('.detail-image').getAttribute('loading'),'eager');assert.equal(w.getComputedStyle(dialog.querySelector('.detail-image')).filter,'none');assert.equal(dialog.getAttribute('aria-labelledby'),'dialog-title');
 assert.equal(dialog.querySelector('.variant-owned')?.textContent,'×2');assert.match(dialog.textContent,/Not collected/);assert.match(dialog.querySelector('.market-guide summary').textContent,/€12\.50/);assert.equal(dialog.querySelector('.market-guide').open,false);
 dialog.querySelector(`.printing-option[data-id="${unlimited.id}"]`).click();await new Promise(r=>setTimeout(r,0));
 assert.equal(dialog.querySelector('.printing-option[aria-pressed="true"]').dataset.id,unlimited.id);assert.equal(dialog.querySelector('.copy-count').textContent,'2');assert.equal(dialog.querySelector('.copy-cost strong').textContent,'€19.99');assert.match(dialog.textContent,/Preserved note/);assert.equal(dialog.querySelector('[data-copy-id="retained-copy-1"] time').textContent,'29 Oct 2026');assert.equal(mutations,0);
 assert.equal(dialog.querySelectorAll('.copy-item').length,2);assert.equal(dialog.querySelector('[data-action="add"]').textContent.trim(),'Add copy');assert.equal(dialog.querySelector('.primary'),null);assert.doesNotMatch(dialog.textContent,/Shared reference|edition or finish may differ|Your purchase cost stays separate/);assert.match(dialog.querySelector('.market-guide summary').textContent,/€4\.03/);
 dialog.querySelector('[data-action="edit-copy"]').click();await new Promise(r=>setTimeout(r,0));assert.equal(dialog.querySelector('[name="price"]').value,'19.99');assert.equal(dialog.querySelector('[name="condition"]').value,'near_mint');assert.equal(mutations,0);w.qa.detail(unlimited.id);
 // Real 1.8.6 records: patterned and ordinary reverses stay distinct in gallery,
 // details and the existing exact EN/DE language switch.
 const wf=fixture.view.entries.find(e=>e.lang==='de'&&e.release==='sv10.5w'&&e.number==='061');
 w.qa.ui.lang='de';w.qa.ui.pokemon=String(wf.dex);w.qa.ui.q='Weiße Flammen';w.qa.render();
 for(const pattern of ['poke_ball','master_ball']){
  const p=wf.printings.find(p=>p.pattern===pattern),tile=[...w.document.querySelectorAll('.card')].find(el=>el.querySelector('.card-visual')?.dataset.id===p.id);assert.ok(tile);
  assert.match(tile.querySelector('.card-printing')?.textContent||tile.textContent,pattern==='poke_ball'?/Poké Ball/:/Master Ball/);
  assert.equal(tile.querySelector('.card-date').textContent,'2025');assert.match(tile.querySelector('.card-date').title,/18 Jul 2025/);assert.equal(tile.querySelector('.rarity-badge').dataset.rarity,'common');
 }
 const master=wf.printings.find(p=>p.pattern==='master_ball');w.qa.detail(master.id);assert.match(dialog.querySelector('.printing-option.active').textContent,/Master Ball/);
 assert.equal(w.getComputedStyle(dialog.querySelector('.detail-image')).filter,'none');
 dialog.querySelector('[data-action="language"][data-lang="en"]').click();await new Promise(r=>setTimeout(r,0));
 assert.match(dialog.querySelector('.printing-option.active').textContent,/Master Ball/);assert.match(dialog.textContent,/18 Jul 2025/);
 dialog.querySelector('[data-action="language"][data-lang="de"]').click();await new Promise(r=>setTimeout(r,0));
 assert.match(dialog.querySelector('.printing-option.active').textContent,/Master Ball/);assert.match(dialog.textContent,/Weiße Flammen/);assert.equal(mutations,0);
 // Compare the search cache with the prior field-by-field semantics across all rows.
 const roster=new Map(fixture.catalog.roster.map(r=>[r.dex,r.name]));
 for(const word of ['world championships 2018','vulpix','alolan','trainer kit','cosmos','neo destiny']){
  w.qa.ui.q=word;
  for(const row of w.qa.rows){const e=row.e,dexes=[...new Set([...(e.subject_dex||[e.dex]),...(e.cameo_dex||[])].filter(Number.isInteger))];const expected=[e.name,e.english,e.number,e.set_name,e.release,...(e.identity_aliases||[]),String(e.dex),...dexes.map(d=>roster.get(d)),...e.sources.map(s=>s.name),...(row.sources||[]).map(s=>s.name),row.label||''].join(' ').toLowerCase().includes(word);assert.equal(w.qa.queryMatches(e,row),expected,row.id+' '+word);}
 }
 // The wishlist control is printing-specific, remains keyboard-focused after save,
 // and never changes owned copies or their purchase metadata.
 const copiesBefore=JSON.stringify(fixture.state.copies);w.qa.detail(first.id);
 assert.equal(dialog.querySelector('.detail-image-wrap button'),null);
 assert.equal(dialog.querySelector('.printing-section .detail-section-heading .detail-wish').dataset.id,first.id);
 assert.equal(dialog.querySelector('.detail-wish').getAttribute('aria-pressed'),'false');
 dialog.querySelector('.detail-wish').click();await new Promise(r=>setTimeout(r,10));
 assert.deepEqual(wishlistRequests,[{printing_id:first.id,wanted:true}]);assert.equal(dialog.querySelector('.detail-wish').getAttribute('aria-pressed'),'true');assert.equal(w.document.activeElement,dialog.querySelector('.detail-wish'));
 dialog.querySelector(`.printing-option[data-id="${unlimited.id}"]`).click();await new Promise(r=>setTimeout(r,0));assert.equal(dialog.querySelector('.detail-wish').getAttribute('aria-pressed'),'false');assert.equal(dialog.querySelector('.detail-wish').dataset.id,unlimited.id);
 dialog.querySelector(`.printing-option[data-id="${first.id}"]`).click();await new Promise(r=>setTimeout(r,0));assert.equal(dialog.querySelector('.detail-wish').getAttribute('aria-pressed'),'true');
 dialog.querySelector('.detail-wish').click();await new Promise(r=>setTimeout(r,10));assert.deepEqual(wishlistRequests,[{printing_id:first.id,wanted:true},{printing_id:first.id,wanted:false}]);assert.equal(dialog.querySelector('.detail-wish').getAttribute('aria-pressed'),'false');assert.equal(JSON.stringify(fixture.state.copies),copiesBefore);assert.equal(mutations,2);
 const preserved=fixture.state.copies.map(c=>c.id);assert.deepEqual(preserved,['retained-copy-1','retained-copy-2']);
 // The set name, symbol and year remain one working source-navigation target.
 dialog.querySelector('[data-action="close"]').click();w.qa.ui.lang='en';w.qa.ui.pokemon='37';w.qa.ui.q='';w.document.querySelector('#nav-all').click();await new Promise(r=>setTimeout(r,0));
 const sourceTile=[...w.document.querySelectorAll('.card')].find(el=>el.querySelector('.card-visual')?.dataset.id===unlimited.id);assert.ok(sourceTile);sourceTile.querySelector('.card-set').click();await new Promise(r=>setTimeout(r,0));
 assert.equal(w.qa.ui.view,'sources');assert.match(w.qa.ui.source.name,/Base Set/);assert.equal(JSON.stringify(fixture.state.copies),copiesBefore);assert.equal(mutations,2);
 if(process.env.DOGDEX_UI_PREVIEW_DIR){
  const out=process.env.DOGDEX_UI_PREVIEW_DIR;fs.mkdirSync(out,{recursive:true});fixture.state.copies.length=0;w.qa.rebuild();
  const snapshot=()=>dom.serialize().replaceAll('src="/images/','src="../ui181_work/DogDex/data/images/').replaceAll('src="/flags/','src="../ui181_work/DogDex/static/flags/');
  w.document.querySelector('#dialog').open=false;w.qa.ui.q='';w.qa.ui.lang='en';w.qa.ui.view='all';w.qa.ui.pokemon='';w.qa.ui.limit=16;w.qa.render();
  fs.writeFileSync(path.join(out,'overview.html'),snapshot());
  w.qa.detail(first.id);w.document.querySelector('#dialog').removeAttribute('open');
  fs.writeFileSync(path.join(out,'detail.html'),snapshot().replace('</body>','<script>document.querySelector("#dialog").showModal();</script></body>'));
 }
 w.close();
});
