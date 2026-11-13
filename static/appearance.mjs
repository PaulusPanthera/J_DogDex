// Presentation only. Rarity, artwork and physical finish remain separate fields.
// Western symbols follow the official Scarlet & Violet checklist and rarity guide.
// https://www.pokemon.com/uk/news/pokemon-tcg-scarlet-and-violet-revamps-pokemon-tcg-card-aesthetic
// Older special rarities and Asian letter codes retain their labels rather than
// inheriting a modern Western symbol merely because the names sound similar.
const rarityNames={common:'Common',uncommon:'Uncommon',rare:'Rare',rare_holo:'Holo Rare',double_rare:'Double Rare',ultra_rare:'Ultra Rare',illustration_rare:'Illustration Rare',special_illustration_rare:'Special Illustration Rare',hyper_rare:'Hyper Rare',mega_hyper_rare:'Mega Hyper Rare',mega_attack_rare:'Mega Attack Rare',shiny_rare:'Shiny Rare',shiny_ultra_rare:'Shiny Ultra Rare',rainbow_rare:'Rainbow Rare',secret_rare:'Secret Rare',rare_holo_EX_uppercase:'Holo Rare EX',rare_holo_ex_lowercase:'Holo Rare ex (classic)',rare_holo_gx:'Holo Rare GX',rare_holo_v:'Holo Rare V',rare_holo_vmax:'Holo Rare VMAX',rare_holo_vstar:'Holo Rare VSTAR',rare_holo_lvx:'Holo Rare LV.X',rare_prime:'Prime',legend:'LEGEND',rare_break:'BREAK',amazing_rare:'Amazing Rare',radiant_rare:'Radiant Rare',shiny_rare_gx:'Shiny Rare GX',ace_spec:'ACE SPEC Rare',black_white_rare:'Black White Rare',promo:'Promo',not_printed:'No printed rarity',unresolved:'Unclassified'};
export function rarityDisplayLabel(code,lang,original){return ['en','de'].includes(lang)?rarityNames[code]||original||String(code):original||String(code);}
const starPath='M8 1.1 10.1 5.4 14.8 6.1 11.4 9.4 12.2 14.1 8 11.9 3.8 14.1 4.6 9.4 1.2 6.1 5.9 5.4Z';
const star=hollow=>`<svg viewBox="0 0 16 16" aria-hidden="true"><path d="${starPath}" fill="${hollow?'none':'currentColor'}" stroke="currentColor" stroke-width="${hollow?1.6:0.5}" stroke-linejoin="round"/></svg>`;
export function rarityAppearance(value){
 const e=value.e||value,code=value.rarity_key||e.rarity_key||(e.rarity_state==='not_printed'?'not_printed':e.rarity_state==='unresolved'?'unresolved':e.rarity_code||'unresolved');
 const original=value.rarity_label||e.rarity_label,label=rarityDisplayLabel(code,e.lang,original),western=['en','de'].includes(e.lang);
 const result={code,label,short:western?label:code,original,tone:'neutral',symbol:'',count:0};
 if(!western)return result;
 const modern=/^(?:sv|me)\d/.test(e.release||'')||/(?:^|:)(?:sv|me)\d/.test(e.rarity_namespace||'');
 if(code==='common'||code==='uncommon')return {...result,tone:'ink',symbol:code==='common'?'circle':'diamond',count:1};
 if(code==='rare'||code==='rare_holo')return {...result,tone:'ink',symbol:'star',count:1};
 if(code==='double_rare')return {...result,tone:'ink',symbol:'star',count:2};
 if(code==='ultra_rare'&&modern)return {...result,tone:'silver',symbol:'star',count:2};
 if(['illustration_rare','special_illustration_rare','hyper_rare'].includes(code))return {...result,tone:'gold',symbol:'star',count:{illustration_rare:1,special_illustration_rare:2,hyper_rare:3}[code]};
 return result;
}
export function rarityMarkup(value,esc,compact=false){
 const r=rarityAppearance(value);
 const glyph=r.symbol==='circle'?'<svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="4.5"/></svg>':r.symbol==='diamond'?'<svg viewBox="0 0 16 16" aria-hidden="true"><path d="m8 1.8 6.2 6.2L8 14.2 1.8 8Z"/></svg>':r.symbol==='star'?Array.from({length:r.count},()=>star(false)).join(''):'';
 return `<span class="rarity-badge rarity-${r.tone}" data-rarity="${esc(r.code)}" title="${esc(r.original&&r.original!==r.label?r.label+' · '+r.original:r.label)}" aria-label="Rarity: ${esc(r.label)}">${glyph?`<span class="rarity-symbols" aria-hidden="true">${glyph}</span>`:''}<span class="rarity-name">${esc(compact?r.short:r.label)}</span></span>`;
}
export function finishClass(printing){return {non_holo:'finish-non-holo',holo:'finish-holo',reverse_holo:'finish-reverse'}[printing?.finish]||'finish-unknown';}
