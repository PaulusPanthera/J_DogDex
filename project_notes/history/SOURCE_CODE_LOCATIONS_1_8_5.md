# Actual DogDex code locations — 1.8.4 → 1.8.5

Line ranges below were extracted from the supplied 1.8.4 ZIP and the delivered 1.8.5 source. Paths are relative to the DogDex folder.

The original cause combines creation and presentation: provider subset codes create separate release records; `base_sources` includes per-printing retail provenance; the old `sourceView` renders every membership as a separate progress-bearing tile. This update leaves those IDs intact and introduces a source-role/parent overlay.

| Relative path / function | Original lines | Updated lines | Responsibility |
|---|---|---|---|
| `editor.py` · `base_sources` | 52–63 | 53–64 | Creates source records from provider releases and source-product assertions; the original distinct subset IDs originate here. |
| `editor.py` · `sources` | 66–87 | 67–89 | Merges persisted custom sources, overrides, trash and source pictures; applies navigation overlay. |
| `editor.py` · `catalog_entries` | 89–173 | 91–176 | Resolves card/printing overlays and membership without changing stored IDs. |
| `editor.py` · `_source_values` | 182–203 | 185–207 | Validates source fields and parent/subset role before persistence. |
| `editor.py` · `save_source` | 205–219 | 209–223 | Stores new/edited source JSON in collection tables. |
| `editor.py` · `_card_values` | 221–252 | 225–257 | Validates canonical card source; a retail product is not automatically a numbered set. |
| `collector.py` · `Collection.__init__` | 73–90 | 73–93 | Creates source-version backup and opens existing collection without rekeying. |
| `collector.py` · `Collection.state` | 100–108 | 103–111 | Reads persisted collection/overlay tables. |
| `collector.py` · `Collection.backup` | 319–326 | 322–329 | Exports all collection records and user images. |
| `collector.py` · `Collection.restore` | 327–396 | 330–399 | Validates and restores collection backups. |
| `release_info.py` · `decorate_sources` | 43–64 | 43–64 | Language-specific dates, eras, sequence and exact canonical set metadata. |
| `source_structure.py` · `facts` | New | 15–15 | Loads explicit language-scoped source registry. |
| `source_structure.py` · `annotate_sources` | New | 24–63 | Validates canonical parents, sections, aliases, products and fallback issues. |
| `source_structure.py` · `annotate_entry` | New | 88–98 | Adds expansion, section and distribution navigation fields. |
| `source_structure.py` · `distribution_ids` | New | 65–86 | Many-to-many product membership with card/printing-level provenance. |
| `source_structure.py` · `validate_source_structure` | New | 100–117 | Same-language parent, independent role and unique section-key validation. |
| `source_structure.py` · `guard_primary_source` | New | 119–120 | Prevents a new product context becoming an accidental confirmed set identity. |
| `source_inventory.py` · `inventory_rows` | New | 25–37 | Exhaustive current source inventory including zero/retired/removed/manual sources. |
| `source_inventory.py` · `product_mapping` | New | 51–79 | Explicit old source → canonical card → printing → distribution mapping. |
| `source_inventory.py` · `write_reports` | New | 81–92 | Counts and exact ID before/after reconciliation. |
| `source_inventory.py` · `inventory_csv` | New | 47–47 | Runtime CSV download for the collector’s saved overlays. |
| `special_import.py` · `add_printing` | 21–38 | 21–42 | Keeps normalized physical tuple duplicate gate; appends another product membership on an existing ID. |
| `prepare.py` · `build` | 24–61 | 24–61 | Original checkpoint import creates stable cards/printings and source product assertions. |
| `catalog_enrich.py` · `main` | 126–148 | 126–148 | Reproducible reviewed enrichment pipeline, not run against the released catalog in this update. |
| `catalog_enrich.py` · `make_sqlite` | 108–124 | 108–124 | Derived SQLite tables entries, printings, releases, facts. |
| `mobile_export.py` · `build_snapshot` | 12–44 | 12–44 | Exports public navigation/membership alongside existing ownership counts. |
| `mobile_export.py` · `export_mobile` | 46–107 | 46–107 | Copies matching viewer module and produces one-way docs snapshot. |
| `app.py` · `make_server` | 7–62 | 7–65 | Serves application/state and full runtime source-inventory CSV. |
| `static/app.js` · `rebuild` | 24–30 | 25–31 | Source grouping, filtering, navigation or editor UI. |
| `static/app.js` · `searchText` | 36 | 37 | Source grouping, filtering, navigation or editor UI. |
| `static/app.js` · `queryMatches` | 37 | 40 | Source grouping, filtering, navigation or editor UI. |
| `static/app.js` · `filteredRows` | 39 | 43–48 | Source grouping, filtering, navigation or editor UI. |
| `static/app.js` · `matchesScope` | 45 | 54 | Source grouping, filtering, navigation or editor UI. |
| `static/app.js` · `card` | 54–57 | 63–67 | Source grouping, filtering, navigation or editor UI. |
| `static/app.js` · `sourceView` | 62–69 | 73–82 | Unified expansion tiles versus distribution products without completion bars. |
| `static/app.js` · `sourceContext` | See module | 83–89 | Source grouping, filtering, navigation or editor UI. |
| `static/app.js` · `openSource` | See module | 90 | Source grouping, filtering, navigation or editor UI. |
| `static/app.js` · `render` | 73–77 | 95–99 | Source grouping, filtering, navigation or editor UI. |
| `static/app.js` · `detail` | 86–107 | 108–129 | Source grouping, filtering, navigation or editor UI. |
| `static/app.js` · `switchLanguage` | 109–125 | 131–147 | Preserves parent and equivalent section with explicit fallback. |
| `static/source-ui.mjs` · `sourceRoot` | New | 4–7 | Source grouping, filtering, navigation or editor UI. |
| `static/source-ui.mjs` · `inSource` | New | 8–15 | Source grouping, filtering, navigation or editor UI. |
| `static/source-ui.mjs` · `groupSources` | New | 16–22 | Source grouping, filtering, navigation or editor UI. |
| `static/source-ui.mjs` · `subsetSections` | New | 23–30 | Source grouping, filtering, navigation or editor UI. |
| `static/source-ui.mjs` · `localizedScope` | New | 31–39 | Source grouping, filtering, navigation or editor UI. |
| `static/source-ui.mjs` · `setDestination` | New | 40 | Source grouping, filtering, navigation or editor UI. |
| `static/localization.mjs` · `recognizedSetQuery` | 4 | 4–10 | Source grouping, filtering, navigation or editor UI. |
| `static/localization.mjs` · `equivalentSource` | 5 | 11 | Source grouping, filtering, navigation or editor UI. |
| `static/localization.mjs` · `equivalentCard` | 8 | 14 | Exact set/card namespace match; parent expansion is not used to invent a regional release. |
| `static/localization.mjs` · `equivalentPrinting` | 10 | 16 | Source grouping, filtering, navigation or editor UI. |
| `static/editor-ui.mjs` · `structureFields` | See module | 20–23 | Source grouping, filtering, navigation or editor UI. |
| `static/editor-ui.mjs` · `sourceFields` | 19–21 | 24–26 | Source grouping, filtering, navigation or editor UI. |
| `static/editor-ui.mjs` · `source` | 22–25 | 27–30 | Source grouping, filtering, navigation or editor UI. |
| `static/editor-ui.mjs` · `health` | 74–84 | 79–89 | Source grouping, filtering, navigation or editor UI. |
| `static/editor-ui.mjs` · `change` | 113–138 | 118–147 | Source grouping, filtering, navigation or editor UI. |
| `static/editor-ui.mjs` · `sourceData` | 141 | 150 | Persists explicit role/parent/section selection in existing JSON overlays. |
| `static/editor-ui.mjs` · `submit` | 142–169 | 151–178 | Source grouping, filtering, navigation or editor UI. |
| `static/catalog.mjs` · `uniqueProgress` | 14 | 14 | Counts normalized physical identities once, including multiple copies and overlapping memberships. |
| `static/catalog.mjs` · `compareSources` | 29–43 | 29–43 | Source grouping, filtering, navigation or editor UI. |
| `static/catalog.mjs` · `compareRows` | 11 | 11 | Source grouping, filtering, navigation or editor UI. |

## Stored and generated data

- `data/catalog.sqlite3`: immutable original checkpoint, including releases, entries and source-product bindings.
- `data/catalog-collector.sqlite3`: derived entries/printings/releases/facts index, unchanged in this release.
- `data/catalog.json`: original card identities, provider codes, physical tuples and evidence, unchanged.
- `data/research/sources_185/source_relations.json`: explicit source role, root, subset namespace, aliases, distribution splits and reasons for every source.
- `source_structure_build.py`: deterministic registry reproduction from `baseline_184.json`; mappings are language-bound, not inferred from name substrings at runtime.
- `my_collection/collection.sqlite3`: saved `manual_sources`, `source_overrides`, `release_overrides`, manual cards/printings, copies, wishes, image mappings and audit history. Existing schemas are retained; only a meta structure-version marker is added.
- `static/editor-ui.mjs`: source editor controls for parent/role/key, separate from the code that originally imported IDs.
- `static/app.js` click handler: `source`, `card-source`, `subset`, `source-tab`, `source-back` actions call the non-destructive navigation helpers.
- `static/app.css`: source tabs, compact wrapping subset filters, source-name buttons and structure-issue styling.

## Explicit source definitions and distribution mapping

| Relative file | Lines | Responsibility |
|---|---|---|
| `source_structure_build.py` | 31–40 | Exact EN/DE external subset codes and canonical parents. |
| `source_structure_build.py` | 76–87 | Explicit source-type review of regional numbered expansions, boxes, sheets and packs. |
| `source_structure_build.py` | 103–107 | Combined ETB/UPC provenance split into three distribution records over the same promo printing IDs. |
