"""Presentation metadata only. Never replaces regional dates or catalog IDs."""
import re

ERAS = [
    ('base', 'Base & Gym · Generation I'), ('neo', 'Neo & e-Card · Generation II'),
    ('ex', 'EX · Generation III'), ('dp', 'Diamond & Pearl · Generation IV'),
    ('pl', 'Platinum · Generation IV'), ('hgss', 'HeartGold & SoulSilver · Generation IV'),
    ('bw', 'Black & White · Generation V'), ('xy', 'XY · Generation VI'),
    ('sm', 'Sun & Moon · Generation VII'), ('swsh', 'Sword & Shield · Generation VIII'),
    ('sv', 'Scarlet & Violet · Generation IX'), ('me', 'Mega Evolution · Generation IX'),
    ('other', 'Other products / era unassigned')]
ERA_INDEX = {key: i for i, (key, _) in enumerate(ERAS)}
ERA_NAMES = dict(ERAS)
# Marketplace codes differ from provider/online-game abbreviations.
MARKET_CODES = {'gym1': 'GH', 'gym2': 'GC', 'col1': 'CL', 'swsh1': 'SSH',
                'hgss3': 'UD', 'ex7': 'RR', 'sm8': 'LOT', 'basep': 'WOTC',
                'tk-ex-m': 'TK2 M', '2018sm': 'MCD18F', '2019sm': 'MCD19F'}

def era_key(code, name='', date=None):
    code = code.lower()
    for prefix, era in [('swsh', 'swsh'), ('hgss', 'hgss'), ('ecard', 'neo'),
                        ('neo', 'neo'), ('base', 'base'), ('gym', 'base'),
                        ('pl', 'pl'), ('dp', 'dp'), ('bw', 'bw'), ('xy', 'xy'),
                        ('sm', 'sm'), ('sv', 'sv'), ('me', 'me'), ('ex', 'ex')]:
        if code.startswith(prefix): return era
    for token, era in [('tk-ex', 'ex'), ('tk-dp', 'dp'), ('tk-bw', 'bw'),
                       ('tk-xy', 'xy'), ('tk-sm', 'sm'), ('swsh', 'swsh'),
                       ('2011bw', 'bw'), ('2015xy', 'xy'), ('2016xy', 'xy')]:
        if token in code: return era
    special = {'lc': 'neo', 'col1': 'hgss', 'ru1': 'pl', 'dc1': 'xy', 'g1': 'xy',
               'det1': 'sm', 'cel25': 'swsh', 'mfb': 'sv', '30th': 'me', '30th-c': 'me'}
    if code in special: return special[code]
    # Product-only sources are grouped by their recorded period, not assigned a new date.
    year = int(str(date)[:4]) if re.match(r'^\d{4}', str(date or '')) else None
    if year==2025 and not re.match(r'^2025-(?:09-(?:2[6-9]|30)|1[0-2])',str(date or '')): return 'other'
    if year:
        for start, era in [(2025, 'me'), (2023, 'sv'), (2020, 'swsh'), (2017, 'sm'),
                           (2014, 'xy'), (2011, 'bw'), (2010, 'hgss'), (2009, 'pl'),
                           (2007, 'dp'), (2003, 'ex'), (2001, 'neo'), (1996, 'base')]:
            if year >= start: return era
    return 'other'

def decorate_sources(sources, catalog):
    releases = {(r['lang'], r['release']): r for r in catalog.get('releases', []) + catalog.get('retired_releases', [])}
    english = {r['release']: r for r in catalog.get('releases', []) if r['lang'] == 'en'}
    for source in sources.values():
        code = source.get('release') or ''
        source['canonical_set_id']=source.get('canonical_set_id') or (('western:'+code if source['lang'] in ('en','de') else 'regional:'+source['lang']+':'+code) if source.get('state')=='catalog_release' and code else 'source:'+source['id'])
        raw = releases.get((source['lang'], code), {})
        reference = english.get(code, raw)
        era = era_key(code, source['name'], source.get('release_date'))
        source['era_order'] = ERA_INDEX[era]
        source['series'] = source.get('series') or ERA_NAMES[era]
        source['series_basis'] = 'source_code_or_recorded_period'
        # Sequence hints are not asserted regional release dates. They only resolve
        # overlapping year/month precision. Fully specified dates always win.
        source['sequence_hint'] = reference.get('date') or raw.get('reference_date')
        if source.get('name') == code and code.startswith('tk-'):
            source['name'] = reference.get('name') or source['name']
        if source['lang'] in ('en', 'de'):
            abbreviation = reference.get('abbreviation') or {}
            source['market_code'] = MARKET_CODES.get(code) or abbreviation.get('official') or reference.get('tcg_online')
            source['market_set_name'] = reference.get('name') or source['name']
    return sources

def market_name_index(catalog):
    result={}
    for entry in catalog['entries']:
        if entry['lang']=='en':
            number=re.sub(r'^0+(?=\d)', '',str(entry['number'])).casefold()
            result.setdefault((entry['release'],number),set()).add(entry['name'])
    return result

def decorate_market_entry(entry, source, names_by_identity):
    if entry['lang'] not in ('en','de') or entry.get('market_link_override'): return
    def key(value): return re.sub(r'^0+(?=\d)', '', str(value)).casefold()
    if entry['lang']=='en': name=entry['name']
    else:
        names=names_by_identity.get((entry['release'],key(entry['number'])),set())
        name=next(iter(names)) if len(names)==1 else entry.get('market_name') or entry.get('english') or entry['name']
    entry['market_name']=name
    if source:
        entry['market_code']=source.get('market_code')
        entry['market_set_name']=source.get('market_set_name')
    code=entry['release']; number=str(entry['number'])
    modern=re.match(r'^(?:sv\d|me\d|swsh1[0-2])',code)
    if re.fullmatch(r'\d+',number): number=number.zfill(3) if modern else str(int(number))
    entry['market_number']=number
