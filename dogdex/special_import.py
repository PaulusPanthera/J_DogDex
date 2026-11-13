"""Merge sourced physical-card facts, preserving every existing catalog identifier.

Research files contain explicit tuples. No rarity-to-finish Cartesian products are
created here. Unknown identities/rarities/tuples remain review-only records.
"""
import collections,hashlib,io,json,re,sqlite3,unicodedata,urllib.request,uuid
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
from .printing_model import physical_key,legacy_physical_key,legacy_label as printing_label
from .prepare import rarity_family

ROOT=Path(__file__).resolve().parents[1]
FACTS=ROOT/'data/research'
def stable(kind,value):return 'research_'+kind+'_'+uuid.uuid5(uuid.NAMESPACE_URL,json.dumps(value,ensure_ascii=False,sort_keys=True)).hex
def norm(value):return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',str(value)).encode('ascii','ignore').decode().lower())
def number(value):return str(value or 'Unnumbered').split('/')[0].lstrip('0') or '0'
def load(name):return json.loads((FACTS/name).read_text(encoding='utf-8'))
def write_json(path,value):
 tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(value,ensure_ascii=False,separators=(',',':')),encoding='utf-8');tmp.replace(path)
def date_fields(value,state,source):return dict(release_date=value,date_precision={4:'year',7:'month',10:'day'}.get(len(value or '')),year=int(value[:4]) if value else None,date_state=state,date_source=source)
def add_printing(e,raw,provenance,review):
 if e['metadata_state']!='approved' or e.get('identity_status') in ('provisional','disputed','excluded','announced'):
  review.append(dict(entry_id=e['id'],reason='identity_not_documented',source=provenance));return None
 p={k:raw.get(k,default) for k,default in [('finish',None),('pattern','none'),('edition',None),('layout','standard'),('size','standard'),('material','paper'),('print_state','standard'),('printed_rarity_state','inherit'),('printed_rarity_code',None)]}
 p['stamps_json']=json.dumps(sorted(set(raw.get('stamps',json.loads(raw.get('stamps_json','[]'))))),ensure_ascii=False,separators=(',',':'))
 if p['finish'] not in ('non_holo','holo','reverse_holo') or p['edition'] not in ('first_edition','unlimited','not_applicable','unstamped') or p['size'] not in ('standard','oversized') or p['material'] not in ('paper','metal'):
  review.append(dict(entry_id=e['id'],reason='unsupported_or_incomplete_physical_tuple',source=provenance));return None
 key=physical_key(e['id'],p)
 existing=next((old for old in e['printings'] if physical_key(e['id'],old)==key),None)
 if existing:
  if raw.get('product_name'):
   source=dict(id=stable('product',[e['lang'],raw['product_name']]),name=raw['product_name'],state='verified_product')
   if not any(s['id']==source['id'] for s in existing.get('sources',[])):existing.setdefault('sources',[]).append(source)
  return existing
 p.update(id=stable('printing',legacy_physical_key(e['id'],p)),entry_id=e['id'],image=e.get('image'),image_scope='entry',category='jumbo' if p['size']=='oversized' or p['material']=='metal' else 'cameo' if e['category']=='cameo' else 'standard',provenance=provenance)
 p['label']=printing_label(p)
 if raw.get('product_name'):
  p['sources']=[dict(id=stable('product',[e['lang'],raw['product_name']]),name=raw['product_name'],state='verified_product')]
 if raw.get('release_date'):p.update(date_fields(raw['release_date'],'sourced_product',raw.get('source_url')))
 cm=raw.get('raw_variant',{}).get('thirdParty',{}).get('cardmarket')
 if type(cm) is int:p['market_product_id']=cm
 e['printings'].append(p);return p

def rarity_map():
 c=sqlite3.connect((ROOT/'data/catalog.sqlite3').as_uri()+'?mode=ro',uri=True);mapping=collections.defaultdict(set)
 for lang,raw,code,state in c.execute("SELECT e.lang,a.raw_value_json,a.mapped_code,a.state FROM rarity_assertions a JOIN published_entries e ON e.id=a.entry_id WHERE a.state IN ('known','not_printed')"):
  label=json.loads(raw)
  if isinstance(label,str):mapping[lang,label].add((code,state))
 c.close();return {k:next(iter(v)) for k,v in mapping.items() if len(v)==1}

def import_special(catalog):
 data=load('special_cards.json');entries=catalog['entries'];byid={e['id']:e for e in entries};lookup=collections.defaultdict(list);roster={r['dex'] for r in catalog['roster']};mapping=rarity_map();review=[];jobs=[]
 for e in entries:lookup[e['lang'],e['release'],number(e['number'])].append(e)
 for record in data['cameos']:
  e=byid.get(record.get('existing_entry_id'))
  if not e:
   matches=lookup[record['lang'],record['set_key'],number(record.get('number'))]
   if len(matches)==1:e=matches[0]
   elif len(matches)>1:review.append(dict(source_id=record['source_id'],reason='ambiguous_identity'));continue
  if not e:
   raw=record.get('rarity_label');code,state=mapping.get((record['lang'],raw),(None,'unresolved'))
   if record.get('rarity_state')=='not_printed' or raw=='No printed rarity' or (record['lang']=='ja' and raw=='Promo'):code,state=None,'not_printed'
   if state=='unresolved' and raw in ('C','U','R','RR','RRR','SR','SAR','AR','UR','HR','CHR','CSR','SSR','S','P'):code,state=raw,'known'
   cameo=sorted(set(record.get('cameo_dex',[]))&roster);subject=sorted(set(record.get('subject_dex',[]))&roster)
   if not cameo and not subject:review.append(dict(source_id=record['source_id'],reason='outside_roster'));continue
   eid=stable('entry',[record['lang'],record['source_id']]);num=str(record.get('number') or 'Unnumbered');category='standard' if subject else 'cameo'
   e=dict(id=eid,lang=record['lang'],name=record['name'],english=record.get('english_name') or record['name'],dex=(subject or cameo)[0],subject_dex=subject,cameo_dex=cameo,number=num,number_key=record.get('unnumbered_key') or num,identifier_namespace=record.get('identifier_namespace','collector'),release=record['set_key'],set_name=record['set_name'],year=None,year_basis='set',release_date=None,date_precision=None,date_state='unresolved',rarity_code=code,rarity_state=state,rarity_namespace='sourced_localized',rarity_label='No printed rarity' if state=='not_printed' else raw or 'Needs research',rarity_family=rarity_family(code),metadata_state=record.get('metadata_state','review'),category=category,image=None,printings=[],sources=[dict(id='release:'+record['lang']+':'+record['set_key'],name=record['set_name'],state='catalog_release')],links=record.get('source_urls',[])[:8],art_style=None,art_style_state='unresolved',provenance=dict(source_id=record['source_id'],cameo_evidence=record.get('cameo_evidence'),source_urls=record.get('source_urls',[])))
   entries.append(e);byid[eid]=e;lookup[e['lang'],e['release'],number(num)].append(e)
  e['cameo_dex']=sorted(set(e.get('cameo_dex',[]))|set(record.get('cameo_dex',[]))&roster)
  e['english']=record.get('english_name') or e['english']
  e['links']=list(dict.fromkeys(e.get('links',[])+record.get('source_urls',[])))[:10]
  e['cameo_source']=dict(source_urls=record.get('source_urls',[]),evidence=record.get('cameo_evidence'))
  if record.get('release_date'):
   e.update(date_fields(record['release_date'],'sourced_card',next(iter(record.get('source_urls',[])),None)),year_basis='card')
  for raw in record.get('printings',[]):add_printing(e,raw,dict(kind='cameo_physical_tuple',source_url=raw.get('source_url'),evidence=raw.get('evidence'),raw_tuple=raw.get('raw_variant')),review)
  if not e.get('image') and record.get('image_url'):jobs.append(dict(entry_id=e['id'],url=record['image_url'],local=record.get('image_local')))
 for record in data['jumbo_printings']:
  e=byid.get(record.get('existing_entry_id'))
  if not e:review.append(dict(source_id=record.get('provider_id'),reason='jumbo_identity_not_found'));continue
  add_printing(e,record['printing'],dict(kind='manufacturer_oversized_product',source_urls=record.get('source_urls',[]),evidence=record['printing'].get('evidence'),raw_tuple=record['printing'].get('raw_variant')),review)
 catalog['special_research']=data.get('pending',[]);catalog['special_import_review']=review
 return jobs

def acquire_images(catalog,jobs,download=False):
 cachepath=FACTS/'image_cache.json';cache=load('image_cache.json') if cachepath.exists() else {};byid={e['id']:e for e in catalog['entries']};failures=[]
 def fetch(job):
  url=job['url'];cached=cache.get(url,{})
  if cached.get('filename') and (ROOT/'data/images'/cached['filename']).is_file():return job,cached
  from PIL import Image,ImageOps
  local=Path(job.get('local') or '/')
  if local.is_file():raw=local.read_bytes()
  elif download:
   request=urllib.request.Request(url,headers={'User-Agent':'DogDex catalog reference research (local collection)'})
   with urllib.request.urlopen(request,timeout=15) as response:raw=response.read(15_000_001)
  else:raise ValueError('Reference image not cached; run catalog_enrich.py --images during source preparation')
  if len(raw)>15_000_000:raise ValueError('Image is too large')
  im=ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert('RGB');im.thumbnail((900,1260));output=io.BytesIO();im.save(output,format='WEBP',quality=90);content=output.getvalue();filename=hashlib.sha256(content).hexdigest()+'.webp';(ROOT/'data/images'/filename).write_bytes(content)
  return job,dict(filename=filename,source_sha256=hashlib.sha256(raw).hexdigest(),source_url=url,width=im.width,height=im.height)
 with ThreadPoolExecutor(max_workers=6) as pool:
  tasks={pool.submit(fetch,job):job for job in jobs}
  for task in as_completed(tasks):
   try:
    job,info=task.result();cache[job['url']]=info;e=byid[job['entry_id']];e['image']=info['filename'];e['image_source']=job['url']
    for p in e['printings']:
     if not p.get('image'):p.update(image=e['image'],image_scope='entry')
    write_json(cachepath,cache)
   except Exception as exc:
    job=tasks[task];failures.append(dict(entry_id=job['entry_id'],source_url=job['url'],reason=str(exc)))
 catalog['image_acquisition_review']=sorted(failures,key=lambda record:(record['entry_id'],record['source_url']))
 return len(jobs)-len(failures)
