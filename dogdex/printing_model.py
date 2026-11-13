"""Normalized physical identities; evidence and ownership are independent."""
import copy,json,re,unicodedata

def token(value):
 value=unicodedata.normalize('NFKD',str(value or '')).casefold()
 # Fold Latin accents for known aliases, but retain regional script and kana
 # voicing marks. Native stamp names must never collapse to an empty identity.
 value=''.join(c for c in value if not (unicodedata.combining(c) and '\u0300'<=c<='\u036f'))
 return re.sub(r'[^\w]+','_',unicodedata.normalize('NFKC',value)).strip('_')
PATTERNS=dict(none='None',unspecified='Standard / no special pattern recorded',energy='Energy',friend_ball='Friend Ball',poke_ball='Poké Ball',master_ball='Master Ball',dusk_ball='Dusk Ball',love_ball='Love Ball',quick_ball='Quick Ball',rocket='Team Rocket R',mirror='Mirror',cosmos='Cosmos',cosmos_smooth='Cosmos smooth',cosmos_pixel='Cosmos pixel',ripple='Ripple',rainbow='Rainbow',confetti='Confetti',sparkle='Sparkle',cracked_ice='Cracked ice',line='Line',gold='Gold',tinsel='Tinsel',crosshatch='Crosshatch',spinning_squares='Spinning squares',water_web='Water web',sequin='Sequin',sheen='Sheen')
ALIASES=dict(standard='unspecified',regular='unspecified',unknown='unspecified',energy_symbol='energy',energy_symbols='energy',energy_pattern='energy',energy_symbol_pattern='energy',energy_foil='energy',energie='energy',energiesymbol='energy',friendball='friend_ball',friend_ball_pattern='friend_ball',freundesball='friend_ball',pokeball='poke_ball',poke_ball_pattern='poke_ball',pokeball_pattern='poke_ball',masterball='master_ball',master_ball_pattern='master_ball',meisterball='master_ball',duskball='dusk_ball',finsterball='dusk_ball',loveball='love_ball',sympaball='love_ball',quickball='quick_ball',flottball='quick_ball',team_rocket='rocket',r='rocket',cosmic='cosmos',crackedice='cracked_ice',not_applicable='none')
PATTERNS['mirage']='Mirage'
STAMP_LABELS=dict(play_pokemon='Play! Pokémon',white_flare='White Flare logo',pikachu_jack_o_lantern='Pikachu jack-o’-lantern')
STAMP_LABELS['30th_anniversary']='30th anniversary'
STAMP_LABELS['chaos_rising']='Chaos Rising logo'
FINISHES=dict(non_holo='Non-holo',holo='Holo',reverse_holo='Reverse holo')
EDITIONS=dict(not_applicable='Standard',first_edition='First edition',unlimited='Unlimited',unstamped='Unstamped')
LAYOUTS=dict(standard='Standard',shadowed='Shadowed',shadowless='Shadowless')
def pattern_key(value,finish=None):
 key=token(value);key=ALIASES.get(key,key)
 if not key:return 'none' if finish=='non_holo' else 'unspecified'
 if finish in ('holo','reverse_holo') and key=='none':return 'unspecified'
 return 'none' if finish=='non_holo' and key=='unspecified' else key

def normalized(p):
 finish=token(p.get('finish'));finish=dict(normal='non_holo',nonholo='non_holo',holofoil='holo',reverse='reverse_holo',reverse_holofoil='reverse_holo').get(finish,finish)
 edition=token(p.get('edition')) or 'not_applicable';edition={'standard':'not_applicable','no_edition_distinction':'not_applicable','1st_edition':'first_edition','first':'first_edition'}.get(edition,edition)
 stamps=p.get('stamps',p.get('stamps_json','[]'))
 if isinstance(stamps,str):
  try:stamps=json.loads(stamps)
  except ValueError:stamps=stamps.split(',')
 return dict(finish=finish,pattern=pattern_key(p.get('pattern'),finish),edition=edition,layout=token(p.get('layout')) or 'standard',size=token(p.get('size')) or 'standard',material=token(p.get('material')) or 'paper',stamps_json=json.dumps(sorted({token(s) for s in stamps if token(s)}),separators=(',',':')),print_state=token(p.get('print_state')) or 'standard')
def physical_key(entry_id,p):
 n=normalized(p);return (entry_id,*(n[k] for k in ('finish','pattern','edition','layout','size','material','stamps_json','print_state')))
def pattern_label(value):return PATTERNS.get(pattern_key(value),str(value or '').replace('custom_','').replace('_',' ').title())
def printing_label(p):
 n=normalized(p);parts=[FINISHES.get(n['finish'],str(p.get('finish','Unknown')))]
 if n['pattern'] not in ('none','unspecified'):parts.append(pattern_label(n['pattern']))
 if n['edition'] in ('first_edition','unlimited'):parts.append('1st edition' if n['edition']=='first_edition' else 'Unlimited')
 if n['layout'] not in ('standard','shadowed'):parts.append(LAYOUTS.get(n['layout'],n['layout'].replace('_',' ').title()))
 if n['size']=='oversized':parts.append('Jumbo')
 if n['material']!='paper':parts.append(n['material'].title())
 stamps=p.get('stamps_json','[]');parts.extend(STAMP_LABELS.get(s,s) for s in (json.loads(stamps) if isinstance(stamps,str) else stamps))
 if n['print_state']!='standard':parts.append(str(p.get('print_state')).replace('_',' '))
 return ' · '.join(parts)
def verification(p):
 value=copy.deepcopy(p.get('verification') or {});value.setdefault('existence',dict(status='previously_accepted' if p.get('collection_status') not in ('provisional','disputed','excluded') else p['collection_status'],source_urls=[]));value.setdefault('specimen',dict(status='not_inspected'));return value

def image_review(e,p=None):
 obj=p or e;image=obj.get('image') or e.get('image');review=obj.get('image_review') or {}
 if image and review.get('image')==image:
  if p and review.get('physical_key') and review['physical_key']!=list(physical_key(e['id'],p)):return review|dict(status='unverified',reason='Physical printing changed since the image was checked.')
  return review
 return dict(kind='representative',status='unverified',image=image)
def taxonomy():return dict(finishes=FINISHES,patterns=PATTERNS,editions=EDITIONS,layouts=LAYOUTS)

# Historical ID/label encodings are frozen for deterministic rebuilds. They are
# never used by the editor's normalized duplicate gate or for new reviewed IDs.
def legacy_physical_key(entry_id,p):
 return (entry_id,*(p.get(k) for k in ['finish','pattern','edition','layout','size','material']),tuple(json.loads(p.get('stamps_json','[]'))),p.get('print_state'))
def legacy_label(p):
 parts=[FINISHES[p['finish']]]
 if p['pattern'] not in ('none','unspecified'):parts.append(p['pattern'].replace('_',' ').title())
 if p['edition'] in ('first_edition','unlimited'):parts.append({'first_edition':'1st edition','unlimited':'Unlimited'}[p['edition']])
 if p['layout']=='shadowless':parts.append('Shadowless')
 if p['size']=='oversized':parts.append('Jumbo')
 if p['material']=='metal':parts.append('Metal')
 parts.extend(json.loads(p['stamps_json']))
 if p['print_state']!='standard':parts.append(p['print_state'].replace('_',' '))
 return ' · '.join(parts)
