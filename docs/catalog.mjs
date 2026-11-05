export function dateParts(value){const m=/^(\d{4})(?:-(\d{2})(?:-(\d{2}))?)?$/.exec(String(value||''));return m?m.slice(1).map(v=>v?Number(v):null):[null,null,null];}
export function compareDates(a,b,direction=1){const x=dateParts(a),y=dateParts(b);for(let i=0;i<3;i++){if(x[i]==null&&y[i]==null)continue;if(x[i]==null)return 1;if(y[i]==null)return -1;if(x[i]!==y[i])return (x[i]-y[i])*direction;}return 0;}
export const effectiveDate=r=>r.date_state==='unresolved_product_date'?null:r.release_date||r.e?.release_date||r.e?.year||null;
export const pokemonIds=e=>[...new Set([...(e.subject_dex||[e.dex]),...(e.cameo_dex||[])].filter(Number.isInteger))];
export const primaryPokemonIds=e=>[...new Set((e.subject_dex??(e.category==='cameo'?[]:[e.dex])).filter(Number.isInteger))];
export const isCameo=e=>!primaryPokemonIds(e).length&&(e.category==='cameo'||!!e.cameo_dex?.length);
export const isFullArt=e=>e.art_style==='full_art';
// Entry thumbnails can use a printing image without assigning it to other printings.
export function entryPreview(e){
 if(e.image)return {image:e.image,printing:null};
 const printing=[...(e.printings||[]),...(e.printing_claims||[])].find(p=>p.image);
 return {image:printing?.image||null,printing:printing||null};
}
export function hasMissingPictures(e){
 const printings=[...(e.printings||[]),...(e.printing_claims||[])];
 return printings.length?printings.some(p=>!p.image&&!e.image):!e.image;
}
export function rarityKey(value){const e=value.e||value;return value.rarity_key||e.rarity_key||(e.rarity_state==='not_printed'?'not_printed':e.rarity_state==='unresolved'?'unresolved':e.rarity_code||'unresolved');}
export function inCategory(r,c){if(!c||c==='all')return true;if(c==='cameo')return isCameo(r.e);if(c==='jumbo')return r.size==='oversized'||r.material==='metal'||r.research&&r.e.category==='jumbo';return r.size!=='oversized'&&r.material!=='metal'&&!isCameo(r.e)&&!(r.research&&r.e.category==='jumbo');}
const rank=e=>e.rarity_order??({common:0,C:0,uncommon:10,U:10,rare:20,R:20,rare_holo:21,RR:25,double_rare:25,RRR:27,ultra_rare:30,SR:30,illustration_rare:40,AR:40,CHR:40,special_illustration_rare:50,SAR:50,CSR:50,hyper_rare:60,UR:60,MUR:70}[e.rarity_code]??80);
// A relative printing sequence breaks same-card date ties; it never supplies a date.
export function comparePrintings(a,b,direction=1){
 const research=p=>!!p.research||['provisional','disputed','excluded'].includes(p.collection_status);
 const order=p=>p.print_state==='1999-2000-copyright'?3:p.edition==='first_edition'?0:p.layout==='shadowless'?1:2;
 return Number(research(a))-Number(research(b))||(order(a)-order(b))*direction||String(a.label||'').localeCompare(String(b.label||''));
}
export function compareRows(a,b,sort='pokedex',roster=new Map()){const x=a.e,y=b.e,dex=e=>e.subject_dex?.[0]||e.cameo_dex?.[0]||e.dex||9999;let order=sort==='pokedex'?dex(x)-dex(y):sort==='pokemon'?(roster.get(dex(x))||x.english).localeCompare(roster.get(dex(y))||y.english,'en'):sort==='rarity'?(a.rarity_order??rank(x))-(b.rarity_order??rank(y)):0;return order||compareDates(effectiveDate(a),effectiveDate(b),sort==='newest'?-1:1)||x.release.localeCompare(y.release,'en',{numeric:true})||String(x.number).localeCompare(String(y.number),'en',{numeric:true})||dex(x)-dex(y)||((x===y||x.id&&x.id===y.id)?comparePrintings(a,b,sort==='newest'?-1:1):0)||a.label.localeCompare(b.label);}
const dateFormats={month:new Intl.DateTimeFormat('en-GB',{month:'short',year:'numeric',timeZone:'UTC'}),day:new Intl.DateTimeFormat('en-GB',{day:'numeric',month:'short',year:'numeric',timeZone:'UTC'})};
export function dateLabel(e,p=null){if(p?.date_state==='unresolved_product_date')return 'Product date needs research';let v=p?.release_date||e.release_date||e.year;if(!v)return e.date_state==='sourced_regional_period'&&e.release_period?e.release_period:'Date needs research';v=String(v);const prefix=(!p?.release_date&&e.date_state==='provider_reference'||p?.date_state==='provider_reference')?'≈ ':'';if(v.length===4)return prefix+v;if(v.length===7)return prefix+dateFormats.month.format(new Date(v+'-01T00:00:00Z'));return prefix+dateFormats.day.format(new Date(v+'T00:00:00Z'));}
export function yearLabel(e,p=null){
 if(p?.date_state==='unresolved_product_date')return '';
 const [year]=dateParts(p?.release_date||e.release_date||e.year);
 if(year){const approximate=(!p?.release_date&&e.date_state==='provider_reference')||p?.date_state==='provider_reference';return (approximate?'≈ ':'')+year;}
 if(e.date_state!=='sourced_regional_period')return '';
 const years=[...new Set(String(e.release_period||'').match(/\b(?:19|20)\d{2}\b/g)||[])];
 return years.length<=2?years.join('–'):'';
}
export function uniqueProgress(list,copies){const groups=new Map();for(const r of list){if(r.research||['provisional','disputed','excluded','announced'].includes(r.e?.identity_status)||['provisional','disputed','excluded'].includes(r.collection_status))continue;const key=r.physical_key?JSON.stringify(r.physical_key):r.id;groups.set(key,groups.get(key)||!!copies.get(r.id)?.length);}return {total:groups.size,owned:[...groups.values()].filter(Boolean).length};}
function trustedProductUrl(value){try{const u=new URL(value);return u.protocol==='https:'&&['cardmarket.com','www.cardmarket.com'].includes(u.hostname)&&!u.username&&!u.password&&!u.port&&/^\/(?:en|de|fr|es|it)\/Pokemon\/Products(?:\/Singles\/|$)/.test(u.pathname)?u.href:null;}catch{return null;}}
function baseMarketLink(e,p){
 if(p?.market_confirmed&&p.market_match?.method==='collector_product_search'&&Number.isSafeInteger(p.price_product_id))return {url:trustedProductUrl(p.market_match.canonical_url)||('https://www.cardmarket.com/en/Pokemon/Products?'+new URLSearchParams({idProduct:p.price_product_id})),label:'Open matched Cardmarket product',exact:true};
 if(e.market_link_override&&/^https:\/\/(?:www\.)?cardmarket\.com\//.test(e.cardmarket_url||''))return {url:e.cardmarket_url,label:'Open Cardmarket listing',exact:false};
 if(p?.market_confirmed&&Number.isSafeInteger(p.price_product_id))return {url:'https://www.cardmarket.com/en/Pokemon/Products?'+new URLSearchParams({idProduct:p.price_product_id}),label:'Open matched Cardmarket product',exact:true};
 if(!e.market_link_override&&/^https:\/\/(?:www\.)?cardmarket\.com\//.test(p?.cardmarket_url||''))return {url:p.cardmarket_url,label:'Open Cardmarket listing',exact:true};
 if(/^https:\/\/(?:www\.)?cardmarket\.com\//.test(e.cardmarket_url||''))return {url:e.cardmarket_url,label:'Open card on Cardmarket',exact:false};
 const name=(!e.market_link_override&&p?.market_name)||e.market_name||e.english||e.name;
 const code=e.market_code||e.cardmarket_code,number=e.market_number||e.number;
 const query=(!e.market_link_override&&p?.cardmarket_search)||e.cardmarket_search||(code?`${name} (${code} ${number})`:[name,number==='Unnumbered'?'':number,e.market_set_name||e.set_name].filter(Boolean).join(' '));
 return {url:'https://www.cardmarket.com/en/Pokemon/Products/Search?'+new URLSearchParams({searchString:query}),label:'Search Cardmarket',exact:false,query};
}

export const marketConditions=[['','Any condition'],['1','Mint'],['2','Near Mint+'],['3','Excellent+'],['4','Good+'],['5','Light Played+'],['6','Played+'],['7','Poor+']];
export function filteredProductUrl(value,e,p={},condition='3'){
 try{
  const url=new URL(value);
  if(url.protocol!=='https:'||!['cardmarket.com','www.cardmarket.com'].includes(url.hostname)||url.username||url.password||url.port)return value;
  if(!/\/Pokemon\/Products(?:\/Singles\/|$)/.test(url.pathname))return value;
  const lang={en:'1',de:'3',ja:'7',ko:'10'}[e.lang];if(lang)url.searchParams.set('language',lang);
  if(condition&&marketConditions.some(([v])=>v===String(condition)))url.searchParams.set('minCondition',String(condition));else url.searchParams.delete('minCondition');
  if(p.edition)url.searchParams.set('isFirstEd',p.edition==='first_edition'?'Y':'N');
  if(p.finish)url.searchParams.set('isReverseHolo',p.finish==='reverse_holo'?'Y':'N');
  return url.href;
 }catch{return value;}
}
export function offerFilterLabel(e,p={},condition='3'){
 return [({en:'English',de:'German',ja:'Japanese',ko:'Korean'})[e.lang],marketConditions.find(([v])=>v===String(condition))?.[1],p.edition==='first_edition'?'First Edition':p.edition?'Not First Edition':'',p.finish==='reverse_holo'?'Reverse holo':p.finish?'Not reverse holo':''].filter(Boolean).join(' · ');
}
export function marketLink(e,p,options={}){
 const link=baseMarketLink(e,p),url=filteredProductUrl(link.url,e,p,options.condition??'3');
 return {...link,url,offers:url!==link.url||/\/Products\/Singles\//.test(link.url),filterLabel:offerFilterLabel(e,p,options.condition??'3')};
}

export const sourceDate=s=>s.lang==='de'&&s.date_state==='provider_reference'?null:s.release_date;
export function sourceDateLabel(s){return s.lang==='de'&&s.date_state==='provider_reference'?'Regional date unconfirmed':dateLabel(s);}
export function compareSources(a,b,direction=1){
 let order=((a.era_order??99)-(b.era_order??99))*direction||String(a.series||'Other products').localeCompare(String(b.series||'Other products'));
 if(order)return order;
 if(a.sort_order!=null||b.sort_order!=null){order=(a.sort_order??100001)-(b.sort_order??100001);if(order)return order*direction;}
 const x=dateParts(sourceDate(a)),y=dateParts(sourceDate(b));
 for(let i=0;i<3;i++){
  if(x[i]==null||y[i]==null){
   if(i===0)return x[i]==null?(y[i]==null?String(a.name).localeCompare(String(b.name)):1):-1;
   const hint=a.sequence_hint&&b.sequence_hint?compareDates(a.sequence_hint,b.sequence_hint,direction):0;
   return hint||compareDates(sourceDate(a),sourceDate(b),direction)||a.name.localeCompare(b.name);
  }
  if(x[i]!==y[i])return (x[i]-y[i])*direction;
 }
 return a.name.localeCompare(b.name);
}
