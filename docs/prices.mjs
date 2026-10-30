const guideMoney=new Intl.NumberFormat('en-GB',{style:'currency',currency:'EUR'});
const priceNames={trend:'Trend',avg30:'30-day average',avg7:'7-day average',low:'Low'};
const validPrice=v=>typeof v==='number'&&Number.isFinite(v)&&v>=0;
export function primaryPrice(prices,pid){
 const value=prices?.printings?.[pid];if(!value)return null;
 const key=['trend','avg30','avg7','low'].find(k=>validPrice(value[k]));if(!key)return null;
 return {value:value[key],key,label:priceNames[key],text:guideMoney.format(value[key])};
}
function priceContext(prices,pid){
 const updated=prices.updated_at||'',stamp=Date.parse(updated);
 return {date:updated.slice(0,10)||'Date unavailable',stale:Number.isFinite(stamp)&&Date.now()-stamp>7*86400000,series:prices.printings[pid].series==='reverse'?'Reverse holo':'Standard'};
}
export function pricePreview(prices,pid,esc){
 const selected=primaryPrice(prices,pid);if(!selected)return '';
 const context=priceContext(prices,pid),title=`Cardmarket ${selected.label} · ${context.series} · ${context.date}${context.stale?' · Older snapshot':''} · all available languages and conditions`;
 return `<span class="card-price" data-price-kind="${selected.key}" title="${esc(title)}" aria-label="${esc(title+': '+selected.text)}">${selected.key==='low'?'<small>from</small>':''}<strong>${esc(selected.text)}</strong></span>`;
}
export function priceMarkup(prices,pid,esc){
 const selected=primaryPrice(prices,pid);if(!selected)return '';
 const value=prices.printings[pid],context=priceContext(prices,pid);
 return `<details class="market-guide" title="Product reference across available languages and conditions"><summary><span class="market-heading">Cardmarket</span><strong class="market-primary">${selected.key==='low'?'<small>from </small>':''}${esc(selected.text)}</strong><span class="price-chevron" aria-hidden="true">⌄</span></summary><div class="market-breakdown">${['trend','avg7','avg30','low'].map(key=>`<span><small>${esc(priceNames[key])}</small><strong>${validPrice(value[key])?esc(guideMoney.format(value[key])):'—'}</strong></span>`).join('')}<span class="market-updated">${esc(selected.label)} · ${esc(context.date)} · ${context.series} · EUR${context.stale?' · older snapshot':''}</span></div></details>`;
}
