# DogDex 1.8.16 - Bulk artwork and rarity editing

Data health > Cards > Select cards opens full-colour thumbnail checkboxes. Select individual cards or optionally all filtered matches, choose artwork or card rarity, review the exact changes and apply atomically. Only unclassified cards change by default. Undo restores the edited fields and protects newer classifications. Rarity remains ledger-specific; identity/existence, printing variants, ownership, paid prices, pictures and marketplace links are preserved. See BULK_HEALTH_1_8_16.md and UPDATE_1_8_16.txt.

# 1.8.15 — Clean gallery prices and printing order

Removed the Guide suffix beside gallery prices; scope remains in hover/accessibility text and the card-detail guide. Editions of the same card use their known sequence instead of alphabetical labels, with the later English Base Set copyright variant last. Newest-first sorting reverses that sequence; details and editor choices remain oldest first. No variant dates are fabricated. Values, matching, catalogue records and personal data are unchanged. Re-export/push the mobile viewer.

# 1.8.14 — Reusable Cardmarket products and filtered offers

The finder starts from a saved product ID/listing, promotes confirmed related matches, and saves selected compatible printing mappings in one atomic confirmation. V1 and English Shadowless V2 stay separate. Existing conflicting products and related manual guide-series choices are preserved. Open offers applies language, First Edition, reverse-holo and a saved minimum-condition setting. Gallery and detail prices are explicitly product-wide Guides; no filtered asking price is fabricated. Catalogue data and all owned records remain unchanged. Re-export/push the mobile viewer. See CARDMARKET_UPDATE_1_8_14.md and CARDMARKET_VALIDATION_1_8_14.md.

# 1.8.13 — Data health picture coverage

Corrected a false Missing pictures flag and blank Data health thumbnail when a card has individual printing uploads but no shared reference. Coverage checks each printing; a missing sibling still needs a picture. Entry thumbnails can use a printing image without assigning it to other printings or marking it verified. The Picture tab labels its empty shared slot explicitly. Gallery/detail associations, catalogue data and all personal records are unchanged. Re-export/push to publish the updated mobile viewer. See UI_UPDATE_1_8_13.md and UI_VALIDATION_1_8_13.md.

# 1.8.12 — English Unlimited-era reconciliation and German Skyridge

Reconciled all 32 existing English First Edition-era identities against explicit edition listings. Added 27 missing Unlimited printings (Gym Heroes 4, Gym Challenge 6, Neo Genesis 2, Neo Discovery 7, Neo Revelation 2, Neo Destiny 6), including all five missing Vulpix cases. Five previously present Unlimited controls, Base Set Shadowless/copyright distinctions and all old physical IDs are retained. German Skyridge selects 15 August 2003, retaining Bisafans’ conflicting winter period in Data health. Matching manual printings keep their IDs, copies, costs and images. JA/KO and the 1.8.11 UI remain unchanged. Details: DATA_CORRECTIONS_1_8_12.md and DATA_VALIDATION_1_8_12.md.

# 1.8.11 — Unified gallery tiles and clean artwork

Three caption rows group identity/price, set/year and rarity/finish/add. Full dates remain in details; chronology uses the original complete dates. Gallery ownership and wishlist overlays are removed. Owned tiles have a subtle lavender tint and accent border; Wishlist moves beside Printing in details. The sidebar title uses a bundled Growlithe illustration. Catalogue and personal collection data are unchanged. Re-export and push the mobile viewer to update GitHub Pages. See UI_UPDATE_1_8_11.md and UI_VALIDATION_1_8_11.md.

# 1.8.10 — Species sidebar space

Moved Data health and save/publication status into the main header. Restored a compact DogDex title at the top of the desktop sidebar and reclaimed its footer space for species. Health remains accessible with the sidebar hidden; the mobile picker retains its full width. Catalogue, collection IDs and personal data are unchanged. See UI_UPDATE_1_8_10.md and UI_VALIDATION_1_8_10.md.

# 1.8.9 — native German cameo and Zygarde forme scope

Completed the existing German Illumina City 077 entry with a native picture and two documented physical printings. EN/DE Mega Zygarde ex 104 is excluded from completion; 120 remains collectible as a 10% cameo. Existing physical IDs, ownership and user overrides are preserved. The previous UI update is included.

# 1.8.8 — set symbols and navigation refinement

Added local gallery set symbols, subtle generation groups and a persistent sidebar toggle. Gallery captions wrap long set names and align their footer controls. Optional preference-storage failures no longer stop browsing. Catalogue and collection data are unchanged. See UI_UPDATE_1_8_8.md and UI_VALIDATION_1_8_8.md.

# 1.8.7 — Compact navigation and independent browse filters

- Main navigation in the first row, flags below, shorter search with filters aligned right.
- Removed sidebar/loading logo. Two-column desktop species list; mobile expandable picker.
- Cameos/Jumbo retain selected species and species retain selected category; independent clear chips and persisted combinations.
- No catalog or collection-data change. Re-export and push to refresh GitHub Pages.
- Details: UI_UPDATE_1_8_7.md; validation: UI_VALIDATION_1_8_7.md.

# 1.8.6 — Reviewed physical-printing corrections

- 26 new stable printing IDs, zero removed IDs and no new card identities. White Flare EN 26 / DE 25.
- English logo Zoroark, Melmetal-deck Zacian, Cosmos Zacian 045, Mirage/stamped Houndoom and Cosmos Parallel Fidough; German Play!-stamped Hisuian Arcanine.
- Existing Arcanine specials and Zacian Non-Holo retained without duplication; product-specific dates/provenance corrected.
- EN White Flare July 18 manufacturer date; DE Obsidianflammen name and old search alias.
- Four native German physical variants plus one English product date remain explicit unresolved claims.
- JA/KO card records, Sources grouping, approved UI and original physical keys unchanged. Matching prior manual printings retain their IDs, costs, copies, wishes and images. First-open upgrade backup.
- Exact changes/evidence/queue: PRINTING_CORRECTIONS_1_8_6.md and data/research/printing_186. Tests: PRINTING_VALIDATION_1_8_6.md.

# 1.8.5 — Expansions, subsets and products

- Unified Crown Zenith/Galarian Gallery (22), Shining Fates/Shiny Vault (15), four Trainer Galleries and Hidden Fates. Empty Celebrations Classic Collection and older numbering sections are metadata, not invented cards.
- Products tab shows existing distributed printings without extra collectible progress. The combined ETB Plus/UPC context resolves into its three distinct products.
- Set-name navigation, aliases, same-section language switching, source parent editing and exhaustive runtime CSV export.
- All catalog bytes and printing IDs unchanged: 4,517 raw; 4,509 accepted. First launch saves a source-upgrade backup over an existing collection.
- Full inventory of 994 original sources plus 21 navigation-only records; all 15 requested product contexts and comparable contexts mapped.
- See SOURCES_UPDATE_1_8_5.md, SOURCE_CODE_LOCATIONS_1_8_5.md and SOURCE_VALIDATION_1_8_5.md.

# DogDex 1.8.4

- Canonical source identity preserves EN/DE set context and unique set-prefix searches. In-detail flags resolve exact card/printing counterparts; missing or ambiguous matches show an explicit fallback. Asian groups remain regional.
- Finish and contextual pattern controls lead the printing editor. Advanced edition/size/stamp and marketplace fields remain available; sources default to relevant products in the same language.
- Controlled physical comparison prevents synonym duplicates. Existing manually entered equivalents retain their IDs and collection references; historical ID encoding remains stable on rebuild.
- Existence, personal inspection, exact-image verification and market matching are independent. Uploading a picture does not promote a held claim or freeze older printing facts. Physical changes clear stale price matches/image verification.
- 24 evidenced regular-printing additions across the ten existing ASC identities in each EN/DE ledger: 10 → 22 printings per language. Okidogi remains Rare with a base Holo finish. No reverse variants inferred for ex/illustration cards.
- Data health printing checks and persistent reconciliation distinguish verified missing variants, raw unmatched claims and information gaps. No global completeness/accuracy percentage is asserted.
- Automatic upgrade backup. Existing copy IDs, costs, wishes, manual edits and image files remain untouched. No new collection schema is required. JA/KO raw facts are unchanged.
- The full offline rebuild reproduces catalogue JSON and derived SQLite exactly. Read `PRINTING_UPDATE_1_8_4.md` for evidence, denominators, installation and continuation.

The **1.8.4 patch includes catalogue data** and requires 1.8.3. Close DogDex, copy its `DogDex` contents into `J_DogDex`, replace matching files including supplied `data` files, and keep `my_collection`. Restart, Ctrl+F5, then re-export/push the mobile view. The full package has the same changes.

# DogDex 1.8.3

- **Find Cardmarket product** is available on card details and accepted printings
  in Data health. It recovers existing provider/evidence references before searching
  a daily cached official product catalogue. No TCGGO integration or key is needed.
- Search by name, product ID or Cardmarket URL. Numeric `idProduct` links can select
  a candidate directly; pretty slugs never turn a collector number into an ID.
  Existing references are suggestions, including compatible EN/DE counterpart
  references. They establish neither language availability nor an exact variant.
- Selection opens a focused confirmation step. Open the product, check its card,
  set, number, language and physical printing, then confirm the price series.
  Ordinary holo uses regular pricing; reverse holo can use its separate series.
  A successful save refreshes the cached guide and returns to the same printing.
  A failed download keeps existing evidence/prices and any successfully saved link.
- The official singles feed lacks complete set/number/language/variant details.
  Broad name matches are labelled unchecked; online code-card products are excluded.
  Uncertain products remain unconfirmed. Direct/manual mappings remain available.
- Confirmations retain their method, date and catalogue provenance in the local
  printing override/audit log. Copies, costs, wishlist and picture edits survive
  the change and v4 backup/restore. No collection-schema migration is required.
- Larger gallery pictures and captions; set names have their own line. Price pills
  show one amount with source/date in a tooltip. No unpriced dash or “CM trend”
  caption. Trend is preferred, then 30-day, 7-day, and explicitly labelled Low.
- Detail headers now hold language/native name, Pokédex number and rarity/artwork.
  Printing, owned copies and market reference have separate regions below. Owned
  purchase records lead the view; Add copy remains a compact action.
- EN/DE rarity display uses English terms while retaining original catalogue
  wording. Japanese/Korean codes and systems remain separate. Full Art and foil
  finish remain distinct from rarity. No factual rarity reclassification is made.
- The read-only mobile export shares the UI and confirmed prices, with no finder,
  editing API, catalogue cache, collection notes or purchase costs exposed.
- All three catalogue checkpoints, all IDs and the factual 1.7 dataset are unchanged.

Close DogDex and copy the contents of the patch's `DogDex` folder into the existing
`J_DogDex`. Restart, Ctrl+F5, then export/push the mobile snapshot again. The patch
is cumulative from 1.8, 1.8.1 or 1.8.2. The full package contains the same update.

# DogDex 1.8.2

- Owned copies lead the detail view: condition, date and price paid have a dedicated
  panel; adding another copy is a small action in its heading.
- Gallery captions include rarity and finish badges plus one guide price. Trend
  is preferred, then 30-day average, 7-day average, and explicitly labelled Low.
  No matched value is shown as a dash. Prices remain per confirmed printing.
- The Cardmarket guide is a collapsed one-row disclosure. Secondary figures and
  source date remain available when expanded; redundant prose has been removed.
- Blue non-holo, violet holo and teal reverse-holo labels remain separate from
  rarity. Western circle/diamond/star symbols use the official rarity scheme;
  older special rarities and Japanese/Korean letter codes keep their own labels.
  Modern Ultra Rare's two silver stars are not applied to older Ultra Rare cards.
- Full Art is visible in card details without replacing printed rarity.
- Gray unowned images, full-colour details, picture editing, wishes, manual
  marketplace mappings and existing copies/costs keep their current behavior.
- The editor distinguishes a listing URL (link) from a product ID (guide prices).
- Mobile exports include the same UI and the new rarity presentation module.
- Catalog data, collection schemas and price-provider integrations are unchanged.

Small update: close DogDex and copy the contents of the ZIP's DogDex directory
into the existing J_DogDex directory, replacing matching application files. Start
DogDex again and use Ctrl+F5 in the browser. Re-export and push the mobile view.
The patch contains no data, runtime, research archive or my_collection directory.

Official rarity reference:
https://www.pokemon.com/uk/news/pokemon-tcg-scarlet-and-violet-revamps-pokemon-tcg-card-aesthetic

# DogDex 1.8.1

- Compact three-row card captions: name and collector number, source/date,
  complete finish/edition badges. Long labels wrap; source/date tooltips retain
  the full text. Each printing remains an individual tile.
- Card details group printing selection, owned copies, purchase records and
  marketplace/editor actions. Selected versions have an explicit accessible
  state; printing counts show their own copies. Held claims remain visible
  without being turned into new accepted collection targets.
- Detail pictures load eagerly at high priority. The modal uses a dimmed
  backdrop without the previous full-screen blur. Unowned previews remain gray
  and detail pictures remain in full colour.
- Cached date formatters and a per-catalog search index avoid repeated work.
  Cache rebuilds accompany catalog/manual edits, preserving search semantics.
- The factual catalog and every original ID remain byte-for-byte unchanged.
  The mobile export shares the updated UI. A small 1.8-to-1.8.1 patch is also
  supplied; close the app before replacing files and refresh the browser cache.

# DogDex 1.8.0

- Public read-only mobile snapshot exported to `docs`, with GitHub Desktop setup
  instructions. Existing `J_DogDex` folder layout is supported; generated website
  files are the only application assets selected by the supplied `.gitignore`.
- Source tiles grouped by TCG series/era with generation labels. Sort and label
  now use the same source date. Partial-date ties use existing expansion sequence
  hints. German provider reference dates remain explicitly unconfirmed.
- Manual source covers, montage fallback and source editor order override. Covers
  are preserved by automatic schema upgrade, v4 backups and mobile exports.
- EN/DE Cardmarket search fallbacks include set and number, distinguish printed
  form names, and preserve direct links/manual overrides. Searches are labelled
  as searches. No quarantined product IDs are silently promoted.
- Optional official daily EUR price guide cache. Prices display only for explicit
  per-printing product/price-series confirmations. This release does not claim
  language/condition-specific pricing or add automatic collection valuations.
- The 1.7 factual catalog, gallery and every identity/printing ID are unchanged.
  Previous research archives and queues remain valid. No new completeness claim.

Setup, limitations and upgrade instructions: MOBILE_README.md.

# DogDex 1.7.0

Focused Japanese/Korean identity and physical-printing reconciliation. English/German catalog entries and releases are unchanged from 1.6; every earlier identity and printing ID is preserved.

- Added 19 documented identities and 88 visible provisional Japanese inventory/product/cameo claims. Added 84 source-supported physical targets, with no generic Normal or cross-language variant generation.
- Corrected or qualified 42 existing records: Japanese Mega labels, Korean promo source groups, unsupported promo-series dates, scope and exact physical details. Four existing Japanese identities now have a documented status after native comparison.
- Kept Korean manufacturer catalog rarity tiers separate from printed symbols. Refined eight Korean Poké Ball foil records and two promo stamp fields on their existing IDs.
- Reconciled the retrieved native searches for all 41 species in both languages, a Japanese authored inventory, 128 regional product pages and 22 recovered cameo claims. Historical assertions and current selections remain separate in the editor.
- Research entries remain visible without invented printings. Existing primary canine hosts are not duplicated as cameo-only cards. Unknown rarity is supported on a documented physical target.

Read DATA_AUDIT_1_7.md and SPECIES_MATRIX_1_7.md. The evidence ledger and queue are in data/research/asia_17. This is a bounded pass; historical Japanese numbering and unresolved regional variants still need evidence. The counts do not establish worldwide completeness.

# DogDex 1.6.0

The EN/DE pass reconciles all 41 species against broader primary, product and cameo inventories, with native German checks added. It admits 51 identities (16 documented and 35 provisional), restores three earlier claim IDs with their evidence, adds 85 supported physical targets and refines 50 existing foil-pattern records in place. Two existing rarity errors and an omitted LV.X name marker are corrected; seven promo-series date inheritances are cleaned. Five disputed physical claims leave confirmed totals without losing collection data.

Incomplete cards are visible research entries. Identity status and physical confirmation are separate from missing metadata. An Evidence tab exposes original and superseded claims, source links and conflicts. 1,334 missing artwork fields receive exact-image assessments; 54 old-record gaps remain. All 923 held marketplace IDs remain unresolved after primary-catalog re-screening. No global completeness or accuracy percentage is claimed.

All existing entry/printing IDs, owned copies, costs, wishes, corrections and picture overrides are preserved. JA/KO canonical records and the 41-species roster are unchanged. The approved dark UI, gray unowned grid and full-colour details remain. See DATA_AUDIT_1_6.md, SPECIES_MATRIX_1_6.md and data/research/completion_16/.

Previous release history follows.

# DogDex 1.5.0

Twelve existing records corrected or withdrawn against the frozen 1.4 baseline: two German rarity fields, seven English dates or unsupported date precisions, and three withdrawn unsupported German alternate identities. Adds four native numbered German EX Trainer Kit 2 cards and one explicitly documented English Delinquent 98a Sheen Holo printing. Fills 63 missing artwork fields after direct image review.

A native Carddex batch compares 358 existing German identities across 64 accessible set inventories; 303 rarity categories can be mapped without collapsing native terminology. A consolidated field ledger separates prior review claims, provider assertions, inferences and current checks. Four of nine finish alerts are documented product exceptions; five remain unresolved. Thirteen German primary candidates remain in the named species reference inventory.

All old entry/printing IDs remain addressable, including the three withdrawn regional claims. Owned copies, costs, wishlists, corrections and picture overrides survive upgrade and backup restoration. The 41-species roster, JA/KO entries and approved UI are unchanged. Software checks are separate from factual validation. See DATA_AUDIT_1_5.md.

Previous release history follows.

# DogDex 1.4.0

Corrects 149 existing EN/DE records: 52 rarity fields, 100 dates or unsupported date precision values, and two DP12 titles. Adds ten evidenced German identities and 31 physical printings, including native cameo cards and alternate-numbered Riolu. See DATA_AUDIT_1_4.md for source denominators, the 80-record diagnostic sample and unresolved cases.

The build now separates inferred artwork labels and unverified marketplace IDs from verified facts. Date cohorts use explicit regional evidence; uncertain German release periods are shown without invented days. Existing card/printing IDs, personal collection overlays, special variants, JA/KO records and the approved UI are retained.

Validation: 61 Python tests, 12 JavaScript/DOM tests, stable-ID/collection upgrade checks, two identical offline rebuilds, SQLite integrity and package manifest/CRC checks. Native Windows execution remains untested here.

Previous release history follows.

# DogDex 1.3.2

The English/German database audit adds **43 physical printing targets** and corrects existing facts without changing collection IDs.

- **34 English World Championships replicas** added after reviewing 80 retail deck lists. Printed player signatures, special backs, source decks and actual retail dates are distinct. Detail explains that these official replicas are not tournament legal. Search now finds printing source names such as World Championships.
- **19 non-holo errors corrected to holo**, with expansion-logo stamps restored on six prerelease targets. Three English STAFF variants, Rockruff Sequin Holo, two Pixel Cosmos variants, Riolu Pokémon Center stamp and two oversized SM230 cards have their own slots. Supported non-holo exceptions remain.
- **26 card dates corrected**, including 16 German records. German month precision is preserved where a specific launch day is uncertain. German Riolu MEP010 is 10 October 2025; English remains 26 September. Lucario SWSH186 uses the early prerelease date while its later STAFF copy keeps 2023.
- **Seven native German pictures added** and three missing German Full Art classifications verified. Zamazenta GG54 now has direct German visual evidence.
- **41 faulty marketplace product references removed**, with a name check to prevent unrelated card names being attached again. World Championships searches retain their specific product identity; reviewed direct listings are used where available.

| Ledger | Records | Printings | Awaiting printing | Missing pictures |
|---|---:|---:|---:|---:|
| English | 997 | 1,588 | 1 | 13 |
| German | 897 | 1,407 | 1 | 58 |
| Japanese | 965 | 793 | 244 | 36 |
| Korean | 789 | 500 | 305 | 5 |

All **3,648 previous identities and 4,245 printing IDs survive**. Japanese/Korean card records are unchanged. The 41-species roster, family exclusions and approved dark UI are retained. Unowned previews stay gray; opened cards are full colour. Coverage remains incomplete: 112 pictures and 124 dates are missing, and 23 card dates remain provisional.

Upgrade: export a backup, close the old app, extract this bundle into a separate folder, and copy the old **my_collection** folder beside the new **app.py** before launching **START_DOGDEX.bat**. Keep the old folder until checked. Your collection has its own storage; do not replace it with catalog files.

Research: `data/research/REGIONAL_PRODUCTS_AUDIT.md`. Validation: `VALIDATION.md`. Native Windows launcher execution is still unverified in this Linux environment.

# DogDex 1.3.1

Unowned cards are gray in the overview, including on hover. Opening a card shows its reference in full colour. Owned previews remain in colour with their count badge and border. The approved sidebar layout and other UI behavior are retained.

This database pass concentrates on English and German:

- **10 missing card identities and 12 physical printings added.** Seven identities are German, three English. German additions include Fynx XY02, Fennexis-EX XY19, Zoroark BW19, Alola-Vulpix 21a, Zoroark-GX 77a, Lucario 3/11 and Lucario MEP095. English additions include Electrike 2/12, Riolu 6/11 and Lucario MEP095. English Zoroark BW19 gains its separate oversized lenticular card.
- **A German printing hold resolved.** A native Zorua 9/12 scan plus the contemporary German/Austrian campaign announcement confirm the McDonald's card. Its actual German date is **9 March 2012**, despite the international set being called McDonald's Collection 2011.
- **37 missed Full Art classifications corrected**, including Delphox/Fennexis V 173, Alolan Vulpix V 173 and several Galarian Gallery/alternate-art cards. Eighteen regular EX/GX/BREAK layouts are explicitly Standard. The new German Zoroark-GX 77a is also Full Art. Printed rarity stays independent from artwork.
- **Two German rarity corrections:** Wizards Arkani 6 and Farbeagle 32 have printed Black Star Promo symbols and now appear under Promo instead of Common.
- **12 existing card dates corrected.** Regional product dates replace inappropriate promo-series dates; the English DP Trainer Kit source and inherited Lucario date are corrected together. German XY19 uses September 2014, and MEP095 retains German October month precision instead of copying the US September day.
- **80 regional reference pictures cached:** 72 fill existing German gaps and eight illustrate new identities. Pictures were checked against native language and collector number; foreign-language candidates remain held. Exact-printing picture replacement is retained.
- All **3,638 previous active record IDs and 4,233 printing IDs survive**. Refining the existing BW19 regular holo to Cosmos retains its ID. Ownership, prices, wishlists and picture overrides remain attached to their original targets. Japanese/Korean records are unchanged; Eevee/Shinx families remain excluded.

| Ledger | Records | Printings | Awaiting printing | Missing pictures |
|---|---:|---:|---:|---:|
| English | 997 | 1,546 | 1 | 13 |
| German | 897 | 1,406 | 1 | 65 |
| Japanese | 965 | 793 | 244 | 36 |
| Korean | 789 | 500 | 305 | 5 |

The two newly cataloged English trainer-kit cards still lack exact reference pictures. Coverage is not exhaustive: 119 pictures are missing, 124 records have no date and 38 retain reference-only card dates. There are 340 Full Art identities, 93 cameo-only records and 25 jumbo choices. The discovery scan covers 957 numbered native checklist rows across all 41 tracked species; individual regional editions and physical variants still require separate evidence.

Upgrade: export a backup, close the old app, extract this bundle into a separate folder, and copy the old **my_collection** folder beside the new **app.py** before launching **START_DOGDEX.bat**. Keep the old folder until checked. Do not overwrite or discard your collection folder.

Evidence and limits: `data/research/EXPANDED_RESEARCH_REPORT.md`. Checks: `VALIDATION.md`. Native Windows launcher execution remains unverified in this Linux environment.
