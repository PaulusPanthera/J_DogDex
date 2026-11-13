"""Language-aware display names; rarity, artwork and physical finish stay separate."""
import copy,re

REFERENCE_URLS=[
 'https://www.pokemon.com/uk/news/pokemon-tcg-scarlet-and-violet-revamps-pokemon-tcg-card-aesthetic',
 'https://www.pokemon.com/de/pokemon-news/neue-kartenaesthetik-in-der-pokemon-sammelkartenspiel-erweiterung-karmesin-and-purpur',
 'https://www.pokemon.com/cards?mo_ar=true',
 'https://www.pokemon.com/de/karten?mo_ar=true',
]
NAMES={
 'common':('Common','Häufig'), 'uncommon':('Uncommon','Nicht so häufig'),
 'rare':('Rare','Selten'), 'rare_holo':('Holo Rare','Selten, holografisch'),
 'double_rare':('Double Rare','Doppelselten'), 'ultra_rare':('Ultra Rare','Ultraselten'),
 'illustration_rare':('Illustration Rare','Selten, Illustration'),
 'special_illustration_rare':('Special Illustration Rare','Selten, besondere Illustration'),
 'hyper_rare':('Hyper Rare','Hyperselten'), 'mega_hyper_rare':('Mega Hyper Rare','Hyperselten, Mega'),
 'mega_attack_rare':('Mega Attack Rare','Selten, Mega-Attacke'),
 'shiny_rare':('Shiny Rare','Selten, Schillernd'), 'shiny_ultra_rare':('Shiny Ultra Rare','Ultraselten, Schillernd'),
 'rainbow_rare':('Rainbow Rare','Regenbogenselten'), 'secret_rare':('Secret Rare','Geheime Seltenheit'),
 'rare_holo_EX_uppercase':('Holo Rare EX','Selten, holografisch EX'),
 'rare_holo_ex_lowercase':('Holo Rare ex (classic)','Selten, holografisch ex (klassisch)'),
 'rare_holo_gx':('Holo Rare GX','Selten, holografisch GX'),
 'rare_holo_v':('Holo Rare V','Selten, holografisch V'),
 'rare_holo_vmax':('Holo Rare VMAX','Selten, holografisch VMAX'),
 'rare_holo_vstar':('Holo Rare VSTAR','Selten, holografisch VSTAR'),
 'rare_holo_lvx':('Holo Rare LV.X','Selten, holografisch LV.X'),
 'rare_prime':('Prime','Primus'), 'legend':('LEGEND','LEGENDE'),
 'rare_break':('BREAK','TURBO'), 'amazing_rare':('Amazing Rare','Atemberaubend'),
 'radiant_rare':('Radiant Rare','Selten, Strahlend'),
 'shiny_rare_gx':('Shiny Rare GX','Schillernd GX'),
 'ace_spec':('ACE SPEC Rare','ASS-KLASSE'), 'black_white_rare':('Black White Rare','Selten, Schwarz Weiß'),
 'promo':('Promo','Promo'),
}
REGIONAL={'C':'Common','U':'Uncommon','R':'Rare','RR':'Double Rare','RRR':'Triple Rare','SR':'Super Rare','AR':'Art Rare','SAR':'Special Art Rare','UR':'Ultra Rare','HR':'Hyper Rare','CHR':'Character Rare','CSR':'Character Super Rare','SSR':'Shiny Super Rare','S':'Shiny Rare','A':'Amazing Rare','MUR':'Mega Ultra Rare','MA':'Mega Attack Rare','P':'Promo'}
ORDER=list(NAMES)+list(REGIONAL)+['S_legacy_lvx']

def key(entry):
    state=entry.get('rarity_state')
    if state=='not_printed':return 'not_printed'
    if state!='known' or not entry.get('rarity_code'):return 'unresolved'
    if entry['rarity_code']=='S' and 'legacy' in entry.get('rarity_namespace',''):return 'S_legacy_lvx'
    return str(entry['rarity_code'])

def label(code,lang='en',namespace=''):
    if code=='not_printed':return 'No printed rarity' if lang!='de' else 'Keine Seltenheit aufgedruckt'
    if not code or code=='unresolved':return 'Needs identification'
    if code=='S_legacy_lvx':return 'S · Special Rare (LV.X)'
    if lang in ('ja','ko'):
        # S also identified Special Rare / LV.X in older eras. Never reinterpret it as Shiny.
        if code=='S' and 'legacy' in namespace:return 'S · Special Rare (LV.X)'
        return code+' · '+REGIONAL[code] if code in REGIONAL else code
    return NAMES.get(code,(str(code),str(code)))[1 if lang=='de' else 0]

def normalize(entry):
    code=key(entry)
    entry['rarity_key']=code
    entry['rarity_order']=ORDER.index(code) if code in ORDER else 1000 if code=='not_printed' else 1001
    if entry.get('rarity_family')=='full_art' and not entry.get('art_style'):
        entry.update(art_style='full_art',art_style_state='manual_verified',art_style_source='Migrated legacy manual artwork classification.')
    if entry.get('rarity_state') in ('known','not_printed'):
        entry.setdefault('original_rarity_label',entry.get('rarity_label'))
        entry['rarity_label']=label(code,entry['lang'],entry.get('rarity_namespace',''))
    return entry

def options(lang,entries=None,all_values=False):
    codes=set(NAMES if lang in ('en','de') else list(REGIONAL)+['S_legacy_lvx']) if all_values else {key(e) for e in entries or [] if e['lang']==lang}
    if all_values:codes|={'not_printed','unresolved'}
    ordered=sorted(codes,key=lambda code:(ORDER.index(code) if code in ORDER else 1000 if code=='not_printed' else 1001 if code=='unresolved' else 999,code))
    return [dict(code=code,label=label(code,lang)) for code in ordered]

def apply(catalog):
    changes=[]
    for e in catalog['entries']:
        normalize(e)
        if e['lang'] not in ('en','de') or e.get('art_style_state')=='manual_verified':continue
        modern=bool(re.match(r'^(?:sv|me)\d',e['release']))
        style=None
        if modern and e['rarity_code']=='double_rare':style='standard'
        elif modern and e['rarity_code'] in ('ultra_rare','illustration_rare','special_illustration_rare','hyper_rare'):style='full_art'
        source=dict(method='official_modern_rarity_artwork_definition',source_url=REFERENCE_URLS[1 if e['lang']=='de' else 0],inference=True,release=e['release'],rarity_code=e['rarity_code'])
        if e['release']=='me01' and e['number']=='188' and e['rarity_code']=='mega_hyper_rare':
            style='full_art';source=dict(method='visual_review_of_exact_regional_reference',image=e.get('image'),printed_identifier='188/132',note='The illustration extends across the card; exact artwork classification is independent of its Mega Hyper Rare tier.',source_url='https://www.pokemon.com/uk/pokemon-tcg/pokemon-cards/series/me01/188/')
        if style and e.get('art_style')!=style:
            changes.append(dict(entry_id=e['id'],lang=e['lang'],release=e['release'],number=e['number'],name=e['name'],before=e.get('art_style'),after=style,evidence=source))
            e.update(art_style=style,art_style_state='verified',art_style_source=source)
    catalog['artwork_refinements']=changes
    catalog['rarity_options']={lang:options(lang,all_values=True) for lang in ('en','de','ja','ko')}
    catalog['rarity_policy']=dict(reference_urls=REFERENCE_URLS,notes=[
     'Keep the original source code and language/era namespace; UI filters use the exact code, not one broad Rare bucket.',
     'Reverse holo is a finish, not a rarity. Full Art is an independently evidenced artwork attribute.',
     'Double Rare is distinct from Ultra Rare. Do not mark all ex/EX/GX/V cards as Full Art.',
     'Japanese and Korean abbreviations remain native codes; SR/SAR/UR are not globally translated into western rarity tiers.',
    ])
    return catalog
