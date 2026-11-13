"""The collector's explicitly chosen species scope; excluded ownership stays recoverable."""
import copy

EXCLUDED_DEX=frozenset({133,134,135,136,196,197,470,471,700,403,404,405})
LANGUAGES=('en','de','ja','ko')

def is_cameo(entry):
    """A background appearance on a card without a tracked primary subject."""
    primary=entry.get('subject_dex')
    if primary is None:primary=[] if entry.get('category')=='cameo' else [entry.get('dex')]
    return not primary and (entry.get('category')=='cameo' or bool(entry.get('cameo_dex')))

def species(entry):
    primary=entry.get('subject_dex')
    if primary is None:primary=[] if entry.get('category')=='cameo' else [entry.get('dex')]
    return set(primary or [])|set(entry.get('cameo_dex') or [])

def in_scope(entry):
    return bool(species(entry)-EXCLUDED_DEX)

def trim_species(entry):
    entry['subject_dex']=sorted(set(entry.get('subject_dex') or ([] if entry.get('category')=='cameo' else [entry.get('dex')]))-EXCLUDED_DEX)
    entry['cameo_dex']=sorted(set(entry.get('cameo_dex') or [])-EXCLUDED_DEX)
    entry['dex']=(entry['subject_dex'] or entry['cameo_dex'])[0]
    if not entry['subject_dex']:entry['category']='cameo'
    return entry

def apply_scope(catalog):
    retired={e['id']:e for e in catalog.get('retired_entries',[])};active=[]
    for e in catalog['entries']:
        if in_scope(e):active.append(trim_species(e))
        else:retired[e['id']]=e
    catalog['entries']=active
    catalog['retired_entries']=list(retired.values())
    catalog['roster']=[r for r in catalog['roster'] if r['dex'] not in EXCLUDED_DEX]
    live_releases={(e['lang'],e['release']) for e in active}
    removed_sources={r['lang']+':'+r['release']:r for r in catalog.get('retired_releases',[])}
    for r in catalog.get('releases',[]):
        if (r['lang'],r['release']) not in live_releases:removed_sources[r['lang']+':'+r['release']]=r
    catalog['releases']=[r for r in catalog.get('releases',[]) if (r['lang'],r['release']) in live_releases]
    catalog['retired_releases']=list(removed_sources.values())
    pending=[]
    for original in catalog.get('special_research',[]):
        r=copy.deepcopy(original)
        if not (set(r.get('subject_dex') or [])|set(r.get('cameo_dex') or []))-EXCLUDED_DEX:continue
        for key in ('subject_dex','cameo_dex'):r[key]=sorted(set(r.get(key) or [])-EXCLUDED_DEX)
        pending.append(r)
    catalog['special_research']=pending
    catalog['scope']=dict(excluded_dex=sorted(EXCLUDED_DEX),excluded_families=['Eevee and its evolutions','Shinx, Luxio and Luxray'],retired_entries=len(retired),retired_printings=sum(len(e['printings']) for e in retired.values()),research_priority=['de','en'],secondary_languages=['ja','ko'])
    return catalog
