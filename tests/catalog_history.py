"""Replay historical releases from frozen inputs; never roll back the live catalogue.

Golden hashes in printing_184/baseline_183 and printing_186/baseline_185 anchor
these reconstructions independently of today's catalogue output.
"""
import copy,json
from functools import lru_cache
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))

def _statistics(c):
    from dogdex.scope import is_cameo
    es=c['entries'];ps=[p for e in es for p in e['printings']]
    c['statistics']=dict(entries=len(es),printings=len(ps),without_printings=sum(not e['printings'] for e in es),missing_images=sum(not e.get('image') for e in es),full_art_entries=sum(e.get('art_style')=='full_art' for e in es),cameo_entries=sum(is_cameo(e) for e in es),jumbo_printings=sum(p['size']=='oversized' or p['material']=='metal' for p in ps),missing_release_dates=sum(not e.get('release_date') for e in es),reference_dates=sum(e.get('date_state')=='provider_reference' for e in es))
    c['language_stats']={lang:dict(entries=sum(e['lang']==lang for e in es),with_printings=sum(e['lang']==lang and bool(e['printings']) for e in es),printings=sum(len(e['printings']) for e in es if e['lang']==lang),full_art=sum(e['lang']==lang and e.get('art_style')=='full_art' for e in es),cameos=sum(e['lang']==lang and is_cameo(e) for e in es)) for lang in ('en','de','ja','ko')}

@lru_cache(maxsize=None)
def _frozen(version):
    paths={'1.4':'data/research/reconciliation_15/baseline_140.json','1.5':'data/research/completion_16/baseline_150.json','1.6':'data/research/asia_17/baseline_160.json'}
    if version in paths:return read(paths[version])
    stages={'1.7':('1.6','dogdex.asia_enrich'),'1.8.4':('1.7','dogdex.printing_enrich'),'1.8.6':('1.8.4','dogdex.printing_corrections'),'1.8.9':('1.8.6','dogdex.identity_corrections')}
    previous,module=stages[version];c=copy.deepcopy(_frozen(previous))
    import importlib
    importlib.import_module(module).apply(c);_statistics(c);c['revision']=version
    return c

def catalog_at(version):
    """Each caller owns its copy; later corrections cannot rewrite an old fixture."""
    return copy.deepcopy(_frozen(version))
