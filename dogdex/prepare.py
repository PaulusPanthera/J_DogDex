"""Build a portable, source-preserving collector index from a reviewed checkpoint."""
import argparse,collections,hashlib,json,re,sqlite3,urllib.request,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASELINE_SHA='e79d48ff8d056d88fa0d6b1f0771f220d79f62d82797c886183e20ada9c22da0'
def label(value):return str(value or '').replace('_',' ').strip().title()
def rarity_family(code):
 if code in ('common','C'):return 'common'
 if code in ('uncommon','U'):return 'uncommon'
 # Rarity alone does not verify full-art artwork. That group is assigned by
 # explicit manual review, or a future accepted art-style assertion.
 if code in ('promo','P'):return 'other'
 return 'rare' if code else 'other'
def printing_label(v):
 parts=[{'non_holo':'Non-holo','holo':'Holo','reverse_holo':'Reverse holo'}[v['finish']]]
 if v['pattern'] not in ('none','unspecified'):parts.append(label(v['pattern']))
 if v['edition'] in ('first_edition','unlimited'):parts.append({'first_edition':'1st edition','unlimited':'Unlimited'}[v['edition']])
 if v['layout'] not in ('standard','shadowed'):parts.append(label(v['layout']))
 if v['size']=='oversized':parts.append('Jumbo')
 if v['material']!='paper':parts.append(label(v['material']))
 parts.extend(label(s) for s in json.loads(v.get('stamps_json','[]')))
 if v['print_state']!='standard':parts.append(label(v['print_state']))
 return ' · '.join(parts)
def build(write=True):
 db=ROOT/'data/catalog.sqlite3'
 if hashlib.sha256(db.read_bytes()).hexdigest()!=BASELINE_SHA:raise ValueError('Unexpected catalog checkpoint')
 c=sqlite3.connect(db.resolve().as_uri()+'?mode=ro',uri=True);c.row_factory=sqlite3.Row;roster=[dict(r) for r in c.execute('SELECT * FROM roster ORDER BY dex')];english={r['dex']:r['name'] for r in roster};variants=collections.defaultdict(list);images=collections.defaultdict(list);products=collections.defaultdict(list);refs=collections.defaultdict(list);roles=collections.defaultdict(set);years=collections.defaultdict(list)
 for row in c.execute('SELECT * FROM available_variants'):
  v=dict(row);p={k:v[k] for k in ['id','entry_id','finish','pattern','edition','layout','size','material','stamps_json','print_state','printed_rarity_state','printed_rarity_code']};p['label']=printing_label(v);p['category']='jumbo' if v['size']=='oversized' or v['material']=='metal' else 'standard';variants[v['entry_id']].append(p)
 for r in c.execute('''SELECT r.entry_id,r.variant_id,a.asset_sha256,i.preview,i.width,i.height FROM usable_image_acquisitions a JOIN image_refs r ON r.id=a.image_ref_id JOIN image_assets i ON i.sha256=a.asset_sha256 WHERE a.status='downloaded' '''):
  name=Path(r['preview']).name
  if (ROOT/'data/images'/name).is_file():images[r['entry_id']].append(dict(filename=name,variant_id=r['variant_id'],area=(r['width'] or 0)*(r['height'] or 0)))
 for r in c.execute('SELECT entry_id,role FROM subjects WHERE state=\'approved\''):roles[r['entry_id']].add(r['role'])
 for r in c.execute('SELECT p.*,ep.entry_id,ep.date_claim_json FROM source_products p JOIN entry_source_products ep ON ep.product_id=p.id'):
  products[r['entry_id']].append(dict(id=r['id'],name=r['display_name'],state=r['state']))
  claim=json.loads(r['date_claim_json']);match=re.search(r'\b(19\d\d|20\d\d)\b',str(claim.get('raw') or ''))
  if match:years[r['entry_id']].append(int(match[1]))
 for r in c.execute("SELECT b.entry_id,s.source_url FROM source_bindings b JOIN source_records s ON s.id=b.record_id WHERE b.state='bound' AND s.source_url LIKE 'https://%' ORDER BY s.source_id"):
  if r['source_url'] not in refs[r['entry_id']]:refs[r['entry_id']].append(r['source_url'])
 entries=[];used=set()
 for row in c.execute('SELECT e.*,r.release_date,r.date_state FROM published_entries e JOIN releases r ON r.id=e.release_id ORDER BY e.lang,e.species_dex,e.release_key,e.number_key'):
  e=dict(row);eid=e['id'];ims=sorted(images[eid],key=lambda x:-x['area']);image=ims[0]['filename'] if ims else None
  if image:used.add(image)
  ps=variants[eid];category='cameo' if 'cameo' in roles[eid] and 'subject' not in roles[eid] else 'jumbo' if e['track']=='supplementary' else 'standard'
  for p in ps:
   if category=='cameo':p['category']='cameo'
   matches=[x for x in ims if x['variant_id']==p['id']];p['image']=matches[0]['filename'] if matches else image;p['image_scope']='printing' if matches else 'entry'
   if p['image']:used.add(p['image'])
  year=int(e['release_date'][:4]) if e['release_date'] and re.match(r'^\d{4}',e['release_date']) else None;year_basis='set'
  if years[eid] and (year is None or min(years[eid])>year):year=min(years[eid]);year_basis='product_source_claim'
  source_products=products[eid] or [dict(id='release:'+e['lang']+':'+e['release_key'],name=e['release_name'],state='catalog_release')]
  entries.append(dict(id=eid,lang=e['lang'],name=e['display_name'],english=english.get(e['species_dex'],e['display_name']),dex=e['species_dex'],number=e['number_display'],number_key=e['number_key'],identifier_namespace=e['identifier_namespace'],release=e['release_key'],set_name=e['release_name'],year=year,year_basis=year_basis,rarity_code=e['rarity_code'],rarity_state=e['rarity_state'],rarity_namespace=e['rarity_namespace'],rarity_label='No printed rarity' if e['rarity_state']=='not_printed' else label(e['rarity_code']) if e['rarity_state']=='known' else 'Needs research',rarity_family=rarity_family(e['rarity_code']),metadata_state=e['metadata_state'],category=category,image=image,printings=ps,sources=source_products,links=refs[eid][:5]))
 original={r['id']:dict(r) for r in c.execute('SELECT e.id,e.art_style,e.art_style_state,r.release_date,r.date_state FROM published_entries e JOIN releases r ON r.id=e.release_id')}
 for e in entries:
  facts=original[e['id']];date=facts['release_date']
  if e['year_basis']=='product_source_claim':date=str(e['year']) if e['year'] else None
  e.update(release_date=date,date_precision={4:'year',7:'month',10:'day'}.get(len(date or '')),date_state='provider_reference' if e['year_basis']=='product_source_claim' else 'catalog_known' if date else 'unresolved',subject_dex=[e['dex']] if e['category']!='cameo' else [],cameo_dex=[e['dex']] if e['category']=='cameo' else [],art_style=facts['art_style'],art_style_state=facts['art_style_state'])
  if e['lang']=='en':e['english']=e['name']
 payload=dict(format=1,catalog_sha256=BASELINE_SHA,catalog_date='2026-10-27',entries=entries,roster=[dict(dex=r['dex'],name=r['name']) for r in roster if r['dex']],statistics=dict(entries=len(entries),printings=sum(len(e['printings']) for e in entries),without_printings=sum(not e['printings'] for e in entries),missing_images=sum(not e['image'] for e in entries)),used_images=sorted(used))
 if write:(ROOT/'data/catalog.json').write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 c.close();print(json.dumps(payload['statistics']|dict(image_files=len(used))));return payload
def runtime():
 url='https://www.python.org/ftp/python/3.14.10/python-3.14.10-embed-amd64.zip';expected='90905e64a840557d8c1bc4f5b74db3d7ee85e3ffb217611cac1c7813acea4159';p=ROOT/'runtime-download.zip'
 if not p.is_file():
  with urllib.request.urlopen(url,timeout=60) as r:p.write_bytes(r.read(30_000_000))
 if hashlib.sha256(p.read_bytes()).hexdigest()!=expected:raise ValueError('Windows runtime hash differs from Python.org release')
 with zipfile.ZipFile(p) as z:
  names=z.namelist()
  if '_sqlite3.pyd' not in names or 'python.exe' not in names:raise ValueError('Required runtime modules absent')
  z.extractall(ROOT/'runtime')
 (ROOT/'runtime/python314._pth').write_text('python314.zip\n.\n..\n',encoding='utf-8')
 (ROOT/'data/runtime-receipt.json').write_text(json.dumps(dict(url=url,sha256=expected,version='3.14.10',architecture='Windows x64'),indent=2),encoding='utf-8');print('Windows runtime verified')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('command',choices=['catalog','runtime']);a=p.parse_args();build() if a.command=='catalog' else runtime()
