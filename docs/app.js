import {setSymbolMarkup} from './set-symbols.mjs';
import {sourceRoot,inSource,groupSources,subsetSections,localizedScope,setDestination} from './source-ui.mjs';
import {canonicalSet,recognizedSetQuery,equivalentSource,equivalentCard,equivalentPrinting} from './localization.mjs';
import {makeEditor} from './editor-ui.mjs?v=1.8.12';
import {priceMarkup,pricePreview} from './prices.mjs';
import {rarityMarkup,finishClass,rarityDisplayLabel} from './appearance.mjs';
import {makeMarketFinder} from './market-ui.mjs';
import {compareRows,compareDates,dateLabel,yearLabel,effectiveDate,pokemonIds,primaryPokemonIds,isCameo,isFullArt,inCategory,uniqueProgress,marketLink,rarityKey,compareSources,sourceDateLabel} from './catalog.mjs?v=1.8.11';
const $=s=>document.querySelector(s);
const readOnly=document.documentElement?.dataset?.readonly==='true';
let marketPrices={},publishedAt=null;
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const paths={sidebar:'M3 4h18v16H3z M9 4v16 M5.5 8h1 M5.5 12h1 M5.5 16h1',cards:'M4 3h13v16H4z M8 7h13v16H8',collection:'M4 5h16v15H4z M4 9h16 M9 9v11',heart:'M20.5 5.5a5 5 0 0 0-7 0L12 7l-1.5-1.5a5 5 0 0 0-7 7L12 21l8.5-8.5a5 5 0 0 0 0-7Z',box:'M3 7l9-4 9 4v11l-9 4-9-4z M3 7l9 4 9-4 M12 11v11 M7 5l10 4',gear:'M9 3h6l1 4 4 1v6l-4 1-1 5H9l-1-5-4-1V8l4-1z M15 11a3 3 0 1 1-6 0 3 3 0 0 1 6 0',plus:'M12 5v14 M5 12h14',search:'M20 20l-5-5 M17 10a7 7 0 1 1-14 0 7 7 0 0 1 14 0',close:'M5 5l14 14 M19 5L5 19',edit:'M15 4l5 5 M4 20l4-1L21 6l-4-4L4 15z',trash:'M4 6h16 M9 6V3h6v3 M6 6l1 15h10l1-15 M10 10v7 M14 10v7',download:'M12 3v12 M7 10l5 5 5-5 M4 16v5h16v-5',arrow:'M15 5l-7 7 7 7',link:'M14 3h7v7 M21 3l-9 9 M10 5H4v15h15v-6',check:'M4 12l5 5L20 6'};
const icon=(name,fill=false)=>`<svg viewBox="0 0 24 24" fill="${fill?'currentColor':'none'}" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="${paths[name]||paths.cards}"/></svg>`;
const languages={en:'English',de:'German',ja:'Japanese',ko:'Korean'};
const conditionLabels={unassessed:'Unassessed',mint:'Mint',near_mint:'Near mint',excellent:'Excellent',good:'Good',light_played:'Light played',played:'Played',poor:'Poor'};
const pretty=x=>String(x||'').replaceAll('_',' ').replace(/\b\w/g,c=>c.toUpperCase());
const formatMoney=(minor,currency)=>new Intl.NumberFormat('en-GB',{style:'currency',currency}).format(minor/(['JPY','KRW'].includes(currency)?1:100));
const imgUrl=image=>!image?null:image.startsWith('/user-images/')?(readOnly?'.'+image:image):(readOnly?'./images/':'/images/')+encodeURIComponent(image);
const imageMarkup=(image,alt,cls='')=>image?`<img class="${cls}" src="${esc(imgUrl(image))}" alt="${esc(alt)}" loading="${cls.includes('detail-image')?'eager':'lazy'}" ${cls.includes('detail-image')?'fetchpriority="high"':''} decoding="async">`:`<div class="placeholder ${cls}" role="img" aria-label="Catalog picture unavailable">◇<small>Catalog picture<br>not available yet</small></div>`;
let prefs={};try{const saved=JSON.parse(localStorage.getItem('dogdex-view-v1')||'{}');if(saved&&typeof saved==='object'&&!Array.isArray(saved))prefs=saved;}catch{}
const ui={lang:prefs.lang||'en',view:prefs.view||'all',sort:prefs.sort||'pokedex',rarity:prefs.rarity==='full_art'?'':prefs.rarity||'',category:['cameo','jumbo'].includes(prefs.category)?prefs.category:'all',pokemon:prefs.pokemon||'',pending:prefs.pending!==false,q:'',source:null,subset:'all',sourcesTab:'sets',limit:96,health:'cards',issue:'',browseOpen:false,sidebarCollapsed:prefs.sidebarCollapsed===true,artwork:prefs.artwork||(prefs.rarity==='full_art'?'full_art':'')};
let catalog,user,token,serverView=null,sourceRecords=[],entries=[],rows=[],byEntry=new Map(),byPrinting=new Map(),copies=new Map(),wishes=new Set(),roster=new Map(),toastTimer,speciesScrollTop=0,searchIndex=new WeakMap();
let modal={kind:null,id:null,entryId:null,printingId:null,tab:'identity'};
const persist=()=>{try{localStorage.setItem('dogdex-view-v1',JSON.stringify({lang:ui.lang,view:ui.view,sort:ui.sort,rarity:ui.rarity,category:ui.category,pokemon:ui.pokemon,pending:ui.pending,artwork:ui.artwork,sidebarCollapsed:ui.sidebarCollapsed}));}catch{}};
function rebuild(){
 entries=serverView?.entries||catalog.entries;sourceRecords=serverView?.sources||[];if(ui.source)ui.source=sourceRoot(ui.source.id,sourceRecords)||null;byEntry=new Map(entries.map(e=>[e.id,e]));rows=[];byPrinting=new Map();copies=new Map();wishes=new Set();const aliases=new Map(entries.flatMap(e=>Object.entries(e.printing_aliases||{})));for(const r of user.wishlist)wishes.add(aliases.get(r.printing_id)||r.printing_id);roster=new Map(catalog.roster.map(r=>[r.dex,r.name]));
 searchIndex=new WeakMap();for(const e of entries)searchIndex.set(e,searchText(e));
 for(const c of user.copies){const pid=aliases.get(c.printing_id)||c.printing_id;if(!copies.has(pid))copies.set(pid,[]);copies.get(pid).push(c);}
 for(const e of entries)for(const p of [...e.printings,...(e.printing_claims||[])]){const r={...p,e,research:!e.printings.some(x=>x.id===p.id),category:isCameo(e)?'cameo':p.size==='oversized'||p.material==='metal'?'jumbo':'standard',image:p.image||e.image,image_scope:p.image_scope||'entry'};rows.push(r);byPrinting.set(p.id,r);searchIndex.set(r,searchIndex.get(e)+' '+[(p.sources||[]).map(s=>s.name).join(' '),p.label||''].join(' ').toLowerCase());}
 for(const [alias,winner] of aliases)if(byPrinting.has(winner))byPrinting.set(alias,byPrinting.get(winner));
}

if(readOnly&&ui.view==='health')ui.view='all';
function progress(list){return uniqueProgress(list,copies);}

const bar=p=>`<div class="bar"><progress value="${p.owned}" max="${p.total||1}" aria-label="${p.owned} of ${p.total} printings collected"></progress></div>`;
function searchText(e){return [e.name,e.english,e.number,e.set_name,e.expansion_name,e.release,...(e.source_search_terms||[]),...(e.identity_aliases||[]),String(e.dex),...pokemonIds(e).map(d=>roster.get(d)),...(e.sources||[]).map(s=>s.name)].join(' ').toLowerCase();}
let queryScopeCache={};
function queryScope(){if(queryScopeCache.q!==ui.q||queryScopeCache.lang!==ui.lang||queryScopeCache.sources!==sourceRecords)queryScopeCache={q:ui.q,lang:ui.lang,sources:sourceRecords,value:recognizedSetQuery(ui.q,ui.lang,sourceRecords)};return queryScopeCache.value;}
function queryMatches(e,p=null){const q=ui.q.trim().toLowerCase();if(!q)return true;const text=(searchIndex.get(p||e)||searchText(e)+' '+[(p?.sources||[]).map(s=>s.name).join(' '),p?.label||''].join(' ').toLowerCase());if(text.includes(q))return true;const scope=queryScope();return !!scope&&inSource(p?.e?p:{e,...p},scope,scope.source_role==='subset'?scope.subset_key:'all',sourceRecords);}

function matchesSpecies(e){return !ui.pokemon||(ui.category==='all'?primaryPokemonIds(e):pokemonIds(e)).includes(Number(ui.pokemon));}
function matches(e,p=null,ignoreQuery=false){return e.lang===ui.lang&&(ignoreQuery||queryMatches(e,p))&&matchesSpecies(e)&&(!ui.artwork||(ui.artwork==='full_art'?isFullArt(e):ui.artwork==='unclassified'?!e.art_style:e.art_style==='standard'));}
function filteredRows(category=true,pending=false,{ignoreQuery=false,ignoreScope=false}={}){
 let list=rows.filter(r=>(!r.research||ui.view==='collection'||ui.view==='wishlist')&&matches(r.e,r,ignoreQuery)&&(!ui.rarity||rarityKey(r)===ui.rarity));
 if(ui.view==='collection')list=list.filter(r=>copies.get(r.id)?.length);if(ui.view==='wishlist')list=list.filter(r=>wishes.has(r.id));
 if(pending&&['all','sources'].includes(ui.view)&&ui.pending)list.push(...entries.filter(e=>e.identity_status!=='excluded'&&(!e.printings.length||e.printing_claims?.length||e.variant_claims?.some(x=>x.disposition!=='matched'))&&matches(e,null,ignoreQuery)&&(!ui.rarity||rarityKey(e)===ui.rarity)).map(e=>({e,id:e.id,image:e.image,research:true,label:e.identity_status==='disputed'?'Disputed · research':e.identity_status==='provisional'?'Identity / language unconfirmed':e.identity_status==='announced'?'Announced · unreleased':'Printing claims need research',distribution_source_ids:[...new Set(e.printing_claims?.flatMap(p=>p.distribution_source_ids||[])||[])],size:e.category==='jumbo'||e.variant_claims?.some(c=>c.normalized_partial?.size==='oversized')?'oversized':'standard',material:'paper'})));
 if(ui.source&&!ignoreScope)list=list.filter(r=>inSource(r,ui.source,ui.subset,sourceRecords));if(category)list=list.filter(r=>inCategory(r,ui.category));return list.sort((a,b)=>compareRows(a,b,ui.sort,roster));
}

function spending(list){const totals={},ids=list?new Set(list.filter(r=>byPrinting.has(r.id)).map(r=>r.id)):null;let count=0;for(const c of user.copies){if(byPrinting.get(c.printing_id)?.e.lang!==ui.lang||ids&&!ids.has(c.printing_id))continue;count++;if(c.price_minor!=null)totals[c.currency]=(totals[c.currency]||0)+c.price_minor;}return {count,text:Object.entries(totals).map(([k,v])=>formatMoney(v,k)).join(' · ')||'—'};}

function filters(){const source=ui.view==='sources'&&!ui.source,sorts=source?[['oldest','Release date · oldest'],['newest','Release date · newest']]:[['pokedex','Pokémon # · release date'],['pokemon','Pokémon A–Z · release date'],['oldest','Release date · oldest'],['newest','Release date · newest'],['rarity','Rarity → release date']];const codes=new Map(entries.filter(e=>e.lang===ui.lang).map(e=>[rarityKey(e),rarityDisplayLabel(rarityKey(e),e.lang,e.rarity_label)]));for(const r of rows.filter(r=>r.e.lang===ui.lang))codes.set(rarityKey(r),rarityDisplayLabel(rarityKey(r),r.e.lang,r.rarity_label||r.e.rarity_label));const order=(catalog.rarity_options?.[ui.lang]||[]).map(r=>r.code);const rare=[...codes].sort((a,b)=>(order.indexOf(a[0])<0?999:order.indexOf(a[0]))-(order.indexOf(b[0])<0?999:order.indexOf(b[0])));
 return `<div class="filters"><div class="search">${icon('search')}<input id="search" type="search" placeholder="Search card, number or source…" value="${esc(ui.q)}" aria-label="Search cards"></div><select id="sort" aria-label="Sort cards">${sorts.map(([v,n])=>`<option value="${v}" ${ui.sort===v||source&&!['oldest','newest'].includes(ui.sort)&&v==='oldest'?'selected':''}>${n}</option>`).join('')}</select><select id="rarity" aria-label="Filter rarity"><option value="">All rarities</option>${rare.map(([code,label])=>`<option value="${esc(code)}" ${ui.rarity===code?'selected':''}>${esc(label)}</option>`).join('')}</select><select id="artwork" aria-label="Filter artwork">${[['','All artwork'],['full_art','Full Art'],['standard','Standard artwork'],['unclassified','Not classified']].map(([v,n])=>`<option value="${v}" ${ui.artwork===v?'selected':''}>${n}</option>`).join('')}</select></div>`;}
function matchesScope(e){return (!ui.source||inSource(e,ui.source,ui.subset,sourceRecords))&&matchesSpecies(e)&&(ui.category==='cameo'?isCameo(e):ui.category==='jumbo'?e.category==='jumbo'||e.printings.some(p=>p.size==='oversized'||p.material==='metal')||e.variant_claims?.some(c=>c.normalized_partial?.size==='oversized'):true);}
function scopeLabel(){const species=roster.get(Number(ui.pokemon)),category=ui.category==='cameo'?'Cameos':ui.category==='jumbo'?'Jumbo / special':'';return [category,species].filter(Boolean).join(' · ')||'All Pokémon';}
const pokemonGenerations=[
 {generation:'I',region:'Kanto',max:151},{generation:'II',region:'Johto',max:251},
 {generation:'III',region:'Hoenn',max:386},{generation:'IV',region:'Sinnoh',max:493},
 {generation:'V',region:'Unova',max:649},{generation:'VI',region:'Kalos',max:721},
 {generation:'VII',region:'Alola',max:809},{generation:'VIII',region:'Galar',max:905},
 {generation:'IX',region:'Paldea',max:1025}
];
function sidebarBrowse(){
 const select=(key,label,active,dex='')=>`<button id="browse-${key}" class="browse-item ${active?'active':''}" data-action="browse" data-scope="${key}" aria-pressed="${active}">${dex?`<span class="species-number">${dex}</span>`:''}<span>${esc(label)}</span></button>`;
 const groups=pokemonGenerations.map((g,i)=>{
  const min=i?pokemonGenerations[i-1].max:0,species=catalog.roster.filter(r=>r.dex>min&&r.dex<=g.max);
  if(!species.length)return '';
  return `<section class="species-generation" aria-labelledby="generation-${g.generation}"><h2 id="generation-${g.generation}" class="species-generation-label">Gen ${g.generation}<span> · ${g.region}</span></h2>${species.map(r=>select(String(r.dex),r.name,String(r.dex)===String(ui.pokemon),String(r.dex).padStart(3,'0'))).join('')}</section>`;
 }).join('');
 return `<section class="sidebar-browse ${ui.browseOpen?'expanded':''}" aria-label="Browse Pokémon"><button id="browse-toggle" class="browse-toggle" data-action="browse-toggle" aria-expanded="${ui.browseOpen}" aria-controls="browse-panel"><span>Browse Pokémon</span><strong>${esc(scopeLabel())}</strong><span aria-hidden="true">⌄</span></button><div id="browse-panel" class="browse-panel"><div class="browse-specials">${select('all','All Pokémon',!ui.pokemon)}${select('cameo','Cameos',ui.category==='cameo')}${select('jumbo','Jumbo / special',ui.category==='jumbo')}</div><div id="species-list" class="species-list" aria-label="Species">${groups}</div></div></section>`;
}
function sidebarToggle(){return `<button id="sidebar-toggle" class="sidebar-toggle" data-action="sidebar-toggle" aria-controls="species-sidebar" aria-expanded="${!ui.sidebarCollapsed}" aria-label="${ui.sidebarCollapsed?'Show':'Hide'} Pokémon sidebar" title="${ui.sidebarCollapsed?'Show':'Hide'} Pokémon sidebar">${icon('sidebar')}</button>`;}
function sidebarBrand(){return `<div class="sidebar-brand"><span class="sidebar-brand-mark" aria-hidden="true"><img src="${readOnly?'./':'/'}brand/growlithe.svg" alt="" width="30" height="26"></span><span>DogDex</span></div>`;}
function headerUtilities(){
 const updated=publishedAt?.slice(0,10),status=readOnly?`Read-only${updated?' · Updated '+updated:''}`:'Saved on this PC';
 return `<div class="header-utilities" role="group" aria-label="Application status">${readOnly?'':`<button id="nav-health" class="header-health ${ui.view==='health'?'active':''}" data-action="view" data-view="health" aria-label="Data health" title="Data health" ${ui.view==='health'?'aria-current="page"':''}>${icon('gear')}<span>Data health</span></button>`}<span class="save-status ${readOnly?'is-readonly':''}" title="${esc(status)}"><i aria-hidden="true"></i><span>${esc(status)}</span></span></div>`;
}
function applySidebarState(){
 const shell=$('.shell'),side=$('#species-sidebar'),button=$('#sidebar-toggle');
 shell?.classList.toggle('sidebar-hidden',ui.sidebarCollapsed);
 if(side)side.hidden=ui.sidebarCollapsed;
 if(button){button.setAttribute('aria-expanded',String(!ui.sidebarCollapsed));button.setAttribute('aria-label',(ui.sidebarCollapsed?'Show':'Hide')+' Pokémon sidebar');button.title=(ui.sidebarCollapsed?'Show':'Hide')+' Pokémon sidebar';}
}

function activeFilters(){const chips=[];const add=(key,label)=>chips.push(`<button class="filter-pill" data-action="clear-filter" data-filter="${key}" aria-label="Clear ${esc(label)}">${esc(label)}${icon('close')}</button>`);if(ui.pokemon)add('pokemon',roster.get(Number(ui.pokemon))||'Pokémon');if(ui.category!=='all')add('category',ui.category==='cameo'?'Cameos':'Jumbo / special');if(ui.q.trim())add('q','Search: '+ui.q.trim());if(ui.source)add('source',ui.source.name);if(ui.view==='health'){if(ui.health!=='sets'&&ui.issue)add('issue',({'printings':'Missing printings','images':'Missing pictures','dates':'Date needs checking','rarity':'Rarity needs checking','artwork':'Artwork not classified'})[ui.issue]||ui.issue);}else{if(ui.rarity){const r=rows.find(r=>r.e.lang===ui.lang&&rarityKey(r)===ui.rarity),e=entries.find(e=>e.lang===ui.lang&&rarityKey(e)===ui.rarity);add('rarity',rarityDisplayLabel(ui.rarity,ui.lang,r?.rarity_label||r?.e.rarity_label||e?.rarity_label||pretty(ui.rarity)));}if(ui.artwork)add('artwork',({'full_art':'Full Art','standard':'Standard artwork','unclassified':'Artwork not classified'})[ui.artwork]||ui.artwork);if(ui.view==='all'&&!ui.pending)add('pending','Verified printings only');}return chips.length?`<div class="active-filters" aria-label="Active filters">${chips.join('')}<button class="clear-filters" data-action="clear-filters">Clear all</button></div>`:'';}
function clearFilters(){clearTimeout(searchTimer);ui.q='';ui.pokemon='';ui.category='all';ui.rarity='';ui.artwork='';ui.issue='';ui.source=null;ui.subset='all';ui.pending=true;ui.limit=96;}
function resetButton(){return `<button data-action="clear-filters">Clear filters</button>`;}

function printingParts(label){return String(label||'').split(' · ').map(v=>v.trim().replaceAll('_',' ').replace(/^1999-2000-Copyright$/i,'1999–2000 copyright')).filter(Boolean);}
function printingBadges(label,printing){return printingParts(label).map((v,i)=>`<span class="printing-chip ${i===0?finishClass(printing):''}">${esc(v)}</span>`).join('<span class="sr-only"> · </span>');}
function card(r){
 const distributionUnverified=ui.view==='sources'&&ui.source?.overview_section==='products'&&r.distribution_bindings?.some(b=>b.source_id===ui.source.id&&b.basis==='card');
 const count=copies.get(r.id)?.length||0,title=r.e.lang==='en'?r.e.name:r.e.english,year=yearLabel(r.e,r),date=dateLabel(r.e,r);
 const ownership=count?`${count} ${count===1?'copy':'copies'} collected`:'Not collected';
 const research=r.research?(r.e.scope_review?.decision==='excluded_form'?'<span class="research-badge out-of-scope">Out of scope</span>':'<span class="research-badge">Research</span>'):'';
 const add=!readOnly?`<button class="add" data-action="${r.research?'review':'add'}" data-id="${r.research?r.e.id:r.id}" aria-label="${r.research?'Review printing research':'Add a physical copy'}">${icon(r.research?'edit':'plus')}</button>`:'';
 return `<article class="card ${count?'owned':'unowned'} ${r.research?'research-card':''}" aria-label="${esc(title)} ${esc(r.e.number)} · ${ownership}">
  <button class="card-visual" data-action="${r.research&&!byPrinting.has(r.id)?'review':'detail'}" data-id="${r.id}" aria-label="View ${esc(title)} ${esc(r.e.number)}, ${esc(r.label)} · ${ownership}">${imageMarkup(r.image,r.e.name)}</button>
  <div class="card-meta">
   <div class="card-heading"><div class="card-title" title="${esc(title)} ${esc(r.e.number)}"><span class="card-name">${esc(title)}</span><span class="collector-number">${/^Unnumbered$/i.test(r.e.number)?'—':'#'+esc(r.e.number)}</span></div>${pricePreview(marketPrices,r.id,esc)}</div>
   <div class="card-origin"><button class="card-source" data-action="card-source" data-id="${esc(r.e.id)}" title="${esc(r.e.set_name)}${r.e.subset_key!=='main'?' · '+esc(r.e.subset_name||''):''} · ${esc(date)}">${setSymbolMarkup(r.e,esc,readOnly)}<span class="card-set">${esc(r.e.expansion_name||r.e.set_name)}</span>${year?` <span class="card-date" title="${esc(date)}">${esc(year)}</span>`:''}</button></div>
   <div class="card-classification"><div class="card-tags">${rarityMarkup(r,esc,true)}<span class="printing-label" title="${esc(r.label)}">${printingBadges(r.label,r)}</span>${research}</div>${add}</div>
   ${distributionUnverified?'<span class="distribution-review" title="Card-level source assertion; the exact distributed printing is unverified.">Distribution unverified</span>':''}
   ${isCameo(r.e)?`<div class="artwork-credit">Cameo: ${(r.e.cameo_dex||[r.e.dex]).map(d=>esc(roster.get(d))).join(', ')}</div>`:''}
  </div></article>`;
}

function empty(title,description,button=''){return `<div class="empty"><h2>${title}</h2><p>${description}</p>${button}</div>`;}
function grid(){const list=filteredRows(true,true),p=progress(list),n=list.filter(r=>r.research).length,spent=!readOnly&&ui.view==='collection'?spending(list):null,line=`<div class="results-line"><span>${p.total.toLocaleString()} confirmed ${p.total===1?'printing':'printings'}${n?` · ${n} research ${n===1?'card':'cards'}`:''}${spent?` · ${spent.count} physical ${spent.count===1?'copy':'copies'} · Paid: ${esc(spent.text)}`:''}</span>${['all','sources'].includes(ui.view)?`<label class="check" title="Research cards have no verified collectible printing yet and do not count toward completion."><input id="pending" type="checkbox" ${ui.pending?'checked':''}>Show research cards</label>`:`<span>${p.owned} collected</span>`}</div>`;return line+(list.length?`<div class="card-grid">${list.slice(0,ui.limit).map(card).join('')}</div>${list.length>ui.limit?`<div class="page-more"><button data-action="more">Show ${Math.min(96,list.length-ui.limit)} more</button></div>`:''}`:empty('No matching cards.','Clear a filter or choose another language.',resetButton()));}

function sourceTabs(){return `<div class="source-tabs" role="group" aria-label="Source section">${[['sets','Expansions & series'],['products','Products']].map(([v,n])=>`<button data-action="source-tab" data-tab="${v}" aria-pressed="${ui.sourcesTab===v}" class="${ui.sourcesTab===v?'active':''}">${n}</button>`).join('')}</div>`;}
function sourceView(){
 const base=filteredRows(true,true,{ignoreQuery:true}),q=ui.q.trim().toLowerCase(),recognized=queryScope(),groups=groupSources(base,sourceRecords,ui.lang,ui.sourcesTab,!ui.rarity&&!ui.artwork&&!ui.pokemon&&ui.category==='all');
 const list=groups.filter(g=>!q||(recognized?(sourceRoot(recognized,sourceRecords)?.id===g.id):[g.name,g.release,g.series,...g.members.flatMap(m=>[m.name,...(m.aliases||[]),...(m.subset_aliases||[])])].join(' ').toLowerCase().includes(q)||[...g.items.values()].some(r=>queryMatches(r.e,r)))).sort((a,b)=>compareSources(a,b,ui.sort==='newest'?-1:1));
 const tabs=sourceTabs();if(!list.length)return tabs+empty('No sources match this view.','Clear a filter or choose another language.',resetButton());
 const series=new Map();for(const g of list.slice(0,ui.limit)){const key=g.series||(ui.sourcesTab==='products'?'Other products':'Other series / era unassigned');if(!series.has(key))series.set(key,[]);series.get(key).push(g);}
 return tabs+`<div class="results-line"><span>${list.length.toLocaleString()} ${ui.sourcesTab==='products'?'products':'expansions & series'}</span>${ui.sourcesTab==='products'?'<span>Distribution · existing card identities</span>':''}</div>`+[...series].map(([name,group])=>`<section class="source-series"><h2>${esc(name)}</h2><div class="sources-grid">${group.map(g=>{
 const items=[...g.items.values()],p=progress(items),images=[...new Set(items.map(x=>x.image).filter(Boolean))].slice(0,3),cover=g.image||g.members.find(m=>m.image)?.image,sections=subsetSections(g,sourceRecords,items).filter(x=>x.key!=='all'&&x.key!=='main'),selectedSubset=recognized&&sourceRoot(recognized,sourceRecords)?.id===g.id&&recognized.source_role==='subset'?recognized.subset_key:'all',n=items.filter(r=>r.research).length;
 return `<button class="source-card ${ui.sourcesTab==='products'?'product-card':''}" data-action="source" data-id="${esc(g.id)}" data-name="${esc(g.name)}" data-subset="${esc(selectedSubset)}"><div class="source-art ${cover?'source-cover-art':''}">${cover?imageMarkup(cover,g.name,'source-cover'):images.map(x=>imageMarkup(x,g.name)).join('')||'<div class="placeholder">◇</div>'}</div><h3>${esc(g.name)}</h3>${sections.length?`<div class="source-subsets">${sections.map(x=>esc(x.name)).join(' · ')}</div>`:''}<p>${esc(sourceDateLabel(g))} · ${p.total} ${ui.sourcesTab==='products'?'indexed printings':'printings'}${n?' · '+n+' research':''}</p>${ui.sourcesTab==='products'?'':bar(p)+`<div class="overview-line"><span>${p.owned} of ${p.total} collected</span><strong>${p.total?Math.round(p.owned/p.total*100):0}%</strong></div>`}</button>`;
 }).join('')}</div></section>`).join('')+(list.length>ui.limit?'<div class="page-more"><button data-action="more">Show more sources</button></div>':'');
}
function sourceContext(){
 if(!ui.source||ui.view!=='sources')return '';const s=sourceRoot(ui.source,sourceRecords)||ui.source,sections=subsetSections(s,sourceRecords,filteredRows(true,true,{ignoreScope:true}));
 const chips=sections.length?`<div class="subset-filter" role="group" aria-label="Expansion subset">${sections.map(x=>`<button class="${ui.subset===x.key?'active':''}" data-action="subset" data-subset="${esc(x.key)}" aria-pressed="${ui.subset===x.key}">${esc(x.name)} <span>${x.count}</span></button>`).join('')}</div>`:'';
 const members=sourceRecords.filter(v=>(v.navigation_source_id||v.id)===s.id),product=s.overview_section==='products',unverified=product?new Set(filteredRows(true,true,{ignoreScope:true}).filter(r=>r.distribution_bindings?.some(b=>b.source_id===s.id&&b.basis==='card')).map(r=>r.e.id)).size:0;
 const provenance=product?`<details class="source-provenance"><summary>Distribution sources & contents</summary><ul>${members.map(m=>`<li>${esc(m.name)} <small>${esc(m.id)}</small></li>`).join('')}</ul>${s.links?.length?`<p>${s.links.filter(u=>/^https?:\/\//.test(u)).map(u=>`<a href="${esc(u)}" target="_blank" rel="noopener noreferrer">Source ↗</a>`).join(' · ')}</p>`:''}</details>`:'';
 return `<div class="breadcrumb"><button data-action="source-back">${product?'Products':'Sources'}</button><span>/</span><strong>${esc(s.name)}</strong>${!readOnly?`<button class="source-edit" data-action="edit-source" data-id="${esc(s.id)}">Edit source / cover</button>`:''}</div>${chips}${unverified?`<p class="distribution-review">Distribution needs review · ${unverified} ${unverified===1?'card':'cards'}</p>`:''}${provenance}`;
}
function openSource(source,subset='all'){const s=sourceRoot(source,sourceRecords);if(!s)return;ui.view='sources';ui.source=s;ui.subset=subset;ui.sourcesTab=s.overview_section||'sets';ui.q='';ui.limit=96;render();window.scrollTo(0,0);}

function setForm(key){editor.source(key);}
function health(){return editor.health();}

function render(){
 const focused=document.activeElement?.id,position=focused==='search'?document.activeElement.selectionStart:null,scroll=window.scrollY,oldList=$('#species-list');if(oldList?.clientHeight)speciesScrollTop=oldList.scrollTop;persist();const languageRows=rows.filter(r=>r.e.lang===ui.lang),p=progress(languageRows),total=progress(rows);const navs=[['all','cards','All cards'],['collection','collection','My collection'],['wishlist','heart','Wishlist'],['sources','box','Sources']];const titles={all:'All cards',collection:'My collection',wishlist:'Wishlist',sources:'Sets & sources',health:'Data health'};
 $('#app').innerHTML=`<a class="skip-link" href="#main-content">Skip to cards</a><div class="shell ${ui.sidebarCollapsed?'sidebar-hidden':''} ${readOnly?'is-readonly':''}"><header class="catalog-header"><div class="topbar">${sidebarToggle()}<nav class="nav collection-nav" aria-label="Collection views">${navs.map(([v,i,n])=>`<button id="nav-${v}" class="${ui.view===v?'active':''}" data-action="view" data-view="${v}" ${ui.view===v?'aria-current="page"':''}>${icon(i)}${n}${v==='collection'?`<span class="nav-count">${p.owned}</span>`:v==='wishlist'?`<span class="nav-count">${languageRows.filter(r=>wishes.has(r.id)).length}</span>`:''}</button>`).join('')}</nav>${headerUtilities()}<div class="overview"><div class="overview-line"><span>Collected printings</span><strong>${p.owned.toLocaleString()} / ${p.total.toLocaleString()}</strong></div>${bar(p)}<div class="overall">${total.owned.toLocaleString()} / ${total.total.toLocaleString()} across all four ledgers</div></div></div><div class="catalog-toolbar"><div class="ledgers" aria-label="Language ledgers">${Object.entries(languages).map(([key,name])=>`<button id="lang-${key}" class="ledger ${ui.lang===key?'active':''}" data-action="language" data-lang="${key}" aria-label="${name} collection" title="${name}" aria-pressed="${ui.lang===key}"><img src="${readOnly?'./':'/'}flags/${key}.svg" alt=""><span>${name}</span></button>`).join('')}</div>${ui.view==='health'?'':filters()}</div></header><aside id="species-sidebar" class="sidebar" ${ui.sidebarCollapsed?'hidden':''}>${sidebarBrand()}${sidebarBrowse()}</aside><main id="main-content" class="main" tabindex="-1"><h1 class="sr-only">${esc(titles[ui.view]||titles.all)} · ${languages[ui.lang]}</h1>${sourceContext()}${ui.view==='health'?health():`${activeFilters()}${ui.view==='sources'&&!ui.source?sourceView():grid()}`}</main></div>`;
 const newList=$('#species-list');if(newList)newList.scrollTop=speciesScrollTop;if(focused==='search'){const el=$('#search');el?.focus({preventScroll:true});el?.setSelectionRange(position,position);}else if(focused){const mobileClosed=!ui.browseOpen&&window.matchMedia?.('(max-width:700px)').matches&&focused.startsWith('browse-');document.getElementById?.(mobileClosed?'browse-toggle':focused)?.focus({preventScroll:true});}window.scrollTo(0,scroll);
}

function toast(message,undo){const box=$('#toast');($('#dialog').open?$('#dialog'):document.body).append(box);clearTimeout(toastTimer);$('#toast').innerHTML=`<span>${esc(message)}</span>${undo?`<button data-action="undo-copy" data-id="${esc(undo)}">Undo</button>`:''}`;$('#toast').classList.add('show');toastTimer=setTimeout(()=>$('#toast').classList.remove('show'),6000);}
async function post(action,data,binary=false){
 if(readOnly)throw new Error('This is a read-only collection view. Edit DogDex on your PC.');
 const response=await fetch('/api/'+action,{method:'POST',headers:{'X-DogDex-Token':token,'Content-Type':binary?'application/zip':'application/json'},body:binary?data:JSON.stringify(data)});const result=await response.json();if(!response.ok)throw new Error(result.error||'Could not save this change.');if(result.state)user=result.state;if(result.prices)marketPrices=result.prices;if(result.result?.prices)marketPrices=result.result.prices;if(result.view)serverView=result.view;if(result.state||result.view)rebuild();return result.result;
}
function openDialog(title,subtitle,body,kind,id=null,entryId=null,headerExtra=''){if($('#toast').parentElement===$('#dialog'))document.body.append($('#toast'));modal={kind,id,entryId,tab:modal.tab||'identity'};if($('#dialog').dataset)$('#dialog').dataset.kind=kind;$('#dialog').setAttribute?.('aria-labelledby','dialog-title');$('#dialog').innerHTML=`<div class="modal-head"><div><h2 id="dialog-title">${esc(title)}</h2><p>${kind==='detail'&&byEntry.get(entryId)?`<button class="detail-source" data-action="card-source" data-id="${esc(entryId)}">${esc(byEntry.get(entryId).expansion_name||byEntry.get(entryId).set_name)}</button> · ${esc(dateLabel(byEntry.get(entryId),byPrinting.get(id)))}`:esc(subtitle||'')}</p></div>${headerExtra?`<div class="modal-context">${headerExtra}</div>`:''}<button class="quiet icon close" data-action="close" aria-label="Close dialog">${icon('close')}</button></div>${body}`;if(!$('#dialog').open)$('#dialog').showModal();}
function closeDialog(){$('#dialog').close();document.body.append($('#toast'));modal.kind=null;}
function detail(pid){
 const r=byPrinting.get(pid);if(!r)return;pid=r.id;
 const e=r.e,list=copies.get(pid)||[],cm=marketLink(e,r),switching=modal.kind==='detail'&&modal.entryId===e.id,title=e.lang==='en'?e.name:e.english;
 const variants=[...e.printings,...(e.printing_claims||[])];
 const options=variants.map(p=>{
  const count=copies.get(p.id)?.length||0,research=!e.printings.some(q=>q.id===p.id);
  return `<button class="printing-option ${finishClass(p)} ${p.id===pid?'active':''}" data-action="detail" data-id="${esc(p.id)}" aria-pressed="${p.id===pid}" title="${esc(p.label)}"><span class="variant-check" aria-hidden="true">${p.id===pid?icon('check'):''}</span><span class="variant-text">${esc(printingParts(p.label).join(' · '))}${research?'<small class="variant-research">Research</small>':''}</span>${count?`<span class="variant-owned" aria-label="${count} ${count===1?'copy':'copies'} owned">×${count}</span>`:''}</button>`;
 }).join('');
 const copyRows=readOnly?`<p class="public-owned">${list.length} ${list.length===1?'copy':'copies'} collected</p>`:list.map(c=>{
  const date=c.purchased_on?dateLabel({release_date:c.purchased_on}):'',notes=[c.notes,c.misprint_notes?'Misprint: '+c.misprint_notes:''].filter(Boolean).join(' · ');
  return `<div class="copy-item" data-copy-id="${esc(c.id)}"><div class="copy-description"><strong class="copy-condition">${esc(conditionLabels[c.condition]||'Unassessed')}</strong>${date?`<time datetime="${esc(c.purchased_on)}">${esc(date)}</time>`:''}${notes?`<p>${esc(notes)}</p>`:''}</div><span class="copy-cost">${c.price_minor==null?'<strong>—</strong>':`<strong>${esc(formatMoney(c.price_minor,c.currency))}</strong>`}<small>paid</small></span><div class="buttons"><button class="quiet" data-action="edit-copy" data-id="${esc(c.id)}" aria-label="Edit copy" title="Edit copy">${icon('edit')}</button><button class="quiet" data-action="remove-copy" data-id="${esc(c.id)}" data-printing="${pid}" aria-label="Remove copy" title="Remove copy">${icon('trash')}</button></div></div>`;
 }).join('');
 const addCopy=!readOnly&&!r.research?`<button class="add-copy" data-action="add" data-id="${pid}">${icon('plus')}Add copy</button>`:'';
 const header=`<div class="detail-native"><div class="detail-languages" aria-label="Card languages">${Object.entries(languages).map(([key,name])=>`<button class="${key===e.lang?'active':''}" data-action="language" data-lang="${key}" aria-label="${name} card" aria-pressed="${key===e.lang}" title="${name}"><img src="${readOnly?'./':'/'}flags/${key}.svg" alt=""></button>`).join('')}</div><span>${esc(e.name!==title?e.name:languages[e.lang])}</span><span class="detail-dex">#${String(e.dex).padStart(3,'0')}</span></div><div class="detail-facts">${rarityMarkup(r,esc)}${e.scope_review?.decision==='excluded_form'?'<span class="artwork-badge scope-label">Outside Zygarde 10% scope</span>':''}${e.art_style==='full_art'?'<span class="artwork-badge">Full Art</span>':''}</div>`;
 const imageStatus=r.image_review?.status==='verified'?'Verified printing image':r.image_review?.kind==='physical_photo'?'Printing image · unchecked':'Reference artwork';
 const linked=r.market_confirmed&&r.price_product_id;
 const market=`<section class="market-section" aria-label="Market reference"><div class="detail-section-heading"><h3>Market reference</h3>${!readOnly&&!r.research?`<button class="quiet market-find" data-action="market-find" data-id="${pid}">${icon(linked?'edit':'link')}${linked?'Change product':'Find Cardmarket product'}</button>`:''}</div>${priceMarkup(marketPrices,pid,esc)||`<p class="market-empty">${linked?'Price not cached':'Not linked'}</p>`}<a class="market-link" href="${esc(cm.url)}" target="_blank" rel="noopener noreferrer" title="${esc(cm.label)}">${icon('link')}${cm.exact?'Open listing':'Search Cardmarket'}</a></section>`;
 openDialog(title+' '+(/^Unnumbered$/i.test(e.number)?'· Unnumbered':'#'+e.number),`${e.set_name} · ${dateLabel(e,r)}`,
  `<div class="modal-body"><div class="detail"><div class="detail-media"><div class="detail-image-wrap">${imageMarkup(r.image,e.name,'detail-image')}</div>${!readOnly?`<div class="detail-image-caption"><span class="image-review-badge">${esc(imageStatus)}</span><button class="quiet btn-small" data-action="picture" data-id="${e.id}" data-printing="${pid}">${icon('edit')}Change picture</button></div>`:''}</div><div class="detail-info"><section class="printing-section" aria-label="Printing selection"><div class="detail-section-heading"><h3>Printing</h3>${!readOnly?`<button class="quiet detail-wish ${wishes.has(pid)?'wanted':''}" data-action="wish-detail" data-id="${pid}" aria-label="${wishes.has(pid)?'Remove from':'Add to'} wishlist" aria-pressed="${wishes.has(pid)}" title="${wishes.has(pid)?'Remove from':'Add to'} wishlist">${icon('heart',wishes.has(pid))}<span>Wishlist</span></button>`:''}</div><div class="detail-printings" role="group" aria-label="Choose a printing">${options}</div></section>${r.world_championship_year||r.date_note?`<p class="form-note printing-note">${esc(r.world_championship_year?r.notes:r.date_note)}</p>`:''}<section class="copy-list ${list.length?'has-copies':''}" aria-label="Your collection"><div class="detail-section-heading"><h3>Your copies${list.length?`<span class="copy-count" aria-label="${list.length} physical ${list.length===1?'copy':'copies'}">${list.length}</span>`:''}</h3>${addCopy}</div>${list.length?copyRows:'<p class="detail-empty">Not collected</p>'}</section>${market}${!readOnly?`<div class="detail-links"><button class="quiet" data-action="review" data-id="${e.id}" data-printing="${pid}">${icon('edit')}Edit catalog</button></div>`:''}</div></div></div>`,'detail',pid,e.id,header);

 if(switching)document.querySelector('.printing-option[aria-pressed="true"]')?.focus?.({preventScroll:true});
}

function switchLanguage(lang){
 if(!languages[lang]||lang===ui.lang)return;
 const previous=ui.lang,oldDetail=modal.kind==='detail'?byPrinting.get(modal.id):null;
 const recognized=queryScope(),source=ui.source||recognized;
 let message='';
 if(source){const selected=ui.source?ui.subset:recognized?.source_role==='subset'?recognized.subset_key:'all',localized=localizedScope(source,selected,lang,sourceRecords);ui.source=localized.source;ui.subset=localized.subset;if(recognized)ui.q='';if(localized.missing==='source')message='No linked '+languages[lang]+' source. Showing the '+languages[lang]+' ledger.';else if(localized.missing==='subset')message='This subset is not recorded in '+languages[lang]+'. Showing all cards in '+localized.source.name+'.';}
 ui.lang=lang;ui.limit=96;
 if(ui.rarity&&!rows.some(r=>r.e.lang===lang&&rarityKey(r)===ui.rarity))ui.rarity='';
 render();
 if(oldDetail){
  const e=equivalentCard(oldDetail.e,lang,entries),p=e&&equivalentPrinting(oldDetail,e);
  if(p)detail(p.id);
  else if(e&&(e.printings.length||e.printing_claims?.length)){detail((e.printings[0]||e.printing_claims[0]).id);message='This physical printing is not recorded in '+languages[lang]+'. Showing the card’s available printings.';}
  else{closeDialog();message='No matching '+languages[lang]+' card is recorded. Showing '+(ui.source?.name||'the '+languages[lang]+' ledger')+'.';}
 }
 if(message)toast(message);
}
function copyForm(pid,cid=null){
 const r=byPrinting.get(pid),c=cid?user.copies.find(c=>c.id===cid):null;if(!r)return;const unit=c?.currency||'EUR',price=c?.price_minor==null?'':c.price_minor/(['JPY','KRW'].includes(unit)?1:100);
 openDialog(cid?'Edit physical copy':'Add a physical copy',`${r.e.english} ${r.e.number} · ${r.label}`,`<div class="modal-body"><p class="form-note">${esc(r.e.set_name)} · ${languages[r.e.lang]} · ${esc(r.label)}</p><form id="copy-form"><div class="form-grid"><label>Card condition<select name="condition">${Object.entries(conditionLabels).map(([v,n])=>`<option value="${v}" ${(c?.condition||'unassessed')===v?'selected':''}>${n}</option>`).join('')}</select></label>${cid?'':`<label>Number of physical copies<input name="quantity" type="number" min="1" max="100" step="1" value="1" required></label>`}<label>Price paid · per copy<input name="price" inputmode="decimal" value="${price}" placeholder="Optional"></label><label>Currency<select name="currency">${['EUR','USD','GBP','JPY','KRW'].map(x=>`<option ${x===unit?'selected':''}>${x}</option>`).join('')}</select></label><label>Purchase date<input name="purchased_on" type="date" value="${esc(c?.purchased_on||'')}"></label><label>Misprint details<input name="misprint_notes" value="${esc(c?.misprint_notes||'')}" placeholder="Optional"></label><label class="wide">Notes<textarea name="notes" placeholder="Seller, storage location or other notes">${esc(c?.notes||'')}</textarea></label>${!cid&&wishes.has(pid)?'<label class="check wide"><input name="remove_from_wishlist" type="checkbox" checked>Remove this printing from my wishlist</label>':''}</div><p class="form-error" role="alert"></p><div class="form-footer"><button type="button" data-action="detail" data-id="${pid}">Cancel</button><button class="primary" type="submit">${cid?'Save changes':'Add to my collection'}</button></div></form></div>`,'copy',cid,pid);
}
function review(eid,tab='card',pid=null){editor.card(eid,tab,pid);}
function newCard(key=null){editor.card(null,'card',null,key);}
const editor=makeEditor({rarityLabel:rarityDisplayLabel,prices:()=>marketPrices,esc,pretty,icon,languages,ui,dateLabel,imageMarkup,matchesScope,activeFilters,resetButton,openDialog,closeDialog,post,render,toast,catalog:()=>catalog,taxonomy:()=>serverView?.printing_taxonomy,state:()=>user,entries:()=>entries,sources:()=>sourceRecords,trash:()=>serverView?.trash||[]});
const marketFinder=makeMarketFinder({esc,icon,languages,imageMarkup,post,openDialog,render,detail,toast,printing:pid=>byPrinting.get(pid),isOpen:()=>modal.kind==='market-finder'});
document.addEventListener('click',async event=>{
 const b=event.target.closest('[data-action]');if(!b)return;const a=b.dataset.action,id=b.dataset.id;
 try{
  if(!readOnly&&await marketFinder.click(a,b))return;
  if(await editor.click(a,b))return;
  if(readOnly&&a==='review'){const e=byEntry.get(id);if(e)openDialog(e.name+' · '+e.number,e.set_name,`<div class="modal-body">${imageMarkup(e.image,e.name,'detail-image')}<p class="image-note">Research entry · ${esc(pretty(e.identity_status||'documented'))}. Physical printing details need review on the PC.</p></div>`,'research',id);return;}
  if(a==='mobile-export'){b.disabled=true;try{const r=await post('mobile/export',{});toast(r.message);}finally{b.disabled=false;}return;}
  if(a==='market-refresh'){b.disabled=true;try{const r=await post('market/refresh',{});toast(`Cardmarket guide refreshed · ${Object.keys(r.prices?.printings||{}).length} confirmed printing matches.`);}finally{b.disabled=false;}return;}
  if(a==='view'){ui.view=b.dataset.view;ui.source=null;ui.subset='all';ui.limit=96;render();window.scrollTo(0,0);}
  else if(a==='language')switchLanguage(b.dataset.lang);
  else if(a==='sidebar-toggle'){ui.sidebarCollapsed=!ui.sidebarCollapsed;persist();applySidebarState();}
  else if(a==='browse-toggle'){ui.browseOpen=!ui.browseOpen;render();}
  else if(a==='browse'){const scope=b.dataset.scope;if(scope==='all')ui.pokemon='';else if(['cameo','jumbo'].includes(scope))ui.category=ui.category===scope?'all':scope;else if(/^\d+$/.test(scope))ui.pokemon=String(ui.pokemon)===scope?'':scope;ui.limit=96;ui.browseOpen=false;render();window.scrollTo(0,0);}
  else if(a==='clear-filters'){clearFilters();render();}
  else if(a==='clear-filter'){clearTimeout(searchTimer);const key=b.dataset.filter;if(key==='scope'){ui.pokemon='';ui.category='all';}else if(key==='category')ui.category='all';else if(key==='source'){ui.source=null;ui.subset='all';}else if(key==='pending')ui.pending=true;else ui[key]='';ui.limit=96;render();}
  else if(a==='detail')detail(id);
  else if(a==='add')copyForm(id);
  else if(a==='edit-copy'){const c=user.copies.find(c=>c.id===id);if(c)copyForm(c.printing_id,id);}
  else if(a==='wish'||a==='wish-detail'){await post('wishlist',{printing_id:id,wanted:!wishes.has(id)});render();if(a==='wish-detail'){detail(id);$('#dialog .detail-wish')?.focus({preventScroll:true});}}
  else if(a==='remove-copy'){await post('copy/remove',{id});render();detail(b.dataset.printing);toast('Physical copy removed.',id);}
  else if(a==='undo-copy'){await post('copy/undo',{id});render();if(modal.kind==='detail')detail(modal.id);toast('Physical copy restored.');}
  else if(a==='more'){ui.limit+=96;render();}
  else if(a==='source')openSource(id,b.dataset.subset||'all');
  else if(a==='card-source'){const e=byEntry.get(id),dest=e&&setDestination(e,sourceRecords);if(dest?.source){closeDialog();openSource(dest.source,dest.subset);}}
  else if(a==='subset'){ui.subset=b.dataset.subset;ui.limit=96;render();}
  else if(a==='source-tab'){ui.sourcesTab=b.dataset.tab;ui.source=null;ui.subset='all';ui.limit=96;render();}
  else if(a==='source-back'){ui.source=null;ui.subset='all';ui.limit=96;render();}
  else if(a==='health-tab'){ui.health=b.dataset.tab;ui.limit=96;render();}
  else if(a==='close')closeDialog();
  else if(a==='backup'){const link=document.createElement('a');link.href='/api/backup';link.download='DogDex_Collection_Backup.zip';link.click();toast('Collection backup downloaded.');}
  else if(a==='restore')$('#restore-file').click();
  else if(a==='reload')location.reload();
 }catch(error){toast(error.message||'Could not connect to DogDex.');}
});
let searchTimer;document.addEventListener('input',event=>{if(event.target.id==='search'){ui.q=event.target.value;ui.limit=96;clearTimeout(searchTimer);searchTimer=setTimeout(render,150);}});
document.addEventListener('change',async event=>{
 if(!readOnly&&marketFinder.change(event.target))return;
 if(editor.change(event.target))return;
 if(event.target.id==='pending'){ui.pending=event.target.checked;render();}
 if(event.target.id==='sort'){ui.sort=event.target.value;render();}
 if(event.target.id==='artwork'){ui.artwork=event.target.value;ui.limit=96;render();}
 if(event.target.id==='rarity'){ui.rarity=event.target.value;ui.limit=96;render();}
 if(event.target.id==='restore-file'&&event.target.files[0]){const file=event.target.files[0];if(!confirm('Replace your current collection with this backup? DogDex will save a copy of your current records first.'))return;try{await post('restore',await file.arrayBuffer(),true);render();toast('Collection backup restored.');}catch(error){toast(error.message);}}
});
$('#dialog').addEventListener('close',()=>{document.body.append($('#toast'));modal.kind=null;});
$('#dialog').addEventListener('click',event=>{if(event.target===$('#dialog')){const rect=$('#dialog').getBoundingClientRect();if(event.clientX<rect.left||event.clientX>rect.right||event.clientY<rect.top||event.clientY>rect.bottom)closeDialog();}});
$('#dialog').addEventListener('submit',async event=>{
 event.preventDefault();const form=event.target;if(!form.reportValidity())return;const fields=Object.fromEntries(new FormData(form));const submit=form.querySelector('button[type=submit],.primary');submit.disabled=true;const errorEl=form.querySelector('.form-error');errorEl.textContent='';
 try{
  if(!readOnly&&await marketFinder.submit(form,fields))return;
  if(await editor.submit(form,fields))return;
  if(form.id==='copy-form'){
   const pid=modal.entryId,editing=!!modal.id;const result=await post(editing?'copy/edit':'copy/add',{...fields,id:modal.id,printing_id:pid,quantity:Number(fields.quantity||1),remove_from_wishlist:form.querySelector('[name=remove_from_wishlist]')?.checked||false});render();detail(pid);toast(editing?'Copy saved.':`${result.ids?.length||1} physical ${result.ids?.length===1?'copy':'copies'} added.`);
  }
 }catch(error){errorEl.textContent=error.message||'Could not save your change.';submit.disabled=false;}
});
async function boot(){
 try{if(readOnly){const response=await fetch('./snapshot.json',{cache:'no-store'});if(!response.ok)throw new Error('The collection snapshot is unavailable.');const snapshot=await response.json();if(snapshot.format!=='dogdex-read-only-1')throw new Error('Unsupported collection snapshot.');catalog={roster:snapshot.roster,rarity_options:snapshot.rarity_options};serverView={entries:snapshot.entries,sources:snapshot.sources};user={copies:Object.entries(snapshot.ownership).flatMap(([pid,count])=>Array.from({length:count},(_,i)=>({id:pid+':'+i,printing_id:pid}))),wishlist:snapshot.wishlist.map(printing_id=>({printing_id}))};marketPrices=snapshot.prices;publishedAt=snapshot.published_at;rebuild();render();return;}const [a,b]=await Promise.all([fetch('/catalog.json'),fetch('/api/state')]);if(!a.ok||!b.ok)throw new Error('DogDex could not open its local files.');catalog=await a.json();const state=await b.json();user=state.state;serverView=state.view;token=state.token;marketPrices=state.prices||{};if(ui.pokemon&&!catalog.roster.some(r=>String(r.dex)===String(ui.pokemon)))ui.pokemon='';rebuild();render();}
 catch(error){$('#app').innerHTML=`<div class="loading"><h1>DogDex could not connect.</h1><p>${esc(error.message)}<br>Keep the DogDex window open, then try again.</p><button data-action="reload">Try again</button></div>`;}
}
document.addEventListener('error',event=>{const image=event.target;if(image?.matches?.('.set-symbol img'))image.closest('.set-symbol').hidden=true;},true);
boot();
