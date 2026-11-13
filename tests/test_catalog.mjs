import test from 'node:test';
import assert from 'node:assert/strict';
import {compareRows,compareDates,dateLabel,yearLabel,isFullArt,inCategory,uniqueProgress,pokemonIds,primaryPokemonIds,isCameo,marketLink} from '../static/catalog.mjs';
const e=(date,release='z',dex=37)=>({release_date:date,release,number:'1',dex,subject_dex:[dex],english:'Vulpix',rarity_code:'common'});
const r=(date,release,dex)=>({id:release,label:'Non-holo',e:e(date,release,dex),size:'standard',material:'paper'});
test('chronology compares full dates before alphabetical set names',()=>{const rows=[r('2023-10-06','Alphabet'),r('2023-03-31','Zebra'),r('2023-06-09','Middle')];assert.deepEqual(rows.sort((a,b)=>compareRows(a,b,'oldest')).map(x=>x.e.release),['Zebra','Middle','Alphabet']);assert.deepEqual(rows.sort((a,b)=>compareRows(a,b,'newest')).map(x=>x.e.release),['Alphabet','Middle','Zebra']);});
test('unknown dates sort last in both directions and partial precision stays visible',()=>{for(const direction of [1,-1])assert.ok(compareDates(null,'1999-12',direction)>0);assert.ok(compareDates('1999','1999-12')>0);assert.equal(dateLabel(e('1999-12')),'Dec 1999');assert.equal(dateLabel(e('2001')),'2001');assert.equal(dateLabel({...e('2023-01-20'),date_state:'provider_reference'}),'≈ 20 Jan 2023');});
test('gallery years preserve printing dates, uncertainty and regional ranges without a fabricated fallback',()=>{
 const card=e('2020-05-01');assert.equal(yearLabel(card),'2020');assert.equal(dateLabel(card),'1 May 2020');
 assert.equal(yearLabel(e('2002-07')),'2002');assert.equal(yearLabel(e('1999')),'1999');
 assert.equal(yearLabel(card,{release_date:'2022-10-14'}),'2022');
 assert.equal(yearLabel(card,{date_state:'unresolved_product_date'}),'');
 assert.equal(yearLabel({...card,date_state:'provider_reference'}),'≈ 2020');
 assert.equal(yearLabel({...card,date_state:'provider_reference'},{release_date:'2023-06-09',date_state:'documented'}),'2023');
 assert.equal(yearLabel(card,{release_date:'2023-06-09',date_state:'provider_reference'}),'≈ 2023');
 assert.equal(yearLabel(e(null)),'');
 assert.equal(yearLabel({...e(null),date_state:'sourced_regional_period',release_period:'Winter 2003/2004'}),'2003–2004');
 assert.equal(yearLabel({...e(null),date_state:'sourced_regional_period',release_period:'Summer 2006'}),'2006');
});
test('Pokémon numeric and alphabetical sorts use dates as secondary order',()=>{const roster=new Map([[37,'Vulpix'],[58,'Growlithe']]);const rows=[r('2002','b',37),r('2001','a',37),r('2003','c',58)];assert.deepEqual([...rows].sort((a,b)=>compareRows(a,b,'pokedex',roster)).map(x=>x.id),['a','b','c']);assert.deepEqual([...rows].sort((a,b)=>compareRows(a,b,'pokemon',roster)).map(x=>x.id),['c','a','b']);assert.deepEqual(pokemonIds({...e('2001'),cameo_dex:[58,37]}),[37,58]);});
test('full art is explicit and secret rarity alone is insufficient',()=>{assert.equal(isFullArt({rarity_code:'secret_rare'}),false);assert.equal(isFullArt({art_style:'full_art'}),true);});
test('a reviewed artwork correction overrides a legacy filter classification',()=>{assert.equal(isFullArt({art_style:'standard',rarity_family:'full_art'}),false);assert.equal(isFullArt({art_style:'full_art',rarity_family:'other'}),true);assert.equal(isFullArt({rarity_family:'full_art'}),false);});
test('researched promo chronology and complete V-UNION use actual independent targets',async()=>{
 const {readFileSync}=await import('node:fs');const catalog=JSON.parse(readFileSync(new URL('../data/catalog.json',import.meta.url),'utf8'));
 for(const lang of ['en','de']){
  const entries=['059','080','033'].map(number=>catalog.entries.find(e=>e.lang===lang&&e.release==='mep'&&e.number===number));
  const rows=entries.map(e=>({...e.printings.find(p=>p.size==='standard'),e}));
  assert.deepEqual([...rows].sort((a,b)=>compareRows(a,b,'oldest')).map(r=>r.e.number),['033','080','059']);
  assert.deepEqual([...rows].sort((a,b)=>compareRows(a,b,'newest')).map(r=>r.e.number),['059','080','033']);
  assert.ok(entries.every(e=>isFullArt(e)&&e.rarity_key==='promo'));
  const complete=catalog.entries.find(e=>e.lang===lang&&e.identifier_namespace==='composite');const panels=complete.component_entry_ids.map(id=>catalog.entries.find(e=>e.id===id));
  const physical=[complete,...panels].flatMap(e=>e.printings.map(p=>({...p,e})));const owned=new Map([[complete.printings[0].id,[{id:'one-jumbo-copy'}]]]);
  assert.deepEqual(uniqueProgress(physical,owned),{total:5,owned:1});
 }
});
test('cameos exclude tracked primary subjects, and duplicate copies do not inflate progress',()=>{const card={...r('2001','one'),e:{...e('2001'),cameo_dex:[58]}};assert.ok(inCategory(card,'standard'));assert.equal(inCategory(card,'cameo'),false);const cameo={...card,e:{...card.e,subject_dex:[],category:'cameo'}};assert.ok(inCategory(cameo,'cameo'));assert.equal(inCategory(cameo,'standard'),false);assert.deepEqual(primaryPokemonIds(cameo.e),[]);assert.equal(isCameo({...card.e,category:'cameo'}),false);const copies=new Map([['one',[{},{}]]]);assert.deepEqual(uniqueProgress([card,card,{...card,id:'pending',research:true}],copies),{total:1,owned:1});assert.ok(inCategory({...card,size:'oversized'},'jumbo'));});
test('Cardmarket uses exact known query or card name and respects manual corrections',()=>{const card={...e('1999'),english:'Growlithe',number:'28',set_name:'Base Set',cardmarket_search:'Growlithe (28 BS)'};assert.equal(new URL(marketLink(card).url).searchParams.get('searchString'),'Growlithe (28 BS)');assert.equal(new URL(marketLink({...card,cardmarket_search:''}).url).searchParams.get('searchString'),'Growlithe 28 Base Set');const direct='https://www.cardmarket.com/en/Pokemon/Products/Singles/Base-Set/Growlithe-V1-BS28';assert.ok(marketLink(card,{cardmarket_url:direct}).url.startsWith(direct+'?'));assert.equal(marketLink({...card,market_link_override:true,cardmarket_search:'Manual query'},{cardmarket_url:direct}).query,'Manual query');assert.equal(marketLink({...card,cardmarket_search:'',english:'Vulpix'},{market_name:'Alolan Vulpix VSTAR'}).query,'Alolan Vulpix VSTAR 28 Base Set');});

test('printing-specific marketplace queries retain World Championships identity',()=>{const card={...e('2016'),english:'N',number:'105'};const p={cardmarket_search:'N (WCD18 FCO 105)'};assert.equal(marketLink(card,p).query,p.cardmarket_search);assert.equal(marketLink({...card,market_link_override:true,cardmarket_search:'Manual query'},p).query,'Manual query');assert.equal(dateLabel(card,{release_date:'2023-06-09',date_state:'provider_reference'}),'≈ 9 Jun 2023');});
test('catalog UI exposes exact rarities, independent artwork, two editor sections and complete forms',async()=>{
 const {readFileSync}=await import('node:fs');const vm=await import('node:vm');const domain=await import('../static/catalog.mjs');const localization=await import('../static/localization.mjs');const sourceUI=await import('../static/source-ui.mjs');const appearance=await import('../static/appearance.mjs');const priceUI=await import('../static/prices.mjs');const {makeEditor}=await import('../static/editor-ui.mjs');const {makeMarketFinder}=await import('../static/market-ui.mjs');const {execFileSync}=await import('node:child_process');
 const root=new URL('../',import.meta.url);const fixture=JSON.parse(readFileSync(new URL('data/catalog.json',root),'utf8'));
 const code="import sys,json,tempfile;from pathlib import Path;sys.path.insert(0,sys.argv[1]);from dogdex.collector import Collection;temp=tempfile.TemporaryDirectory();store=Collection(Path(sys.argv[1]),temp.name);print(json.dumps(dict(view=store.editor_view(),state=store.state())))";
 const stored=JSON.parse(execFileSync('python3',['-c',code,root.pathname],{maxBuffer:150_000_000}).toString());
 const element=()=>({innerHTML:'',open:false,parentElement:null,classList:{add(){},remove(){}},addEventListener(){},showModal(){this.open=true;},close(){this.open=false;},append(){}});
 const app=element(),dialog=element(),toast=element(),els={'#app':app,'#dialog':dialog,'#toast':toast};
 const symbolUI=await import('../static/set-symbols.mjs');
 const context=vm.createContext({...symbolUI,...domain,...localization,...sourceUI,...appearance,...priceUI,makeEditor,makeMarketFinder,fixture,fixtureView:stored.view,state:stored.state,console,structuredClone,setTimeout,clearTimeout,URLSearchParams,Intl,Map,Set,localStorage:{getItem(){return null},setItem(){}},window:{scrollY:0,scrollTo(){}},document:{activeElement:null,querySelector:s=>els[s],addEventListener(){},body:element()}});
 const source=readFileSync(new URL('static/app.js',root),'utf8').replace(/^import[^\n]*\n/gm,'').replace(/boot\(\);\s*$/,'');vm.runInContext(source,context);vm.runInContext('catalog=fixture;user=state;serverView=fixtureView;token="test";rebuild();render();',context);
 const heldEntry=stored.view.entries.find(e=>e.printing_claims?.length&&e.identity_status==='documented');context.heldpid=heldEntry.printing_claims[0].id;context.heldeid=heldEntry.id;context.heldlang=heldEntry.lang;
 vm.runInContext("user.copies.push({id:'held-copy-fixture',printing_id:heldpid,price_minor:1234,currency:'EUR'});rebuild();clearFilters();ui.lang=heldlang;ui.view='collection';render();",context);
 assert.match(app.innerHTML,/€12\.34/);assert.equal(vm.runInContext('progress(filteredRows()).total',context),0);
 vm.runInContext("review(heldeid,'picture',heldpid);",context);assert.ok(dialog.innerHTML.includes(`value="${context.heldpid}" selected`));
 vm.runInContext("user.copies.pop();rebuild();clearFilters();ui.view='all';render();",context);
 for(const lang of ['en','de','ja','ko']){
  vm.runInContext(`ui.lang='${lang}';ui.view='all';ui.rarity='';ui.artwork='full_art';render();`,context);assert.match(app.innerHTML,/card-grid/);assert.doesNotMatch(app.innerHTML,/No matching cards/);
  for(const tab of ['cards','sets']){vm.runInContext(`ui.view='health';ui.health='${tab}';render();`,context);assert.match(app.innerHTML,/Backup &amp; Trash|Backup & Trash/);assert.match(app.innerHTML,/Sets & sources/);assert.doesNotMatch(app.innerHTML,/Printing research<\/button>/);}
 }
 for(const lang of ['en','de']){vm.runInContext(`ui.lang='${lang}';ui.view='all';ui.artwork='';ui.rarity='double_rare';render();`,context);assert.match(app.innerHTML,/value="double_rare" selected/);assert.ok(vm.runInContext('filteredRows().length',context)>0);assert.ok(vm.runInContext("filteredRows().every(r=>rarityKey(r)==='double_rare')",context));}
 vm.runInContext("ui.lang='en';ui.view='all';ui.rarity='';ui.artwork='';ui.q='World Championships 2018';render();",context);assert.equal(vm.runInContext('filteredRows().length',context),7);assert.ok(vm.runInContext('filteredRows().every(r=>r.world_championship_year===2018)',context));const world=stored.view.entries.flatMap(e=>e.printings).find(p=>p.world_championship_year===2018);context.worldpid=world.id;vm.runInContext('detail(worldpid);',context);assert.match(dialog.innerHTML,/not tournament legal/);assert.match(dialog.innerHTML,/2018 replica/);vm.runInContext('clearFilters();',context);
 const card=stored.view.entries.find(e=>e.lang==='en'&&e.release==='base1'&&e.number==='68');context.eid=card.id;context.pid=card.printings[1].id;
 vm.runInContext("review(eid,'picture',pid);",context);assert.ok(dialog.innerHTML.includes(`value="${context.pid}" selected`));assert.match(dialog.innerHTML,/Picture target/);
 vm.runInContext("review(eid,'card');",context);assert.match(dialog.innerHTML,/More card details/);assert.match(dialog.innerHTML,/Remove card/);assert.match(dialog.innerHTML,/name="cameo_dex"/);
 vm.runInContext("review(eid,'printings');",context);assert.match(dialog.innerHTML,/Add printing/);assert.match(dialog.innerHTML,/edit-printing/);
 vm.runInContext("setForm('de:base1');",context);assert.match(dialog.innerHTML,/1999-12/);assert.match(dialog.innerHTML,/Save source/);assert.match(dialog.innerHTML,/Remove source/);
 vm.runInContext("newCard('en:base1');",context);assert.match(dialog.innerHTML,/Add a printing now/);assert.match(dialog.innerHTML,/name="initial_finish"/);assert.match(dialog.innerHTML,/name="source_id"/);
 assert.equal(vm.runInContext('roster.has(133)||roster.has(403)',context),false);
});

test('a sourced regional period stays visible without inventing a sortable day',()=>{const card={...e(null),year:null,release_date:null,date_state:'sourced_regional_period',release_period:'Winter 2003/2004'};assert.equal(dateLabel(card),'Winter 2003/2004');assert.ok(compareDates(card.release_date,'2003-05-12')>0);assert.equal(dateLabel({...card,date_state:'manual_verified'}),'Date needs research');});


test('English Base Set editions use relative printing order instead of alphabetical labels',async()=>{
 const {comparePrintings}=await import('../static/catalog.mjs');
 const card={id:'base-growlithe-order',lang:'en',english:'Growlithe',dex:58,release:'base1',number:'28',release_date:'1999-01-09'};
 const variants=[
  {id:'copyright',label:'Non-holo · 1999-2000 copyright',edition:'unstamped',layout:'shadowed',print_state:'1999-2000-copyright'},
  {id:'first',label:'Non-holo · 1st edition · Shadowless',edition:'first_edition',layout:'shadowless',print_state:'standard'},
  {id:'shadowless',label:'Non-holo · Shadowless',edition:'unstamped',layout:'shadowless',print_state:'standard'},
  {id:'unlimited',label:'Non-holo · Unlimited',edition:'unlimited',layout:'shadowed',print_state:'standard'}
 ];
 const before=JSON.stringify(variants),rows=variants.map(p=>({...p,e:card})),expected=['first','shadowless','unlimited','copyright'];
 for(const sort of ['pokedex','oldest','pokemon'])assert.deepEqual([...rows].sort((a,b)=>compareRows(a,b,sort)).map(p=>p.id),expected);
 assert.deepEqual([...rows].sort((a,b)=>compareRows(a,b,'newest')).map(p=>p.id),[...expected].reverse());
 assert.deepEqual([...variants].sort(comparePrintings).map(p=>p.id),expected);
 const held={...rows[0],id:'research',research:true};
 for(const direction of [1,-1])assert.ok(comparePrintings(held,rows[0],direction)>0);
 assert.equal(JSON.stringify(variants),before);assert.equal(card.release_date,'1999-01-09');assert.ok(rows.every(r=>r.release_date===undefined));
 const dated={...rows[3],release_date:'1998-12-01'};
 assert.ok(compareRows(dated,rows[1],'oldest')<0,'A real printing date still takes priority');
});
