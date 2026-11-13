import test from 'node:test';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const require=createRequire(import.meta.url);
const {JSDOM}=require(process.env.DOGDEX_QA_NODE_MODULES?path.join(process.env.DOGDEX_QA_NODE_MODULES,'jsdom'):'jsdom');
const ROOT=fileURLToPath(new URL('../',import.meta.url));
import fs from 'node:fs';
import assert from 'node:assert/strict';
test('direct catalog editor, scope, images and backup through DOM and real HTTP',{timeout:120000},async()=>{
const {spawn}=await import('node:child_process');const os=await import('node:os');
const tempDir=fs.mkdtempSync(path.join(os.tmpdir(),'dogdex-dom-'));
const server=spawn('python3',[path.join(ROOT,'app.py'),'--port','0','--no-browser','--user-dir',tempDir],{stdio:['ignore','pipe','pipe']});
let logs='';server.stderr.on('data',b=>logs+=b.toString());
try{
const base=await new Promise((resolve,reject)=>{let text='';const timer=setTimeout(()=>reject(Error('Local QA server did not start: '+logs)),20000);server.stdout.on('data',b=>{text+=b.toString();const match=/http:\/\/127\.0\.0\.1:\d+/.exec(text);if(match){clearTimeout(timer);resolve(match[0]);}});server.once('error',reject);});
const dom=new JSDOM('<!doctype html><html><body><main id="app"></main><dialog id="dialog"></dialog><div id="toast"></div></body></html>',{url:base,runScripts:'outside-only',pretendToBeVisual:true});
const w=dom.window;let lastError=null;w.console.error=(...a)=>{lastError=a.join(' ');};w.scrollTo=()=>{};w.confirm=()=>true;
w.fetch=(url,options)=>fetch(new URL(url,base),options);
w.HTMLDialogElement.prototype.showModal=function(){this.open=true;};w.HTMLDialogElement.prototype.close=function(){this.open=false;this.dispatchEvent(new w.Event('close'));};
w.File.prototype.arrayBuffer=function(){return new Promise((resolve,reject)=>{const r=new w.FileReader();r.onload=()=>resolve(r.result);r.onerror=reject;r.readAsArrayBuffer(this);});};
let script=['set-symbols.mjs','source-ui.mjs','localization.mjs','catalog.mjs','prices.mjs','appearance.mjs','market-ui.mjs','editor-ui.mjs','app.js'].map(f=>fs.readFileSync(path.join(ROOT,'static',f),'utf8').replace(/^import[^\n]*\n/gm,'').replace(/\bexport /g,'')).join('\n');
script+='\nwindow.__qa={ui,get entries(){return entries},get rows(){return rows},get sources(){return sourceRecords},get user(){return user},get catalog(){return catalog},get serverView(){return serverView},render,editor,detail,post,filteredRows};';w.eval(script);
const $=s=>w.document.querySelector(s);const wait=async(fn,message)=>{const start=Date.now();while(Date.now()-start<15000){if(fn())return;await new Promise(r=>setTimeout(r,25));}throw Error(message+'; error='+lastError+'; form='+($('.form-error')?.textContent||'')+'; app='+$('#app').textContent.slice(0,600));};
const click=async selector=>{const b=$(selector);assert.ok(b,'Missing '+selector);b.click();await new Promise(r=>setTimeout(r,20));};
const change=(form,name,value)=>{const e=form.elements[name];assert.ok(e,'Missing field '+name);e.value=value;e.dispatchEvent(new w.Event('change',{bubbles:true}));};
const submit=form=>form.dispatchEvent(new w.Event('submit',{bubbles:true,cancelable:true}));
await wait(()=>w.__qa.entries.length>0,'boot');assert.equal(w.__qa.entries.length,w.__qa.catalog.entries.length);assert.ok(!w.__qa.catalog.roster.some(r=>[133,403].includes(r.dex)));
// Incomplete identities are actual searchable tiles, with evidence and no invented target.
const provisional=w.__qa.entries.find(e=>e.lang==='de'&&e.identity_status==='provisional'&&!e.printings.length);
w.__qa.ui.lang='de';w.__qa.ui.q=provisional.name;w.__qa.ui.pending=true;w.__qa.render();
assert.ok(w.__qa.filteredRows(true,true).some(r=>r.e.id===provisional.id&&r.research));
w.__qa.ui.pending=false;assert.ok(!w.__qa.filteredRows(true,true).some(r=>r.e.id===provisional.id));
w.__qa.editor.card(provisional.id,'evidence');assert.ok($('.evidence-list a[href^="https://"]'));assert.ok($('#dialog').textContent.includes('Provisional'));
await click('[data-action="close"]');w.__qa.ui.q='';w.__qa.ui.lang='en';w.__qa.ui.pending=true;w.__qa.render();
// JA provisional identities and documented KO identities without a known finish
// use the same visible research controls and evidence editor as western claims.
const asiaAdded=new Set(w.__qa.catalog.asia_research.added_entry_ids);
for(const lang of ['ja','ko']){
 const card=w.__qa.entries.find(e=>e.lang===lang&&asiaAdded.has(e.id)&&!e.printings.length);
 assert.ok(card);w.__qa.ui.lang=lang;w.__qa.ui.q=card.name;w.__qa.ui.pending=true;w.__qa.render();
 assert.ok(w.__qa.filteredRows(true,true).some(r=>r.e.id===card.id&&r.research));
 w.__qa.ui.pending=false;assert.ok(!w.__qa.filteredRows(true,true).some(r=>r.e.id===card.id));
 w.__qa.editor.card(card.id,'evidence');assert.ok($('.evidence-list a[href^="https://"]'));
 await click('[data-action="close"]');
}
w.__qa.ui.q='';w.__qa.ui.lang='en';w.__qa.ui.pending=true;w.__qa.render();
// Navigate the same controls the collector uses, including legacy-filter reset.
assert.equal(w.document.querySelectorAll('#species-list .browse-item').length,41);
assert.equal($('#pokemon'),null);assert.equal($('.page-heading'),null);assert.equal($('.chips'),null);
const overlap=w.__qa.entries.find(e=>e.lang==='en'&&e.subject_dex.length&&e.cameo_dex.length);
await click('#browse-cameo');assert.ok(w.__qa.filteredRows(true,true).length);assert.ok(w.__qa.filteredRows(true,true).every(r=>!r.e.subject_dex.length));assert.ok(!w.__qa.filteredRows(true,true).some(r=>r.e.id===overlap.id));
await click('#browse-'+overlap.subject_dex[0]);assert.equal(w.__qa.ui.category,'cameo');assert.ok(w.__qa.filteredRows(true,true).every(r=>r.e.cameo_dex.includes(overlap.subject_dex[0])));await click('#browse-cameo');assert.ok(w.__qa.filteredRows(true,true).some(r=>r.e.id===overlap.id));assert.ok(w.__qa.filteredRows(true,true).every(r=>r.e.subject_dex.includes(overlap.subject_dex[0])));
await click('#browse-all');await click('#browse-jumbo');assert.ok(w.__qa.filteredRows().length);assert.ok(w.__qa.filteredRows().every(r=>r.size==='oversized'||r.material==='metal'));
await click('#browse-jumbo');await click('#browse-37');await click('#nav-sources');assert.ok(w.document.querySelectorAll('.source-card').length);assert.ok(w.__qa.filteredRows().every(r=>r.e.subject_dex.includes(37)));
await click('#nav-health');assert.ok(w.document.querySelectorAll('.editor-card-row').length);assert.ok([...w.document.querySelectorAll('.editor-card-row [data-action="review"]')].every(b=>w.__qa.entries.find(e=>e.id===b.dataset.id).subject_dex.includes(37)));
await click('[data-action="health-tab"][data-tab="sets"]');const vulpixSources=new Set(w.__qa.entries.filter(e=>e.lang==='en'&&e.subject_dex.includes(37)).flatMap(e=>[...e.sources,...e.printings.flatMap(p=>p.sources||[])].map(s=>s.id)));assert.ok([...w.document.querySelectorAll('.editor-source-row [data-action="edit-source"]')].every(b=>vulpixSources.has(b.dataset.id)));
await click('[data-action="clear-filters"]');await click('#nav-all');const select=$('#rarity');select.value='double_rare';select.dispatchEvent(new w.Event('change',{bubbles:true}));assert.ok($('.filter-pill').textContent.includes('Double Rare'));assert.ok(w.__qa.filteredRows().length);
await click('[data-action="clear-filter"][data-filter="rarity"]');assert.equal($('#rarity').value,'');
$('#search').value='no-such-card-qa';$('#search').dispatchEvent(new w.Event('input',{bubbles:true}));await wait(()=>$('.empty'),'filtered empty state');await click('[data-action="clear-filters"]');assert.equal($('#search').value,'');assert.ok($('.card-grid'));
w.__qa.ui.view='health';w.__qa.render();assert.equal(w.document.querySelectorAll('.health-tabs button').length,3);
await click('[data-action="health-tab"][data-tab="sets"]');await click('[data-action="new-source"]');let f=$('#source-editor-form');change(f,'name','QA source 1.2');change(f,'kind','deck');change(f,'release','QA12');change(f,'release_date','2021-03-15');submit(f);
await wait(()=>w.__qa.sources.some(s=>s.name==='QA source 1.2'),'source create');const sid=w.__qa.sources.find(s=>s.name==='QA source 1.2').id;
await click('[data-action="health-tab"][data-tab="cards"]');await click('[data-action="new-card"]');f=$('#card-editor-form');change(f,'dex','37');change(f,'name','QA Vulpix');change(f,'number','7');change(f,'source_id',sid);change(f,'rarity_code','double_rare');change(f,'art_style','standard');change(f,'initial_finish','holo');f.elements.initial_confirmed.checked=true;
assert.ok(f.reportValidity(),'New card form should validate with an existing source.');submit(f);
await wait(()=>w.__qa.entries.some(e=>e.name==='QA Vulpix'),'card create');let e=w.__qa.entries.find(e=>e.name==='QA Vulpix');const eid=e.id,pid=e.printings[0].id;assert.equal(e.release_date,'2021-03-15');assert.equal(e.rarity_key,'double_rare');
await click('[data-action="close"]');w.__qa.ui.view='all';w.__qa.ui.rarity='double_rare';w.__qa.render();assert.ok(w.__qa.filteredRows(true,true).every(r=>r.rarity_key==='double_rare'||r.e.rarity_key==='double_rare'));assert.ok($('#rarity').textContent.includes('Double Rare'));
w.__qa.detail(pid);await click('[data-action="add"]');f=$('#copy-form');change(f,'quantity','2');change(f,'price','9.50');change(f,'condition','near_mint');submit(f);await wait(()=>w.__qa.user.copies.some(c=>c.printing_id===pid),'copies saved');assert.equal(w.__qa.user.copies.filter(c=>c.printing_id===pid).length,2);
await click('[data-action="close"]');await click('#nav-collection');assert.ok($('.results-line').textContent.includes('2 physical copies'));assert.ok($('.results-line').textContent.includes('€19.00'));w.__qa.detail(pid);
await click('[data-action="review"]');await click('[data-action="editor-card-tab"][data-tab="printings"]');await click('[data-action="edit-printing"]');f=$('#printing-editor-form');change(f,'finish','reverse_holo');change(f,'pattern','__custom');change(f,'custom_pattern','cosmos');change(f,'stamps','QA stamp');f.elements.confirmed.checked=true;submit(f);await wait(()=>w.__qa.entries.find(e=>e.id===eid)?.printings[0].finish==='reverse_holo','printing edit');assert.equal(w.__qa.entries.find(e=>e.id===eid).printings[0].id,pid);
await click('[data-action="editor-card-tab"][data-tab="picture"]');f=$('#picture-editor-form');change(f,'printing_id',pid);f=$('#picture-editor-form');const asset=w.__qa.catalog.used_images[0],bytes=fs.readFileSync(path.join(ROOT,'data/images',asset));const file=new w.File([bytes],'reference.webp',{type:'image/webp'});Object.defineProperty(f.elements.picture,'files',{value:[file],configurable:true});f.elements.picture.required=false;submit(f);await wait(()=>w.__qa.user.printing_image_overrides.some(r=>r.printing_id===pid),'picture save');
const savedImage=w.__qa.entries.find(e=>e.id===eid).printings[0].image;assert.ok(savedImage.startsWith('/user-images/'));const imageResponse=await fetch(base+savedImage);assert.equal(imageResponse.status,200);assert.equal((await imageResponse.arrayBuffer()).byteLength,bytes.length);
await click('[data-action="close"]');w.__qa.ui.view='health';w.__qa.ui.health='sets';w.__qa.ui.q='QA source';w.__qa.render();await click('[data-action="edit-source"]');f=$('#source-editor-form');change(f,'name','QA source renamed');change(f,'release_date','2022-04');submit(f);await wait(()=>w.__qa.entries.find(e=>e.id===eid)?.set_name==='QA source renamed','source rename');assert.equal(w.__qa.entries.find(e=>e.id===eid).release_date,'2022-04');
await click('[data-action="remove-source"]');await wait(()=>!w.__qa.entries.some(e=>e.id===eid),'source removal cascade');assert.equal(w.__qa.user.copies.filter(c=>c.printing_id===pid).length,2);
await click('[data-action="editor-utilities"]');await click(`[data-action="restore-catalog-item"][data-id="${sid}"]`);await wait(()=>w.__qa.entries.some(e=>e.id===eid),'source restore');
await click('[data-action="close"]');w.__qa.editor.card(eid);await click('[data-action="remove-entry"]');await wait(()=>!w.__qa.entries.some(e=>e.id===eid),'card removal');await click('[data-action="editor-utilities"]');await click(`[data-action="restore-catalog-item"][data-id="${eid}"]`);await wait(()=>w.__qa.entries.some(e=>e.id===eid),'card restore');
// Source covers use the same real upload route and survive collection restore.
w.__qa.editor.source(sid);f=$('#source-picture-form');assert.ok(f);Object.defineProperty(f.elements.picture,'files',{value:[file],configurable:true});f.elements.picture.required=false;submit(f);await wait(()=>w.__qa.user.source_image_overrides.some(r=>r.source_id===sid),'source cover save');
const coverImage=w.__qa.sources.find(s=>s.id===sid).image;assert.ok(coverImage.startsWith('/user-images/'));assert.equal((await fetch(base+coverImage)).status,200);
const backupResponse=await fetch(base+'/api/backup');assert.equal(backupResponse.status,200);const backup=await backupResponse.arrayBuffer();assert.ok(backup.byteLength>1000);
await w.__qa.post('copy/remove',{id:w.__qa.user.copies.find(c=>c.printing_id===pid).id});
assert.equal(w.__qa.user.copies.filter(c=>c.printing_id===pid).length,1);
w.__qa.editor.utilities();const restore=$('#restore-file');Object.defineProperty(restore,'files',{value:[new w.File([backup],'backup.zip',{type:'application/zip'})],configurable:true});restore.dispatchEvent(new w.Event('change',{bubbles:true}));await wait(()=>w.__qa.user.copies.filter(c=>c.printing_id===pid).length===2,'UI backup restore');
assert.equal(w.__qa.user.copies.filter(c=>c.printing_id===pid).length,2);assert.equal(w.__qa.entries.find(e=>e.id===eid).printings[0].image,savedImage);assert.equal(w.__qa.sources.find(s=>s.id===sid).image,coverImage);
console.log(JSON.stringify({ok:true,checks:['visible provisional research tiles and evidence','independent sidebar species and cameo navigation','jumbo physical-size filter','scoped Sources and Data health','removable active filters and reset','filtered collection costs','two-section editor','source create','card with initial printing','exact Double Rare filter','two owned copies','printing edit keeps ID','real FileReader and HTTP picture upload','source rename and month date','source removal and restore','card removal and restore','source cover FileReader upload and backup restore','backup export and restore includes all records'],card_id:eid,printing_id:pid,errors:lastError}));
w.close();

}finally{server.kill();await new Promise(resolve=>server.once('close',resolve));fs.rmSync(tempDir,{recursive:true,force:true});}

});
