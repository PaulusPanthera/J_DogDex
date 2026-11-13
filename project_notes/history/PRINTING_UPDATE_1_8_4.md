# DogDex 1.8.4 — printing identity and language navigation

This release fixes set context during language switches, makes physical-printing editing clearer, and adds a bounded, evidenced Ascended Heroes / Erhabene Helden printing correction. It does not establish worldwide catalogue completeness.

## Install over 1.8.3

Close DogDex. Extract **DogDex_Printing_Update_1_8_4.zip** somewhere temporary. Copy the **contents of its `DogDex` folder** into the existing **`J_DogDex`** folder and replace matching files, **including the supplied `data` files**. Keep your existing **`my_collection`** folder. Start `START_DOGDEX.bat`, then press **Ctrl+F5** in the browser.

The patch and the full Windows package contain the same changes. You need only the patch for an existing 1.8.3 installation. On first start, an existing collection receives a backup under `my_collection/backups/before-printing-1.8.4-*.zip` before the version marker changes. Older schemas get a consistent SQLite backup instead. Ordinary collection backups remain version 4.

For the phone, export the mobile view again, then Commit and Push in GitHub Desktop. The site remains a read-only snapshot. No remote publication is performed by installing this update.

## What changed

- Source identity uses a canonical group independent of localized names. English `Ascended Heroes` and German `Erhabene Helden` share `western:me02.5` while keeping their existing source IDs. A unique set prefix such as `ascen` carries the source into the other ledger; compatible species, sort and artwork filters remain selected.
- Card details contain four language flags. Switching requires an exact canonical source, printed identifier, namespace, primary species and category match. The same physical printing is preferred. An unavailable printing, unavailable card or unlinked regional source produces an explicit fallback message. Unnumbered or ambiguous identities are not guessed.
- JA/KO source groups stay regional. No Asian identity or printing is generated from Western data. Manual source linking is available in advanced source details.
- Printing editor: finish and contextual foil pattern first; source/verification, unusual features and optional marketplace fields are collapsed. Source choices initially show relevant products in the same language. All sources can be opened explicitly.
- Comparison normalizes accents, spacing and known synonyms, including Energy/Energie, Friendball/Friend Ball/Freundesball and Poké Ball/Pokeball. Duplicate physical targets are rejected. Rarity and artwork are outside the physical identity key.
- Existence evidence, personal specimen inspection, exact-image verification and marketplace confirmation have separate states. An image upload cannot promote a disputed printing or freeze a superseded physical fact. Pattern/physical changes invalidate stale exact-image checks and price mappings.
- Data health → **Printing completeness** reconciles saved claims, reviewed specifications and indexed printings. Missing/duplicate/terminology/classification/localization/image/source/market checks have direct editing actions. Confirmed problems, research questions and information gaps are distinguished.

## Bounded factual correction

The scope is the ten **already indexed card identities** below in each Western language, not all cards in the expansion and not every product-exclusive stamp.

| Card number | Identity | Reviewed regular printings per language |
|---|---|---|
| 112 | Riolu | Non-holo; Energy reverse; Friend Ball reverse |
| 113 | Mega Lucario ex | Holo |
| 122 | Okidogi / Boninu | Holo; Energy reverse; Friend Ball reverse |
| 128 | Poochyena | Non-holo; Energy reverse; Dusk Ball reverse |
| 129 | Mightyena | Non-holo; Energy reverse; Dusk Ball reverse |
| 130 | Galarian Zigzagoon | Non-holo; Energy reverse; Dusk Ball reverse |
| 136 | N’s Zorua | Non-holo; Energy reverse; Poké Ball reverse |
| 137 | N’s Zoroark ex | Holo |
| 243 | Mightyena | Holo, separate Illustration Rare identity |
| 286 | N’s Zoroark ex | Holo, separate Special Illustration Rare identity |

| Measure | Before (1.8.3) | After (1.8.4) |
|---|---:|---:|
| Regular printings for these ten English identities | 10 | 22 |
| Regular printings for these ten German identities | 10 | 22 |
| Existing identity records | 3,820 | 3,820 |
| Accepted English collection targets | 1,681 | 1,693 |
| Accepted German collection targets | 1,427 | 1,439 |
| Accepted Japanese / Korean targets | 847 / 530 | 847 / 530 |
| All accepted targets | 4,485 | 4,509 |
| All raw printing records, including eight held claims | 4,493 | 4,517 |

**24 newly documented printings; no added identities, removed old IDs, automatically restored marketplace IDs, or changed JA/KO raw records.** Okidogi retains printed rarity **Rare** with a base **Holo** finish. Rare and holo do not conflict. Reverse patterns were not inferred for ex or illustration cards.

Manufacturer-branded checklist rows establish numbering, rarity and standard versus standard-holo boxes. **That checklist does not enumerate reverse patterns.** Named reverses were checked against card-specific release notes, set reporting and native German inventories. Source lineage and limitations are recorded individually; an inventory of unknown upstream lineage is not counted as independent specimen confirmation. Marketplace candidate IDs remain unconfirmed. Shared pictures remain representative artwork.

Primary release/checklist references:

- [Pokémon: Erhabene Helden overview](https://www.pokemon.com/de/news/sieh-dir-die-komplette-aufstellung-der-pokemon-sammelkartenspiel-erweiterung-mega-entwicklung-erhabene-helden-an)
- [Manufacturer-branded German checklist, mirrored PDF](https://pokezentrum.de/wp-content/uploads/Pokemon-Erhabene-Helden-Kartenliste-Checkliste-PDF-Deutsch.pdf)
- [PokeBeach set reporting](https://www.pokebeach.com/2026/01/ascended-heroes-set-guide-full-set-list-god-packs-reverse-holos-product-lineup-and-more)

Card-specific observations, native inventories, provider claim locators and source access limitations are in `data/research/printing_184/approved_variants.json`. No personally inspected specimen or exact foil photograph is asserted by this release.

## Preservation and repeatability

All 4,493 prior raw printing IDs remain present. All unreviewed entry records, the 41-species roster and the immutable original SQLite checkpoint are unchanged. Collection copies, IDs, costs, wishlists, images and manual overlays are not rewritten.

If an equivalent printing was already entered manually, the view reuses that collector ID and treats the new default ID as an alias. Existing copy rows keep their IDs and references. Already conflicting legacy duplicates are reported instead of silently deleted. Physical duplicates count once toward completion.

The original historical ID encoding is frozen separately from the normalized comparison key. Rebuilding the full enrichment pipeline offline produces the same catalogue JSON and byte-identical derived SQLite database. Run `python catalog_enrich.py` to rebuild; it does not update personal collection data. `python printing_audit.py` regenerates the stock reconciliation report and queue.

## Remaining limits and continuation

The saved-claim scan covers 3,820 indexed identities across all 41 roster species and four ledgers. It reports **514 unmatched active source claims** and **771 review findings**. These are distinct claims/findings, not 514 proven missing cards. The 9,018 image/market information findings are not physical-printing errors. Zero confirmed structural/specification findings after the correction does **not** imply factual accuracy of the entire catalogue.

Only the 20 reviewed identity/language rows have an evidenced expected regular-printing denominator (44 printings). Other sources have no asserted complete physical-variant total. Earlier historical evidence and original provider assertions remain available. JA/KO discovery, new product families, exact image matching and outstanding marketplace mappings are outside this bounded pass.

Continue from `data/research/printing_184/work_queue.json`, using `reconciliation.json` for every recorded identity, its indexed physical variants, expected specification where reviewed, historical claims and disposition. Keep the earlier research archive. The new evidence files are inside the application and this update.

Software checks, upgrade checks and visual layout inspection are documented separately in `VALIDATION.md`. They do not establish a global catalogue accuracy percentage.
