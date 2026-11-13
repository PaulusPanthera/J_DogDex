# DogDex 1.8.12 — English Unlimited-era reconciliation and German Skyridge

## Changes and bounded coverage

All **32 existing in-scope English First Edition-era card identities** were
matched to explicit edition listings. **27** lacked Unlimited printings; five
already had the expected Unlimited printing. The source-specific matrix is
`data/research/corrections_1812/ENGLISH_EDITION_MATRIX.md`, with exact names,
collector numbers, original labels, dispositions, links and cached-source hashes
in `english_edition_matrix.json`.

| Set | Missing Unlimited printings added |
| --- | ---: |
| Gym Heroes | 4 |
| Gym Challenge | 6 |
| Neo Genesis | 2 |
| Neo Discovery | 7 |
| Neo Revelation | 2 |
| Neo Destiny | 6 |
| **Total** | **27** |

The five Vulpix cases are Blaine's Vulpix (Gym Heroes 65), Brock's Vulpix
(Gym Heroes 73), Brock's Vulpix (Gym Challenge 37), Blaine's Vulpix
(Gym Challenge 66), and Vulpix (Neo Destiny 91). Both reported Snubbull cards
are included. Holofoil counterparts for the indexed Ninetales, Arcanine,
Houndour, Houndoom and Smeargle identities were checked separately by exact
number and explicit Holofoil printing label.

The five controls are the four Base Set Pokémon identities and Erika's Kindness
(Gym Challenge 103). Existing Base Set Shadowless and 1999–2000 copyright records
remain intact; no duplicate shadowless printing is created from a marketplace
alias. No new card identity or cross-language printing is generated.

The original checkpoint supplied only First Edition tuples for these 27 cards;
the runtime copied those tuples. Reviewed explicit Unlimited facts now run in
the reproducible builder. Generic Normal fields, tournament legality, rarity
and shared artwork are never used to generate these physical tuples.

All **4,545** previous printing records and IDs are unchanged. A matching
Unlimited printing previously created through the editor keeps its manual ID,
copies, costs, wishlist and image; the new default becomes an alias to it.

German Skyridge and its eight tracked identities display **15 August 2003**,
with the incompatible earlier period retained as a source conflict.

## Evidence and limits

Inventory references include the exact cached English edition pages in the matrix. Representative direct references:

- Neo Genesis: https://www.tcgplayer.com/product/89412/pokemon-neo-genesis-snubbull
  and the explicit variant display at https://arcatcg.com/cards/neo1-74 .
- Neo Revelation: https://www.tcgplayer.com/categories/trading-and-collectible-card-games/pokemon/price-guides/neo-revelation
  and https://arcatcg.com/cards/neo3-55 .

Arca's TCGplayer-derived display and TCGplayer pricing information carried by PokemonTCG API are one upstream family, not independent confirmation. The 32 cached Arca pages explicitly distinguish Unlimited from First Edition, including Holofoil labels where applicable. The two downloaded Snubbull scans were inspected and show 1st Edition stamps. Other existing images remain shared references; no new Unlimited specimen image is claimed verified. No marketplace product or price match is invented.

For German Skyridge, the Information section at
https://bulbapedia.bulbagarden.net/wiki/Skyridge_(TCG) explicitly distinguishes the
German **15 August 2003** release from the English **12 May 2003** release.
https://www.bisafans.de/sammelkarten/sets/e-card/skyridge.php still reports
**Winter 2003/2004**. The exact German date is selected for display, with state
`sourced_regional_date_conflict`. Both claims and the previous selection remain
in the Evidence tab. A contemporary manufacturer/distributor document resolving
the conflict was not located in this bounded pass. Data health's date filter
continues to include these eight entries.

Full dates remain visible in details; the gallery keeps its approved year-only
format. JA/KO, the 41-species scope, exclusions, artwork and existing image files
are unchanged. Confirmed targets change only by the 27 added English printings:
EN 1,707 → 1,734; total 4,535 → 4,562. The 32-row inventory denominator covers existing First Edition-era identities, not every possible cameo identity or paper variation. This is not a global completeness claim.

## Which files control these changes?

| Path | Purpose |
| --- | --- |
| `data/catalog.json` | Active shipped catalogue read by the local application |
| `data/catalog-collector.sqlite3` | Generated catalogue index for tools/exports |
| `data/research/corrections_1812/corrections.json` | Reviewed inputs for these corrections |
| `catalog_corrections.py` | Applies those inputs; integrated into `catalog_enrich.py` |
| `data/research/corrections_1812/` | Before/after records, source assertions, cached evidence and remaining queue |
| `my_collection/collection.sqlite3` | Ownership and all website-created manual catalogue/source/printing changes |
| `my_collection/catalog_images/` | Uploaded picture and release-cover overrides |

`data/catalog.sqlite3` is the immutable original reference checkpoint, not the
file to update for routine corrections. Use **Data health** or **Edit catalog**
for personal edits. Add a missing physical version under **Printings**; edit a
set's date under **Sets & sources**. These changes are saved in `my_collection`.

For a reproducible shipped-data correction, update the reviewed fact input and
run `python catalog_corrections.py`, or use the full offline
`python catalog_enrich.py` rebuild. Both generated catalogue files are supplied
in this patch, so normal users only need to install the update.

## Install

Close DogDex. Extract **DogDex_Data_Update_1_8_12.zip** directly into **J_DogDex**,
merge directories and replace matching supplied files. Keep the existing
`my_collection` folder. Restart DogDex and refresh (Ctrl+F5 if needed).
The full package contains the same data and the approved 1.8.11 UI.
For GitHub/mobile, export the mobile viewer, commit the generated `docs` changes
and push through GitHub Desktop.

Validation: **DATA_VALIDATION_1_8_12.md**.
