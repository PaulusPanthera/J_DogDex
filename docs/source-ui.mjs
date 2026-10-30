// Source navigation never creates, renames or deduplicates physical printings.
export const SET_ROLES=new Set(['numbered_set','promo_series','numbered_series']);
export const PRODUCT_ROLES=new Set(['product','numbered_product','product_bundle','unresolved']);
export function sourceRoot(source,sources){
 const by=sources instanceof Map?sources:new Map(sources.map(s=>[s.id,s]));let s=typeof source==='string'?by.get(source):source,seen=new Set();
 while(s){const id=s.navigation_source_id||s.group_source_id||s.id;if(id===s.id)return s;if(seen.has(id))return s;seen.add(id);const next=by.get(id);if(!next)return s;s=next;}return null;
}
export function inSource(row,source,subset='all',sources=[]){
 if(!source)return true;const e=row.e||row,root=sourceRoot(source,sources)||source,id=root.id;
 const canonical=e.expansion_source_id||e.primary_source_id;
 const distributions=row.e?(row.distribution_source_ids||[]):[...(e.printings||[]),...(e.printing_claims||[])].flatMap(p=>p.distribution_source_ids||[]);
 const aliases=[...(row.sources||[]),...(e.sources||[])].some(s=>(sourceRoot(s.id,sources)||s).id===id);
 const match=canonical===id||distributions.includes(id)||(!e.expansion_source_id&&aliases);
 return match&&(subset==='all'||(e.subset_key||'main')===subset);
}
export function groupSources(rows,sources,lang,tab='sets',includeEmpty=true){
 const by=new Map(sources.map(s=>[s.id,s])),groups=new Map();
 const add=(s,r)=>{const root=sourceRoot(s,by);if(!root||root.lang!==lang||root.source_role==='source_alias_multi'||root.source_role==='product_bundle')return;const section=root.overview_section||(PRODUCT_ROLES.has(root.source_role)?'products':'sets');if(section!==tab)return;if(!groups.has(root.id))groups.set(root.id,{...root,items:new Map(),members:sources.filter(v=>(v.navigation_source_id||v.id)===root.id)});if(r)groups.get(root.id).items.set(r.id,r);};
 for(const r of rows){if(r.e.lang!==lang)continue;add(by.get(r.e.expansion_source_id||r.e.primary_source_id),r);for(const id of r.distribution_source_ids||[])add(by.get(id),r);}
 if(includeEmpty)for(const s of sources.filter(s=>s.lang===lang&&['manual','legacy_manual'].includes(s.state)))add(s);
 return [...groups.values()];
}
export function subsetSections(source,sources,rows){
 const root=sourceRoot(source,sources);if(!root)return [];
 const children=sources.filter(s=>s.source_role==='subset'&&s.parent_source_id===root.id).sort((a,b)=>(a.subset_order||10)-(b.subset_order||10)||a.name.localeCompare(b.name));
 if(!children.length)return [];
 const unique=new Map([['main',{key:'main',name:'Main Set',source_id:root.id}]]);
 for(const s of children)unique.set(s.subset_key,{key:s.subset_key,name:s.subset_name||s.name,source_id:s.id});
 return [{key:'all',name:'All cards'},...unique.values()].map(s=>({...s,count:new Set(rows.filter(r=>!r.research&&inSource(r,root,s.key,sources)).map(r=>r.id)).size}));
}
export function localizedScope(source,subset,lang,sources){
 const root=sourceRoot(source,sources);if(!root)return {source:null,subset:'all',missing:'source'};
 const family=root.canonical_expansion_id||root.canonical_set_id;
 const hits=sources.filter(s=>s.lang===lang&&(s.navigation_source_id||s.id)===s.id&&(s.canonical_expansion_id||s.canonical_set_id)===family);
 if(hits.length!==1)return {source:null,subset:'all',missing:'source'};
 const target=hits[0];if(['all','main'].includes(subset))return {source:target,subset,missing:null};
 if(sources.some(s=>s.parent_source_id===target.id&&s.subset_key===subset))return {source:target,subset,missing:null};
 return {source:target,subset:'all',missing:'subset'};
}
export function setDestination(entry,sources){return {source:sourceRoot(entry.expansion_source_id||entry.primary_source_id,sources),subset:entry.subset_key||'main'};}
