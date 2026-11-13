# DogDex 1.8.5 — Source structure, products and preservation

This release changes source organization and navigation. It does not run a new card-printing factual audit. The original catalog JSON and both SQLite catalog checkpoints remain byte-identical to 1.8.4.

## Inventory and counting

- Original source records: **994**, including retired-only and zero-target metadata. All remain addressable.
- Inventory after adding navigation-only sections/distributions: **1015** rows. Added rows are metadata, not cards or printing targets.
- Current card identities: **3,820**. Raw printing IDs: **4,517**. Accepted completion targets: **4,509**; eight pre-existing held claims stay outside those totals.
- Accepted targets by language, unchanged: EN **1,693**, DE **1,439**, JA **847**, KO **530**.
- Source memberships overlap intentionally. Never sum per-source/product memberships to infer the unique collection total.
- The full CSV includes active, removed, retired and saved custom sources when generated on the collector’s PC. No personal PC database was provided; the supplied package has no personal records.

Files: `source_inventory.csv` / `.json`, `product_printing_mapping.csv` / `.json`, `before_after.json`, `source_relations.json`, `printing_id_reconciliation.csv`, `evidence_log.json`, `work_queue.json`.

## Expansion grouping before / after

| Language | Original source ID → canonical source | Subset | Main | Subset | Combined | Old subset tile |
|---|---|---|---:|---:|---:|---|
| EN | `release:en:swsh12.5gg` → `release:en:swsh12.5` | Galarian Gallery | 16 | 6 | **22** | Visible |
| DE | `release:de:swsh12.5gg` → `release:de:swsh12.5` | Galar-Galerie | 16 | 6 | **22** | Visible |
| EN | `release:en:swsh9tg` → `release:en:swsh9` | Trainer Gallery | 11 | 2 | **13** | Visible |
| DE | `release:de:swsh9tg` → `release:de:swsh9` | Trainer Gallery | 8 | 2 | **10** | Visible |
| EN | `release:en:swsh10tg` → `release:en:swsh10` | Trainer Gallery | 14 | 3 | **17** | Visible |
| DE | `release:de:swsh10tg` → `release:de:swsh10` | Trainer Gallery | 13 | 3 | **16** | Visible |
| EN | `release:en:swsh11tg` → `release:en:swsh11` | Trainer Gallery | 24 | 1 | **25** | Visible |
| DE | `release:de:swsh11tg` → `release:de:swsh11` | Trainer Gallery | 20 | 1 | **21** | Visible |
| EN | `release:en:swsh12tg` → `release:en:swsh12` | Trainer Gallery | 27 | 3 | **30** | Visible |
| DE | `release:de:swsh12tg` → `release:de:swsh12` | Trainer Gallery | 24 | 3 | **27** | Visible |
| EN | `release:en:swsh4.5sv` → `release:en:swsh4.5` | Shiny Vault | 10 | 5 | **15** | Visible |
| DE | `release:de:swsh4.5sv` → `release:de:swsh4.5` | Shiny Vault | 10 | 5 | **15** | Visible |
| EN | `release:en:sma` → `release:en:sm115` | Shiny Vault | 0 | 10 | **10** | Visible |
| DE | `release:de:sma` → `release:de:sm115` | Shiny Vault | 0 | 10 | **10** | Visible |
| EN | `release:en:cel25cc` → `release:en:cel25` | Classic Collection | 3 | 0 | **3** | Not visible / metadata only |
| DE | `release:de:cel25cc` → `release:de:cel25` | Classic Collection | 2 | 0 | **2** | Not visible / metadata only |

Hidden Fates’ main metadata had no active tracked main-set cards. Its existing ten Shiny Vault printings now navigate to Hidden Fates; no retired card was restored. Celebrations Classic Collection contains no active in-scope card here. Its section is retained as zero-card metadata; no Classic Collection identity is invented.

Other inspected numbering sections are RC in Legendary Treasures and Generations; SH in Stormfront, Platinum, Supreme Victors and Arceus; RT in Rising Rivals; AR in Arceus; SL in Call of Legends. Only already indexed in-scope cards participate. Empty out-of-roster sections add zero targets. Ordinary secret numbers remain inside their expansion.

SWSH Black Star Promos, McDonald’s Collection 2021, the three Prize Pack series, Black Bolt and White Flare remain independent. JP/KO regional releases remain separate: Korean `sma` is a starter set; Japanese `S8a` and the anniversary promo-pack release are not Western Celebrations/Classic Collection equivalents.

## The 15 requested product contexts

The table below summarizes indexed contents, not every booster or accessory in the retail package. Full rows contain stable entry/printing IDs, original physical tuples, language, collector namespace, stamps, foil pattern, retained marketplace references, evidence and action. A product name alone does not establish German availability.

| Old source / product | Canonical set and indexed card(s) | Recorded physical printing | Distribution/action |
|---|---|---|---|
| Legends of Galar Tins | SWSH Black Star Promos · Zacian V #SWSH018 (EN); SWSH Black Star Promos · Zamazenta V #SWSH019 (EN) | holo / unspecified / not_applicable / standard; stamps=[] | Existing printing IDs retained; product association, no extra target. |
| Sword & Shield Elite Trainer Box Plus / Ultra-Premium Collection | SWSH Black Star Promos · Zacian V #SWSH076 (EN); SWSH Black Star Promos · Zamazenta V #SWSH077 (EN) | holo / unspecified / not_applicable / standard; stamps=[] | Split old aggregate into Zacian ETB Plus (076), Zamazenta ETB Plus (077), UPC (both); preserve same promo IDs. |
| True Steel Premium Collections | SWSH Black Star Promos · Zacian #SWSH033 (EN); SWSH Black Star Promos · Zamazenta #SWSH034 (EN) | holo / cosmos / not_applicable / standard; stamps=[] | Existing printing IDs retained; product association, no extra target. |
| Battle Styles Build & Battle Box | Battle Styles · Houndoom #96 (EN) | non_holo / none / not_applicable / standard; stamps=[] | Keep the distinct product-exclusive printing collectible under its original numbered card; product has no completion bar. |
| Boltund V Box | SWSH Black Star Promos · Boltund V #SWSH219 (EN) | holo / unspecified / not_applicable / oversized; stamps=[]; holo / unspecified / not_applicable / standard; stamps=[] | Existing printing IDs retained; product association, no extra target. |
| Cosmos Holo Fall 2022 Collector Chest exclusive | Astral Radiance · Hisuian Growlithe #070 (EN) | holo / cosmos / not_applicable / standard; stamps=[] | Keep the distinct product-exclusive printing collectible under its original numbered card; product has no completion bar. |
| Crown Zenith Elite Trainer Box | SWSH Black Star Promos · Lucario VSTAR #SWSH291 (EN) | holo / unspecified / not_applicable / standard; stamps=[] | Existing printing IDs retained; product association, no extra target. |
| Crown Zenith Premium Figure Collection Shiny Zacian | SWSH Black Star Promos · Zacian V #SWSH292 (EN) | holo / unspecified / not_applicable / standard; stamps=[] | Existing printing IDs retained; product association, no extra target. |
| Crown Zenith Premium Figure Collection Shiny Zamazenta | SWSH Black Star Promos · Zamazenta V #SWSH293 (EN) | holo / unspecified / not_applicable / standard; stamps=[] | Existing printing IDs retained; product association, no extra target. |
| Free Demo Deck | Champion's Path · Lucario V #27 (EN) | non_holo / none / not_applicable / standard; stamps=[] | Keep the distinct product-exclusive printing collectible under its original numbered card; product has no completion bar. |
| Galar Collection | Sword & Shield · Zacian V #138 (EN); Sword & Shield · Zamazenta V #139 (EN) | holo / unspecified / not_applicable / oversized; stamps=[] | Keep both oversized printings; recorded pattern remains unspecified. Earlier mirror-pattern provenance retained for later review. |
| Hisuian Zoroark VSTAR Premium Collection | SWSH Black Star Promos · Hisuian Zoroark V #SWSH297 (EN); SWSH Black Star Promos · Hisuian Zoroark VSTAR #SWSH298 (EN) | holo / unspecified / not_applicable / standard; stamps=[]; holo / unspecified / not_applicable / oversized; stamps=[] | Existing printing IDs retained; product association, no extra target. |
| Lucario VSTAR Premium Collection | SWSH Black Star Promos · Lucario V #SWSH213 (EN); SWSH Black Star Promos · Lucario VSTAR #SWSH214 (EN) | holo / unspecified / not_applicable / standard; stamps=[]; holo / unspecified / not_applicable / oversized; stamps=[] | Existing printing IDs retained; product association, no extra target. |
| Non Holo Brilliant Stars Build & Battle Box exclusive | Brilliant Stars · Lucario #079 (EN) | non_holo / none / not_applicable / standard; stamps=[] | Keep the distinct product-exclusive printing collectible under its original numbered card; product has no completion bar. |
| Non Holo Evolving Skies Build & Battle Box exclusive | Evolving Skies · Zoroark #103 (EN) | non_holo / none / not_applicable / standard; stamps=[] | Keep the distinct product-exclusive printing collectible under its original numbered card; product has no completion bar. |

The requested product contexts already link to canonical expansion or SWSH promo identities. The apparent extra completion targets came mainly from rendering distribution sources as collectible source tiles. No physical IDs were merged or deleted. Standard/jumbo sizes are distinct; Cosmos and non-holo product variants remain distinct.

The exhaustive product mapping contains **727 associations/zero-card contexts** over **353 distinct original contexts**, including independently numbered decks, other retail distributions, events and retired-only provenance. It separates printing-level bindings from weaker card-level associations. The latter remain explicitly unresolved; they are not proof that every finish of the card was in that product.

Two exact expansion-reference aliases are merged only in presentation. Same-name regular/jumbo product contexts share a product tile while preserving every member source and every printing. Reissues with uncertain commercial identity are not physically merged.

## Navigation and editing

- Sources has **Expansions & series** and **Products**. Products list existing indexed contents without their own completion bars.
- A unified expansion opens All cards, with internal Main Set / subset filters and counts. Gallery set-name links open the canonical expansion and the correct section.
- Names, localized aliases and subset names participate in search. EN↔DE keeps an equivalent section; an absent region/section gets a clear fallback notice.
- Existing edition, foil pattern, namespace and printed number are unchanged. Exact-card language matching still uses the original set identity, not the broader parent family.
- Data health → Sets & sources edits role, same-language parent, subset name/key and numbering namespace. Missing/cyclic/cross-language parents and uncertain structure appear under Needs structure review.
- Download full inventory exports the current PC overlays, custom sources, archived and removed contexts. Source covers use a parent cover, then a child cover, then the existing card montage.
- Mobile export includes the same grouping and subset navigation. Re-export `docs` after updating, then Commit and Push. No backend or credentials are added to the public viewer.

## Preservation and imports

Catalog checksums, all 4,517 raw IDs, all 4,509 accepted IDs, physical tuples, held claims, images, provenance and marketplace mappings are unchanged. `printing_id_reconciliation.csv` has one explicit unchanged row per raw printing. Membership changes are additive navigation metadata.

A first launch over an existing 1.8.4 collection writes `my_collection/backups/before-sources-1.8.5-*.zip` before setting the structure-version marker. No copy IDs, prices, wishes, image filenames or overlay tables are rewritten. Tests cover upgrade/reopen, backup/restore, covers, manual cards/printings, costs and wishes. This is test-collection verification; the user’s PC files were not available here.

The importer’s normalized physical-tuple duplicate gate now keeps an additional product binding on the existing printing instead of silently discarding that distribution. The actual released catalog is not rebuilt. Two isolated full enrichment reruns preserve raw/accepted printing-ID sets and the unified Crown Zenith count; source relationships are applied at runtime, so upstream subset codes cannot recreate separate tiles. Historical ID encodings remain frozen.

The full source-type review also corrects false positives from the old English-only Collection/BOX heuristic: explicitly identified Japanese/Korean numbered expansions remain expansions, while independently numbered regional boxes/sheets/packs are shown in Products. Their card records and physical variants remain untouched.

## Deliberately unresolved / limits

- **7 source rows** are explicitly marked for structure review in the full inventory/work queue. These are unresolved source structures, not a statement that their cards do not exist.
- `30th-c` is announced/future metadata: its relation to `30th` is not inferred from the display name. It remains separate for review.
- Existing provider-numbered records with product-like names stay independent until their structure is evidenced. Missing native release evidence is not filled from another language.
- Galar Collection jumbo pattern metadata and card-level-only product bindings retain their original evidence and unresolved fields. They were not turned into a new individual-printing audit.
- No overall database completeness or factual-accuracy percentage is claimed. This is completion of the source-structure pass over the supplied catalog.

## Install

Close DogDex. Extract the 1.8.5 update’s contents directly into `J_DogDex`, replacing the included files. Keep `my_collection` and its image/backups folders. The update contains no personal database. Restart `START_DOGDEX.bat`, then export the mobile viewer again if used. The full package is the same application for a fresh installation; it is not an additional required update.
