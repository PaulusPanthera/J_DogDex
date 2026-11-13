import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import path from 'node:path';import {createRequire} from 'node:module';import {fileURLToPath} from 'node:url';import {execFileSync} from 'node:child_process';
const require=createRequire(import.meta.url),{JSDOM}=require(process.env.DOGDEX_QA_NODE_MODULES?path.join(process.env.DOGDEX_QA_NODE_MODULES,'jsdom'):'jsdom'),root=fileURLToPath(new URL('../',import.meta.url));
test('restored German stadium is collectible, 104 is excluded but owned copies remain visible, and 120 is a dog cameo',async()=>{
 const py="import sys,json,tempfile;from pathlib import Path;sys.path.insert(0,sys.argv[1]);from dogdex.collector import Collection;from dogdex.mobile_export import build_snapshot;t=tempfile.TemporaryDirectory();print(json.dumps(build_snapshot(Collection(Path(sys.argv[1]),t.name))))";
 const snapshot=JSON.parse(execFileSync('python3',['-c',py,root],{maxBuffer:100000000}));
 const e77=snapshot.entries.find(e=>e.lang==='de'&&e.release==='me03'&&e.number==='077'),e104=snapshot.entries.find(e=>e.lang==='de'&&e.release==='me03'&&e.number==='104'),pid104=e104.printing_claims[0].id;snapshot.ownership[pid104]=2;
 const dom=new JSDOM('<html data-readonly="true"><body><div id="app"></div><dialog id="dialog"></dialog><div id="toast"></div></body></html>',{url:'https://example.github.io/J_DogDex/',runScripts:'outside-only',pretendToBeVisual:true}),w=dom.window;
 w.scrollTo=()=>{};w.HTMLDialogElement.prototype.showModal=function(){this.open=true};w.HTMLDialogElement.prototype.close=function(){this.open=false};let requests=0;w.fetch=async()=>{requests++;return{ok:true,json:async()=>snapshot}};
 w.eval(['set-symbols.mjs','source-ui.mjs','localization.mjs','catalog.mjs','prices.mjs','appearance.mjs','market-ui.mjs','editor-ui.mjs','app.js'].map(f=>fs.readFileSync(root+'/static/'+f,'utf8').replace(/^import[^\n]*\n/gm,'').replace(/\bexport /g,'')).join('\n')+'\nwindow.qa={ui,render,detail};');
 for(let i=0;i<100&&!w.document.querySelector('.card');i++)await new Promise(r=>setTimeout(r,10));
 try{
  w.qa.ui.lang='de';w.qa.ui.q='Optimale Ordnung';w.qa.render();
  const cards=[...w.document.querySelectorAll('.card')],stadiums=cards.filter(c=>c.querySelector('.collector-number').textContent==='#077');assert.equal(stadiums.length,2);assert.ok(stadiums.every(c=>c.querySelector('img').src.includes(e77.image)));assert.ok(stadiums.every(c=>!c.classList.contains('research-card')));assert.ok(!cards.some(c=>c.querySelector('.collector-number').textContent==='#104'));
  w.qa.ui.q='';w.document.querySelector('#browse-cameo').click();await new Promise(r=>setTimeout(r,0));w.document.querySelector('#browse-718').click();await new Promise(r=>setTimeout(r,0));
  const cameoCards=[...w.document.querySelectorAll('.card')];assert.ok(cameoCards.some(c=>c.querySelector('.collector-number').textContent==='#120'));assert.ok(!cameoCards.some(c=>c.querySelector('.collector-number').textContent==='#104'));
  w.qa.ui.category='all';w.qa.ui.pokemon='';w.qa.ui.view='collection';w.qa.render();
  const retained=w.document.querySelector('.card');assert.ok(retained);assert.equal(retained.querySelector('.collector-number').textContent,'#104');assert.equal(retained.querySelector('.out-of-scope').textContent,'Out of scope');assert.equal(retained.querySelector('.count-badge'),null);assert.match(retained.getAttribute('aria-label'),/2 copies collected/);assert.ok(retained.classList.contains('owned'));
  w.qa.detail(pid104);assert.match(w.document.querySelector('#dialog').textContent,/Outside Zygarde 10% scope/);assert.match(w.document.querySelector('#dialog').textContent,/2 copies collected/);assert.equal(requests,1);
 }finally{w.close();}
});
