"""Local collection records and explicit, audited catalog corrections."""
from __future__ import annotations
import base64,copy,datetime as dt,hashlib,io,json,re,sqlite3,threading,uuid,zipfile
from decimal import Decimal,InvalidOperation
from pathlib import Path
from contextlib import contextmanager
from .editor import CatalogEditor,EDITOR_SCHEMA,NEW_TABLES
from .printing_model import physical_key,printing_label

CONDITIONS=['unassessed','mint','near_mint','excellent','good','light_played','played','poor']
CURRENCIES={'EUR':2,'USD':2,'GBP':2,'JPY':0,'KRW':0}
LEGACY_TABLES=['copies','wishlist','entry_overrides','manual_entries','manual_printings','image_overrides','orphaned_records','audit_log']
V2_TABLES=LEGACY_TABLES+['printing_image_overrides','release_overrides']
V3_TABLES=V2_TABLES+NEW_TABLES
TABLES=V3_TABLES+['source_image_overrides']
SCHEMA='''
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS copies(id TEXT PRIMARY KEY,printing_id TEXT NOT NULL,condition TEXT NOT NULL,price_minor INTEGER,currency TEXT,purchased_on TEXT,notes TEXT NOT NULL,misprint_notes TEXT NOT NULL,created_at TEXT NOT NULL,updated_at TEXT NOT NULL,deleted_at TEXT);
CREATE TABLE IF NOT EXISTS wishlist(printing_id TEXT PRIMARY KEY,created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS entry_overrides(entry_id TEXT PRIMARY KEY,payload_json TEXT NOT NULL,source_note TEXT NOT NULL,updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS manual_entries(id TEXT PRIMARY KEY,payload_json TEXT NOT NULL,source_note TEXT NOT NULL,created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS manual_printings(id TEXT PRIMARY KEY,entry_id TEXT NOT NULL,payload_json TEXT NOT NULL,source_note TEXT NOT NULL,created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS image_overrides(entry_id TEXT PRIMARY KEY,filename TEXT NOT NULL,source_note TEXT NOT NULL,updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS printing_image_overrides(printing_id TEXT PRIMARY KEY,filename TEXT NOT NULL,source_note TEXT NOT NULL,updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS release_overrides(release_id TEXT PRIMARY KEY,payload_json TEXT NOT NULL,source_note TEXT NOT NULL,updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS source_image_overrides(source_id TEXT PRIMARY KEY,filename TEXT NOT NULL,source_note TEXT NOT NULL,updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS orphaned_records(id TEXT PRIMARY KEY,payload_json TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS audit_log(id TEXT PRIMARY KEY,action TEXT NOT NULL,target TEXT NOT NULL,before_json TEXT,after_json TEXT,created_at TEXT NOT NULL);
'''
class ValidationError(ValueError):pass
def now():return dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
def ident(prefix):return prefix+'_'+uuid.uuid4().hex
def js(value):return json.dumps(value,ensure_ascii=False,separators=(',',':'),sort_keys=True)
def text(value,limit=2000):
    if not isinstance(value,str) or len(value)>limit:raise ValidationError('Text is missing or too long.')
    return value.strip()
def note(data):
    value=text(data.get('source_note',''),4000)
    if len(value)<8:raise ValidationError('Add a source link or a short explanation of your research.')
    return value
def catalog_date(value):
    value=text(value,10)
    if not value:return dict(release_date=None,date_precision=None,year=None)
    try:
        if re.fullmatch(r'\d{4}',value):dt.date(int(value),1,1);precision='year'
        elif re.fullmatch(r'\d{4}-\d{2}',value):dt.date.fromisoformat(value+'-01');precision='month'
        elif re.fullmatch(r'\d{4}-\d{2}-\d{2}',value):dt.date.fromisoformat(value);precision='day'
        else:raise ValueError()
        if not 1996<=int(value[:4])<=2100:raise ValueError()
    except ValueError:raise ValidationError('Use YYYY-MM-DD, YYYY-MM or YYYY for the release date.')
    return dict(release_date=value,date_precision=precision,year=int(value[:4]))
def money(value,currency):
    if value in ('',None):return None,None
    if currency not in CURRENCIES:raise ValidationError('Choose a supported currency.')
    try:d=Decimal(str(value).replace(',','.'))
    except InvalidOperation:raise ValidationError('Enter a valid purchase price.')
    factor=Decimal(10)**CURRENCIES[currency]
    if not d.is_finite() or d<0 or d>100000000 or d*factor!=(d*factor).to_integral_value():raise ValidationError('Check the price and decimal places.')
    return int(d*factor),currency
def image_type(raw):
    if raw.startswith(b'\x89PNG\r\n\x1a\n'):return 'png'
    if raw.startswith(b'\xff\xd8\xff'):return 'jpg'
    if raw.startswith((b'GIF87a',b'GIF89a')):return 'gif'
    if raw[:4]==b'RIFF' and raw[8:12]==b'WEBP':return 'webp'
    raise ValidationError('Choose a JPG, PNG, WebP or GIF catalog picture.')
def first_edition_allowed(entry,existing):
    if any(p['edition']=='first_edition' for p in existing):return True
    if entry['lang'] in ('en','de'):return entry['release'] in {'base1','base2','base3','base5','gym1','gym2','neo1','neo2','neo3','neo4'}
    if entry['lang']=='ja':return bool(re.fullmatch(r'(?:VS|web|e\d+|ADV\d+|PCG\d+|DP\d+|DPt\d+|L\d+|BW\d+|XY\d+)(?:[-:].*)?',entry['release']))
    return False

class Collection(CatalogEditor):
    def __init__(self,root,user_dir=None):
        self.root=Path(root);self.user_dir=Path(user_dir or self.root/'my_collection');self.user_dir.mkdir(parents=True,exist_ok=True)
        (self.user_dir/'catalog_images').mkdir(exist_ok=True);(self.user_dir/'backups').mkdir(exist_ok=True)
        self.catalog=json.loads((self.root/'data/catalog.json').read_text(encoding='utf-8'));self.base_entries={e['id']:e for e in self.catalog['entries']};self.lock=threading.RLock();self.db_path=self.user_dir/'collection.sqlite3'
        if self.db_path.is_file():
            with sqlite3.connect(self.db_path) as db:
                tables={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                marker=db.execute("SELECT value FROM meta WHERE key='printing_model_version'").fetchone() if 'meta' in tables else None
                structure_marker=db.execute("SELECT value FROM meta WHERE key='source_structure_version'").fetchone() if 'meta' in tables else None
                correction_marker=db.execute("SELECT value FROM meta WHERE key='printing_corrections_version'").fetchone() if 'meta' in tables else None
            structure_upgrade=not structure_marker or structure_marker[0]!='1.8.5'
            if not marker or marker[0]!='1.8.4' or structure_upgrade or not correction_marker or correction_marker[0]!='1.8.6':
                stamp=dt.datetime.now().strftime('%Y%m%d-%H%M%S-%f');backup_prefix='before-sources-1.8.5-' if structure_upgrade and marker and marker[0]=='1.8.4' else 'before-printing-1.8.4-' if not marker or marker[0]!='1.8.4' else 'before-printing-corrections-1.8.6-'
                if set(TABLES)<=tables:
                    (self.user_dir/'backups'/(backup_prefix+stamp+'.zip')).write_bytes(self.backup())
                else:
                    with sqlite3.connect(self.db_path) as src,sqlite3.connect(self.user_dir/'backups'/(backup_prefix+stamp+'.sqlite3')) as dst:src.backup(dst)
        with self.connect() as c:
            c.executescript(SCHEMA+EDITOR_SCHEMA)
            c.execute("INSERT OR REPLACE INTO meta VALUES('printing_model_version','1.8.4')")
            c.execute("INSERT OR REPLACE INTO meta VALUES('source_structure_version','1.8.5')")
            c.execute("INSERT OR REPLACE INTO meta VALUES('printing_corrections_version','1.8.6')")
        self.seed_legacy()
    @contextmanager
    def connect(self):
        c=sqlite3.connect(self.db_path,timeout=20);c.row_factory=sqlite3.Row
        try:
            c.execute('PRAGMA journal_mode=WAL')
            with c:yield c
        finally:c.close()
    def audit(self,c,action,target,before,after):
        c.execute('INSERT INTO audit_log VALUES(?,?,?,?,?,?)',(ident('audit'),action,target,js(before) if before is not None else None,js(after) if after is not None else None,now()))
    def state(self,include_deleted=False):
        with self.lock,self.connect() as c:
            result={}
            for table in TABLES:
                query='SELECT * FROM '+table
                if table=='copies' and not include_deleted:query+=' WHERE deleted_at IS NULL'
                if table=='audit_log' and not include_deleted:query+=' ORDER BY created_at DESC LIMIT 100'
                result[table]=[dict(r) for r in c.execute(query)]
            return result
    def entries(self,state=None):
        return self.catalog_entries(state)
    def printing_map(self,state=None,include_removed=False,include_retired=False):
        entries=self.catalog_entries(state,include_removed,include_retired);result={p['id']:(e,p) for e in entries.values() for p in e['printings']}
        for e in entries.values():
            for alias,winner in e.get('printing_aliases',{}).items():
                if winner in result:result[alias]=result[winner]
        return result
    def entry(self,eid):
        e=self.entries().get(eid)
        if not e:raise ValidationError('That card is not in this catalog.')
        return e
    def seed_legacy(self):
        with self.lock,self.connect() as c:
            if c.execute("SELECT 1 FROM meta WHERE key='legacy_imported'").fetchone():return
            p=self.root/'data/catalog.sqlite3'
            if p.is_file():
                old=sqlite3.connect(p.resolve().as_uri()+'?mode=ro',uri=True);old.row_factory=sqlite3.Row;known=self.printing_map(include_removed=True,include_retired=True)
                for row in old.execute('SELECT * FROM copies'):
                    r=dict(row)
                    if r['variant_id'] not in known:c.execute('INSERT OR IGNORE INTO orphaned_records VALUES(?,?)',(r['id'],js(dict(kind='legacy_copy',record=r))));continue
                    when=now();c.execute('INSERT OR IGNORE INTO copies VALUES(?,?,?,?,?,?,?,?,?,?,?)',(r['id'],r['variant_id'],r['condition'],r['price_minor'],r['currency'],r['acquired_on'],r['notes'],r['misprint_notes'],when,when,None))
                for row in old.execute('SELECT * FROM unidentified_intake'):c.execute('INSERT OR IGNORE INTO orphaned_records VALUES(?,?)',(row['id'],js(dict(kind='legacy_intake',record=dict(row)))))
                old.close()
            c.execute('INSERT INTO meta VALUES(?,?)',('legacy_imported',self.catalog['catalog_sha256']))
    def copy_fields(self,data):
        condition=data.get('condition','unassessed')
        if condition not in CONDITIONS:raise ValidationError('Choose a card condition.')
        price,currency=money(data.get('price'),data.get('currency','EUR'));date=data.get('purchased_on') or None
        if date:
            try:dt.date.fromisoformat(date)
            except (ValueError,TypeError):raise ValidationError('Use a valid purchase date.')
        return dict(condition=condition,price_minor=price,currency=currency,purchased_on=date,notes=text(data.get('notes',''),4000),misprint_notes=text(data.get('misprint_notes',''),2000))
    def add_copies(self,data):
        pid=data.get('printing_id');known=self.printing_map()
        if pid not in known:raise ValidationError('Choose an accepted printing for this card.')
        pid=known[pid][1]['id']
        quantity=data.get('quantity',1)
        if isinstance(quantity,bool) or not isinstance(quantity,int) or not 1<=quantity<=100:raise ValidationError('Quantity must be between 1 and 100.')
        fields=self.copy_fields(data);ids=[]
        with self.lock,self.connect() as c:
            for _ in range(quantity):
                cid=ident('copy');when=now();r=dict(id=cid,printing_id=pid,**fields,created_at=when,updated_at=when,deleted_at=None);c.execute('INSERT INTO copies VALUES(?,?,?,?,?,?,?,?,?,?,?)',tuple(r.values()));self.audit(c,'copy_added',cid,None,r);ids.append(cid)
            if data.get('remove_from_wishlist') is True:
                c.execute('DELETE FROM wishlist WHERE printing_id=?',(pid,));self.audit(c,'wishlist_changed',pid,None,dict(wanted=False))
        return dict(ids=ids)
    def edit_copy(self,data):
        cid=data.get('id');fields=self.copy_fields(data)
        with self.lock,self.connect() as c:
            row=c.execute('SELECT * FROM copies WHERE id=? AND deleted_at IS NULL',(cid,)).fetchone()
            if not row:raise ValidationError('Copy not found.')
            before=dict(row);after=before|fields|dict(updated_at=now());c.execute('UPDATE copies SET condition=?,price_minor=?,currency=?,purchased_on=?,notes=?,misprint_notes=?,updated_at=? WHERE id=?',tuple(after[k] for k in ['condition','price_minor','currency','purchased_on','notes','misprint_notes','updated_at'])+(cid,));self.audit(c,'copy_edited',cid,before,after)
        return dict(id=cid)
    def remove_copy(self,data,undo=False):
        with self.lock,self.connect() as c:
            row=c.execute('SELECT * FROM copies WHERE id=?',(data.get('id'),)).fetchone()
            if not row:raise ValidationError('Copy not found.')
            before=dict(row);after=before|dict(deleted_at=None if undo else now(),updated_at=now());c.execute('UPDATE copies SET deleted_at=?,updated_at=? WHERE id=?',(after['deleted_at'],after['updated_at'],before['id']));self.audit(c,'copy_restored' if undo else 'copy_removed',before['id'],before,after)
        return dict(id=before['id'])
    def wish(self,data):
        pid=data.get('printing_id')
        known=self.printing_map(include_removed=not data.get('wanted'),include_retired=not data.get('wanted'))
        if pid not in known:raise ValidationError('Printing not found.')
        pid=known[pid][1]['id']
        if not isinstance(data.get('wanted'),bool):raise ValidationError('Wishlist choice is missing.')
        with self.lock,self.connect() as c:
            if data['wanted']:c.execute('INSERT OR IGNORE INTO wishlist VALUES(?,?)',(pid,now()))
            else:
                for key,(_,p) in known.items():
                    if p['id']==pid:c.execute('DELETE FROM wishlist WHERE printing_id=?',(key,))
            self.audit(c,'wishlist_changed',pid,None,dict(wanted=data['wanted']))
        return dict(printing_id=pid)
    def override(self,data):
        e=self.entry(data.get('entry_id'));source_note=note(data);values=data.get('values')
        if not isinstance(values,dict):raise ValidationError('Correction values are missing.')
        allowed={'english','release_date','art_style','cardmarket_url','cardmarket_search','cameo_dex','name','number','year','rarity_code','rarity_state','rarity_label','rarity_family','category','identity_verified'}
        if set(values)-allowed:raise ValidationError('Unsupported correction field.')
        p={}
        for key,value in values.items():
            if key=='release_date':p.update(catalog_date(value));p.update(year_basis='manual',date_state='manual_verified',date_source=source_note)
            elif key=='art_style':
                if value not in ('full_art','standard','unresolved'):raise ValidationError('Choose an artwork style.')
                p.update(art_style=None if value=='unresolved' else value,art_style_state='unresolved' if value=='unresolved' else 'manual_verified',art_style_source=source_note)
            elif key=='cardmarket_url':
                value=text(value,2000) or None
                if value and not re.match(r'https://(?:www\.)?cardmarket\.com/',value):raise ValidationError('Use a full Cardmarket HTTPS listing link.')
                p[key]=value
                if value!=(e.get(key) or None):p['market_link_override']=True
            elif key=='cardmarket_search':
                p[key]=text(value,200)
                if p[key]!=(e.get(key) or ''):p['market_link_override']=True
            elif key=='cameo_dex':
                roster={r['dex'] for r in self.catalog['roster']}
                if not isinstance(value,list) or any(type(d) is not int or d not in roster for d in value):raise ValidationError('Choose cameo Pokémon from this catalog.')
                p[key]=sorted(set(value))
            elif key=='year':
                if value is not None and (isinstance(value,bool) or not isinstance(value,int) or not 1996<=value<=2100):raise ValidationError('Check the release year.')
                p[key]=value
                p['year_basis']='manual'
                if 'release_date' not in values:p.update(release_date=str(value) if value else None,date_precision='year' if value else None,date_state='manual_verified')
            elif key=='identity_verified':
                if not isinstance(value,bool):raise ValidationError('Confirm the identity explicitly.')
                p['metadata_state']='approved' if value else 'review'
                p['identity_status']='documented' if value else 'provisional'
            elif key=='category':
                if value not in ('standard','jumbo','cameo'):raise ValidationError('Choose a collection category.')
                p[key]=value
            elif key=='rarity_state':
                if value not in ('known','not_printed','unresolved'):raise ValidationError('Choose a rarity state.')
                p[key]=value
            elif key=='rarity_family':
                if value not in ('common','uncommon','rare','full_art','other'):raise ValidationError('Choose a rarity group.')
                p[key]=value
            else:p[key]=text(value,150)
        with self.lock,self.connect() as c:
            row=c.execute('SELECT * FROM entry_overrides WHERE entry_id=?',(e['id'],)).fetchone();before=dict(row) if row else None;merged=(json.loads(row['payload_json']) if row else {})|p
            if merged.get('rarity_state')=='not_printed':merged.update(rarity_code=None,rarity_label='No printed rarity',rarity_family='other')
            if merged.get('rarity_state')=='known' and not merged.get('rarity_code',e.get('rarity_code')):raise ValidationError('Enter the verified rarity label.')
            c.execute('INSERT OR REPLACE INTO entry_overrides VALUES(?,?,?,?)',(e['id'],js(merged),source_note,now()));self.audit(c,'catalog_corrected',e['id'],before,dict(values=merged,source_note=source_note))
        return dict(entry_id=e['id'])
    def override_release(self,data):
        lang=data.get('lang');release=text(data.get('release',''),200);source_note=note(data)
        if not any(e['lang']==lang and e['release']==release for e in self.entries().values()):raise ValidationError('Set not found in this language.')
        values=catalog_date(data.get('release_date',''))|dict(date_state='manual_verified',date_source=source_note,year_basis='manual_set');key=lang+':'+release
        with self.lock,self.connect() as c:
            row=c.execute('SELECT * FROM release_overrides WHERE release_id=?',(key,)).fetchone();c.execute('INSERT OR REPLACE INTO release_overrides VALUES(?,?,?,?)',(key,js(values),source_note,now()));self.audit(c,'set_date_corrected',key,dict(row) if row else None,values)
        return dict(release_id=key)
    def new_entry(self,data):
        source_note=note(data);lang=data.get('lang');dex=data.get('dex');roster={r['dex']:r['name'] for r in self.catalog['roster']}
        if lang not in ('en','de','ja','ko') or dex not in roster:raise ValidationError('Choose a language and a Pokémon from this collection.')
        category=data.get('category','standard')
        if category not in ('standard','jumbo','cameo'):raise ValidationError('Choose a category.')
        name=text(data.get('name',''),150);number=text(data.get('number','Unnumbered'),100);set_name=text(data.get('set_name',''),200)
        if not name or not set_name or not number:raise ValidationError('Name, source and printed identifier are required.')
        release=text(data.get('release',''),200);known=next((e for e in self.entries().values() if e['lang']==lang and e['release']==release),None)
        if release and not known:raise ValidationError('Choose an existing set or leave it as a new source.')
        for old in self.entries().values():
            same_source=old['release']==release if release else old['set_name'].casefold()==set_name.casefold()
            if old['lang']==lang and same_source and old['number'].casefold()==number.casefold() and (number.casefold()!='unnumbered' or old['name'].casefold()==name.casefold()):raise ValidationError('This card already exists. Open its record to add another physical printing.')
        eid=ident('manual_entry');release=release or 'manual:'+eid;dates=catalog_date(data.get('release_date',''))
        date_meta=dict(year_basis='manual',date_state='manual_verified' if dates['release_date'] else 'unresolved',date_source=source_note if dates['release_date'] else None)
        if not dates['release_date'] and known:
            regional=next((r for r in self.catalog.get('releases',[]) if r['lang']==lang and r['release']==release),None)
            override=next((r for r in self.state()['release_overrides'] if r['release_id']==lang+':'+release),None)
            if override:
                values=json.loads(override['payload_json']);dates=catalog_date(values.get('release_date') or '')
                date_meta=dict(year_basis='manual_set',date_state=values['date_state'],date_source=override['source_note'])
            elif regional:
                inherited=regional.get('date') or regional.get('reference_date')
                if inherited:
                    dates=catalog_date(inherited)
                    date_meta=dict(year_basis='set',date_state=regional['date_state'] if regional.get('date') else 'provider_reference',date_source=regional.get('source_url') or regional.get('reference_source_url'))
        english=text(data.get('english',''),150) or (name if lang=='en' else roster[dex]);set_name=known['set_name'] if known else set_name
        e=dict(id=eid,lang=lang,name=name,english=english,dex=dex,number=number,number_key=number,identifier_namespace='unnumbered' if number.casefold()=='unnumbered' else 'collector',release=release,set_name=set_name,**dates,**date_meta,rarity_code=None,rarity_state='unresolved',rarity_namespace='manual',rarity_label='Needs research',rarity_family='other',metadata_state='review',category=category,art_style=None,art_style_state='unresolved',subject_dex=[] if category=='cameo' else [dex],cameo_dex=[dex] if category=='cameo' else [],image=None,printings=[],sources=[dict(id='release:'+lang+':'+release,name=set_name,state='manual')],links=[])

        with self.lock,self.connect() as c:c.execute('INSERT INTO manual_entries VALUES(?,?,?,?)',(eid,js(e),source_note,now()));self.audit(c,'catalog_entry_added',eid,None,e)
        return dict(entry_id=eid)
    def new_printing(self,data):
        try:return self.save_printing(data)
        except ValueError as exc:raise ValidationError(str(exc)) from exc
    def catalog_image(self,data):
        e=self.entry(data.get('entry_id'));source_note=note(data);pid=data.get('printing_id') or None
        printing=next((p for p in e['printings']+e.get('printing_claims',[]) if p['id']==pid),None)
        if pid and not printing:raise ValidationError('That printing does not belong to this card.')
        kind=data.get('image_kind','representative');exact=data.get('image_exact') is True
        if kind not in ('representative','physical_photo'):raise ValidationError('Choose the picture type.')
        if exact and (not pid or kind!='physical_photo'):raise ValidationError('Exact image verification requires a printing-specific physical specimen image.')
        from .editor import urls
        links=urls(data.get('image_source_urls',[]))
        try:raw=base64.b64decode(data.get('bytes',''),validate=True)
        except (ValueError,TypeError):raise ValidationError('The picture could not be read.')
        if not 100<=len(raw)<=8_000_000:raise ValidationError('Catalog pictures must be under 8 MB.')
        ext=image_type(raw);filename=hashlib.sha256(raw).hexdigest()+'.'+ext;(self.user_dir/'catalog_images'/filename).write_bytes(raw)
        table,key,target=('printing_image_overrides','printing_id',pid) if pid else ('image_overrides','entry_id',e['id'])
        with self.lock,self.connect() as c:
            row=c.execute('SELECT * FROM '+table+' WHERE '+key+'=?',(target,)).fetchone();c.execute('INSERT OR REPLACE INTO '+table+' VALUES(?,?,?,?)',(target,filename,source_note,now()))
            review=dict(image='/user-images/'+filename,kind=kind,status='verified' if exact else 'unverified',source_urls=links,checked_at=now() if exact else None)
            override_table,override_key=('printing_overrides','printing_id') if pid else ('entry_overrides','entry_id')
            old=c.execute('SELECT payload_json FROM '+override_table+' WHERE '+override_key+'=?',(target,)).fetchone()
            values=(dict(printing) if pid else {})|(json.loads(old[0]) if old else {})
            if pid:review['physical_key']=list(physical_key(e['id'],printing))
            values['_image_review_only']=not old or json.loads(old[0]).get('_image_review_only',False)
            values['image_review']=review
            c.execute('INSERT OR REPLACE INTO '+override_table+' VALUES(?,?,?,?)',(target,js(values),source_note,now()))
            self.audit(c,'printing_picture_set' if pid else 'catalog_picture_set',target,dict(row) if row else None,dict(filename=filename,source_note=source_note,image_review=review))
        return dict(entry_id=e['id'])
    def remove_image(self,data):
        e=self.entry(data.get('entry_id'));pid=data.get('printing_id') or None
        if pid and not any(p['id']==pid for p in e['printings']+e.get('printing_claims',[])):raise ValidationError('Printing not found.')
        table,key,target=('printing_image_overrides','printing_id',pid) if pid else ('image_overrides','entry_id',e['id'])
        with self.lock,self.connect() as c:
            row=c.execute('SELECT * FROM '+table+' WHERE '+key+'=?',(target,)).fetchone();c.execute('DELETE FROM '+table+' WHERE '+key+'=?',(target,));self.audit(c,'picture_override_removed',target,dict(row) if row else None,None)
        return dict(entry_id=e['id'])
    def source_image(self,data,remove=False):
        sid=data.get('source_id')
        if sid not in self.sources():raise ValidationError('Set/source not found.')
        source_note=note(data)
        filename=None
        if not remove:
            try:raw=base64.b64decode(data.get('bytes',''),validate=True)
            except (ValueError,TypeError):raise ValidationError('The cover could not be read.')
            if not 100<=len(raw)<=8_000_000:raise ValidationError('Cover pictures must be under 8 MB.')
            filename=hashlib.sha256(raw).hexdigest()+'.'+image_type(raw)
            (self.user_dir/'catalog_images'/filename).write_bytes(raw)
        with self.lock,self.connect() as c:
            old=c.execute('SELECT * FROM source_image_overrides WHERE source_id=?',(sid,)).fetchone()
            if remove:c.execute('DELETE FROM source_image_overrides WHERE source_id=?',(sid,))
            else:c.execute('INSERT OR REPLACE INTO source_image_overrides VALUES(?,?,?,?)',(sid,filename,source_note,now()))
            self.audit(c,'source_cover_removed' if remove else 'source_cover_set',sid,dict(old) if old else None,dict(filename=filename) if filename else None)
        return dict(source_id=sid)
    def backup(self):
        state=self.state(include_deleted=True);payload=dict(format='dogdex-collector-backup',version=4,catalog_sha256=self.catalog['catalog_sha256'],created_at=now(),tables=state);out=io.BytesIO()
        with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr('collection.json',js(payload))
            for filename in {r['filename'] for r in state['image_overrides']+state['printing_image_overrides']+state['source_image_overrides']}:
                p=self.user_dir/'catalog_images'/filename
                if p.is_file():z.write(p,'catalog_images/'+filename)
        return out.getvalue()
    def restore(self,raw):
        if len(raw)>128_000_000:raise ValidationError('Backup is too large.')
        try:
            z=zipfile.ZipFile(io.BytesIO(raw));info=z.getinfo('collection.json')
            if info.file_size>30_000_000 or sum(i.file_size for i in z.infolist())>256_000_000:raise ValidationError('Backup is too large.')
            payload=json.loads(z.read('collection.json'))
        except (zipfile.BadZipFile,KeyError,ValueError,UnicodeError):raise ValidationError('Choose a DogDex collection backup ZIP.')
        if not isinstance(payload,dict) or payload.get('format')!='dogdex-collector-backup' or payload.get('version') not in (1,2,3,4) or not isinstance(payload.get('tables'),dict) or set(payload['tables']) not in (set(LEGACY_TABLES),set(V2_TABLES),set(V3_TABLES),set(TABLES)):raise ValidationError('Unsupported backup format.')
        for table in TABLES:payload['tables'].setdefault(table,[])
        tables=payload['tables'];known_entries=list(self.base_entries.values())+self.catalog.get('retired_entries',[]);entries={e['id'] for e in known_entries};manual={};printing_ids={p['id'] for e in known_entries for p in e['printings']}
        with self.connect() as c:
            for table in TABLES:
                columns={r[1] for r in c.execute('PRAGMA table_info('+table+')')}
                records=tables[table]
                if not isinstance(records,list) or any(not isinstance(row,dict) or set(row)!=columns for row in records):raise ValidationError('Backup columns do not match this app version.')
                primary='entry_id' if table in ('entry_overrides','image_overrides') else 'printing_id' if table in ('wishlist','printing_image_overrides') else 'release_id' if table=='release_overrides' else 'source_id' if table in ('source_overrides','source_image_overrides') else 'printing_id' if table=='printing_overrides' else 'id'
                ids=[r[primary] for r in records]
                if any(not isinstance(k,str) or not k or len(k)>300 for k in ids) or len(set(ids))!=len(ids):raise ValidationError('Backup contains invalid or repeated record identifiers.')
        for r in tables['manual_entries']:
            e=json.loads(r['payload_json'])
            if r['id'] in entries or e['id']!=r['id'] or e.get('printings') or e.get('lang') not in ('en','de','ja','ko'):raise ValidationError('Invalid manual card in backup.')
            entries.add(r['id']);manual[r['id']]=e
        for r in tables['manual_printings']:
            p=json.loads(r['payload_json'])
            if r['entry_id'] not in entries or p.get('id')!=r['id'] or r['id'] in printing_ids or p.get('finish') not in ('non_holo','holo','reverse_holo'):raise ValidationError('Invalid printing in backup.')
            printing_ids.add(r['id'])
        for r in tables['copies']:
            if r['printing_id'] not in printing_ids or r['condition'] not in CONDITIONS or r['price_minor'] is not None and (isinstance(r['price_minor'],bool) or not isinstance(r['price_minor'],int) or r['price_minor']<0 or r['currency'] not in CURRENCIES):raise ValidationError('Backup contains an unknown printing or invalid copy.')
        if any(r['printing_id'] not in printing_ids for r in tables['wishlist']):raise ValidationError('Backup wishlist references an unknown printing.')
        for key in ['entry_overrides','image_overrides']:
            if any(r['entry_id'] not in entries for r in tables[key]):raise ValidationError('Backup references a card not present in this catalog.')
        if any(r['printing_id'] not in printing_ids for r in tables['printing_overrides']):raise ValidationError('Backup printing correction references an unknown printing.')
        for row in tables['printing_overrides']:
            value=json.loads(row['payload_json'])
            if not isinstance(value,dict) or value.get('id')!=row['printing_id'] or value.get('entry_id') not in entries or value.get('finish') not in ('non_holo','holo','reverse_holo'):raise ValidationError('Invalid printing correction in backup.')
        for row in tables['entry_overrides']:
            value=json.loads(row['payload_json'])
            if not isinstance(value,dict) or 'id' in value and value['id']!=row['entry_id']:raise ValidationError('Invalid card correction in backup.')
        from .editor import base_sources
        baseline_sources=base_sources(self.catalog,True)
        if any(r['id'] in baseline_sources for r in tables['manual_sources']):raise ValidationError('A manual source cannot replace an original source identity.')
        sources=self.sources(tables,True,True)
        for row in tables['manual_sources']:
            source=json.loads(row['payload_json'])
            if not isinstance(source,dict) or source.get('id')!=row['id'] or source.get('lang') not in ('en','de','ja','ko'):raise ValidationError('Invalid source in backup.')
        if any(r['source_id'] not in sources for r in tables['source_overrides']):raise ValidationError('Backup source correction references an unknown source.')
        if any(r['source_id'] not in sources for r in tables['source_image_overrides']):raise ValidationError('Backup cover references an unknown source.')
        for row in tables['catalog_trash']:
            kind=row['kind'];target=row['target_id']
            if row['id']!=kind+':'+target or kind not in ('entry','printing','source') or target not in (entries if kind=='entry' else printing_ids if kind=='printing' else sources):raise ValidationError('Invalid removed catalog item in backup.')
        if any(r['printing_id'] not in printing_ids for r in tables['printing_image_overrides']):raise ValidationError('Backup picture references an unknown printing.')
        images={}
        for r in tables['image_overrides']+tables['printing_image_overrides']+tables['source_image_overrides']:
            name=r['filename']
            if not re.fullmatch(r'[a-f0-9]{64}\.(?:png|jpg|webp|gif)',name):raise ValidationError('Invalid catalog picture filename.')
            try:b=z.read('catalog_images/'+name)
            except KeyError:raise ValidationError('A catalog picture is missing from this backup.')
            if len(b)>8_000_000 or hashlib.sha256(b).hexdigest()!=name.split('.')[0] or image_type(b)!=name.split('.')[1]:raise ValidationError('A catalog picture failed its integrity check.')
            images[name]=b
        with self.lock:
            previous=self.backup();stamp=dt.datetime.now().strftime('%Y%m%d-%H%M%S-%f');(self.user_dir/'backups'/('before-restore-'+stamp+'.zip')).write_bytes(previous)
            with self.connect() as c:
                for table in TABLES:
                    columns=[r[1] for r in c.execute('PRAGMA table_info('+table+')')]
                    if any(set(row)!=set(columns) for row in tables[table]):raise ValidationError('Backup columns do not match this app version.')
                    c.execute('DELETE FROM '+table)
                    for row in tables[table]:c.execute('INSERT INTO '+table+' VALUES('+','.join('?' for _ in columns)+')',[row[k] for k in columns])
                for name,b in images.items():(self.user_dir/'catalog_images'/name).write_bytes(b)
                self.audit(c,'backup_restored','collection',None,dict(backup_date=payload.get('created_at')))
        return dict(restored=True)
    def mutate(self,action,data):
        if action in ('catalog/bulk/preview','catalog/bulk/apply','catalog/bulk/undo'):
            from .bulk_edit import preview,apply,undo
            return {'catalog/bulk/preview':preview,'catalog/bulk/apply':apply,'catalog/bulk/undo':undo}[action](self,data)
        if action=='catalog/printing/audit':
            from .printing_audit import audit
            return audit(self)
        if action=='catalog/source/image':return self.source_image(data)
        if action=='catalog/source/image/remove':return self.source_image(data,True)
        if action=='mobile/export':
            from .mobile_export import export_mobile
            return export_mobile(self)
        if action=='market/refresh':
            from .marketplace import refresh_prices
            return refresh_prices(self)
        if action=='market/search':
            from .marketplace import search_products
            return search_products(self,data)
        if action in ('market/confirm','market/unlink'):
            from .marketplace import confirm_product
            return confirm_product(self,data,action=='market/unlink')
        methods={'catalog/card/save':self.save_card,'catalog/source/save':self.save_source,'catalog/printing/save':self.save_printing,'catalog/remove':self.trash_item,'catalog/restore':lambda d:self.trash_item(d,True),'copy/add':self.add_copies,'copy/edit':self.edit_copy,'copy/remove':self.remove_copy,'copy/undo':lambda d:self.remove_copy(d,True),'wishlist':self.wish,'catalog/correct':self.override,'catalog/new':self.new_entry,'catalog/printing':self.new_printing,'catalog/image':self.catalog_image,'catalog/image/remove':self.remove_image,'catalog/release':self.override_release}
        if action not in methods:raise ValidationError('Unknown action.')
        with self.lock:return methods[action](data)
