"""A one-way, read-only website export for GitHub Pages. No database or server."""
from . import __version__
import json, os, re, shutil, tempfile
from pathlib import Path
from .marketplace import price_state

ENTRY_FIELDS = 'scope_review status_reason expansion_source_id expansion_name canonical_expansion_id subset_key subset_name subset_source_id source_search_terms canonical_set_id primary_source_id printing_aliases id lang name english dex number number_key identifier_namespace release set_name year rarity_code rarity_state rarity_key rarity_label rarity_order metadata_state category image image_language release_date date_precision date_state release_period subject_dex cameo_dex art_style identity_status identity_aliases cardmarket_url cardmarket_search cardmarket_code market_name market_link_override'.split()
PRINT_FIELDS = 'distribution_bindings distribution_source_ids physical_key image_review id entry_id finish pattern edition layout size material stamps_json print_state label category image image_scope printed_rarity_state printed_rarity_code rarity_key rarity_label rarity_order release_date date_state date_note world_championship_year collection_status cardmarket_url cardmarket_search market_name price_product_id price_series market_confirmed'.split()
SOURCE_FIELDS = 'links member_source_ids source_role navigation_source_id group_source_id canonical_expansion_id parent_source_id subset_key subset_name subset_order subset_aliases aliases numbering_namespace overview_section structure_state canonical_set_id id lang release name kind series era_order sort_order sequence_hint market_code market_set_name release_date date_precision year date_state release_period image state'.split()

def select(value, fields): return {key: value[key] for key in fields if key in value}

def build_snapshot(store):
    from .collector import now
    # One coherent SQLite snapshot, including manual catalog overlays.
    with store.lock:
        state = store.state()
        view = store.editor_view()
        sources = {s['id']: select(s, SOURCE_FIELDS) for s in view['sources']}
        entries = []
        for entry in view['entries']:
            clean = select(entry, ENTRY_FIELDS)
            clean.update({k:entry[k] for k in ('market_code','market_number','market_set_name') if k in entry})
            clean['variant_claims']=[select(c,('disposition','normalized_partial')) for c in entry.get('variant_claims',[])]
            clean['sources'] = [sources[s['id']] for s in entry.get('sources', []) if s['id'] in sources]
            for kind in ('printings', 'printing_claims'):
                clean[kind] = []
                for printing in entry.get(kind, []):
                    value = select(printing, PRINT_FIELDS)
                    if value.get('image_review'):value['image_review']=select(value['image_review'],('kind','status'))
                    if printing.get('market_match',{}).get('method')=='collector_product_search':value['market_match']=select(printing['market_match'],('method','canonical_url'))
                    if printing.get('sources'):
                        value['sources'] = [sources[s['id']] for s in printing['sources'] if s['id'] in sources]
                    clean[kind].append(value)
            entries.append(clean)
        ids = {p['id'] for e in entries for p in e['printings'] + e['printing_claims']}
        aliases={a:w for e in entries for a,w in e.get('printing_aliases',{}).items()}
        counts = {}
        for row in state['copies']:
            pid=aliases.get(row['printing_id'],row['printing_id'])
            if pid in ids:counts[pid]=counts.get(pid,0)+1
        return dict(format='dogdex-read-only-1', app_version=__version__, published_at=now(),
                    roster=store.catalog['roster'],rarity_options=store.catalog.get('rarity_options',{}), entries=entries, sources=list(sources.values()),
                    ownership=counts, wishlist=sorted({aliases.get(r['printing_id'],r['printing_id']) for r in state['wishlist'] if aliases.get(r['printing_id'],r['printing_id']) in ids}),
                    prices=price_state(store, view))

def export_mobile(store):
    """Replace only our managed docs folder; never touch personal records."""
    from .collector import ValidationError
    target = store.root / 'docs'
    marker = '.dogdex-export'
    if target.is_symlink(): raise ValidationError('The docs folder must not be a shortcut or symlink.')
    if target.exists() and any(target.iterdir()) and not (target / marker).is_file():
        raise ValidationError('The docs folder contains other files. Rename it before exporting DogDex there.')
    snapshot = build_snapshot(store)
    staging = Path(tempfile.mkdtemp(prefix='mobile-export-', dir=store.user_dir))
    previous = None
    try:
        for filename in ('app.css', 'app.js', 'set-symbols.mjs', 'catalog.mjs', 'prices.mjs', 'appearance.mjs', 'localization.mjs', 'source-ui.mjs'):
            shutil.copyfile(store.root / 'static' / filename, staging / filename)
        # The public viewer has no editor implementation, token, or private API.
        (staging / 'market-ui.mjs').write_text('export function makeMarketFinder(){return {syncSelection:()=>{},click:async()=>false,change:()=>false,submit:async()=>false};}\n', encoding='utf-8')
        (staging / 'editor-ui.mjs').write_text('export function makeEditor(){return {syncSelection:()=>{},click:async()=>false,change:()=>false,submit:async()=>false};}\n', encoding='utf-8')
        shutil.copytree(store.root / 'static' / 'flags', staging / 'flags')
        shutil.copytree(store.root / 'static' / 'set-symbols', staging / 'set-symbols')
        shutil.copytree(store.root / 'static' / 'brand', staging / 'brand')
        html = (store.root / 'static' / 'index.html').read_text(encoding='utf-8')
        html = html.replace('<html lang="en">', '<html lang="en" data-readonly="true">').replace('href="/app.css', 'href="./app.css').replace('src="/app.js', 'src="./app.js')
        html = html.replace('<title>DogDex · My collection</title>', '<title>DogDex · Collection viewer</title>')
        (staging / 'index.html').write_text(html, encoding='utf-8')
        (staging / 'snapshot.json').write_text(json.dumps(snapshot, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
        (staging / '.nojekyll').touch()
        (staging / marker).write_text('DogDex generated website. Replaced by Export mobile view.\n', encoding='utf-8')
        images = set()
        for source in snapshot['sources']:
            if source.get('image'): images.add(source['image'])
        for entry in snapshot['entries']:
            if entry.get('image'): images.add(entry['image'])
            for printing in entry['printings'] + entry['printing_claims']:
                if printing.get('image'): images.add(printing['image'])
        copied = 0
        for image in sorted(images):
            if re.fullmatch(r'[a-f0-9]{64}\.webp', image):
                source = store.root / 'data' / 'images' / image
                output = staging / 'images' / image
            elif re.fullmatch(r'/user-images/[a-f0-9]{64}\.(?:jpg|png|gif|webp)', image):
                source = store.user_dir / 'catalog_images' / Path(image).name
                output = staging / 'user-images' / source.name
            else: continue
            if source.is_file():
                output.parent.mkdir(exist_ok=True)
                shutil.copyfile(source, output)
                copied += 1
        if sum(p.stat().st_size for p in staging.rglob('*') if p.is_file()) > 950_000_000:
            raise ValidationError('The mobile export is too large for GitHub Pages. Reduce large custom pictures first.')
        with store.lock:
            if target.exists():
                previous = Path(tempfile.mkdtemp(prefix='mobile-previous-', dir=store.user_dir))
                previous.rmdir()
                os.replace(target, previous)
            try: os.replace(staging, target)
            except OSError:
                if previous: os.replace(previous, target)
                raise
        return dict(directory='docs', published_at=snapshot['published_at'], cards=len(snapshot['entries']),
                    printings=sum(len(e['printings']) for e in snapshot['entries']), images=copied,
                    message='Mobile view exported. Commit and push in GitHub Desktop to update the website.')
    finally:
        if staging.exists(): shutil.rmtree(staging)
        if previous and previous.exists(): shutil.rmtree(previous)

if __name__ == '__main__':
    from .collector import Collection
    print(json.dumps(export_mobile(Collection(Path(__file__).resolve().parents[1]))))
