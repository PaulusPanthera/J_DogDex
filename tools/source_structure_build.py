import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
"""One explicit source disposition per existing source; no physical tuple edits."""
import collections,copy,hashlib,json,re,unicodedata
from pathlib import Path

def fold(s):return re.sub(r'[^\w]+',' ',unicodedata.normalize('NFKC',s).casefold()).strip()

def main():
    root=Path(__file__).resolve().parents[1];out=root/'data/research/sources_185';c=json.loads((root/'data/catalog.json').read_text(encoding='utf-8'));baseline=json.loads((out/'baseline_184.json').read_text(encoding='utf-8'));sources={s['id']:s for s in baseline['sources']};entries={e['id']:e for e in c['entries']}
    refs={
     'cz':dict(url='https://press.pokemon.com/en-AU/MEDIA-ALERT-New-Pokemon-Trading-Card-Game-Crown-Zenith-Expansion-Intro',publisher='The Pokemon Company',finding='Crown Zenith includes the Galarian Gallery subset. Box promos are additional promotional cards, not part of the booster numbering.'),
     'shf':dict(url='https://www.pokemon.com/uk/pokemon-tcg/shining-fates',publisher='The Pokemon Company',finding='One Shining Fates expansion; its card database and checklist retain separately numbered Shiny Vault cards.'),
     'shf_sv':dict(url='https://www.pokemon.com/us/pokemon-tcg/pokemon-cards/series/swsh45sv/SV122',publisher='The Pokemon Company',finding='Official SV collector namespace within Shining Fates: Shiny Vault.'),
     'hf':dict(url='https://assets.pokemon.com/assets/cms2/pdf/trading-card-game/checklist/sm115_web_cardlist_en.pdf',publisher='The Pokemon Company',finding='Hidden Fates official checklist includes a Shiny Vault section with SV numbering.'),
     'tg9':dict(url='https://www.pokemon.com/uk/pokemon-tcg/sword-shield-brilliant-stars?section=overview',publisher='The Pokemon Company',finding='Official expansion overview identifies the 30-card Trainer Gallery as a subset.'),
     'tg10':dict(url='https://www.pokemon.com/uk/news/a-peek-at-the-cards-of-the-pokemon-tcg-sword-shield-astral-radiance-trainer-gallery',publisher='The Pokemon Company',finding='Official article identifies the Trainer Gallery as a subset with its own TG numbering.'),
     'tg11':dict(url='https://bulbapedia.bulbagarden.net/wiki/Lost_Origin_(TCG)',publisher='Bulbapedia',finding='The Trainer Gallery is an internal numbered section of Lost Origin.'),
     'tg12':dict(url='https://bulbapedia.bulbagarden.net/wiki/Silver_Tempest',publisher='Bulbapedia',finding='Silver Tempest lists Trainer Gallery as an internal numbered section.'),
     'cel':dict(url='https://www.pokemon.com/de/pokemon-sammelkartenspiel/celebrations',publisher='The Pokemon Company',finding='Western Celebrations includes the Classic Collection. Commercial product promos remain outside that numbered expansion.'),
     'cel_asia':dict(url='https://bulbapedia.bulbagarden.net/wiki/S8aP',publisher='Bulbapedia',finding='Japanese and Korean 25th anniversary reprint cards are distributed as separate promo packs; do not merge them into S8a.'),
     'lt_rc':dict(url='https://bulbapedia.bulbagarden.net/wiki/Legendary_Treasures_(TCG)',publisher='Bulbapedia',finding='Radiant Collection uses RC numbers inside Legendary Treasures; original card numbering is retained.'),
     'g_rc':dict(url='https://www.pokemon.com/de/pokemon-sammelkartenspiel/generationen',publisher='The Pokemon Company',finding='Official German expansion overview describes the additional 32-card special-art section; the Radiant Collection uses RC numbering.'),
     'pl_sh':dict(url='https://bulbapedia.bulbagarden.net/wiki/Platinum_(TCG)',publisher='Bulbapedia',finding='SH-numbered Shiny cards stay inside their own expansion. The numbering series is not a new expansion shared across eras.'),
     'col_sl':dict(url='https://bulbapedia.bulbagarden.net/wiki/Call_of_Legends_(TCG)',publisher='Bulbapedia',finding='SL-numbered Shiny Legendary cards remain inside Call of Legends.'),
     'lucario_box':dict(url='https://www.pokemon.com/uk/pokemon-tcg/product-gallery/lucario-vstar-premium-collection',publisher='The Pokemon Company',finding='The same product contains Lucario V, Lucario VSTAR and a separate oversized Lucario VSTAR. Size distinction is preserved.'),
     'cz_products':dict(url='https://press.pokemon.com/en-AU/MEDIA-ALERT-Pokemon-Trading-Card-Game-Crown-Zenith-Expansion-Released-',publisher='The Pokemon Company',finding='Crown Zenith product contents distinguish booster packs from separate Lucario, Shiny Zacian and Shiny Zamazenta promos.'),
     'etb_upc':dict(url='https://bulbapedia.bulbagarden.net/wiki/Elite_Trainer_Box_(TCG)',publisher='Bulbapedia',finding='The Zacian and Zamazenta ETB Plus products are separate from the North American UPC. The UPC includes both gold promos; an ETB Plus contains its respective one.'),
     'sf_sh':dict(url='https://bulbapedia.bulbagarden.net/wiki/Stormfront_(TCG)',publisher='Bulbapedia',finding='Stormfront has an internal SH-numbered Shiny section.'),
     'rr_rt':dict(url='https://bulbapedia.bulbagarden.net/wiki/Rising_Rivals_(TCG)',publisher='Bulbapedia',finding='Rising Rivals has an internal RT1–RT5 Rotom section, not a separate expansion.'),
     'sv_sh':dict(url='https://bulbapedia.bulbagarden.net/wiki/Supreme_Victors_(TCG)',publisher='Bulbapedia',finding='Supreme Victors retains its own SH7–SH9 section.'),
     'ar_sections':dict(url='https://assets.pokemon.com/assets/cms-de-de/pdf/tcg/checklists/PL4_Cardlist_Lo.pdf',publisher='The Pokemon Company',finding='Arceus checklist contains both AR1–AR9 and SH10–SH12 inside the expansion. No out-of-roster cards are added.'),
     'regional_sma':dict(url='https://pokemoncard.co.kr/card/97',publisher='Pokemon Korea',finding='Korean sma is a Sun & Moon starter set, not the Western Hidden Fates Shiny Vault.'),
    }
    for r in refs.values():r.update(checked_on='2026-10-30',scope='Source organization only; not a new printing-completeness assessment.')
    subsets=[
     ('swsh12.5gg','swsh12.5','galarian_gallery','Galarian Gallery','Galar-Galerie','GG','cz'),
     ('swsh9tg','swsh9','trainer_gallery','Trainer Gallery','Trainer Gallery','TG','tg9'),
     ('swsh10tg','swsh10','trainer_gallery','Trainer Gallery','Trainer Gallery','TG','tg10'),
     ('swsh11tg','swsh11','trainer_gallery','Trainer Gallery','Trainer Gallery','TG','tg11'),
     ('swsh12tg','swsh12','trainer_gallery','Trainer Gallery','Trainer Gallery','TG','tg12'),
     ('swsh4.5sv','swsh4.5','shiny_vault','Shiny Vault','Shiny Vault','SV','shf'),
     ('sma','sm115','shiny_vault','Shiny Vault','Shiny Vault','SV','hf'),
     ('cel25cc','cel25','classic_collection','Classic Collection','Classic Collection','original_reprint_numbers','cel'),
    ]
    relations=[];virtual=[]
    for child,parent,key,en,de,ns,ref in subsets:
     for lang in ('en','de'):
      sid=f'release:{lang}:{child}';pid=f'release:{lang}:{parent}'
      if sid not in sources and pid not in sources:continue
      relations.append(dict(source_id=sid,parent_source_id=pid,subset_key=key,subset_name=en if lang=='en' else de,numbering_namespace=ns,aliases=[en,de],order=10,evidence=[ref]))
      if sid in sources and sid not in baseline['active_source_ids']:virtual.append(copy.deepcopy(sources[sid])|dict(state='structural_subset',parent_source_id=pid))
      if sid not in sources:virtual.append(dict(id=sid,lang=lang,release=child,name=(sources[pid]['name']+': '+(en if lang=='en' else de)),parent_source_id=pid,kind='set',state='structural_subset',release_date=sources[pid].get('release_date'),date_precision=sources[pid].get('date_precision'),date_state=sources[pid].get('date_state'),year=sources[pid].get('year'),links=[refs[ref]['url']]))
    inline=[]
    for parent,prefix,key,en,ref in [('bw11','RC','radiant_collection','Radiant Collection','lt_rc'),('g1','RC','radiant_collection','Radiant Collection','g_rc'),('pl1','SH','shiny_cards','Shiny cards (SH)','pl_sh'),('col1','SL','shiny_legends','Shiny Legendary cards (SL)','col_sl'),('dp7','SH','shiny_cards','Shiny cards (SH)','sf_sh'),('pl2','RT','rotom_cards','Rotom cards (RT)','rr_rt'),('pl3','SH','shiny_cards','Shiny cards (SH)','sv_sh'),('pl4','SH','shiny_cards','Shiny cards (SH)','ar_sections'),('pl4','AR','arceus_cards','Arceus cards (AR)','ar_sections')]:
     for lang in ('en','de'):
      pid=f'release:{lang}:{parent}'
      if pid not in sources:continue
      sid=f'section:{lang}:{parent}:{key}';inline.append(dict(parent_source_id=pid,prefix=prefix,subset_key=key,subset_name=en,numbering_namespace=prefix,source_id=sid,order=10,evidence=[ref]))
      virtual.append(dict(id=sid,lang=lang,release=None,name=sources[pid]['name']+': '+en,kind='set',state='structural_subset',parent_source_id=pid,release_date=sources[pid].get('release_date'),date_precision=sources[pid].get('date_precision'),date_state=sources[pid].get('date_state'),year=sources[pid].get('year'),links=[refs[ref]['url']]))
    # A metadata-only parent can be active for navigation without restoring retired cards.
    needed={v['parent_source_id'] for v in relations+inline};parents=[copy.deepcopy(sources[s]) for s in needed if s in sources and s not in baseline['active_source_ids']]
    classifications={}
    for sid,s in sources.items():
     rec=dict(source_role='numbered_set',group_source_id=sid,status='retained',recommendation='retain separate',reason='Distinct recorded language/provider source. No subset relationship is inferred from its name.',source_urls=s.get('links',[]))
     if s['state']=='catalog_release':
      if s['kind']=='promo':rec.update(source_role='promo_series',reason='Independently numbered promotional series; not a subset of retail products.')
      elif s['kind']=='deck' or sid=='release:de:tk-ex-latio' or any(t in s['name'] for t in ('스타터세트','スターターセット','Starter Set')):rec.update(source_role='numbered_product',reason='Independent provider-numbered deck identity; inspect under Products without merging collector numbers.')
      elif s.get('release')=='30th-c':rec.update(status='investigate',recommendation='investigate',reason='Future Classic Collection relationship is not resolved by a similar display name. No automatic merge.')
      elif s['kind']=='box' and not re.fullmatch(r'(?:\d{4}(?:swsh|sm|xy|bw|sv)|g1|sma|sm115|cel25cc|30th-c)',s.get('release') or ''):rec.update(status='investigate',recommendation='investigate',reason='Recorded numbered provider source with a product-like name; retained independently until set/product structure is documented.')
     else:
      rec.update(source_role='product',reason='Additional distribution/product context attached to existing card or printing IDs. No new collectible identity.')
      if s['state']=='research':rec.update(status='investigate',recommendation='investigate',reason='Distribution context is unresolved; retained as a research source without merging identities.')
      # Known expansion-reference aliases are backed by the identical linked canonical set.
      links=baseline['links'].get(sid,[]);roots={p['primary_source_id'] for p in links};target=next(iter(roots)) if len(roots)==1 else None
      if target in sources and fold(sources[target]['name'])==fold(s['name']):rec.update(source_role='source_alias',group_source_id=target,reason='Duplicate expansion reference: exact same localized set and linked printing IDs; only its presentation is merged.',recommendation='merge presentation')
      if re.fullmatch(r'Play Pokemon Prize Pack Series [123]',s['name']):rec.update(source_role='numbered_series',reason='Prize Pack distribution series remains separate from its original booster expansions.')
     classifications[sid]=rec
    # Review source-type false positives from the legacy English-only name heuristic.
    # These exact provider IDs already identify independent numbered regional sets.
    confirmed_expansions={
     'release:en:lc',
     'release:ja:SM1S','release:ja:SM1M','release:ja:SC','release:ja:BW1-Bw','release:ja:L1-Bss','release:ja:L1-Bhg','release:ja:XY1-Bx','release:ja:XY1-By','release:ja:CP2',
     'release:ko:sc','release:ko:bw1w','release:ko:cp3','release:ko:cp2','release:ko:xy1x','release:ko:xy1y','release:ko:S8a','release:ko:sm1m','release:ko:sm1s'}
    numbered_products={'release:ja:BW','release:ja:SP1','release:ko:SP1','release:ja:CS1m','release:ja:CPs','release:ja:CPm','release:ja:CPr'}
    for sid in confirmed_expansions:
     if sid in classifications:classifications[sid].update(source_role='numbered_set',status='recorded_regional_expansion',recommendation='retain separate',reason='Reviewed existing numbered regional expansion metadata. The legacy Collection/BOX name heuristic does not turn this expansion into a retail product. No Western parent inferred.')
    for sid in numbered_products:
     if sid in classifications:classifications[sid].update(source_role='numbered_product',status='recorded_numbered_product',recommendation='retain separate',reason='Independent provider-numbered regional box, collection sheet or collection-pack identity. Keep card numbers/printing IDs; inspect in Products without a second completion ledger.')
    if 'release:en:box-topper' in classifications:classifications['release:en:box-topper'].update(source_role='unresolved',reason='Archived numbered oversized supplement context with no indexed target here. Retain in product inventory; no expansion parent or physical printing inferred.')
    for sid,source in sources.items():
     if source['name']=='Galar Collection' and classifications[sid]['source_role']=='product':classifications[sid].update(status='investigate',recommendation='investigate',reason='Keep existing oversized identities and product provenance. Recorded foil pattern is unspecified while historical provenance is more specific; no printing change in this source pass.')
    for row in relations:
     classifications.setdefault(row['source_id'],{}).update(source_role='subset',group_source_id=row['parent_source_id'],status='documented',recommendation='merge presentation',reason='Documented internal expansion subset; original source ID and collector numbers retained.',source_urls=[refs[k]['url'] for k in row['evidence']])
    for row in inline:classifications[row['source_id']]=dict(source_role='subset',group_source_id=row['parent_source_id'],status='documented',recommendation='merge presentation',reason='Documented internal collector-number section; no new card identity.',source_urls=[refs[k]['url'] for k in row['evidence']])
    # Merge same-product source records used separately for regular/jumbo printings.
    clusters=collections.defaultdict(list)
    for sid,s in sources.items():
     if classifications[sid]['source_role']=='product':clusters[(s['lang'],fold(s['name']))].append(sid)
    for (lang,name),ids in clusters.items():
     if len(ids)<2:continue
     links=[p for sid in ids for p in baseline['links'].get(sid,[])];sets={p['primary_source_id'] for p in links};entries_in={p['entry_id'] for p in links}
     if not links:continue
     # This is source presentation only: preserve every member ID and physical tuple.
     rootid=sorted(ids)[0]
     for sid in ids:classifications[sid].update(group_source_id=rootid,recommendation='merge presentation',reason='Same named product context; member source records and all distinct physical sizes/finishes remain inspectable.',status='same_name_product_group')
    # One old combined distribution label covers three genuinely different products.
    old='research_product_ad7d582149195d998c4f80dc4a063447';targets=[]
    if old in sources:
     for key,name,nums in [('ss_etb_plus_zacian','Sword & Shield Elite Trainer Box Plus — Zacian',['SWSH076']),('ss_etb_plus_zamazenta','Sword & Shield Elite Trainer Box Plus — Zamazenta',['SWSH077']),('ss_upc','Sword & Shield Ultra-Premium Collection — Zacian & Zamazenta',['SWSH076','SWSH077'])]:
      sid='distribution:en:'+key;targets.append(dict(source_id=sid,numbers=nums));virtual.append(dict(id=sid,lang='en',release=None,name=name,kind='box',state='structural_product',source_role='product',links=[refs['etb_upc']['url']],member_source_ids=[old]));classifications[sid]=dict(source_role='product',group_source_id=sid,status='documented',recommendation='retain separate',reason='Distinct retail product distributing the specified existing gold promo IDs.',source_urls=[refs['etb_upc']['url']])
     classifications[old].update(source_role='product_bundle',status='documented',reason='Combined ETB Plus/UPC context, resolved into separate distribution products without copying physical cards.',recommendation='split distribution presentation')
    # Preserve the old aggregate Prize Pack source, while linking its shared printing IDs to each series.
    prize_targets=[]
    combined='research_product_50702df0a4815acda0d464529f5da8d2'
    for n in (1,2):
     ids=[sid for sid,s in sources.items() if s['lang']=='en' and s['name']==f'Play Pokemon Prize Pack Series {n}']
     if ids:prize_targets.append(dict(source_id=ids[0],numbers=None))
    if combined in sources:classifications[combined].update(source_role='source_alias_multi',reason='Recorded shared distribution in Prize Pack Series 1 and 2; one physical printing ID participates in two separate series views.',recommendation='separate series memberships')
    # Canonical localized family names are aliases for navigation, never new regional availability.
    families={}
    for p in sources.values():
     if p['state']=='catalog_release' and p['lang'] in ('en','de') and p.get('release'):
      family='western:'+p['release'];families.setdefault(family,{})[p['lang']]=p['name']
    facts=dict(format='dogdex-source-structure-1',version='1.8.5',reviewed_on='2026-10-30',references=refs,subsets=relations,inline_subsets=inline,structural_parents=parents,virtual_sources=virtual,classifications=classifications,family_names=families,distribution_expansions={old:targets,combined:prize_targets},limits=['Source structure and recorded distribution claims only. No new physical-printing research or variants.','Same-name product presentation preserves every underlying source record; it does not prove identical commercial reissues.','Japanese/Korean sources remain independent unless explicitly documented; Korean sma must not inherit the Western subset mapping.','No user PC database was supplied. Runtime inventory includes saved custom sources; package inventory has no personal records.'])
    (out/'source_relations.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2),encoding='utf-8')
    print('classification rows',len(classifications),'subset links',len(relations),'inline sections',len(inline),'virtual records',len(virtual),'metadata parents',len(parents))
    print('roles',dict(collections.Counter(v['source_role'] for v in classifications.values())))

if __name__ == '__main__':
    import argparse
    argparse.ArgumentParser(description=__doc__).parse_args()
    main()
