"""Saved-claim reconciliation; no global physical-printing completeness claim."""
import collections,hashlib,json,tempfile
from pathlib import Path
from .printing_model import PATTERNS,normalized,pattern_key,physical_key,printing_label,token

def recorded_claims(e):
 result={};facts=[f for f in e.get('evidence',[]) if f.get('field') in ('variant_claims','authored regional variants')]
 facts += [dict(value=c.get('raw'),source_urls=c.get('source_urls',[]),source_family=c.get('source_family'),disposition=c.get('disposition'),summary=c.get('reason')) for c in e.get('variant_claims',[])]
 for f in facts:
  v=f.get('value')
  if not isinstance(v,dict):continue
  for raw in v.get('variants') if isinstance(v.get('variants'),list) else [v]:
   if not isinstance(raw,dict):continue
   finish=dict(normal='non_holo',non_holo='non_holo',holo='holo',holofoil='holo',reverse='reverse_holo',reverse_holo='reverse_holo',reverse_holofoil='reverse_holo').get(token(raw.get('type') or raw.get('finish')))
   if not finish:continue
   partial=dict(finish=finish,pattern=pattern_key(raw.get('foil') or raw.get('pattern'),finish))
   if 'stamps' in raw or 'stamps_json' in raw:partial['stamps_json']=normalized(raw)['stamps_json']
   for k in ('edition','layout','size','material','print_state'):
    if raw.get(k):partial[k]=token(raw[k])
   disposition=str(f.get('disposition') or 'unresolved');active=not any(s in disposition for s in ('excluded','rejected','superseded','duplicate'))
   signature=json.dumps([partial,f.get('source_family'),f.get('source_urls'),active],ensure_ascii=False,sort_keys=True);cid='claim_'+hashlib.sha256(signature.encode()).hexdigest()[:24]
   result.setdefault(cid,dict(claim_id=cid,normalized_partial=partial,raw_label=dict(type=raw.get('type'),foil=raw.get('foil'),edition=raw.get('edition')),source_urls=f.get('source_urls',[]),source_family=f.get('source_family') or 'unknown_lineage',historical_disposition=disposition,active=active,confidence='source_assertion',reason=f.get('summary') or 'Exact regional physical applicability needs review.'))
 return list(result.values())
def claim_matches(claim,p):
 value=normalized(p);return all(value.get(k)==v for k,v in claim['normalized_partial'].items())
def audit(store):
 view=store.editor_view();sources={s['id']:s for s in view['sources']};groups=collections.defaultdict(list);rows=[];sets={};counts=collections.Counter();queue=[]
 for s in sources.values():groups[(s.get('canonical_set_id'),s['lang'])].append(s['id'])
 for e in view['entries']:
  ps=e['printings'];issues=[];physical=collections.defaultdict(list)
  def issue(kind,severity,message,pid=None,urls=None):issues.append(dict(kind=kind,severity=severity,message=message,printing_id=pid,source_urls=urls or []))
  for p in ps:physical[physical_key(e['id'],p)].append(p['id'])
  for ids in physical.values():
   if len(ids)>1:issue('duplicates','confirmed','Multiple records describe the same normalized printing: '+', '.join(ids),ids[0])
  expected=e.get('printing_specification',{}).get('expected',[]);missing=[]
  for spec in expected:
   if physical_key(e['id'],spec) not in physical:missing.append(spec);issue('missing','confirmed','Documented printing missing: '+printing_label(spec),urls=spec.get('source_urls'))
  claims=recorded_claims(e);candidates=[]
  for c in claims:
   ids=[p['id'] for p in ps if claim_matches(c,p)];c['matched_printing_ids']=ids;c['disposition']='matched' if ids and c['active'] else 'historical_exclusion' if not c['active'] else 'needs_review'
   if c['active'] and not ids:candidates.append(c);queue.append(dict(entry_id=e['id'],lang=e['lang'],release=e['release'],number=e['number'],**c))
  if candidates:issue('missing','review',str(len(candidates))+' recorded physical claim(s) are unmatched. Review before importing.',urls=list(dict.fromkeys(u for c in candidates for u in c['source_urls'])))
  for p in ps:
   raw=p.get('pattern');canonical=pattern_key(raw,p['finish'])
   if canonical not in PATTERNS and not canonical.startswith('custom_'):issue('terminology','review','Uncontrolled legacy foil pattern: '+str(raw),p['id'])
   elif raw!=canonical:issue('terminology','review','Normalized equivalent: '+str(raw)+' → '+canonical,p['id'])
   if p['finish']=='non_holo' and canonical!='none':issue('classification','confirmed','Non-holo printing has a foil pattern.',p['id'])
   if p.get('printed_rarity_state')=='known' and not p.get('printed_rarity_code'):issue('classification','confirmed','Known printing-specific rarity has no code.',p['id'])
   review=p.get('image_review',{})
   if review.get('status')!='verified':issue('images','information',review.get('reason') or ('Printing photo unchecked.' if review.get('kind')=='physical_photo' else 'Reference artwork.' if p.get('image') else 'No picture recorded.'),p['id'])
   for s in p.get('sources',[]):
    if s.get('lang') and s['lang']!=e['lang']:issue('sources','confirmed','Printing source belongs to another language.',p['id'])
    elif s['id']!=e['primary_source_id'] and not p.get('verification',{}).get('existence',{}).get('source_urls'):issue('sources','review','Printing-specific source association lacks field-specific evidence links.',p['id'])
   if not p.get('market_confirmed'):issue('market','information','Cardmarket product/price series not confirmed.',p['id'])
  source=sources.get(e['primary_source_id'])
  if not source:issue('localization','confirmed','Primary source is missing.')
  elif len(groups[(source.get('canonical_set_id'),e['lang'])])>1:issue('localization','review','Several sources in this language share a canonical group; navigation is ambiguous.')
  row=dict(entry_id=e['id'],lang=e['lang'],dex=e['dex'],subject_dex=e.get('subject_dex',[]),primary_source_id=e['primary_source_id'],name=e['name'],english=e['english'],number=e['number'],release=e['release'],set_name=e['set_name'],canonical_set_id=e.get('canonical_set_id'),indexed_variants=[dict(id=p['id'],**normalized(p),label=p['label']) for p in ps],confirmed_printings=len(physical),verified_specification=bool(expected),expected_variants=expected,missing_verified=missing,recorded_claims=claims,unresolved_claims=len(candidates),issues=issues);rows.append(row)
  for item in issues:counts[item['severity']]+=1
  key=(e['lang'],e['primary_source_id'])
  if key not in sets:sets[key]=dict(lang=e['lang'],source_id=key[1],name=e['set_name'],canonical_set_id=e.get('canonical_set_id'),identities=0,indexed_printings=0,expected_reviewed=0,reviewed_identities=0,missing_verified=0)
  s=sets[key];s['identities']+=1;s['indexed_printings']+=len(physical);s['expected_reviewed']+=len(expected);s['reviewed_identities']+=bool(expected);s['missing_verified']+=len(missing)
 return dict(format='dogdex-printing-completeness-1',rows=rows,sets=list(sets.values()),queue=queue,summary=dict(identities=len(rows),species=len(store.catalog['roster']),confirmed_errors=counts['confirmed'],review_items=counts['review'],information=counts['information'],unresolved_source_claims=len(queue),reviewed_identities=sum(r['verified_specification'] for r in rows)),limits=['Expected counts exist only for reviewed named specifications.','Other source claims require review, not automatic import.','Images and unmatched prices are information gaps, not missing verified printings.','All 41 species/four ledgers scanned; this is not new worldwide specimen research.'])
if __name__=='__main__':
 from .collector import Collection
 root=Path(__file__).resolve().parents[1]
 with tempfile.TemporaryDirectory() as user:report=audit(Collection(root,user))
 out=root/'data/research/printing_184';out.mkdir(exist_ok=True);(out/'reconciliation.json').write_text(json.dumps(report,ensure_ascii=False,separators=(',',':')),encoding='utf-8');(out/'work_queue.json').write_text(json.dumps(dict(rows=report['queue'],limits=report['limits']),ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report['summary']))
