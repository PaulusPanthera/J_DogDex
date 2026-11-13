"""Direct, reversible local catalog editing. Stable IDs keep collection references intact."""
import copy,datetime,hashlib,json,re,uuid
from .scope import EXCLUDED_DEX,in_scope,trim_species
from .identity_corrections import apply_form_review
from .rarities import normalize as normalize_rarity,label as rarity_label
from .source_structure import annotate_sources,annotate_entry,validate_source_structure,guard_primary_source
from .printing_model import normalized,physical_key,printing_label,PATTERNS,LAYOUTS,token,verification,image_review,taxonomy

LANGS=('en','de','ja','ko')
SOURCE_KINDS=('set','deck','promo','box','event','other')
NEW_TABLES=['manual_sources','source_overrides','printing_overrides','catalog_trash']
EDITOR_SCHEMA='''
CREATE TABLE IF NOT EXISTS manual_sources(id TEXT PRIMARY KEY,payload_json TEXT NOT NULL,source_note TEXT NOT NULL,created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS source_overrides(source_id TEXT PRIMARY KEY,payload_json TEXT NOT NULL,source_note TEXT NOT NULL,updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS printing_overrides(printing_id TEXT PRIMARY KEY,payload_json TEXT NOT NULL,source_note TEXT NOT NULL,updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS catalog_trash(id TEXT PRIMARY KEY,kind TEXT NOT NULL,target_id TEXT NOT NULL,name TEXT NOT NULL,deleted_at TEXT NOT NULL);
'''

def fail(message):raise ValueError(message)
def clean(value,limit=4000):
    if not isinstance(value,str) or len(value)>limit:fail('Text is missing or too long.')
    return value.strip()
def dump(value):return json.dumps(value,ensure_ascii=False,separators=(',',':'),sort_keys=True)
def timestamp():return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
def uid(prefix):return prefix+'_'+uuid.uuid4().hex
def source_note(data):return clean(data.get('source_note') or 'Catalog edit recorded by the collector.',4000)
def date_fields(value):
    value=clean(value or '',10)
    if not value:return dict(release_date=None,date_precision=None,year=None)
    try:
        match=re.fullmatch(r'(\d{4})(?:-(\d{2})(?:-(\d{2}))?)?',value)
        if not match:raise ValueError()
        y,m,d=match.groups();datetime.date(int(y),int(m or 1),int(d or 1))
        if not 1996<=int(y)<=2100:raise ValueError()
    except ValueError:fail('Use a real release date: YYYY-MM-DD, YYYY-MM or YYYY.')
    return dict(release_date=value,date_precision={4:'year',7:'month',10:'day'}[len(value)],year=int(value[:4]))
def urls(values):
    if isinstance(values,str):values=[v.strip() for v in values.splitlines() if v.strip()]
    if not isinstance(values,list) or len(values)>20:fail('Use up to 20 source links, one per line.')
    if any(not isinstance(v,str) or len(v)>2000 or not re.match(r'^https?://[^\s]+$',v) for v in values):fail('Use complete HTTP or HTTPS source links.')
    return list(dict.fromkeys(values))
def market_url(value):
    value=clean(value or '',2000)
    if value and not re.match(r'^https://(?:www\.)?cardmarket\.com/',value):fail('Use a complete HTTPS Cardmarket listing link.')
    return value or None

def source_kind(name,key=''):
    folded=name.casefold()
    if any(x in folded for x in ('promo','promokarten','プロモ','프로모')) or key in ('S-P','SV-P','M-P','SMP','XYP','BWP','DPP','DPtP','LP'):return 'promo'
    if any(x in folded for x in ('deck','デッキ','덱','trainer kit')):return 'deck'
    if any(x in folded for x in ('box','collection','kollektion','コレクション','ボックス','컬렉션','박스')):return 'box'
    return 'set'

def base_sources(catalog,retired=False):
    result={}
    releases=catalog.get('releases',[])+(catalog.get('retired_releases',[]) if retired else [])
    for r in releases:
        sid='release:'+r['lang']+':'+r['release'];date=r.get('date') or r.get('reference_date')
        result[sid]=dict(id=sid,lang=r['lang'],release=r['release'],name=r['name'],kind=r.get('kind') or source_kind(r['name'],r['release']),series=r.get('series') or '',card_total=r.get('card_total'),notes=r.get('notes') or r.get('research_note') or '',links=list(dict.fromkeys([*r.get('source_urls',[]),*[u for u in [r.get('source_url') or r.get('reference_source_url')] if u]])),**date_fields(date),release_period=r.get('release_period'),date_state=r.get('date_state') if r.get('date') or r.get('release_period') else 'provider_reference' if date else 'unresolved',date_source=r.get('source_url') or r.get('reference_source_url'),state='catalog_release')
    entries=catalog['entries']+(catalog.get('retired_entries',[]) if retired else [])
    for e in entries:
        for raw in e.get('sources',[])+[s for p in e['printings'] for s in p.get('sources',[])]:
            if raw['id'] not in result:
                result[raw['id']]=dict(id=raw['id'],lang=e['lang'],release=None,name=raw['name'],kind=raw.get('kind') or source_kind(raw['name']),series=raw.get('series') or '',card_total=raw.get('card_total'),notes=raw.get('notes') or '',links=raw.get('links') or [],**date_fields(raw.get('release_date')),date_state=raw.get('date_state') or 'unresolved',date_source=raw.get('date_source'),state=raw.get('state','catalog_product'))
    for r in releases:
        if r.get('aliases'):result['release:'+r['lang']+':'+r['release']]['aliases']=list(r['aliases'])
    for sid,values in catalog.get('source_metadata',{}).items():
        if sid in result:result[sid].update(copy.deepcopy(values))
    return result

class CatalogEditor:
    def sources(self,state=None,include_removed=False,include_retired=False):
        state=state or self.state();out=base_sources(self.catalog,include_retired)
        for row in state.get('manual_entries',[]):
            e=json.loads(row['payload_json'])
            if not include_retired and not in_scope(e):continue
            sid=e.get('primary_source_id') or 'release:'+e['lang']+':'+e['release']
            if sid not in out:
                out[sid]=dict(id=sid,lang=e['lang'],release=e['release'],name=e['set_name'],kind=source_kind(e['set_name'],e['release']),series='',card_total=None,notes='',links=[],release_date=None,date_precision=None,year=None,date_state='unresolved',date_source=None,state='legacy_manual')
            for product in e.get('sources',[]):
                if product['id'] not in out:out[product['id']]=out[sid]|dict(id=product['id'],name=product['name'])
        for row in state.get('manual_sources',[]):out[row['id']]=json.loads(row['payload_json'])
        for row in state.get('release_overrides',[]):
            sid='release:'+row['release_id']
            if sid in out:out[sid].update(json.loads(row['payload_json']))
        for row in state.get('source_overrides',[]):
            if row['source_id'] in out:out[row['source_id']].update(json.loads(row['payload_json']))
        removed={r['target_id'] for r in state.get('catalog_trash',[]) if r['kind']=='source'}
        if not include_removed:out={k:v for k,v in out.items() if k not in removed}
        for row in state.get('source_image_overrides',[]):
            if row['source_id'] in out:out[row['source_id']]['image']='/user-images/'+row['filename']
        from .release_info import decorate_sources
        decorate_sources(out,self.catalog)
        return annotate_sources(out,self.catalog,removed if not include_removed else frozenset())

    def catalog_entries(self,state=None,include_removed=False,include_retired=False):
        state=state or self.state();out=copy.deepcopy(self.base_entries)
        if include_retired:out.update({e['id']:copy.deepcopy(e) for e in self.catalog.get('retired_entries',[])})
        for row in state['manual_entries']:out[row['id']]=json.loads(row['payload_json'])
        manual_evidence={r['entry_id']:r for r in state['entry_overrides']}
        overrides={r['entry_id']:json.loads(r['payload_json']) for r in state['entry_overrides']}
        sources=self.sources(state,True,include_retired);trash={(r['kind'],r['target_id']) for r in state.get('catalog_trash',[])}
        from .release_info import market_name_index,decorate_market_entry
        market_names=market_name_index(self.catalog)
        for eid,e in out.items():
            if eid in overrides:
                v=overrides[eid]
                if 'year' in v and 'release_date' not in v and v.get('year_basis')=='manual':v.update(release_date=str(v['year']) if v['year'] else None,date_precision='year' if v['year'] else None,date_state='manual_verified')
                e.update(v)
                # Earlier editors recorded explicit identity confirmation as
                # metadata_state only. Preserve that collector decision on upgrade.
                if 'identity_status' not in v and 'metadata_state' in v:e['identity_status']='documented' if v['metadata_state']=='approved' else 'provisional'
                row=manual_evidence[eid];e.setdefault('evidence',[]).append(dict(field='Manual correction',value=v,source_family='collector_manual',disposition='manual_selected_value',summary=row['source_note'],retrieved_on=row['updated_at'],source_urls=[]))
            sid=e.get('primary_source_id') or 'release:'+e['lang']+':'+e['release'];e['primary_source_id']=sid
            source=sources.get(sid)
            if source:
                e['canonical_set_id']=source['canonical_set_id']
                e['set_name']=source['name']
                e['release']=source.get('release') or 'source:'+sid
                use_date=e.get('date_mode')=='source' or (e.get('date_mode') is None and e.get('year_basis') not in ('manual','card','product_source_claim'))
                if use_date:
                    e.update({k:source.get(k) for k in ('release_date','date_precision','year','date_state','date_source')})
            linked=list(dict.fromkeys([sid,*[s['id'] for s in e.get('sources',[])]]))
            e['sources']=[copy.deepcopy(sources[s]) for s in linked if s in sources and (include_removed or ('source',s) not in trash)]
            decorate_market_entry(e,source,market_names)
        for row in state['manual_printings']:
            if row['entry_id'] in out:out[row['entry_id']]['printings'].append(json.loads(row['payload_json']))
        p_overrides={r['printing_id']:json.loads(r['payload_json']) for r in state.get('printing_overrides',[])}
        # Only suppress new derived defaults when exactly one collector record already
        # describes that physical printing. Keep its ID, images, copies and wishlist.
        added=set(self.catalog.get('printing_reconciliation',{}).get('added_printing_ids',[]))|set(self.catalog.get('printing_corrections_186',{}).get('new_printing_ids',[]))|set(self.catalog.get('identity_corrections_189',{}).get('added_printing_ids',[]))|set(self.catalog.get('catalog_corrections_1812',{}).get('added_printing_ids',[]))
        local_ids={r['id'] for r in state['manual_printings']}|set(p_overrides)
        for e in out.values():
            aliases={};suppress=set()
            for p in e['printings']:
                if p['id'] not in added or p['id'] in local_ids:continue
                matches=[q for q in e['printings'] if q['id'] in local_ids and physical_key(e['id'],q|p_overrides.get(q['id'],{}))==physical_key(e['id'],p)]
                if len(matches)==1:
                    winner=matches[0];aliases[p['id']]=winner['id'];suppress.add(p['id'])
                    winner['reviewed_equivalent']=copy.deepcopy(p.get('verification',{}).get('existence',{}))
                    linked={s['id'] for s in winner.get('sources',[])}
                    winner.setdefault('sources',[]).extend(copy.deepcopy(s) for s in p.get('sources',[]) if s['id'] not in linked)
                    if p.get('market_candidate'):winner.setdefault('market_candidate',copy.deepcopy(p['market_candidate']))
            e['printing_aliases']=aliases;e['printings']=[p for p in e['printings'] if p['id'] not in suppress]
        shared={r['entry_id']:'/user-images/'+r['filename'] for r in state['image_overrides']};pictures={r['printing_id']:'/user-images/'+r['filename'] for r in state.get('printing_image_overrides',[])}
        visible={}
        for eid,e in out.items():
            apply_form_review(e)
            if not include_retired and not in_scope(e):continue
            if in_scope(e):trim_species(e)
            if not include_removed and (('entry',eid) in trash or ('source',e['primary_source_id']) in trash):continue
            if eid in shared:e['image']=shared[eid]
            ps=[];claims=[]
            for p in e['printings']:
                manual=p_overrides.get(p['id'],{})
                if manual.get('_image_review_only'):manual={k:v for k,v in manual.items() if k=='image_review'}
                p.update(manual)
                if e.get('scope_review',{}).get('decision')=='excluded_form':p['collection_status']='excluded'
                if p.get('market_confirmed'):
                    from .marketplace import identity_key
                    if p.get('market_identity')!=identity_key(e) or (p.get('market_physical_key') and p['market_physical_key']!=list(physical_key(eid,p))):p['market_confirmed']=False
                # A saved legacy printing override passed the same explicit
                # confirmation gate, before collection_status was introduced.
                if manual and 'collection_status' not in manual and manual.get('finish') in ('non_holo','holo','reverse_holo'):p['collection_status']='documented'
                if not include_removed and ('printing',p['id']) in trash:continue
                held=e['metadata_state']!='approved' or e.get('identity_status') in ('provisional','disputed','excluded','announced') or p.get('collection_status') in ('provisional','disputed','excluded')
                if p.get('sources'):
                    p['sources']=[copy.deepcopy(sources[s['id']]) for s in p['sources'] if s['id'] in sources and (include_removed or ('source',s['id']) not in trash)]
                    if not p['sources'] and not include_removed:continue
                if eid in shared:p.update(image=shared[eid],image_scope='entry')
                if p['id'] in pictures:p.update(image=pictures[p['id']],image_scope='printing',image_state='manual')
                p['physical_key']=list(physical_key(eid,p));p['label']=printing_label(p);p['verification']=verification(p);p['image_review']=image_review(e,p)
                p['category']='jumbo' if p['size']=='oversized' or p['material']=='metal' else 'cameo' if e['category']=='cameo' else 'standard'
                if held and not include_removed:claims.append(p)
                else:ps.append(p)
            e['printings']=ps;e['printing_claims']=claims;normalize_rarity(e)
            for p in ps:
                model=dict(e)
                if p.get('printed_rarity_state') not in (None,'inherit'):
                    model.update(rarity_state=p['printed_rarity_state'],rarity_code=p.get('printed_rarity_code'))
                normalize_rarity(model)
                for key in ('rarity_key','rarity_label','rarity_order'):p[key]=model[key]
            annotate_entry(e,sources)
            visible[eid]=e
        return visible

    def editor_view(self):
        state=self.state();entries=self.catalog_entries(state);sources=self.sources(state)
        counts={}
        for e in entries.values():
            for sid in {e['primary_source_id'],*[s['id'] for s in e['sources']],*[s['id'] for p in e['printings'] for s in p.get('sources',[])]}:counts[sid]=counts.get(sid,0)+1
        return dict(printing_taxonomy=taxonomy(),entries=list(entries.values()),sources=[s|dict(card_count=counts.get(s['id'],0)) for s in sources.values()],trash=state.get('catalog_trash',[]),archived_scope_entries=self.catalog.get('scope',{}).get('retired_entries',0))

    def _source_values(self,data,existing=None):
        lang=data.get('lang',existing.get('lang') if existing else None)
        if lang not in LANGS:fail('Choose the source language.')
        name=clean(data.get('name',''),200)
        if not name:fail('Enter the set or source name.')
        kind=data.get('kind','set')
        if kind not in SOURCE_KINDS:fail('Choose a source type.')
        release=clean(data.get('release') or '',200) or None
        total=data.get('card_total')
        if total in ('',None):total=None
        elif type(total) is not int or not 1<=total<=10000:fail('Card total must be a positive whole number.')
        date=date_fields(data.get('release_date') or '')
        same=existing and existing.get('release_date')==date['release_date']
        values=dict(lang=lang,release=release,name=name,kind=kind,series=clean(data.get('series',''),200),card_total=total,notes=clean(data.get('notes',''),6000),links=urls(data.get('links',[])),**date,date_state=existing.get('date_state') if same else 'manual_verified' if date['release_date'] else 'unresolved',date_source=existing.get('date_source') if same else source_note(data))
        order=data.get('sort_order',(existing or {}).get('sort_order'))
        if order in ('',None):order=None
        elif type(order) is not int or not 0<=order<=100000:fail('Source order must be a whole number from 0 to 100000, or empty.')
        values['sort_order']=order
        canonical=clean(data.get('canonical_set_id',(existing or {}).get('canonical_set_id','')) or '',200)
        if canonical and not re.fullmatch(r'[A-Za-z0-9_:./-]{1,200}',canonical):fail('Use a simple canonical set key.')
        values['canonical_set_id']=canonical or None
        values.update(validate_source_structure(data,existing,self.sources(include_removed=True)))
        return values

    def save_source(self,data):
        state=self.state();all_sources=self.sources(state,True);sid=data.get('source_id');old=all_sources.get(sid) if sid else None
        if sid and not old:fail('That set/source was not found.')
        values=self._source_values(data,old);note=source_note(data)
        if old and values['lang']!=old['lang'] and any(sid in {e.get('primary_source_id'),'release:'+e['lang']+':'+e['release'],*[s['id'] for s in e.get('sources',[])],*[s['id'] for p in e['printings'] for s in p.get('sources',[])]} for e in self.catalog_entries(state,True).values()):fail('A source with cards must keep its language. Move individual cards to a source in the other language instead.')
        if not old and any(s['lang']==values['lang'] and ((values['release'] and s.get('release')==values['release']) or s['name'].casefold()==values['name'].casefold()) for s in all_sources.values()):fail('This set/source already exists. Edit or restore it instead.')
        when=timestamp()
        with self.lock,self.connect() as c:
            if old:c.execute('INSERT OR REPLACE INTO source_overrides VALUES(?,?,?,?)',(sid,dump(values),note,when))
            else:
                sid=uid('manual_source');values['id']=sid
                if not values['release']:values['release']='manual:'+sid
                values['state']='manual';c.execute('INSERT INTO manual_sources VALUES(?,?,?,?)',(sid,dump(values),note,when))
            self.audit(c,'source_saved',sid,old,values)
        return dict(source_id=sid)

    def _card_values(self,data,existing,sources):
        lang=data.get('lang');allowed={r['dex'] for r in self.catalog['roster']}
        if lang not in LANGS:fail('Choose the card language.')
        subject=data.get('subject_dex',[]);cameo=data.get('cameo_dex',[])
        if any(not isinstance(v,list) or any(type(n) is not int or n not in allowed for n in v) for v in (subject,cameo)):fail('Choose Pokémon from the current collecting roster.')
        if not subject and not cameo:fail('Choose a Pokémon, or at least one cameo Pokémon.')
        subject=sorted(set(subject));cameo=sorted(set(cameo));name=clean(data.get('name',''),150)
        if not name:fail('Enter the printed card name.')
        num=clean(data.get('number') or 'Unnumbered',100);sid=data.get('source_id');source=sources.get(sid)
        if not source or source['lang']!=lang:fail('Choose a set/source in this card’s language.')
        category=data.get('category','standard')
        if category not in ('standard','jumbo','cameo'):fail('Choose the card category.')
        if not subject:category='cameo'
        code=clean(data.get('rarity_code') or '',100);rstate=data.get('rarity_state') or ('not_printed' if code=='not_printed' else 'unresolved' if not code or code=='unresolved' else 'known')
        if rstate not in ('known','not_printed','unresolved'):fail('Choose a rarity status.')
        if rstate=='known' and code in ('','unresolved','not_printed'):fail('Choose or enter the known rarity.')
        if rstate!='known':code=None
        art=data.get('art_style') or None
        if art not in (None,'standard','full_art'):fail('Choose an artwork style.')
        extra=data.get('extra_source_ids',[])
        if not isinstance(extra,list) or any(k not in sources or sources[k]['lang']!=lang for k in extra):fail('Additional sources must use the same language.')
        linked=list(dict.fromkeys([sid,*extra]));mode=data.get('date_mode','source')
        if mode not in ('source','card'):fail('Choose source date or individual card date.')
        date=date_fields(data.get('release_date') or '') if mode=='card' else {k:source.get(k) for k in ('release_date','date_precision','year')}
        same=existing and mode==('card' if existing.get('year_basis') in ('card','manual','product_source_claim') else existing.get('date_mode','source')) and date['release_date']==existing.get('release_date')
        meta=dict(date_mode=mode,year_basis='manual' if mode=='card' else 'set',date_state=existing.get('date_state') if same else ('manual_verified' if date['release_date'] else 'unresolved') if mode=='card' else source.get('date_state'),date_source=existing.get('date_source') if same else source_note(data) if mode=='card' else source.get('date_source'))
        if code=='S_legacy_lvx':code='S';data=data|dict(rarity_namespace='ja_legacy_lvx' if lang=='ja' else 'ko_legacy_lvx')
        namespace=clean(data.get('rarity_namespace') or (existing or {}).get('rarity_namespace') or ('manual:'+lang),200)
        art_same=existing and existing.get('art_style')==art
        status=data.get('identity_status') or ('documented' if data.get('identity_verified') is True else 'provisional')
        if status not in ('documented','provisional','disputed','excluded','announced'):fail('Choose an evidence status.')
        guard_primary_source(source,status=='documented',existing)
        return dict(identity_status=status,lang=lang,name=name,english=clean(data.get('english') or name,150),dex=(subject or cameo)[0],subject_dex=subject,cameo_dex=cameo,number=num,number_key=clean(data.get('number_key') or num,100),identifier_namespace=clean(data.get('identifier_namespace') or ('unnumbered' if num.lower()=='unnumbered' else 'collector'),100),primary_source_id=sid,release=source.get('release') or 'source:'+sid,set_name=source['name'],sources=[copy.deepcopy(sources[s]) for s in linked],**date,**meta,rarity_code=code,rarity_state=rstate,rarity_namespace=namespace,rarity_label=rarity_label(code if code else 'not_printed' if rstate=='not_printed' else 'unresolved',lang,namespace),rarity_family='common' if code in ('common','C') else 'uncommon' if code in ('uncommon','U') else 'other' if code is None or code in ('promo','P') else 'rare',category=category,metadata_state='approved' if status=='documented' else 'review',art_style=art,art_style_state=(existing.get('art_style_state') if art_same else 'manual_verified' if art else 'unresolved'),art_style_source=(existing.get('art_style_source') if art_same else source_note(data) if art else None),links=urls(data.get('links',[])),notes=clean(data.get('notes',''),6000),cardmarket_url=market_url(data.get('cardmarket_url')),cardmarket_search=clean(data.get('cardmarket_search') or '',200),market_link_override=bool(data.get('market_link_override')) or bool(data.get('cardmarket_url') or data.get('cardmarket_search')))

    def save_card(self,data):
        state=self.state();eid=data.get('entry_id');entries=self.catalog_entries(state,True);old=entries.get(eid) if eid else None
        if eid and not old:fail('That card was not found in the current catalog.')
        sources=self.sources(state);new_source=None
        if not data.get('source_id') and data.get('new_source'):
            new_source=self._source_values(data['new_source']);sid=uid('manual_source');new_source.update(id=sid,release=new_source['release'] or 'manual:'+sid,state='manual')
            if any(s['lang']==new_source['lang'] and (s['name'].casefold()==new_source['name'].casefold() or new_source.get('release') and s.get('release')==new_source['release']) for s in self.sources(state,True).values()):fail('That source already exists. Select it from the list.')
            sources[sid]=new_source;data=data|dict(source_id=sid)
        values=self._card_values(data,old,sources);eid=eid or uid('manual_entry')
        for other in entries.values():
            if other['id']!=eid and other['lang']==values['lang'] and other.get('primary_source_id')==values['primary_source_id'] and other['number_key'].casefold()==values['number_key'].casefold() and (values['identifier_namespace']!='unnumbered' or other['name'].casefold()==values['name'].casefold()):fail('This identifier already belongs to a card in that source. Edit it or add another printing there.')
        e=(old or dict(id=eid,image=None,printings=[]))|values
        initial=data.get('initial_printing');p=None
        if initial and initial.get('finish'):p=self._printing_values(e,initial,None)
        when=timestamp();note=source_note(data)
        with self.lock,self.connect() as c:
            if new_source:c.execute('INSERT INTO manual_sources VALUES(?,?,?,?)',(new_source['id'],dump(new_source),note,when))
            if old:
                row=c.execute('SELECT payload_json FROM entry_overrides WHERE entry_id=?',(eid,)).fetchone();merged=(json.loads(row[0]) if row else {})|values
                c.execute('INSERT OR REPLACE INTO entry_overrides VALUES(?,?,?,?)',(eid,dump(merged),note,when))
            else:c.execute('INSERT INTO manual_entries VALUES(?,?,?,?)',(eid,dump(e),note,when))
            if p:c.execute('INSERT INTO manual_printings VALUES(?,?,?,?,?)',(p['id'],eid,dump(p),note,when))
            self.audit(c,'card_saved',eid,old,e)
        return dict(entry_id=eid,printing_id=p['id'] if p else None)

    def _printing_values(self,e,data,old):
        from .collector import first_edition_allowed
        previous=old or {};check=copy.deepcopy(data.get('verification') or previous.get('verification') or {})
        existence=check.setdefault('existence',{});specimen=check.setdefault('specimen',{})
        inspected=specimen.get('status')=='inspected'
        if data.get('confirmed') is True:existence['status']=existence.get('status') if existence.get('status') in ('documented','collector_verified','previously_accepted') else 'collector_verified'
        if inspected and existence.get('status') not in ('documented','collector_verified','previously_accepted'):existence['status']='collector_verified'
        if existence.get('status') not in ('documented','collector_verified','previously_accepted'):fail('Document the printing’s existence, separately from specimen inspection.')
        existence['source_urls']=urls(existence.get('source_urls',[]));specimen.setdefault('status','not_inspected')
        if specimen['status'] not in ('inspected','not_inspected'):fail('Choose whether you inspected a specimen.')
        if e['metadata_state']!='approved' or e.get('identity_status') in ('provisional','disputed','excluded','announced'):fail('Document the card identity before confirming a printing. Rarity can remain unknown.')
        raw=previous|data
        for k in ('finish','pattern','edition','layout','size','material','print_state'):
            if k in raw:clean(raw[k] or '',150)
        n=normalized(raw)
        if data.get('pattern_custom') and n['pattern'] not in PATTERNS and not n['pattern'].startswith('custom_'):n['pattern']='custom_'+n['pattern']
        if n['finish'] not in ('non_holo','holo','reverse_holo') or n['edition'] not in ('first_edition','unlimited','unstamped','not_applicable') or n['size'] not in ('standard','oversized') or n['material'] not in ('paper','metal'):fail('Check finish, edition, size and material.')
        if n['pattern'] not in PATTERNS and not n['pattern'].startswith('custom_') and (not old or n['pattern']!=normalized(old)['pattern']):fail('Choose a known foil pattern or record an explicit custom pattern.')
        if n['finish']=='non_holo' and n['pattern']!='none':fail('A non-holo printing cannot have a foil pattern.')
        if n['layout'] not in LAYOUTS and not n['layout'].startswith('custom_') and (not old or n['layout']!=normalized(old)['layout']):fail('Choose a supported layout or an explicit custom layout.')
        if n['edition']=='first_edition' and not first_edition_allowed(e,e['printings']):fail('This release has no supported first-edition issue.')
        if n['edition']=='unlimited' and not first_edition_allowed(e,e['printings']) and not any(p['edition']=='unlimited' for p in e['printings']):fail('This release has no supported first-edition/unlimited distinction.')
        if n['layout'] in ('shadowed','shadowless') and not (e['lang']=='en' and e['release']=='base1') and not any(p['layout']==n['layout'] for p in e['printings']):fail('This layout is not supported for this release.')
        if e['lang']=='en' and e['release']=='base1' and n['edition']=='first_edition' and n['layout']!='shadowless':fail('English Base Set first-edition cards use the shadowless layout.')
        stamps=data.get('stamps',json.loads(previous.get('stamps_json','[]')))
        if isinstance(stamps,str):stamps=[v.strip() for v in stamps.split(',') if v.strip()]
        if not isinstance(stamps,list) or len(stamps)>20 or any(not isinstance(v,str) or not 0<len(v)<=100 for v in stamps):fail('Enter stamp names separated by commas.')
        state=data.get('printed_rarity_state',previous.get('printed_rarity_state','inherit'));code=clean(data.get('printed_rarity_code',previous.get('printed_rarity_code')) or '',100) or None
        if state not in ('inherit','known','not_printed','unresolved') or state=='known' and not code:fail('Check the printing-specific rarity.')
        p=dict(previous);p.update(n);p.update(id=previous.get('id') or uid('manual_printing'),entry_id=e['id'],collection_status='documented',verification=check,stamps_json=dump(sorted(set(stamps))),printed_rarity_state=state,printed_rarity_code=code if state=='known' else None,notes=clean(data.get('notes',previous.get('notes','')),4000),cardmarket_url=market_url(data.get('cardmarket_url',previous.get('cardmarket_url'))),**date_fields(data.get('release_date',previous.get('release_date')) or ''))
        originals={k:data[k] for k in ('pattern','finish','edition','layout') if k in data and data[k]!=p[k]}
        if originals:p['original_terminology']=previous.get('original_terminology',{})|originals
        changed=bool(old and physical_key(e['id'],old)!=physical_key(e['id'],p))
        if changed:
            if data.get('cardmarket_url') in (None,old.get('cardmarket_url')):p['cardmarket_url']=None
            p.update(price_product_id=None,price_series=None,market_confirmed=False)
            if p.get('image_review',{}).get('status')=='verified':p['image_review']=p['image_review']|dict(status='unverified',reason='Physical printing changed since the image was checked.')
        from .marketplace import validate_price_mapping,identity_key
        if 'price_product_id' in data or 'market_confirmed' in data:
            mapping=validate_price_mapping(data,None if changed else old)
            if mapping.get('market_confirmed'):
                if mapping['price_series']=='reverse' and p['finish']!='reverse_holo':fail('The reverse-holo guide series must refer to a reverse-holo printing.')
                p.update(mapping,market_identity=identity_key(e),market_physical_key=list(physical_key(e['id'],p)))
            elif not changed:p.update(mapping)
        p['label']=printing_label(p);p['category']='jumbo' if p['size']=='oversized' or p['material']=='metal' else 'cameo' if e['category']=='cameo' else 'standard';p.setdefault('image',e.get('image'));p.setdefault('image_scope','entry')
        sources=self.sources();ids=data.get('source_ids',[s['id'] for s in previous.get('sources',[])])
        if not isinstance(ids,list) or any(s not in sources or sources[s]['lang']!=e['lang'] for s in ids):fail('Choose printing sources in the same language.')
        if ids:p['sources']=[copy.deepcopy(sources[s]) for s in dict.fromkeys(ids)]
        else:p.pop('sources',None)
        if p['release_date']:p.update(date_state='manual_verified',date_source=source_note(data))
        for other in e['printings']+e.get('printing_claims',[]):
            if other['id']!=p['id'] and physical_key(e['id'],other)==physical_key(e['id'],p):fail('That physical printing already exists. Edit it instead.')
        return p

    def save_printing(self,data):
        eid=data.get('entry_id');e=self.catalog_entries(include_removed=True).get(eid)
        if not e:fail('Card not found.')
        pid=data.get('printing_id');old=next((p for p in e['printings'] if p['id']==pid),None) if pid else None
        if pid and not old:fail('Printing does not belong to this card.')
        p=self._printing_values(e,data,old);note=source_note(data);when=timestamp()
        with self.lock,self.connect() as c:
            if old:c.execute('INSERT OR REPLACE INTO printing_overrides VALUES(?,?,?,?)',(pid,dump(p),note,when))
            else:c.execute('INSERT INTO manual_printings VALUES(?,?,?,?,?)',(p['id'],eid,dump(p),note,when))
            self.audit(c,'printing_saved',p['id'],old,p)
        return dict(entry_id=eid,printing_id=p['id'])

    def trash_item(self,data,restore=False):
        kind=data.get('kind');target=data.get('target_id');state=self.state();all_entries=self.catalog_entries(state,True);all_sources=self.sources(state,True)
        if kind=='entry':obj=all_entries.get(target);name=obj['english']+' '+obj['number'] if obj else None
        elif kind=='source':obj=all_sources.get(target);name=obj['name'] if obj else None
        elif kind=='printing':
            found=next(((e,p) for e in all_entries.values() for p in e['printings'] if p['id']==target),None);obj=found[1] if found else None;name=found[0]['english']+' · '+obj['label'] if found else None
        else:fail('Choose a card, printing or source.')
        if not obj:fail('This item is not in the current catalog.')
        key=kind+':'+target
        with self.lock,self.connect() as c:
            if restore:c.execute('DELETE FROM catalog_trash WHERE id=?',(key,))
            else:c.execute('INSERT OR REPLACE INTO catalog_trash VALUES(?,?,?,?,?)',(key,kind,target,name,timestamp()))
            self.audit(c,'catalog_restored' if restore else 'catalog_removed',target,None,dict(kind=kind,name=name))
        return dict(kind=kind,target_id=target)
