// The public mobile export replaces this editor-only module with a no-op stub.
import {filteredProductUrl,offerFilterLabel} from './catalog.mjs?v=1.8.14';
export function makeMarketFinder(env){
 const E=env.esc;let finder=null,generation=0;
 const offers=(url,f)=>filteredProductUrl(url,f.row.e,f.row,env.condition?.()??'3');
 function draw(){
  if(!finder)return;
  const f=finder,data=f.data,ctx=data?.context||{},selected=f.selected;
  const row=p=>{const origin=p.reusable?p.reused_from:p.origins?.[0],url=offers(p.listing_url,f);return `<article class="market-candidate ${selected?.product_id===p.product_id?'selected':''}"><div><h3>${E(p.name)}</h3><p>${p.code_product?'Online code product':p.current?'Current match':p.reusable?'Confirmed related printing':p.suggested?'Existing reference':'Catalogue result · details unchecked'}${origin?.release?' · '+E(env.languages[origin.lang]||origin.lang)+' '+E(origin.release)+' #'+E(origin.number):''}</p><small>Product ${E(p.product_id)}${!p.catalogue_present?' · catalogue not checked':''}</small></div><div class="candidate-actions"><a href="${E(url)}" target="_blank" rel="noopener noreferrer" title="${E(offerFilterLabel(f.row.e,f.row,env.condition?.()??'3'))}">Open offers ${env.icon('link')}</a><button type="button" data-action="market-select" data-id="${p.product_id}" aria-pressed="${selected?.product_id===p.product_id}" ${p.code_product?'disabled':''}>${selected?.product_id===p.product_id?env.icon('check')+'Selected':p.reusable?'Reuse product':'Select'}</button></div></article>`;};
  const references=(data?.products||[]).filter(p=>p.current||p.suggested),others=(data?.products||[]).filter(p=>!p.current&&!p.suggested);
  const rows=references.map(row).join('')+(references.length&&others.length?`<details class="finder-other"><summary>Other catalogue matches</summary>${others.map(row).join('')}</details>`:others.map(row).join(''));
  const related=selected?.related_printings||[],targets=related.length>1?`<fieldset class="market-related"><legend>Link selected printings · ${related.length} available</legend>${related.map(t=>`<label class="check related-target"><input type="checkbox" name="printing_target" value="${E(t.printing_id)}" ${f.targets.has(t.printing_id)?'checked':''} ${t.current?'disabled':''}><span><strong>${E(env.languages[t.lang])}</strong> · ${E(t.label)}<small>${t.current?'This printing':t.already_linked?'Already linked':'Same product'} · ${t.price_series==='reverse'?'Reverse guide':'Regular guide'}</small></span></label>`).join('')}</fieldset>`:'';
  const body=`<div class="modal-body product-finder"><div class="finder-context">${ctx.image?env.imageMarkup(ctx.image,ctx.native_name,'finder-image'):''}<div><strong>${E(ctx.name||f.row.e.english)} #${E(ctx.number||f.row.e.number)}</strong><span>${E(ctx.set_name||f.row.e.set_name)}</span><span>${E(env.languages[ctx.lang||f.row.e.lang])} · ${E(ctx.release||f.row.e.release)} · ${E(ctx.printing||f.row.label)}</span>${data?.existing_url?`<a class="finder-existing" href="${E(offers(data.existing_url,f))}" target="_blank" rel="noopener noreferrer">Saved listing ↗</a>`:''}</div></div><div class="finder-browse" ${selected?'hidden':''}><form id="market-search-form" class="finder-search"><label class="sr-only" for="market-query">Product name, ID or Cardmarket URL</label><input id="market-query" name="query" value="${E(f.query||'')}" placeholder="Card name, product ID or Cardmarket URL" maxlength="2000"><button type="submit" ${f.loading?'disabled':''}>${env.icon('search')}${f.loading?'Searching…':'Search catalogue'}</button><p class="form-error" role="alert">${E(f.error||'')}</p></form><div class="finder-status" aria-live="polite"><span>${data?`${data.total} ${data.total===1?'candidate':'candidates'}${data.catalogue.available?' · Catalogue '+E(data.catalogue.updated_at?.slice(0,10)||'cached'):' · Existing source references'}`:'Loading references…'}</span>${data?`<div><button class="quiet" data-action="market-wide" ${f.loading?'disabled':''}>Search all ${E(ctx.name)} products</button><button class="quiet" data-action="market-catalogue-refresh" ${f.loading?'disabled':''}>${data.catalogue.available?'Refresh catalogue':'Load catalogue'}</button></div>`:''}</div>${data?.warning?`<p class="finder-notice">${E(data.warning)}</p>`:''}${data?.pasted_url&&!/[?&]idProduct=/.test(data.pasted_url)?`<p class="finder-notice">${data.products.some(p=>p.suggested)?'Saved references are shown first.':'This URL has no numeric ID. Select the matching product below.'} <a href="${E(offers(data.pasted_url,f))}" target="_blank" rel="noopener noreferrer">Open listing ↗</a></p>`:''}<div class="market-candidates" aria-label="Cardmarket product candidates" aria-busy="${f.loading}">${rows||(!f.loading?'<p class="finder-empty">No matching product found. Search a different name or enter a known product ID.</p>':'')}</div>${data?.next_offset!=null?'<button class="finder-more" data-action="market-more">Show more products</button>':''}</div>${selected?`<form id="market-confirm-form" class="market-confirm"><div class="match-selection"><div><small>Selected product</small><strong>${E(selected.name)}</strong></div><div class="match-selection-actions"><a href="${E(offers(selected.listing_url,f))}" target="_blank" rel="noopener noreferrer">Open offers ↗</a><button type="button" class="quiet" data-action="market-reselect">Change selection</button></div></div><label>Price series · this printing<select name="price_series"><option value="standard" ${f.series==='standard'?'selected':''}>Regular product guide · includes holo cards</option>${ctx.finish==='reverse_holo'?`<option value="reverse" ${f.series==='reverse'?'selected':''}>Reverse-holo guide</option>`:''}</select></label>${targets}<label class="check match-check"><input name="confirmed" type="checkbox" required>I checked this product and the selected printings.</label><p class="form-error" role="alert"></p><div class="finder-footer"><button type="button" class="quiet" data-action="market-back">Back to card</button><button class="primary" type="submit">${env.icon('check')}Confirm & save</button></div></form>`:`<div class="finder-footer"><button type="button" data-action="market-back">Back to card</button>${data?.current_product_id?'<button class="quiet danger" data-action="market-unlink">Remove price match</button>':''}</div>`}</div>`;
  env.openDialog('Find Cardmarket product','Use an existing match or choose another product.',body,'market-finder',f.pid,f.row.e.id);
 }
 async function search(options={}){
  if(!finder)return;
  const f=finder,ticket=++generation;f.loading=true;f.error='';draw();
  try{
   const data=await env.post('market/search',{printing_id:f.pid,query:f.query,cache_only:options.cacheOnly===true,refresh:options.refresh===true,offset:options.more?f.data.next_offset:0});
   if(finder!==f||ticket!==generation||!env.isOpen())return;
   if(options.more)data.products=[...f.data.products,...data.products];
   f.data=data;if(f.query===undefined)f.query=data.query;
   if(!options.more){f.series=data.current_series||data.default_series;f.selected=null;f.targets=new Set();}
   f.loading=false;draw();
   if(options.cacheOnly&&!data.catalogue.available&&!data.products.length)await search();
  }catch(error){if(finder===f&&ticket===generation&&env.isOpen()){f.loading=false;f.error=error.message;draw();}}
 }
 async function open(pid){
  const row=env.printing(pid);if(!row||row.research)return;
  finder={pid,row,query:undefined,selected:null,targets:new Set(),data:null,series:row.finish==='reverse_holo'?'reverse':'standard',loading:false,error:''};
  await search({cacheOnly:true});
 }
 async function click(action,b){
  if(action==='market-find'){await open(b.dataset.id);return true;}
  if(!finder||!action.startsWith('market-'))return false;
  if(action==='market-select'){
   finder.selected=finder.data.products.find(p=>String(p.product_id)===b.dataset.id)||null;
   finder.targets=new Set((finder.selected?.related_printings||[]).map(t=>t.printing_id));draw();
   document.querySelector('#market-confirm-form')?.scrollIntoView?.({block:'nearest',behavior:'smooth'});
  }else if(action==='market-reselect'){finder.selected=null;draw();}
  else if(action==='market-back'){generation++;env.detail(finder.pid);}
  else if(action==='market-wide'){finder.query=finder.data.context.name;await search({cacheOnly:true});}
  else if(action==='market-catalogue-refresh')await search({refresh:true});
  else if(action==='market-more')await search({more:true});
  else if(action==='market-unlink'){
   const f=finder;await env.post('market/unlink',{printing_id:f.pid,context_key:f.data.context_key});generation++;env.render();env.detail(f.pid);env.toast('Price match removed.');
  }else return false;
  return true;
 }
 function change(target){
  if(target.form?.id!=='market-confirm-form')return false;
  if(target.name==='price_series')finder.series=target.value;
  else if(target.name==='printing_target'){if(target.checked)finder.targets.add(target.value);else finder.targets.delete(target.value);}
  else return false;
  target.form.elements.confirmed.checked=false;return true;
 }
 async function submit(form,fields){
  if(form.id==='market-search-form'){finder.query=fields.query;await search();return true;}
  if(form.id!=='market-confirm-form')return false;
  const f=finder;if(!f?.selected)throw new Error('Select a Cardmarket product first.');
  const targets=(f.selected.related_printings||[]).filter(t=>f.targets.has(t.printing_id)).map(t=>({printing_id:t.printing_id,context_key:t.context_key}));
  const result=await env.post('market/confirm',{printing_id:f.pid,context_key:f.data.context_key,product_id:f.selected.product_id,listing_url:f.selected.listing_url,price_series:fields.price_series,confirmed:form.elements.confirmed.checked,...(targets.length?{targets}:{})});
  generation++;env.render();env.detail(f.pid);env.toast(result.price_warning?'Product linked. Price refresh unavailable; try again later.':`Cardmarket product linked${result.linked_count>1?' to '+result.linked_count+' printings':''}.`);return true;
 }
 return {open,click,change,submit};
}
