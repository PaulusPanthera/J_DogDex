import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {spawn} from 'node:child_process';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
const require=createRequire(import.meta.url),{JSDOM}=require(process.env.DOGDEX_QA_NODE_MODULES?path.join(process.env.DOGDEX_QA_NODE_MODULES,'jsdom'):'jsdom');
const root=fileURLToPath(new URL('../',import.meta.url));

test('individual card picker, optional all-filtered selection, review, atomic HTTP save and Undo',{timeout:120000},async()=>{
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'dogdex-bulk-')),app=path.join(temp,'app');fs.mkdirSync(path.join(app,'data'),{recursive:true});
 fs.cpSync(path.join(root,'static'),path.join(app,'static'),{recursive:true});
 const catalog=JSON.parse(fs.readFileSync(path.join(root,'data/catalog.json'),'utf8'));
 const de=catalog.entries.filter(e=>e.lang==='de'&&e.metadata_state==='approved'&&!e.art_style&&e.printings.length).slice(0,8);
 assert.equal(de.length,8);const known={...structuredClone(de[0]),id:'qa-already-classified',number:'QA',number_key:'QA',art_style:'full_art',printings:[]};
 const en=catalog.entries.find(e=>e.lang==='en'&&e.metadata_state==='approved'&&e.printings.length),ja=catalog.entries.find(e=>e.lang==='ja'&&e.metadata_state==='approved'&&e.printings.length);
 catalog.entries=[...de,known,en,ja];catalog.retired_entries=[];catalog.retired_releases=[];
 fs.writeFileSync(path.join(app,'data/catalog.json'),JSON.stringify(catalog));
 const code="import sys;sys.path.insert(0,sys.argv[1]);from app import make_server;s=make_server(sys.argv[2],0,user_dir=sys.argv[3]);e=next(e for e in s.store.entries().values() if e['lang']=='de' and e['printings']);s.store.add_copies(dict(printing_id=e['printings'][0]['id'],quantity=2,condition='excellent',price='4.25',notes='Keep purchase',misprint_notes='One misprint'));print('http://127.0.0.1:'+str(s.server_port),flush=True);s.serve_forever()";
 const server=spawn('python3',['-c',code,root,app,path.join(temp,'collection')],{stdio:['ignore','pipe','pipe']});let logs='',dom;
 server.stderr.on('data',b=>logs+=b);
 try{
  const base=await new Promise((resolve,reject)=>{let text='';const timer=setTimeout(()=>reject(Error(logs||'Server did not start')),20000);server.stdout.on('data',b=>{text+=b;const m=text.match(/http:\/\/127\.0\.0\.1:\d+/);if(m){clearTimeout(timer);resolve(m[0]);}});server.once('error',reject);});
  dom=new JSDOM('<html><body><div id="app"></div><dialog id="dialog"></dialog><div id="toast"></div></body></html>',{url:base,runScripts:'outside-only',pretendToBeVisual:true});
  const w=dom.window;w.scrollTo=()=>{};w.fetch=(url,options)=>fetch(new URL(url,base),options);
  w.HTMLDialogElement.prototype.showModal=function(){this.open=true;};w.HTMLDialogElement.prototype.close=function(){this.open=false;};
  let error=null;w.console.error=(...args)=>{error=args.join(' ');};
  const code=['set-symbols.mjs','source-ui.mjs','localization.mjs','catalog.mjs','prices.mjs','appearance.mjs','market-ui.mjs','editor-ui.mjs','app.js'].map(f=>fs.readFileSync(path.join(root,'static',f),'utf8').replace(/^import[^\n]*\n/gm,'').replace(/\bexport /g,'')).join('\n')+'\nwindow.qa={ui,render,editor,post,get entries(){return entries},get user(){return user}};';
  const $=s=>w.document.querySelector(s),all=s=>[...w.document.querySelectorAll(s)];
  const wait=async(fn,label)=>{const until=Date.now()+18000;while(!fn()){if(Date.now()>until)throw Error('Timed out: '+label+' '+(error||logs));await new Promise(r=>setTimeout(r,15));}};
  const click=async selector=>{const el=$(selector);assert.ok(el,'Missing '+selector);el.click();await new Promise(r=>setTimeout(r,10));};
  const submit=selector=>{const form=$(selector);assert.ok(form);form.dispatchEvent(new w.Event('submit',{bubbles:true,cancelable:true}));};
  const state=async()=>await (await fetch(base+'/api/state')).json();
  w.eval(code);await wait(()=>w.qa.entries.length,'boot');
  const originalCopies=JSON.stringify(w.qa.user.copies);
  Object.assign(w.qa.ui,{view:'health',health:'cards',lang:'de',issue:'artwork',q:'',pokemon:'',category:'all',limit:2});w.qa.render();
  assert.equal(all('.editor-card-row').length,2);assert.equal($('.bulk-card-grid'),null);
  await click('[data-action="bulk-toggle"]');assert.equal(all('[data-bulk-card]').length,2);assert.match($('.bulk-toolbar').textContent,/0 selected/);assert.equal($('[data-action="bulk-config"]').disabled,true);
  all('[data-bulk-card]')[0].click();assert.match($('.bulk-toolbar').textContent,/1 selected/);
  const first=all('[data-bulk-card]')[0].dataset.bulkCard;
  all('[data-bulk-card]')[1].click();assert.match($('.bulk-toolbar').textContent,/2 selected/);
  all('[data-bulk-card]')[0].click();assert.match($('.bulk-toolbar').textContent,/1 selected/);assert.equal(all('[data-bulk-card]')[1].checked,true);
  await click('[data-action="bulk-select-all"]');assert.match($('.bulk-toolbar').textContent,/8 selected/);assert.equal(all('[data-bulk-card]').length,2,'Select all must include matching cards beyond the visible page');
  await click('[data-action="bulk-clear"]');assert.equal(all('[data-bulk-card]:checked').length,0);
  all('[data-bulk-card]')[0].click();all('[data-bulk-card]')[1].click();
  const ids=all('[data-bulk-card]:checked').map(el=>el.dataset.bulkCard),before=await state();
  await click('[data-action="bulk-config"][data-field="artwork"]');assert.ok($('#bulk-config-form'));assert.equal($('#bulk-config-form [name="value"]').value,'standard');
  submit('#bulk-config-form');await wait(()=>$('#bulk-apply-form'),'review');assert.equal(all('.bulk-review-card').length,2);assert.match($('#bulk-apply-form').textContent,/Standard artwork/);
  assert.equal(JSON.stringify((await state()).state),JSON.stringify(before.state),'Review cannot alter records');
  submit('#bulk-apply-form');await wait(()=>!$('#dialog').open&&$('.bulk-feedback'),'apply');
  for(const id of ids)assert.equal(w.qa.entries.find(e=>e.id===id).art_style,'standard');
  assert.equal(w.qa.entries.find(e=>e.id===de[2].id).art_style,null);
  assert.equal(JSON.stringify(w.qa.user.copies),originalCopies);
  await click('.bulk-feedback [data-action="bulk-undo"]');await wait(()=>ids.every(id=>!w.qa.entries.find(e=>e.id===id).art_style),'undo');
  assert.equal(JSON.stringify(w.qa.user.copies),originalCopies);
  // Selection is tied to the current scope, and never follows the user into another ledger.
  all('[data-bulk-card]')[0].click();assert.match($('.bulk-toolbar').textContent,/1 selected/);
  $('#search').value='No matching card';$('#search').dispatchEvent(new w.Event('input',{bubbles:true}));await wait(()=>$('.bulk-toolbar').textContent.includes('0 selected'),'search resets selection');assert.equal(all('[data-bulk-card]').length,0);
  w.qa.ui.q='';w.qa.render();all('[data-bulk-card]')[0].click();await click('#lang-en');await wait(()=>w.qa.ui.lang==='en','ledger change');assert.match($('.bulk-toolbar').textContent,/0 selected/);
  Object.assign(w.qa.ui,{lang:'ja',issue:'',q:'',limit:96});w.qa.render();all('[data-bulk-card]')[0].click();
  await click('[data-action="bulk-config"][data-field="rarity"]');const values=all('#bulk-config-form [name="value"] option').map(o=>o.value);assert.ok(values.includes('AR')&&values.includes('S_legacy_lvx'));assert.ok(!values.includes('illustration_rare'));
  await click('[data-action="close"]');
  // Known values remain excluded by default and are listed as skipped in review.
  Object.assign(w.qa.ui,{lang:'de',issue:'',q:'',limit:96});w.qa.render();await click('[data-action="bulk-select-all"]');
  await click('[data-action="bulk-config"][data-field="artwork"]');submit('#bulk-config-form');await wait(()=>$('#bulk-apply-form'),'skip review');assert.equal(all('.bulk-review-card').length,8);assert.match($('#bulk-apply-form').textContent,/1 selected card skipped/);
  await click('[data-action="close"]');assert.equal(JSON.stringify(w.qa.user.copies),originalCopies);
  // Closing review saves nothing. Recent successful batches remain accessible for Undo.
  await click('[data-action="editor-utilities"]');assert.match($('#dialog').textContent,/Recent bulk edits/);
  assert.equal(error,null);assert.ok(first);
 }finally{dom?.window.close();server.kill();await new Promise(resolve=>server.once('close',resolve));fs.rmSync(temp,{recursive:true,force:true});}
});
