"""Complete runtime source inventory and reproducible 1.8.5 source reports.

The CSV endpoint includes saved manual/removed/retired source contexts. Counts
are ID sets, not a claim that every historical product association is verified.
"""
from __future__ import annotations
import argparse,collections,csv,hashlib,io,json,tempfile
from pathlib import Path
from .source_structure import facts,PRODUCT_ROLES,root_source

ROOT=Path(__file__).resolve().parents[1]
FIELDS=['source_id','set_code','upstream_provider_id','display_name','language','era','release_date','date_precision','date_state','old_parent','old_subset','card_identities','accepted_printing_records','held_printing_claims','retired_card_identities','retired_printing_records','old_overview_visible','active_source','removed','manual','source_role','canonical_expansion_id','canonical_source_id','canonical_name','subset_key','subset_name','numbering_namespace','overview_section','recommendation','structure_state','justification','evidence_urls','structure_issues']

def source_links(entries):
    result=collections.defaultdict(lambda:dict(cards=set(),accepted=set(),held=set()))
    for e in entries.values():
        base={e['primary_source_id'],*[s['id'] for s in e.get('sources',[])]}
        for sid in base:result[sid]['cards'].add(e['id'])
        for field,target in [('printings','accepted'),('printing_claims','held')]:
            for p in e.get(field,[]):
                for sid in base|{s['id'] for s in p.get('sources',[])}|set(p.get('distribution_source_ids',[])):
                    result[sid]['cards'].add(e['id']);result[sid][target].add(p['id'])
    return result

def inventory_rows(store):
    state=store.state();sources=store.sources(state,True,True);active=store.sources(state)
    entries=store.catalog_entries(state);all_entries=store.catalog_entries(state,True,True)
    links=source_links(entries);retired=source_links({k:v for k,v in all_entries.items() if k not in entries})
    removed={r['target_id'] for r in state.get('catalog_trash',[]) if r['kind']=='source'}
    manual={r['id'] for r in state.get('manual_sources',[])}
    baseline=json.loads((ROOT/'data/research/sources_185/baseline_184.json').read_text(encoding='utf-8'))
    old={s['id']:s for s in baseline['sources']};visible=set(baseline['overview_visible_source_ids']);rules=facts()['classifications']
    rows=[]
    for sid,s in sorted(sources.items(),key=lambda pair:(pair[1]['lang'],pair[1]['name'].casefold(),pair[0])):
        root=root_source(s,sources) or s;v=links[sid];r=retired[sid];rule=rules.get(sid,{})
        rows.append(dict(source_id=sid,set_code=s.get('release'),upstream_provider_id=s.get('provider_id') or s.get('upstream_provider_id'),display_name=s['name'],language=s['lang'],era=s.get('series'),release_date=s.get('release_date'),date_precision=s.get('date_precision'),date_state=s.get('date_state'),old_parent=old.get(sid,{}).get('parent_source_id'),old_subset=old.get(sid,{}).get('subset_key'),card_identities=len(v['cards']),accepted_printing_records=len(v['accepted']),held_printing_claims=len(v['held']),retired_card_identities=len(r['cards']),retired_printing_records=len(r['accepted']|r['held']),old_overview_visible=sid in visible,active_source=sid in active,removed=sid in removed,manual=sid in manual or s.get('state') in ('manual','legacy_manual'),source_role=s['source_role'],canonical_expansion_id=s.get('canonical_expansion_id'),canonical_source_id=root['id'],canonical_name=root['name'],subset_key=s['subset_key'],subset_name=s['subset_name'] if s['source_role']=='subset' else '',numbering_namespace=s.get('numbering_namespace'),overview_section=s['overview_section'],recommendation=rule.get('recommendation','retain separate'),structure_state=s['structure_state'],justification=s['structure_reason'],evidence_urls=list(dict.fromkeys(s.get('structure_source_urls',[])+s.get('links',[]))),structure_issues=s.get('structure_issues',[])))
    return rows

def csv_bytes(rows,fields=None):
    fields=fields or (list(rows[0]) if rows else FIELDS);stream=io.StringIO(newline='');writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
    for row in rows:
        safe={k:json.dumps(v,ensure_ascii=False,separators=(',',':')) if isinstance(v,(dict,list)) else '' if v is None else str(v) for k,v in row.items() if k in fields}
        # Prevent a manually entered source label becoming an Excel formula.
        writer.writerow({k:"'"+v if v.startswith(('=','+','-','@','\t','\r')) else v for k,v in safe.items()})
    return ('\ufeff'+stream.getvalue()).encode('utf-8')

def inventory_csv(store):return csv_bytes(inventory_rows(store),FIELDS)

REQUIRED=[('Legends of Galar Tins','Legends of Galar Tins'),('Sword & Shield Elite Trainer Box Plus / Ultra-Premium Collection','Elite Trainer Box Plus'),('True Steel Premium Collections','True Steel Premium'),('Battle Styles Build & Battle Box','Battle Styles Build'),('Boltund V Box','Boltund V Box'),('Cosmos Holo Fall 2022 Collector Chest exclusive','Fall 2022 Collector Chest'),('Crown Zenith Elite Trainer Box','Crown Zenith Elite Trainer Box'),('Crown Zenith Premium Figure Collection Shiny Zacian','Shiny Zacian'),('Crown Zenith Premium Figure Collection Shiny Zamazenta','Shiny Zamazenta'),('Free Demo Deck','Free Demo Deck'),('Galar Collection','Galar Collection'),('Hisuian Zoroark VSTAR Premium Collection','Hisuian Zoroark VSTAR Premium Collection'),('Lucario VSTAR Premium Collection','Lucario VSTAR Premium Collection'),('Non Holo Brilliant Stars Build & Battle Box exclusive','Non Holo Brilliant Stars'),('Non Holo Evolving Skies Build & Battle Box exclusive','Non Holo Evolving Skies')]

def product_mapping(store):
    state=store.state();sources=store.sources(state,True,True);entries=store.catalog_entries(state,True,True);active=set(store.catalog_entries(state));rows=[]
    baseline=json.loads((ROOT/'data/research/sources_185/baseline_184.json').read_text(encoding='utf-8'));old={s['id']:s for s in baseline['sources']};seen=set()
    for e in entries.values():
        primary=sources.get(e['primary_source_id'],{});base=[s for s in e.get('sources',[]) if s['id']!=e['primary_source_id'] or primary.get('source_role') in PRODUCT_ROLES]
        for field in ('printings','printing_claims'):
            for p in e.get(field,[]):
                contexts={v['id']:('card',v) for v in base};contexts.update({v['id']:('printing',v) for v in p.get('sources',[])})
                if primary.get('source_role')=='numbered_product':contexts[primary['id']]=('canonical_numbered_product',primary)
                for sid,(basis,raw) in contexts.items():
                    source=sources.get(sid,raw);role=source.get('source_role')
                    if role not in PRODUCT_ROLES|{'source_alias','source_alias_multi','numbered_series'}:continue
                    key=sid,p['id']
                    if key in seen:continue
                    seen.add(key);bindings=[v for v in p.get('distribution_bindings',[]) if v['origin_source_id']==sid]
                    resolved=[v['source_id'] for v in bindings] or [source.get('navigation_source_id',sid)]
                    physically_special=p.get('size')=='oversized' or p.get('material')!='paper' or p.get('pattern') not in ('none','unspecified') or p.get('finish')=='non_holo'
                    if basis=='card' or field=='printing_claims':classification='Unresolved identity/distribution requiring manual verification'
                    elif primary.get('source_role')=='promo_series':classification='Independently numbered promotional card'
                    elif physically_special and p.get('provenance',{}).get('kind') in ('manufacturer_oversized_product','manufacturer_product','dedicated_regional_source_tuple','reviewed_western_physical_printing','product_exclusive','product_source_physical_tuple'):classification='Unique product-exclusive physical printing of existing numbered card'
                    elif physically_special and any(t in str(p.get('provenance',{})).lower() for t in ('exclusive','product','oversized')):classification='Unique product-exclusive physical printing of existing numbered card'
                    else:classification='Existing physical printing distributed through product'
                    urls=list(dict.fromkeys(source.get('links',[])+source.get('structure_source_urls',[])+p.get('provenance',{}).get('source_urls',[])+[u for u in [p.get('provenance',{}).get('source_url')] if u]))
                    physical={k:p.get(k) for k in ('finish','pattern','edition','layout','size','material','stamps_json','print_state')}
                    rows.append(dict(old_source_id=sid,old_source=old.get(sid,source)['name'],language=e['lang'],canonical_set_id=e['primary_source_id'],canonical_set=e['set_name'],entry_id=e['id'],card=e['name'],collector_number=e['number'],identifier_namespace=e.get('identifier_namespace'),printing_id=p['id'],physical_printing=physical,distribution_product_ids=resolved,distribution_products=[sources[v]['name'] for v in resolved if v in sources],association_basis=basis,unresolved_fields=['pattern: recorded as unspecified; historical product evidence may be more specific'] if p.get('pattern')=='unspecified' else [],classification=classification,accepted=field=='printings',active_entry=e['id'] in active,action='Preserve printing ID; associate distribution; no additional completion target',market_reference={k:p.get(k) for k in ('cardmarket_url','price_product_id','market_product_id','market_candidate') if p.get(k) is not None},evidence_urls=urls,existing_provenance=p.get('provenance',{})))
    for sid,s in sources.items():
        if sid in old and s['source_role'] in PRODUCT_ROLES and not any(r['old_source_id']==sid for r in rows):
            rows.append(dict(old_source_id=sid,old_source=s['name'],language=s['lang'],canonical_set_id=None,canonical_set=None,entry_id=None,card=None,collector_number=None,identifier_namespace=None,printing_id=None,physical_printing={},distribution_product_ids=[s.get('navigation_source_id',sid)],distribution_products=[(root_source(s,sources) or s)['name']],association_basis='no indexed card',classification='Unresolved identity/distribution requiring manual verification',accepted=False,active_entry=False,action='Retain zero-card/archived provenance; no printing inferred',market_reference={},evidence_urls=s.get('structure_source_urls',[]),existing_provenance={}))
    return sorted(rows,key=lambda r:(r['old_source'],r['language'],r['collector_number'] or '',r['printing_id'] or ''))

def write_reports(store,directory):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True);inv=inventory_rows(store);mapping=product_mapping(store)
    (directory/'source_inventory.json').write_text(json.dumps(inv,ensure_ascii=False,indent=2),encoding='utf-8');(directory/'source_inventory.csv').write_bytes(csv_bytes(inv,FIELDS))
    (directory/'product_printing_mapping.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2),encoding='utf-8');(directory/'product_printing_mapping.csv').write_bytes(csv_bytes(mapping))
    view=store.editor_view();entries=view['entries'];raw=store.catalog['entries'];baseline=json.loads((ROOT/'data/research/sources_185/baseline_184.json').read_text(encoding='utf-8'));ids=sorted(p['id'] for e in entries for p in e['printings']);rawids=sorted(p['id'] for e in raw for p in e['printings']);groups=[]
    for rel in facts()['subsets']:
        lang=rel['source_id'].split(':')[1];child=[p['id'] for e in entries if e['primary_source_id']==rel['source_id'] for p in e['printings']];main=[p['id'] for e in entries if e['primary_source_id']==rel['parent_source_id'] for p in e['printings']]
        groups.append(dict(language=lang,old_source_id=rel['source_id'],parent_id=rel['parent_source_id'],subset=rel['subset_name'],old_child_visible=rel['source_id'] in baseline['overview_visible_source_ids'],main_printings=len(set(main)),subset_printings=len(set(child)),combined_printings=len(set(main+child)),printing_ids=sorted(set(main+child))))
    before_entries=baseline['entries'];current_hashes={e['id']:hashlib.sha256(json.dumps(e,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest() for e in raw}
    checks=dict(raw_printing_ids_unchanged=rawids==sorted(baseline['raw_printing_ids']),accepted_printing_ids_unchanged=ids==sorted(baseline['accepted_printing_ids']),raw_catalog_hashes_unchanged=all(hashlib.file_digest((ROOT/'data'/n).open('rb'),'sha256').hexdigest()==v for n,v in baseline['catalog_hashes'].items()),accepted_by_language=dict(collections.Counter(e['lang'] for e in entries for p in e['printings'])),source_rows=len(inv),original_source_rows=len(baseline['sources']),original_sources_all_retained=set(s['id'] for s in baseline['sources'])<=set(r['source_id'] for r in inv),user_pc_database_supplied=False)
    (directory/'before_after.json').write_text(json.dumps(dict(checks=checks,groups=groups),ensure_ascii=False,indent=2),encoding='utf-8')
    return dict(checks=checks,groups=groups,inventory=inv,mapping=mapping)

if __name__=='__main__':
    from .collector import Collection
    parser=argparse.ArgumentParser();parser.add_argument('--output',default=str(ROOT/'data/research/sources_185'));parser.add_argument('--user-dir');args=parser.parse_args()
    with tempfile.TemporaryDirectory() as temporary:
        result=write_reports(Collection(ROOT,args.user_dir or temporary),args.output)
    print(json.dumps(result['checks']))
