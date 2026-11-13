"""Reviewed, atomic card-field edits. Collection and printing identities stay intact."""
import hashlib,json
from .editor import clean,dump,fail,timestamp,uid
from .rarities import label,options

FIELDS={
    'artwork':('art_style','art_style_state','art_style_source'),
    'rarity':('rarity_code','rarity_state','rarity_namespace','rarity_label','rarity_family'),
}

def subset(value,keys):return {key:value[key] for key in keys if key in value}

def changed_values(entry,field,value,note):
    if field=='artwork':
        return dict(art_style=value,art_style_state='manual_verified',art_style_source=note)
    code='S' if value=='S_legacy_lvx' else None if value=='not_printed' else value
    namespace=entry.get('rarity_namespace') or 'manual:'+entry['lang']
    if value=='S_legacy_lvx':namespace=entry['lang']+'_legacy_lvx'
    elif code=='S' and 'legacy' in namespace:namespace='manual:'+entry['lang']
    state='not_printed' if value=='not_printed' else 'known'
    family='common' if code in ('common','C') else 'uncommon' if code in ('uncommon','U') else 'other' if code is None or code in ('promo','P') else 'rare'
    return dict(rarity_code=code,rarity_state=state,rarity_namespace=namespace,
                rarity_label=label(value,entry['lang'],namespace),rarity_family=family)

def plan(store,data):
    field=data.get('field');lang=data.get('lang');value=data.get('value')
    ids=data.get('entry_ids');only=data.get('only_unclassified',True)
    if field not in FIELDS:fail('Bulk editing is available for artwork and card rarity.')
    if lang not in ('en','de','ja','ko'):fail('Choose one language ledger.')
    if not isinstance(ids,list) or not 1<=len(ids)<=5000 or any(not isinstance(eid,str) for eid in ids) or len(set(ids))!=len(ids):
        fail('Select between 1 and 5000 different cards.')
    if type(only) is not bool:fail('Choose whether existing classifications can be replaced.')
    allowed=('standard','full_art') if field=='artwork' else [r['code'] for r in options(lang,all_values=True) if r['code']!='unresolved']
    if value not in allowed:fail('Choose a classification from this ledger’s options.')
    note=clean(data.get('source_note') or 'Bulk '+field+' classification recorded by the collector.',4000)
    state=store.state();entries=store.catalog_entries(state)
    overrides={r['entry_id']:json.loads(r['payload_json']) for r in state['entry_overrides']}
    changes=[];skipped=[];contexts=[]
    for eid in ids:
        entry=entries.get(eid)
        if not entry or entry['lang']!=lang:fail('A selected card is unavailable or belongs to another language. Reselect the cards.')
        old=subset(overrides.get(eid,{}),FIELDS[field]);values=changed_values(entry,field,value,note)
        contexts.append(dict(entry_id=eid,identity=subset(entry,('lang','name','english','number','primary_source_id','set_name','identity_status','metadata_state')),field=subset(entry,FIELDS[field]),override=old))
        title=dict(entry_id=eid,name=entry.get('english') or entry['name'],number=entry['number'],set_name=entry['set_name'],image=entry.get('image') or next((p.get('image') for p in [*entry['printings'],*entry.get('printing_claims',[])] if p.get('image')),None))
        classified=bool(entry.get('art_style')) if field=='artwork' else entry.get('rarity_state') in ('known','not_printed')
        same=entry.get('art_style')==value if field=='artwork' else all(entry.get(key)==values[key] for key in ('rarity_code','rarity_state','rarity_namespace'))
        if only and classified or same:
            skipped.append(title|dict(reason='Already classified' if only and classified else 'Already has this value'))
            continue
        before=('Full Art' if entry.get('art_style')=='full_art' else 'Standard artwork' if entry.get('art_style')=='standard' else 'Not classified') if field=='artwork' else label(entry.get('rarity_key'),lang,entry.get('rarity_namespace',''))
        after=('Standard artwork' if value=='standard' else 'Full Art') if field=='artwork' else label(value,lang,values['rarity_namespace'])
        changes.append(title|dict(before=before,after=after,values=values,old=old))
    key=hashlib.sha256(dump(dict(field=field,lang=lang,value=value,only_unclassified=only,note=note,contexts=contexts)).encode()).hexdigest()
    return dict(field=field,lang=lang,value=value,preview_key=key,selected_count=len(ids),changes=changes,skipped=skipped,note=note)

def preview(store,data):
    with store.lock:
        result=plan(store,data)
        return {key:value for key,value in result.items() if key!='note'}

def apply(store,data):
    with store.lock,store.connect() as db:
        db.execute('BEGIN IMMEDIATE')
        result=plan(store,data)
        if data.get('preview_key')!=result['preview_key']:fail('The selected cards changed after review. Review the batch again before saving.')
        if not result['changes']:fail('No selected cards need this change.')
        batch=uid('bulk');when=timestamp();before=[];after=[]
        for change in result['changes']:
            eid=change['entry_id'];row=db.execute('SELECT * FROM entry_overrides WHERE entry_id=?',(eid,)).fetchone()
            old=json.loads(row['payload_json']) if row else {};merged=old|change['values']
            note=(row['source_note']+'\n' if row and row['source_note'] else '')+result['note']
            db.execute('INSERT OR REPLACE INTO entry_overrides VALUES(?,?,?,?)',(eid,dump(merged),note,when))
            before.append(dict(entry_id=eid,values=change['old']))
            after.append(dict(entry_id=eid,values=change['values']))
        store.audit(db,'catalog_bulk_applied',batch,dict(field=result['field'],entries=before),
                    dict(field=result['field'],lang=result['lang'],value=result['value'],count=len(after),entries=after))
    return dict(batch_id=batch,field=result['field'],changed=len(after),skipped=len(result['skipped']))

def undo(store,data):
    batch=clean(data.get('batch_id') or '',100)
    with store.lock,store.connect() as db:
        db.execute('BEGIN IMMEDIATE')
        row=db.execute("SELECT * FROM audit_log WHERE action='catalog_bulk_applied' AND target=?",(batch,)).fetchone()
        if not row:fail('That bulk edit was not found.')
        if db.execute("SELECT 1 FROM audit_log WHERE action='catalog_bulk_undone' AND target=?",(batch,)).fetchone():fail('This bulk edit has already been undone.')
        before=json.loads(row['before_json']);after=json.loads(row['after_json']);keys=FIELDS[after['field']]
        old_values={r['entry_id']:r['values'] for r in before['entries']};rows=[]
        # Validate every target before writing anything. Other card fields may change freely.
        for record in after['entries']:
            saved=db.execute('SELECT * FROM entry_overrides WHERE entry_id=?',(record['entry_id'],)).fetchone()
            values=json.loads(saved['payload_json']) if saved else {}
            if subset(values,keys)!=record['values']:fail('A classification changed after this bulk edit. Undo would replace that newer change; review the affected cards individually.')
            rows.append((record['entry_id'],saved,values))
        when=timestamp()
        for eid,saved,values in rows:
            restored={key:value for key,value in values.items() if key not in keys}|old_values[eid]
            if restored:
                db.execute('INSERT OR REPLACE INTO entry_overrides VALUES(?,?,?,?)',(eid,dump(restored),saved['source_note']+'\nBulk '+after['field']+' edit undone by the collector.',when))
            else:db.execute('DELETE FROM entry_overrides WHERE entry_id=?',(eid,))
        store.audit(db,'catalog_bulk_undone',batch,None,dict(field=after['field'],count=len(rows)))
    return dict(batch_id=batch,changed=len(rows))
