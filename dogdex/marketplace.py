"""Optional official Cardmarket price snapshots, separate from purchase costs.

Only explicitly confirmed product/price-series mappings are priced. An old
provider candidate or a working search URL is not a confirmed price mapping.
"""
import datetime, hashlib, json, math, os, re, threading, unicodedata, urllib.parse, urllib.request
from pathlib import Path

PRICE_URL = 'https://downloads.s3.cardmarket.com/productCatalog/priceGuide/price_guide_6.json'
PRODUCT_URL = 'https://downloads.s3.cardmarket.com/productCatalog/productList/products_singles_6.json'
_product_lock = threading.RLock()

def product_url(product_id):
    return 'https://www.cardmarket.com/en/Pokemon/Products?idProduct=' + str(product_id)

def numeric_product_id(value):
    if type(value) is int and 0 < value <= 9_999_999_999:return value
    if isinstance(value,str) and re.fullmatch(r'[1-9]\d{0,9}',value.strip()):return int(value)
    return None

def product_id_from_url(value):
    """A pretty slug's trailing card number is never a product ID."""
    try:
        url=urllib.parse.urlsplit(value)
        if url.scheme!='https' or url.hostname not in ('cardmarket.com','www.cardmarket.com'):return None
        values=urllib.parse.parse_qs(url.query).get('idProduct',[])
        return numeric_product_id(values[0]) if len(values)==1 else None
    except (ValueError,TypeError):return None

def canonical_product_url(value):
    """Keep product identity; language, condition and edition are offer filters."""
    try:
        url=urllib.parse.urlsplit(value or '')
        if url.scheme!='https' or url.hostname not in ('cardmarket.com','www.cardmarket.com') or url.username or url.password or url.port:return None
        if not re.match(r'^/(?:en|de|fr|es|it)/Pokemon/Products(?:/|$)',url.path):return None
        pid=product_id_from_url(value)
        if pid:return product_url(pid)
        if not re.match(r'^/(?:en|de|fr|es|it)/Pokemon/Products/Singles/[^/]+/[^/]+/?$',url.path):return None
        return 'https://www.cardmarket.com'+re.sub(r'^/(?:en|de|fr|es|it)/','/en/',url.path).rstrip('/')
    except (ValueError,TypeError):return None

def listing_key(value):
    url=canonical_product_url(value)
    return urllib.parse.unquote(url).casefold() if url else None

def saved_listing(entry,printing):
    match=printing.get('market_match') or {}
    if printing.get('market_confirmed') and match.get('canonical_url'):return canonical_product_url(match['canonical_url'])
    if entry.get('market_link_override'):
        return canonical_product_url(entry.get('cardmarket_url'))
    return canonical_product_url(printing.get('cardmarket_url')) or canonical_product_url(entry.get('cardmarket_url'))

def _same_card(a,b):
    if a['lang']!=b['lang'] and {a['lang'],b['lang']}!={'en','de'}:return False
    number=lambda e:re.sub(r'^0+(?=\d)','',str(e['number'])).casefold()
    return (a['release']==b['release'] and number(a)==number(b) and a.get('identifier_namespace','collector')==b.get('identifier_namespace','collector') and _fold(a.get('english') or a['name'])==_fold(b.get('english') or b['name']))

def _compatible(entry,printing,other,p):
    if not _same_card(entry,other):return False
    if any(printing.get(k)!=p.get(k) for k in ('size','material','stamps_json')):return False
    plain={'none','unspecified',None}
    if printing.get('pattern')!=p.get('pattern') and not {printing.get('pattern'),p.get('pattern')}<=plain:return False
    # English Base Shadowless is its own Cardmarket product, including First Edition.
    shadowless=lambda e,q:e['lang']=='en' and e['release']=='base1' and q.get('layout')=='shadowless'
    if shadowless(entry,printing)!=shadowless(other,p):return False
    return True

def related_printings(entry,printing,product_id,url,family):
    key=listing_key(url);current_key=listing_key(saved_listing(entry,printing));out=[]
    for other,p in family:
        current=p['id']==printing['id']
        if not current:
            if not _compatible(entry,printing,other,p):continue
            if p.get('market_confirmed') and p.get('price_product_id')!=product_id:continue
            same_url=key and current_key==key and listing_key(saved_listing(other,p))==key
            same_confirmed=p.get('market_confirmed') and p.get('price_product_id')==product_id
            if not (same_url or same_confirmed):continue
        out.append(dict(printing_id=p['id'],entry_id=other['id'],context_key=match_context(other,p),lang=other['lang'],name=other['name'],number=other['number'],set_name=other['set_name'],label=p['label'],price_series=p.get('price_series') if p.get('market_confirmed') and p.get('price_product_id')==product_id and p.get('price_series') in ('standard','reverse') else ('reverse' if p['finish']=='reverse_holo' else 'standard'),current=current,already_linked=p.get('market_confirmed') is True and p.get('price_product_id')==product_id))
    return sorted(out,key=lambda x:(not x['current'],x['lang'],x['label']))

def _fold(value):
    value=unicodedata.normalize('NFKD',str(value)).casefold()
    return ' '.join(''.join(c if c.isalnum() else ' ' for c in value if not unicodedata.combining(c)).split())

def _code_product(name):return _fold(name).startswith('online code card')

def match_context(entry,printing):
    physical=('id','finish','pattern','edition','layout','size','material','stamps_json','print_state','printed_rarity_state','printed_rarity_code','price_product_id','price_series','market_confirmed','cardmarket_url')
    value=dict(identity=identity_key(entry),set_name=entry.get('set_name'),listing=saved_listing(entry,printing),printing={k:printing.get(k) for k in physical})
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False).encode()).hexdigest()

def _target(store,printing_id,entries=None):
    from .collector import ValidationError
    for entry in (entries if entries is not None else store.entries().values()):
        for printing in entry['printings']:
            if printing['id']==printing_id:return entry,printing
    raise ValidationError('This printing is no longer an active collection target. Reopen the card.')

def provider_variant_matches(entry,printing,variant):
    """Match an explicit provider tuple, never a finish-only product hint.

    Edition filters can share one listing; patterns, stamps and Base Shadowless
    cannot. Regional provider mirrors are references, not availability evidence.
    """
    from .printing_model import normalized,pattern_key,token
    kinds={'holo':'holo','holofoil':'holo','reverse':'reverse_holo','reverse_holo':'reverse_holo','normal':'non_holo','non_holo':'non_holo'}
    p=normalized(printing);finish=kinds.get(token(variant.get('type')))
    if finish!=p['finish']:return False
    foil=variant.get('foil',variant.get('pattern'))
    if token(foil)=='kosmos':foil='cosmos'
    if pattern_key(foil,finish)!=p['pattern']:return False
    size={'jumbo':'oversized','ubergross':'oversized'}.get(token(variant.get('size')),token(variant.get('size')) or 'standard')
    if size!=p['size'] or (token(variant.get('material')) or 'paper')!=p['material']:return False
    stamps=variant.get('stamp',[])
    if not isinstance(stamps,list):return False
    edition_marks={'1st_edition','1_auflage','first_edition'}
    raw_stamps={token(s) for s in stamps}-edition_marks
    aliases={'trick_or_trade':'pikachu_jack_o_lantern','set_logo':{'me04':'chaos_rising'}.get(entry.get('release'),'unresolved_set_logo')}
    if {aliases.get(s,s) for s in raw_stamps}!=set(json.loads(p['stamps_json'])):return False
    subtype=token(variant.get('subtype'))
    shadowless=subtype in ('shadowless','schattenlos')
    if entry.get('release')=='base1':
        if shadowless and entry.get('lang')!='en':return False
        if shadowless!=(p['layout']=='shadowless'):return False
    elif variant.get('layout') and token(variant['layout'])!=p['layout']:return False
    state='1999_2000_copyright' if subtype in ('1999_2000_copyright','copyright_1999_2000') else 'standard'
    if token(p['print_state'])!=state:return False
    return True

def provider_products(entry,printing):
    """Recover positive source assertions, without treating them as confirmation."""
    out={}
    def add(value,source,url=None,name=None):
        pid=numeric_product_id(value)
        if not pid:return
        item=out.setdefault(pid,dict(product_id=pid,name=name or '',origins=[]))
        origin=dict(label=source,source_url=url,lang=entry['lang'],release=entry['release'],number=entry['number'])
        if origin not in item['origins']:item['origins'].append(origin)
        if name and not item['name']:item['name']=name
    if printing.get('market_confirmed'):add(printing.get('price_product_id'),'Current confirmed match')
    candidate=printing.get('market_candidate') or {}
    from .printing_model import physical_key,pattern_key
    valid_candidate=(not candidate.get('physical_key') or candidate['physical_key']==list(physical_key(entry['id'],printing)))
    if candidate.get('finish') and candidate['finish']!=printing.get('finish'):valid_candidate=False
    if candidate.get('pattern') and pattern_key(candidate['pattern'],printing.get('finish'))!=pattern_key(printing.get('pattern'),printing.get('finish')):valid_candidate=False
    if valid_candidate:
        add(candidate.get('product_id'),'Unverified provider reference',candidate.get('source_url'),candidate.get('name'))
        pid=numeric_product_id(candidate.get('product_id'))
        if pid in out and canonical_product_url(candidate.get('canonical_url')):out[pid]['listing_url']=canonical_product_url(candidate['canonical_url'])
    for obj in (printing,entry):
        pid=product_id_from_url(obj.get('cardmarket_url'))
        if obj is printing and not valid_candidate:continue
        if obj is entry and pid not in out:
            from .printing_model import normalized
            n=normalized(printing)
            if n['pattern'] not in ('none','unspecified') or n['stamps_json']!='[]' or n['size']!='standard' or n['material']!='paper' or (entry.get('release')=='base1' and n['layout']=='shadowless'):continue
        add(pid,'Existing numeric listing link',obj.get('cardmarket_url'))
    # Authored regional evidence attaches IDs to an explicit finish. Do not
    # borrow a different finish's ID, or recursively interpret arbitrary numbers.
    for fact in entry.get('evidence',[]):
        if fact.get('disposition') in ('excluded','rejected','superseded'):continue
        value=fact.get('value')
        if not isinstance(value,dict):continue
        for variant in value.get('variants',[]) if isinstance(value.get('variants'),list) else []:
            if not isinstance(variant,dict) or not provider_variant_matches(entry,printing,variant):continue
            third=variant.get('thirdParty') or {}
            if isinstance(third,dict):
                add(third.get('cardmarket'),'Regional provider reference',(fact.get('source_urls') or [None])[0],entry.get('english') or entry['name'])
    return out

def _references(store,entry,printing,entries):
    refs=provider_products(entry,printing);url=saved_listing(entry,printing);key=listing_key(url)
    for pid,item in refs.items():
        if printing.get('market_confirmed') and pid==printing.get('price_product_id'):item['listing_url']=url
        elif not item.get('listing_url'):item['listing_url']=url if len(refs)==1 else product_url(pid)
    # Inspect the merged collector view, so saved matches and manual edits participate.
    for other in entries:
        if not _same_card(entry,other):continue
        for p in other['printings']:
            if p['id']==printing['id'] or not _compatible(entry,printing,other,p):continue
            other_url=saved_listing(other,p);same_url=key and listing_key(other_url)==key
            same_physical=all(p.get(k)==printing.get(k) for k in ('finish','pattern','edition','layout','size','material','stamps_json','print_state'))
            if not same_url and not same_physical:continue
            for pid,item in provider_products(other,p).items():
                linked=p.get('market_confirmed') and p.get('price_product_id')==pid
                label='Confirmed related printing' if linked else 'Same listing reference · unconfirmed' if same_url else 'Other Western ledger reference · language/printing unchecked'
                target=refs.setdefault(pid,dict(product_id=pid,name=item.get('name') or '',origins=[]))
                target['origins'].extend({**o,'label':label} for o in item['origins'])
                if same_url:target['listing_url']=url
                if linked:
                    target['reusable']=True;target['reused_from']=dict(printing_id=p['id'],lang=other['lang'],release=other['release'],number=other['number'],label=p['label'])
                    target['listing_url']=other_url or url
    return refs

def read_products(store):
    path=store.user_dir/'market_products.json'
    try:
        stat=path.stat();stamp=(stat.st_mtime_ns,stat.st_size)
        cached=getattr(store,'_market_product_cache',None)
        if cached and cached[0]==stamp:return cached[1]
        value=json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(value,dict) or value.get('format')!='dogdex-cardmarket-products-1' or not isinstance(value.get('products'),dict):return {}
        if not isinstance(value.get('source_created_at'),str) or any(not isinstance(row,dict) or numeric_product_id(key)!=row.get('product_id') or not isinstance(row.get('name'),str) for key,row in value['products'].items()):return {}
        store._market_product_cache=(stamp,value)
        return value
    except (OSError,ValueError,TypeError):return {}

def refresh_products(store,force=False):
    from .collector import ValidationError,now
    with _product_lock:
        previous=read_products(store)
        if previous and not force and previous.get('fetched_at','')[:10]==now()[:10]:return previous
        try:
            request=urllib.request.Request(PRODUCT_URL,headers={'User-Agent':'DogDex/1.8.3 (personal collection product lookup)'})
            with urllib.request.urlopen(request,timeout=25) as response:raw=response.read(80_000_001)
            if len(raw)>80_000_000:raise ValueError('Product catalogue exceeds the size limit')
            data=json.loads(raw)
            if not isinstance(data.get('products'),list):raise ValueError('Unsupported product catalogue')
            created=data.get('createdAt');datetime.datetime.fromisoformat(created)
            products={}
            for row in data['products']:
                pid=numeric_product_id(row.get('idProduct'));name=row.get('name')
                if not pid or not isinstance(name,str) or not name.strip() or str(pid) in products:raise ValueError('Invalid product identity')
                products[str(pid)]=dict(product_id=pid,name=name,id_expansion=row.get('idExpansion'),id_metacard=row.get('idMetacard'))
            if not products:raise ValueError('Empty product catalogue')
            value=dict(format='dogdex-cardmarket-products-1',source_url=PRODUCT_URL,source_created_at=created,fetched_at=now(),products=products)
            target=store.user_dir/'market_products.json';temporary=target.with_suffix('.tmp')
            temporary.write_text(json.dumps(value,ensure_ascii=False,separators=(',',':')),encoding='utf-8');os.replace(temporary,target)
            store._market_product_cache=None
            return read_products(store)
        except (OSError,ValueError,TypeError,KeyError) as exc:
            raise ValidationError('The product catalogue could not be refreshed. Cached references are kept. '+str(exc)) from exc

def search_products(store,data):
    from .collector import ValidationError
    entries=list(store.entries().values());entry,printing=_target(store,data.get('printing_id'),entries);refs=_references(store,entry,printing,entries)
    existing=saved_listing(entry,printing)
    default=str(printing['price_product_id']) if printing.get('market_confirmed') and printing.get('price_product_id') else existing or entry.get('market_name') or entry.get('english') or entry['name']
    query=data.get('query',default)
    if not isinstance(query,str) or len(query)>2000:raise ValidationError('Use a card name, numeric product ID or Cardmarket URL.')
    query=query.strip();typed=numeric_product_id(query) or product_id_from_url(query);pasted_url=None
    if query.startswith('https://'):
        pasted_url=canonical_product_url(query)
        if not pasted_url:raise ValidationError('Use a Cardmarket Pokémon product URL.')
    cache=read_products(store);warning=None
    if data.get('refresh') is True or not cache and not data.get('cache_only'):
        try:cache=refresh_products(store,data.get('refresh') is True)
        except ValidationError as exc:warning=str(exc)
    products=cache.get('products',{});tokens=_fold((entry.get('market_name') or entry.get('english') or entry['name']) if pasted_url else query).split()[:12]
    family=[(e,p) for e in entries if _same_card(entry,e) for p in e['printings']]
    matches={}
    def candidate(pid,reference=None):
        raw=products.get(str(pid)) or {};hint=reference or {};url=hint.get('listing_url') or product_url(pid)
        name=raw.get('name') or hint.get('name') or 'Cardmarket product '+str(pid)
        return dict(product_id=pid,name=name,id_expansion=raw.get('id_expansion'),catalogue_present=bool(raw),origins=hint.get('origins',[]),listing_url=url,suggested=bool(reference),reusable=bool(hint.get('reusable')),reused_from=hint.get('reused_from'),code_product=_code_product(name),current=pid==printing.get('price_product_id') and printing.get('market_confirmed') is True,related_printings=related_printings(entry,printing,pid,url,family))
    if typed:matches[typed]=candidate(typed,refs.get(typed))
    else:
        for pid,hint in refs.items():matches[pid]=candidate(pid,hint)
        for key,row in products.items():
            name=_fold(row.get('name',''))
            if tokens and not _code_product(row.get('name','')) and all(token in name for token in tokens):
                pid=int(key);matches.setdefault(pid,candidate(pid))
    results=sorted(matches.values(),key=lambda p:(not p['current'],not p['reusable'],not p['suggested'],p['name'].casefold(),p['product_id']))
    offset=data.get('offset',0)
    if type(offset) is not int or not 0<=offset<=100000:raise ValidationError('Invalid results page.')
    return dict(context_key=match_context(entry,printing),entry_id=entry['id'],printing_id=printing['id'],query=query,existing_url=existing,context=dict(name=entry.get('market_name') or entry.get('english') or entry['name'],native_name=entry['name'],lang=entry['lang'],release=entry['release'],set_name=entry['set_name'],number=entry['number'],printing=printing['label'],finish=printing['finish'],edition=printing.get('edition'),image=printing.get('image') or entry.get('image')),default_series='reverse' if printing['finish']=='reverse_holo' else 'standard',current_product_id=printing.get('price_product_id') if printing.get('market_confirmed') else None,current_series=printing.get('price_series'),products=results[offset:offset+60],next_offset=offset+60 if offset+60<len(results) else None,total=len(results),catalogue=dict(available=bool(cache),updated_at=cache.get('source_created_at'),count=len(products)),warning=warning,pasted_url=pasted_url)

def confirm_product(store,data,unlink=False):
    from .collector import ValidationError
    from .printing_model import physical_key
    from .editor import dump,timestamp
    with store.lock:
        entries=list(store.entries().values());entry,printing=_target(store,data.get('printing_id'),entries)
        if data.get('context_key')!=match_context(entry,printing):raise ValidationError('The card or printing changed. Reopen the product finder before saving.')
        before=dict(printing);selected_url=None
        if unlink:
            targets=[dict(printing_id=printing['id'],context_key=match_context(entry,printing))]
            allowed={printing['id']:(entry,printing)}
        else:
            fields=validate_price_mapping(dict(price_product_id=data.get('product_id'),price_series=data.get('price_series'),market_confirmed=data.get('confirmed')),printing)
            if not fields['price_product_id']:raise ValidationError('Select a product to confirm.')
            pid=fields['price_product_id']
            if fields['price_series']=='reverse' and printing['finish']!='reverse_holo':raise ValidationError('Only a reverse-holo printing can use the reverse-holo price series.')
            row=read_products(store).get('products',{}).get(str(pid),{})
            if _code_product(row.get('name','')):raise ValidationError('That product is an online code card. Choose the physical Pokémon card listing.')
            refs=_references(store,entry,printing,entries)
            known_url=refs.get(pid,{}).get('listing_url')
            selected_url=canonical_product_url(data.get('listing_url')) or known_url or product_url(pid)
            # Batch reuse is allowed only for the same existing listing or a saved product match.
            requested_key=listing_key(selected_url)
            if requested_key not in {listing_key(saved_listing(entry,printing)),listing_key(known_url)}:selected_url=product_url(pid)
            family=[(e,p) for e in entries if _same_card(entry,e) for p in e['printings']]
            choices=related_printings(entry,printing,pid,selected_url,family)
            ids={x['printing_id'] for x in choices};allowed={p['id']:(e,p) for e,p in family if p['id'] in ids}
            targets=data.get('targets',[dict(printing_id=printing['id'],context_key=data['context_key'])])
            if not isinstance(targets,list) or not 1<=len(targets)<=100 or any(not isinstance(x,dict) for x in targets):raise ValidationError('Choose the related printings to link.')
            target_ids=[x.get('printing_id') for x in targets]
            if any(not isinstance(x,str) for x in target_ids) or len(set(target_ids))!=len(target_ids) or printing['id'] not in target_ids or any(x not in allowed for x in target_ids):raise ValidationError('These printings do not share the selected product. Reopen the finder.')
        for target in targets:
            e,p=allowed[target['printing_id']]
            if target.get('context_key')!=match_context(e,p):raise ValidationError('A related printing changed. Reopen the product finder before saving.')
        when=timestamp();cache=read_products(store)
        with store.connect() as db:
            for target in targets:
                e,p=allowed[target['printing_id']]
                if unlink:values=dict(price_product_id=None,price_series=None,market_confirmed=False,market_identity=None)
                else:
                    series=fields['price_series'] if p['id']==printing['id'] else p['price_series'] if p.get('market_confirmed') and p.get('price_product_id')==pid and p.get('price_series') in ('standard','reverse') else ('reverse' if p['finish']=='reverse_holo' else 'standard')
                    values=dict(price_product_id=pid,price_series=series,market_confirmed=True,market_identity=identity_key(e),market_physical_key=list(physical_key(e['id'],p)),cardmarket_url=selected_url,market_match=dict(method='collector_product_search',canonical_url=selected_url,confirmed_at=when,product_name=row.get('name'),catalogue_source=PRODUCT_URL if row else None,catalogue_created_at=cache.get('source_created_at') if row else None,shared_confirmation=len(targets)>1))
                old=db.execute('SELECT payload_json FROM printing_overrides WHERE printing_id=?',(p['id'],)).fetchone()
                payload={**(json.loads(old[0]) if old else {}),**p};payload.pop('_image_review_only',None);payload.update(values)
                db.execute('INSERT OR REPLACE INTO printing_overrides VALUES(?,?,?,?)',(p['id'],dump(payload),'Cardmarket match removed by the collector.' if unlink else 'Collector confirmed the selected product and related printings; price series assigned separately for each printing.',when))
                store.audit(db,'market_unlinked' if unlink else 'market_confirmed',p['id'],{k:p.get(k) for k in values},values)
    result=dict(saved=True,printing_id=printing['id'],product_id=None if unlink else pid,linked_count=0 if unlink else len(targets),linked_printing_ids=[] if unlink else [t['printing_id'] for t in targets])
    if not unlink:
        try:result['prices']=refresh_prices(store)['prices']
        except ValidationError as exc:result['price_warning']=str(exc)
    return result

def identity_key(entry):
    return {key:entry.get(key) for key in ('lang','release','number','name')}

def read_cache(store):
    try:
        value = json.loads((store.user_dir / 'market_prices.json').read_text(encoding='utf-8'))
        return value if value.get('format') == 'dogdex-cardmarket-prices-1' else {}
    except (OSError, ValueError, TypeError): return {}

def price_state(store, view=None):
    view = view or store.editor_view()
    cache = read_cache(store)
    result = dict(updated_at=cache.get('source_created_at'), fetched_at=cache.get('fetched_at'),
                  source_url=PRICE_URL, currency='EUR', printings={})
    for entry in view['entries']:
        if entry.get('identity_status') not in (None, 'documented'): continue
        for printing in entry['printings']:
            product = printing.get('price_product_id')
            series = printing.get('price_series')
            if not printing.get('market_confirmed') or not product or series not in ('standard', 'reverse'): continue
            if printing.get('market_identity')!=identity_key(entry): continue
            raw = cache.get('products', {}).get(str(product))
            if not raw: continue
            suffix = '-holo' if series == 'reverse' else ''
            fields = {key: raw.get(key + suffix) for key in ('trend', 'avg7', 'avg30', 'low')}
            if not any(value is not None for value in fields.values()): continue
            result['printings'][printing['id']] = dict(product_id=product, series=series, **fields)
    return result

def refresh_prices(store, force=False):
    from .collector import ValidationError, now
    previous = read_cache(store)
    # Opening a card never causes a download. Explicit refresh is cached for a day.
    if not force and previous.get('fetched_at', '')[:10] == now()[:10]:
        return dict(prices=price_state(store), cached=True)
    request = urllib.request.Request(PRICE_URL, headers={'User-Agent': 'DogDex/1.8 (personal collection price guide)'})
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            raw = response.read(40_000_001)
        if len(raw) > 40_000_000: raise ValueError('Price file is too large')
        data = json.loads(raw)
        if data.get('version') != 1 or not isinstance(data.get('priceGuides'), list):
            raise ValueError('Unsupported price guide format')
        created = data.get('createdAt')
        if not isinstance(created, str): raise ValueError('Missing source date')
        datetime.datetime.fromisoformat(created)
        products = {}
        for row in data['priceGuides']:
            pid = row.get('idProduct')
            if type(pid) is not int or pid <= 0 or str(pid) in products: raise ValueError('Invalid product identity')
            values = {k: row.get(k) for k in ('trend', 'avg7', 'avg30', 'low', 'trend-holo', 'avg7-holo', 'avg30-holo', 'low-holo')}
            if any(v is not None and (type(v) not in (int, float) or not math.isfinite(v) or v < 0) for v in values.values()):
                raise ValueError('Invalid price value')
            products[str(pid)] = values
        if not products: raise ValueError('Empty price guide')
        value = dict(format='dogdex-cardmarket-prices-1', source_url=PRICE_URL,
                     source_created_at=created, fetched_at=now(), products=products)
        target = store.user_dir / 'market_prices.json'
        temporary = target.with_suffix('.tmp')
        with store.lock:
            temporary.write_text(json.dumps(value, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
            os.replace(temporary, target)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        raise ValidationError('Cardmarket prices could not be refreshed. Earlier cached prices are kept. ' + str(exc)) from exc
    return dict(prices=price_state(store), cached=False, products=len(products))

def validate_price_mapping(data, old):
    """A deliberate per-printing decision; no automatic use of quarantined IDs."""
    from .collector import ValidationError
    product = data.get('price_product_id', (old or {}).get('price_product_id'))
    if product in ('', None): return dict(price_product_id=None, price_series=None, market_confirmed=False)
    if isinstance(product, str) and re.fullmatch(r'[1-9]\d{0,9}', product): product = int(product)
    if type(product) is not int or not 1 <= product <= 9_999_999_999:
        raise ValidationError('Use the numeric Cardmarket product ID, or leave it empty.')
    series = data.get('price_series', (old or {}).get('price_series'))
    confirmed = data.get('market_confirmed') is True
    if not confirmed or series not in ('standard', 'reverse'):
        raise ValidationError('Confirm the Cardmarket card, set, number and exact price series, or clear the product ID.')
    return dict(price_product_id=product, price_series=series, market_confirmed=True)
