"""Non-destructive expansion/subset/product navigation over stable catalogue IDs.

An expansion membership is not a distribution membership. Neither creates a
physical printing. All original source, entry and printing records remain intact.
"""
from __future__ import annotations
import copy,json,re,unicodedata
from functools import lru_cache
from pathlib import Path
FACT_PATH=Path(__file__).resolve().parents[1]/'data/research/sources_185/source_relations.json'
SET_ROLES={'numbered_set','promo_series','numbered_series'}
PRODUCT_ROLES={'product','numbered_product','product_bundle'}
ROLES=SET_ROLES|PRODUCT_ROLES|{'subset','source_alias','source_alias_multi','unresolved'}
@lru_cache(maxsize=1)
def facts():return json.loads(FACT_PATH.read_text(encoding='utf-8'))
def fold(value):return re.sub(r'[^\w]+',' ',unicodedata.normalize('NFKC',str(value or '')).casefold()).strip()
def root_source(source,sources):
 seen=set()
 while source and source.get('group_source_id',source['id'])!=source['id']:
  if source['id'] in seen:return None
  seen.add(source['id']);source=sources.get(source['group_source_id'])
 return source

def annotate_sources(sources,catalog,removed=frozenset()):
 """Apply explicit language-scoped IDs. Unknown sources never inherit a subset."""
 f=facts();relations={r['source_id']:r for r in f['subsets']+f['inline_subsets']}
 for parent in f['structural_parents']:
  if parent['id'] not in sources and parent['id'] not in removed and any(r['parent_source_id']==parent['id'] and r['source_id'] in sources for r in f['subsets']):sources[parent['id']]=copy.deepcopy(parent)|dict(state='structural_parent')
 for v in f['virtual_sources']:
  needed=v.get('parent_source_id') in sources or any(s in sources for s in v.get('member_source_ids',[]))
  if v['id'] not in sources and v['id'] not in removed and needed:sources[v['id']]=copy.deepcopy(v)
 for sid,s in sources.items():
  rule=f['classifications'].get(sid,{})
  default='numbered_product' if s.get('kind')=='deck' and s.get('state') in ('manual','legacy_manual') else 'product' if s.get('kind') in ('deck','box','event') and s.get('state')!='catalog_release' else 'promo_series' if s.get('kind')=='promo' else 'numbered_set'
  if s.get('state') not in ('catalog_release','manual','legacy_manual','structural_parent','structural_subset','structural_product') and not rule:default='product'
  role=s.get('source_role') or rule.get('source_role') or default
  s['source_role']=role;s['structure_state']=rule.get('status','manual' if s.get('state') in ('manual','legacy_manual') else 'unreviewed');s['structure_reason']=rule.get('reason','Independent source. Set a parent explicitly to create a subset.');s['structure_source_urls']=rule.get('source_urls',[]);s['structure_issues']=[]
  rel=relations.get(sid,{})
  group=s.get('parent_source_id') if role=='subset' else s.get('group_source_id')
  if s.get('source_role') and role!=rule.get('source_role') and role!='subset':group=sid
  group=group or (rel.get('parent_source_id') if role=='subset' else rule.get('group_source_id')) or sid
  s['group_source_id']=group;s['parent_source_id']=group if role=='subset' else None
  if role=='subset':
   s['subset_key']=s.get('subset_key') or rel.get('subset_key') or 'custom:'+sid
   s['subset_name']=s.get('subset_name') or rel.get('subset_name') or s['name']
   s['numbering_namespace']=s.get('numbering_namespace') or rel.get('numbering_namespace') or 'collector'
   s['subset_order']=s.get('subset_order',rel.get('order',10))
  else:s.update(subset_key='main',subset_name='Main Set',subset_order=0)
  s.setdefault('canonical_set_id',('western:' if s['lang'] in ('en','de') else 'regional:'+s['lang']+':')+str(s.get('release') or sid))
  if s['structure_state']=='investigate':s['structure_issues'].append(s['structure_reason'])
 for sid,s in sources.items():
  parent=root_source(s,sources)
  if not parent or parent['lang']!=s['lang']:
   s['structure_issues'].append('Parent/group source is missing, cyclic or in another language.');s['navigation_source_id']=sid;parent=s
  elif s['source_role']=='subset' and parent['source_role'] not in SET_ROLES:
   s['structure_issues'].append('A subset must belong to a numbered expansion or series.');s['navigation_source_id']=sid;parent=s
  else:s['navigation_source_id']=parent['id']
  s['canonical_expansion_id']=parent.get('canonical_set_id') or 'source:'+parent['id']
  names=f['family_names'].get(s['canonical_expansion_id'],{})
  s['aliases']=list(dict.fromkeys([s['name'],*([str(s['release'])] if s.get('release') else []),*s.get('aliases',[]),*names.values()]))
  s['subset_aliases']=list(dict.fromkeys([s['subset_name'],s.get('numbering_namespace',''),*relations.get(sid,{}).get('aliases',[])])) if s['source_role']=='subset' else []
  s['overview_section']='products' if parent['source_role'] in PRODUCT_ROLES or parent['source_role']=='unresolved' else 'sets'
 return sources

def distribution_ids(entry,printing,sources):
 """Resolve explicit product associations, without altering printing tuples."""
 f=facts();out=[]
 def put(sid,basis,origin=None):
  s=sources.get(sid)
  if not s:return
  expanded=f['distribution_expansions'].get(sid)
  if expanded:
   for target in expanded:
    if target.get('numbers') is None or entry['number'] in target['numbers']:put(target['source_id'],basis,origin or sid)
   return
  role=s.get('source_role')
  if role not in PRODUCT_ROLES|{'numbered_series'}:return
  root=s.get('navigation_source_id',sid)
  binding=dict(source_id=root,origin_source_id=origin or sid,basis=basis,state='recorded_distribution' if basis=='printing' else 'card_level_association')
  if not any(v['source_id']==root for v in out):out.append(binding)
 for source in printing.get('sources',[]):put(source['id'],'printing')
 for source in entry.get('sources',[]):
  if source['id']!=entry.get('primary_source_id'):put(source['id'],'card')
 primary=sources.get(entry.get('primary_source_id'))
 if primary and primary['source_role'] in PRODUCT_ROLES:put(primary['id'],'canonical_numbered_product' if primary['source_role']=='numbered_product' else 'card')
 return out

def annotate_entry(entry,sources):
 source=sources.get(entry.get('primary_source_id'));root=sources.get(source.get('navigation_source_id')) if source else None
 if not root or root['lang']!=entry['lang']:root=source
 if not root:return
 entry.update(expansion_source_id=root['id'],expansion_name=root['name'],canonical_expansion_id=root.get('canonical_expansion_id'),subset_key=source.get('subset_key','main'),subset_name=source.get('subset_name','Main Set'),subset_source_id=source['id'],source_structure_issues=list(source.get('structure_issues',[])))
 for section in facts()['inline_subsets']:
  if section['parent_source_id']==source['id'] and str(entry['number']).upper().startswith(section['prefix']):entry.update(subset_key=section['subset_key'],subset_name=section['subset_name'],subset_source_id=section['source_id'])
 entry['source_search_terms']=list(dict.fromkeys([*root.get('aliases',[]),entry['subset_name'],*source.get('aliases',[])]))
 for p in entry['printings']+entry.get('printing_claims',[]):
  p['distribution_bindings']=distribution_ids(entry,p,sources);p['distribution_source_ids']=[v['source_id'] for v in p['distribution_bindings']]
 return entry

def validate_source_structure(data,old,sources):
 """Validate only user-selected relationships, never infer one from names."""
 role=data.get('source_role',(old or {}).get('source_role'))
 if not role:return {}
 if role not in ROLES:raise ValueError('Choose an expansion, subset, series or distribution role.')
 parent=data.get('parent_source_id',(old or {}).get('parent_source_id')) or None
 values=dict(source_role=role,parent_source_id=parent if role=='subset' else None,group_source_id=parent if role=='subset' else (old or {}).get('id'))
 if role=='subset':
  p=sources.get(parent)
  if not p or p['lang']!=data.get('lang',(old or {}).get('lang')):raise ValueError('Choose a parent expansion in the same language.')
  if p['id']==(old or {}).get('id') or p.get('source_role') not in SET_ROLES:raise ValueError('Choose an independent numbered expansion/series as parent, not a product or another subset.')
  label=str(data.get('subset_name',(old or {}).get('subset_name')) or '').strip()
  if not label or len(label)>150:raise ValueError('Enter the subset name.')
  key=str(data.get('subset_key',(old or {}).get('subset_key')) or 'custom:'+fold(label).replace(' ','_')).strip()
  if len(key)>200 or not re.fullmatch(r'[\w:.-]+',key):raise ValueError('Use a simple stable subset key.')
  if any(s['id']!=(old or {}).get('id') and s.get('parent_source_id')==parent and s.get('subset_key')==key for s in sources.values()):raise ValueError('That subset key already exists under this expansion. Edit the existing source instead.')
  values.update(subset_name=label,subset_key=key,numbering_namespace=str(data.get('numbering_namespace',(old or {}).get('numbering_namespace')) or 'collector')[:100])
 return values

def guard_primary_source(source,documented,old=None):
 if documented and source.get('source_role') in {'product','product_bundle','source_alias_multi'} and (not old or old.get('primary_source_id')!=source['id'] or old.get('identity_status') in ('provisional','disputed','announced','excluded')):raise ValueError('Choose the card’s numbered set/promo series. Associate retail products with its existing printing. An unresolved product identity can remain a research card.')
