import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
import {entryPreview,hasMissingPictures} from '../static/catalog.mjs';

const require=createRequire(import.meta.url);
const {JSDOM}=require(process.env.DOGDEX_QA_NODE_MODULES?path.join(process.env.DOGDEX_QA_NODE_MODULES,'jsdom'):'jsdom');
const root=fileURLToPath(new URL('../',import.meta.url));
const modules=['set-symbols.mjs','source-ui.mjs','localization.mjs','catalog.mjs','prices.mjs','appearance.mjs','market-ui.mjs','editor-ui.mjs','app.js'];
const code=modules.map(f=>fs.readFileSync(path.join(root,'static',f),'utf8').replace(/^import[^\n]*\n/gm,'').replace(/\bexport /g,'')).join('\n')+'\nwindow.qa={ui,render,detail,rebuild,editor,get entries(){return entries}};';
const tick=()=>new Promise(resolve=>setTimeout(resolve,0));

test('German Ninetales printing uploads supply the overview without changing the shared reference or sibling images',{timeout:30000},async()=>{
 const python=`import sys,json,tempfile,base64,shutil
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from dogdex.collector import Collection
from dogdex.mobile_export import build_snapshot,export_mobile
with tempfile.TemporaryDirectory() as temp:
 original=Path(sys.argv[1]);app=Path(temp)/'app';app.mkdir();(app/'data/images').mkdir(parents=True)
 shutil.copytree(original/'static',app/'static');shutil.copyfile(original/'data/catalog.json',app/'data/catalog.json')
 s=Collection(app,Path(temp)/'collection')
 e=next(e for e in s.editor_view()['entries'] if e['lang']=='de' and e['release']=='base1' and e['number']=='12')
 assert e['image'] is None and len(e['printings'])==2
 for p,asset in zip(e['printings'],s.catalog['used_images'][:2]):
  shutil.copyfile(original/'data/images'/asset,s.root/'data/images'/asset)
  s.mutate('catalog/image',dict(entry_id=e['id'],printing_id=p['id'],bytes=base64.b64encode((s.root/'data/images'/asset).read_bytes()).decode(),image_kind='representative',image_exact=False,source_note='QA: two deliberately distinct printing picture files.'))
 pid=e['printings'][0]['id']
 s.add_copies(dict(printing_id=pid,condition='excellent',price='12.34',currency='EUR',quantity=2,notes='Preserve copies',misprint_notes='Misprint copy fixture',purchased_on='2026-10-31'))
 s.wish(dict(printing_id=e['printings'][1]['id'],wanted=True))
 view=s.editor_view();view['entries']=[x for x in view['entries'] if x['id']==e['id']]
 view['sources']=[x for x in view['sources'] if x['id']==e['primary_source_id']]
 snapshot=build_snapshot(s);snapshot['entries']=[x for x in snapshot['entries'] if x['id']==e['id']];snapshot['sources']=view['sources']
 assert snapshot['entries'][0]['image'] is None
 # Exercise the actual export and backup restore; neither may synthesize a shared override.
 from unittest.mock import patch
 with patch('dogdex.mobile_export.build_snapshot',return_value=snapshot):export_mobile(s)
 for p in snapshot['entries'][0]['printings']:
  name=Path(p['image']).name
  assert (s.root/'docs/user-images'/name).read_bytes()==(s.user_dir/'catalog_images'/name).read_bytes()
 assert (s.root/'docs/catalog.mjs').read_bytes()==(s.root/'static/catalog.mjs').read_bytes()
 before=s.state();other=Collection(s.root,Path(temp)/'restored');other.restore(s.backup());after=other.state()
 for key in before:
  if key!='audit_log':assert before[key]==after[key],key
 assert not before['image_overrides']
 catalog=dict(roster=s.catalog['roster'],rarity_options=s.catalog['rarity_options'],entries=view['entries'])
 print(json.dumps(dict(catalog=catalog,view=view,state=before,snapshot=snapshot)))`;
 const fixture=JSON.parse(execFileSync('python3',['-c',python,root],{maxBuffer:10000000}));
 const e=fixture.view.entries[0],first=e.printings.find(p=>p.edition==='first_edition'),unlimited=e.printings.find(p=>p.edition==='unlimited');
 assert.ok(first&&unlimited);assert.notEqual(first.image,unlimited.image);assert.equal(e.image,null);
 const before=JSON.stringify(fixture.state),physicalBefore=e.printings.map(p=>({id:p.id,image:p.image,physical_key:p.physical_key}));
 let mutations=0;
 async function boot(readOnly=false){
  const html='<html'+(readOnly?' data-readonly="true"':'')+'><body><div id="app"></div><dialog id="dialog"></dialog><div id="toast"></div></body></html>';
  const dom=new JSDOM(html,{url:'http://localhost/J_DogDex/',runScripts:'outside-only',pretendToBeVisual:true});const w=dom.window;
  w.scrollTo=()=>{};w.HTMLDialogElement.prototype.showModal=function(){this.open=true;};w.HTMLDialogElement.prototype.close=function(){this.open=false;};
  w.fetch=async(url,options)=>{if(options?.method==='POST'){mutations++;throw new Error('Read-only inspection unexpectedly attempted a mutation');}return {ok:true,json:async()=>readOnly?fixture.snapshot:String(url).includes('catalog.json')?fixture.catalog:{state:fixture.state,view:fixture.view,prices:{},token:'qa'}};};
  w.eval(code);for(let i=0;i<100&&!w.qa?.entries.length;i++)await new Promise(resolve=>setTimeout(resolve,10));
  assert.equal(w.qa.entries.length,1);return {dom,w,$:s=>w.document.querySelector(s)};
 }
 const {w,$}=await boot();
 try{
  w.qa.ui.lang='de';w.qa.ui.view='health';w.qa.render();
  assert.equal($('.editor-card-row img').getAttribute('src'),e.printings[0].image);
  w.qa.ui.issue='images';w.qa.render();assert.equal($('.editor-card-row'),null,'Two available printing pictures resolve Missing pictures without a shared upload');
  w.qa.editor.card(e.id,'picture');
  assert.equal($('[name="printing_id"]').value,'');assert.equal($('.detail-image').getAttribute('aria-label'),'No shared reference saved');
  assert.match($('.image-note').textContent,/Overview uses the Holo/);assert.equal($('#picture-editor-form .detail-image img'),null);
  for(const p of [first,unlimited]){
   const select=$('[name="printing_id"]');select.value=p.id;select.dispatchEvent(new w.Event('change',{bubbles:true}));await tick();
   assert.equal($('.detail-image').getAttribute('src'),p.image);assert.equal($('.image-note'),null);
  }
  w.qa.ui.view='all';w.qa.ui.issue='';w.qa.render();
  for(const p of [first,unlimited]){
   assert.equal($(`.card-visual[data-id="${p.id}"] img`).getAttribute('src'),p.image);
   w.qa.detail(p.id);assert.equal($('.detail-image').getAttribute('src'),p.image);
  }
  assert.equal(JSON.stringify(fixture.state),before);assert.deepEqual(e.printings.map(p=>({id:p.id,image:p.image,physical_key:p.physical_key})),physicalBefore);
  // An overview thumbnail must not hide an actually missing sibling image.
  const original=unlimited.image;unlimited.image=null;w.qa.rebuild();w.qa.ui.view='health';w.qa.ui.issue='images';w.qa.render();
  assert.ok($('.editor-card-row'));assert.equal($('.editor-card-row img').getAttribute('src'),first.image);
  w.qa.detail(unlimited.id);assert.ok($('.detail-image.placeholder'));assert.equal($('.detail-image-wrap img'),null,'Never substitute the First Edition picture for an Unlimited printing');
  unlimited.image=original;
  // An explicit shared upload still has priority for the entry preview.
  e.image='/user-images/'+'c'.repeat(64)+'.jpg';w.qa.rebuild();w.qa.ui.view='health';w.qa.ui.issue='';w.qa.render();
  assert.equal($('.editor-card-row img').getAttribute('src'),e.image);
  for(const p of [first,unlimited]){w.qa.detail(p.id);assert.equal($('.detail-image').getAttribute('src'),p.image);}
  e.image=null;
 }finally{w.close();}
 const mobile=await boot(true);
 try{
  mobile.w.qa.ui.lang='de';mobile.w.qa.render();
  for(const p of fixture.snapshot.entries[0].printings){
   assert.equal(mobile.$(`.card-visual[data-id="${p.id}"] img`).getAttribute('src'),'.'+p.image);
   mobile.w.qa.detail(p.id);assert.equal(mobile.$('.detail-image').getAttribute('src'),'.'+p.image);
  }
  assert.equal(mobile.$('#nav-health'),null);
 }finally{mobile.w.close();}
 assert.equal(mutations,0);assert.equal(JSON.stringify(fixture.state),before);
});

test('entry previews also handle research-only and genuinely empty records without mutating them',()=>{
 const claim={id:'unresolved-claim',image:'claim.webp'},e={image:null,printings:[],printing_claims:[claim]},before=JSON.stringify(e);
 assert.equal(entryPreview(e).image,'claim.webp');assert.equal(entryPreview(e).printing,claim);assert.equal(hasMissingPictures(e),false);assert.equal(JSON.stringify(e),before);
 assert.equal(entryPreview({image:null,printings:[]}).image,null);assert.equal(hasMissingPictures({image:null,printings:[]}),true);
 assert.equal(entryPreview({image:'shared.webp',printings:[]}).image,'shared.webp');assert.equal(hasMissingPictures({image:'shared.webp',printings:[]}),false);
});
