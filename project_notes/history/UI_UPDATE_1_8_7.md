# DogDex 1.8.7 — Navigation and combined species filters

- Main navigation moves to the top row. Language flags sit on the next row.
- The shorter search field and sort/rarity/artwork filters are grouped on the right on wide screens.
- The DogDex logo is removed from the sidebar and loading screen.
- A two-column desktop species list gives all 41 species room without reducing the existing card/detail typography. Scrolling remains available for short windows; mobile retains an expandable species picker.
- Cameos and Jumbo / special combine with the selected species. Either click order works. Select another species to refine the same category, or click the selected category again to turn it off.
- All Pokémon clears only the species selection. Category and species have separate removable filter chips. Combined choices survive reload and language changes.
- Cameo matching uses depicted species while retaining the exclusion of cards whose tracked Pokémon is already the primary subject. Jumbo filtering retains physical size/material rules.

No catalogue facts, card/printing IDs, collection records, prices or picture files are changed. Existing Sources/subset navigation and grayscale unowned / full-colour detail behavior are retained.

## Install over 1.8.6

1. Close DogDex and its console window.
2. Extract **DogDex_UI_Update_1_8_7.zip directly into J_DogDex**, replacing the included program/UI files.
3. Keep `my_collection`, `data` and existing pictures. The patch contains no collection, catalogue or image replacement.
4. Start START_DOGDEX.bat. Refresh the browser if it retained an old page.
5. Export the mobile view again, then Commit and Push in GitHub Desktop to update the public site.

The full Windows package is an alternative for a fresh installation, not an additional required update. The catalogue remains at the 1.8.6 data revision with 4,535 accepted targets.

## Checks

See `UI_VALIDATION_1_8_7.md`. This change was checked using DOM/HTTP interaction tests and static CSS review. The cloud browser could not access the local preview, so no visual Chrome/Android rendering verification is claimed.
