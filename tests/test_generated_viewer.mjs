import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
const require=createRequire(import.meta.url),{JSDOM}=require(process.env.DOGDEX_QA_NODE_MODULES?path.join(process.env.DOGDEX_QA_NODE_MODULES,'jsdom'):'jsdom');
const root=fileURLToPath(new URL('../',import.meta.url));
test('actual exported editor stub renders released inventory and exact subset identities without private APIs',{timeout:120000},async()=>{
 const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'dogdex-export-'));let dom;
 try{
  let docs=process.env.DOGDEX_VIEWER_DIR;
  if(!docs){
   const code="import pathlib,shutil,sys;sys.path.insert(0,sys.argv[1]);from dogdex.collector import Collection;from dogdex.mobile_export import export_mobile;r=pathlib.Path(sys.argv[2]);(r/'data').mkdir(parents=True);shutil.copyfile(pathlib.Path(sys.argv[1])/'data/catalog.json',r/'data/catalog.json');shutil.copytree(pathlib.Path(sys.argv[1])/'static',r/'static');export_mobile(Collection(r));print(r/'docs')";
   docs=execFileSync('python3',['-c',code,root,path.join(tmp,'app')],{encoding:'utf8',maxBuffer:1000000}).trim();
  }
  const snapshot=JSON.parse(fs.readFileSync(path.join(docs,'snapshot.json'),'utf8'));
  assert.equal(snapshot.app_version,fs.readFileSync(path.join(root,'dogdex/__init__.py'),'utf8').match(/__version__ = "([^"]+)"/)[1]);const replaced=snapshot.entries.find(e=>e.lang==='de'&&e.release==='30th-c');replaced.image='/user-images/'+('a'.repeat(64))+'.webp';for(const p of replaced.printings)p.image=replaced.image;const editor=fs.readFileSync(path.join(docs,'editor-ui.mjs'),'utf8');assert.match(editor,/syncSelection/);assert.doesNotMatch(editor,/catalog\/bulk|catalog\/entry\/save/);
  dom=new JSDOM(fs.readFileSync(path.join(docs,'index.html'),'utf8'),{url:'https://example.github.io/J_DogDex/',runScripts:'outside-only',pretendToBeVisual:true});const w=dom.window;w.scrollTo=()=>{};w.HTMLDialogElement.prototype.showModal=function(){this.open=true;};w.HTMLDialogElement.prototype.close=function(){this.open=false;};const errors=[],requests=[];w.addEventListener('error',e=>errors.push(e.message));
  w.fetch=async value=>{const url=new URL(value,w.location.href);requests.push(url.pathname);assert.equal(url.pathname,'/J_DogDex/snapshot.json');return {ok:true,json:async()=>snapshot};};
  const files=['set-symbols.mjs','source-ui.mjs','localization.mjs','catalog.mjs','prices.mjs','appearance.mjs','market-ui.mjs','editor-ui.mjs'];const script=files.map(n=>fs.readFileSync(path.join(docs,n),'utf8').replace(/\bexport /g,'')).join('\n')+'\n'+fs.readFileSync(path.join(docs,'app.js'),'utf8').replace(/^import[^\n]*\n/gm,'')+'\nwindow.qa={ui,render,detail,closeDialog};';w.eval(script);
  for(let i=0;i<1000&&!w.document.querySelector('.card');i++)await new Promise(r=>setTimeout(r,10));assert.ok(w.document.querySelector('.card'));
  w.qa.ui.lang='de';w.qa.ui.q='Delta-Herrschaft';w.qa.render();assert.equal(w.document.querySelectorAll('.card').length,9);
  const ordinary=snapshot.entries.find(e=>e.lang==='de'&&e.release==='me06'&&e.number==='018');w.qa.detail(ordinary.printings[0].id);assert.equal(w.document.querySelectorAll('#dialog .printing-option').length,2);w.qa.closeDialog();
  const ir=snapshot.entries.find(e=>e.lang==='de'&&e.release==='me06'&&e.number==='106');w.qa.detail(ir.printings[0].id);assert.match(w.document.querySelector('#dialog').textContent,/English reference artwork/);w.qa.closeDialog();
  w.qa.ui.q='30 Jahre';w.qa.ui.view='sources';w.qa.render();const tiles=w.document.querySelectorAll('[data-action="source"][data-id="release:de:30th"]');assert.equal(tiles.length,1);tiles[0].click();await new Promise(r=>setTimeout(r,0));assert.equal(w.document.querySelectorAll('.card').length,15);const subset=w.document.querySelector('[data-action="subset"][data-subset="classic_collection"]');assert.ok(subset);subset.click();await new Promise(r=>setTimeout(r,0));assert.equal(w.document.querySelectorAll('.card').length,1);
  const classic=snapshot.entries.find(e=>e.lang==='de'&&e.release==='30th-c');assert.equal(classic.number,'138');assert.equal(classic.subset_key,'classic_collection');w.qa.detail(classic.printings[0].id);assert.match(w.document.querySelector('#dialog').textContent,/Zacian V #138/);assert.match(w.document.querySelector('#dialog').textContent,/16 Sept? 2026/);assert.doesNotMatch(w.document.querySelector('#dialog').textContent,/English reference artwork/);
  assert.equal(w.document.querySelector('[data-action="add"],[data-action="market-find"],[data-action="review"]'),null);assert.deepEqual(errors,[]);assert.deepEqual(requests,['/J_DogDex/snapshot.json']);
 }finally{dom?.window.close();fs.rmSync(tmp,{recursive:true,force:true});}
});
