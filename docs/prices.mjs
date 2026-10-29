export function priceMarkup(prices,pid,esc){
 const value=prices?.printings?.[pid];if(!value)return '';
 const money=v=>v==null?'Unavailable':new Intl.NumberFormat('en-GB',{style:'currency',currency:'EUR'}).format(v);
 const updated=prices.updated_at||'Unknown date',stamp=Date.parse(updated),stale=Number.isFinite(stamp)&&Date.now()-stamp>7*86400000;
 return `<div class="market-guide"><h3>Cardmarket guide${stale?' · Older snapshot':''}</h3><div class="market-values"><span><strong>${esc(money(value.trend))}</strong> Trend</span><span>${esc(money(value.avg30))}<small>30-day average</small></span></div><p class="image-note">${value.series==='reverse'?'Reverse-holo':'Standard product'} price series · EUR · ${esc(updated.slice(0,10))}<br>Product reference across available languages and conditions. Your purchase cost stays separate.</p></div>`;
}
