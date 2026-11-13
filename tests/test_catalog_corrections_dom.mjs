import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
const require=createRequire(import.meta.url),{JSDOM}=require(process.env.DOGDEX_QA_NODE_MODULES?path.join(process.env.DOGDEX_QA_NODE_MODULES,'jsdom'):'jsdom'),root=fileURLToPath(new URL('../',import.meta.url));

test('English-era Unlimited pairs including all five Vulpix versions and the selected German Skyridge date are visible; the date conflict stays in Data health',async()=>{
 const code="import sys,json,tempfile;from pathlib import Path;sys.path.insert(0,sys.argv[1]);from dogdex.collector import Collection;t=tempfile.TemporaryDirectory();s=Collection(Path(sys.argv[1]),t.name);print(json.dumps(dict(catalog=s.catalog,view=s.editor_view(),state=s.state())))";
 const fixture=JSON.parse(execFileSync('python3',['-c',code,root],{maxBuffer:150000000}));
 const dom=new JSDOM('<html><body><div id="app"></div><dialog id="dialog"></dialog><div id="toast"></div></body></html>',{url:'http://localhost/',runScripts:'outside-only',pretendToBeVisual:true}),w=dom.window;
 w.scrollTo=()=>{};w.HTMLDialogElement.prototype.showModal=function(){this.open=true};w.HTMLDialogElement.prototype.close=function(){this.open=false};let posts=0;
 w.fetch=async(u,o)=>{if(o?.method==='POST')posts++;return{ok:true,json:async()=>String(u).includes('catalog.json')?fixture.catalog:{state:fixture.state,view:fixture.view,token:'qa',prices:{}}}};
 w.eval(['set-symbols.mjs','source-ui.mjs','localization.mjs','catalog.mjs','prices.mjs','appearance.mjs','market-ui.mjs','editor-ui.mjs','app.js'].map(n=>fs.readFileSync(root+'/static/'+n,'utf8').replace(/^import[^\n]*\n/gm,'').replace(/\bexport /g,'')).join('\n')+'\nwindow.qa={ui,render,detail,review};');
 for(let i=0;i<100&&!w.document.querySelector('.card');i++)await new Promise(r=>setTimeout(r,10));
 try{
  w.qa.ui.lang='en';w.qa.ui.pokemon='209';w.qa.render();
  for(const release of ['neo1','neo3']){
   const entry=fixture.view.entries.find(e=>e.lang==='en'&&e.release===release&&e.dex===209);assert.equal(entry.printings.length,2);
   assert.deepEqual(entry.printings.map(p=>p.edition).sort(),['first_edition','unlimited']);
   for(const p of entry.printings){const b=w.document.querySelector(`.card-visual[data-id="${p.id}"]`);assert.ok(b);assert.match(b.closest('.card').querySelector('.card-tags').textContent,p.edition==='unlimited'?/Unlimited/:/1st edition/);}
   const unlimited=entry.printings.find(p=>p.edition==='unlimited');w.qa.detail(unlimited.id);assert.equal(w.document.querySelector('.printing-option.active').dataset.id,unlimited.id);
  }
  w.qa.ui.pokemon='37';w.qa.render();
  for(const [release,number] of [['gym1','65'],['gym1','73'],['gym2','37'],['gym2','66'],['neo4','91']]){
   const e=fixture.view.entries.find(e=>e.lang==='en'&&e.release===release&&e.number===number),p=e.printings.find(p=>p.edition==='unlimited');assert.ok(p);
   const b=w.document.querySelector(`.card-visual[data-id="${p.id}"]`);assert.ok(b);assert.match(b.closest('.card').querySelector('.card-tags').textContent,/Unlimited/);
   w.qa.detail(p.id);assert.equal(w.document.querySelector('.printing-option.active').dataset.id,p.id);
  }
  const sk=fixture.view.entries.find(e=>e.lang==='de'&&e.release==='ecard3'&&e.number==='101');
  w.qa.ui.lang='de';w.qa.ui.pokemon='';w.qa.ui.q='Skyridge';w.qa.render();
  const tile=w.document.querySelector(`.card-visual[data-id="${sk.printings[0].id}"]`).closest('.card');assert.equal(tile.querySelector('.card-date').textContent,'2003');assert.match(tile.querySelector('.card-date').title,/15 Aug 2003/);
  w.qa.detail(sk.printings[0].id);assert.match(w.document.querySelector('.modal-head p').textContent,/Skyridge · 15 Aug 2003/);
  w.qa.ui.view='health';w.qa.ui.health='cards';w.qa.ui.issue='dates';w.qa.ui.q='';w.qa.render();assert.ok(w.document.querySelector(`[data-action="review"][data-id="${sk.id}"]`));
  w.qa.review(sk.id,'evidence');assert.match(w.document.querySelector('#dialog').textContent,/Winter 2003\/2004/);assert.match(w.document.querySelector('#dialog').textContent,/2003-08-15/);assert.equal(posts,0);
 }finally{w.close();}
});
