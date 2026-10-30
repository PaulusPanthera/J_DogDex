// Canonical identities are navigation metadata, never a language-release inference.
export const foldSet=v=>String(v||'').normalize('NFKD').replace(/\p{M}/gu,'').toLowerCase().replace(/[^\p{L}\p{N}]+/gu,' ').trim();
export function canonicalSet(value){return value?.canonical_set_id||((['en','de'].includes(value?.lang)?'western:':'regional:'+value?.lang+':')+(value?.release||value?.id||''));}
export function recognizedSetQuery(q,lang,sources){
 const needle=foldSet(q);if(!needle)return null;const available=sources.filter(s=>s.lang===lang&&s.source_role!=='source_alias_multi'&&s.source_role!=='product_bundle');
 const collapse=hits=>{const roots=new Set(hits.map(s=>s.navigation_source_id||s.id));if(roots.size!==1)return null;return hits.find(s=>s.id===[...roots][0])||hits.find(s=>s.source_role==='subset')||hits[0];};
 let hits=available.filter(s=>[s.name,s.release,...(s.subset_aliases||[])].some(v=>v&&foldSet(v)===needle));if(hits.length)return collapse(hits);
 hits=available.filter(s=>(s.aliases||[]).some(v=>v&&foldSet(v)===needle));if(hits.length)return collapse(hits);
 if(needle.length>=3)hits=available.filter(s=>(['numbered_set','promo_series','numbered_series','subset'].includes(s.source_role)||!s.source_role&&s.state==='catalog_release')&&[s.name,s.release].some(v=>v&&foldSet(v).startsWith(needle)));return collapse(hits);
}
export function equivalentSource(source,lang,sources){if(!source)return null;const hits=sources.filter(s=>s.lang===lang&&canonicalSet(s)===canonicalSet(source));return hits.length===1?hits[0]:null;}
const num=v=>String(v||'').trim().toLowerCase().replace(/^0+(?=\d)/,'');
const subject=e=>JSON.stringify([...(e.subject_dex||[e.dex])].sort((a,b)=>a-b));
export function equivalentCard(entry,lang,entries){if(!entry||entry.identifier_namespace==='unnumbered'||/^unnumbered$/i.test(entry.number||''))return null;const hits=entries.filter(e=>e.lang===lang&&canonicalSet(e)===canonicalSet(entry)&&num(e.number)===num(entry.number)&&(e.identifier_namespace||'collector')===(entry.identifier_namespace||'collector')&&subject(e)===subject(entry)&&e.category===entry.category);return hits.length===1?hits[0]:null;}
const physical=p=>p.physical_key?.slice(1)||[p.finish,p.pattern,p.edition,p.layout,p.size,p.material,p.stamps_json||'[]',p.print_state];
export function equivalentPrinting(printing,entry){if(!printing||!entry)return null;const key=JSON.stringify(physical(printing)),hits=[...entry.printings,...(entry.printing_claims||[])].filter(p=>JSON.stringify(physical(p))===key);return hits.length===1?hits[0]:null;}
