# DogDex 1.8.8 — set symbols and clearer navigation

Application release: 1.8.8. Catalogue checkpoint: 1.8.6. Catalogue identities and collection targets are unchanged.

## Changes

- Gallery captions show the set symbol between the Pokémon name and collector number. The set name remains a separate clickable label.
- The 41 species are grouped into nine generations. Quiet region labels and thin separators keep adjacent generations from sharing a row.
- The panel button at the top left hides or restores the Pokémon sidebar. This preference is remembered independently from filters. Hiding it does not rebuild the cards, reset selection, or replace loaded images.
- Full set names can use two lines. Dates, prices and add buttons align at the bottom of each gallery row.
- Keyboard users have a skip link to the gallery. The sidebar toggle exposes its current state to assistive technology and retains focus.
- Optional browser-preference storage errors no longer prevent the catalogue from opening or being browsed.
- The existing grayscale unowned previews, full-colour details, prices, ownership display, English-coded Western rarities, independent Asian rarities, source relationships and combined Cameo/Jumbo filters remain in place.

## Symbol handling

The bundle includes 139 compact, locally stored symbol images, used by 152 English release IDs and 141 German release IDs. Assets are selected from an exact set identity or exact English reference name within an already established Western set family. German titles do not have to match an English filename. Internal subsets use their canonical expansion symbol without changing their physical identities or numbering.

The original Base Set deliberately has no symbol. My First Battle, MEP Black Star Promos and the Art Academy source remain without a guessed icon because the selected reference indexes did not supply an exact asset. Custom or unresolved sources also stay blank unless their canonical set is explicitly established.

Japanese and Korean do not borrow English expansion symbols. For 85 Japanese and 59 Korean modern release IDs, the gallery shows the existing regional set identifier as a compact text mark, explicitly labelled as an identifier. Other regional sets currently have no added mark. This presentation mapping is not evidence of a language release or physical printing.

Reference credits and per-asset URLs, hashes and source families are in `static/set-symbols/provenance.json`:

- [Pokemon Symbols set index](https://pokesymbols.com/tcg/sets) and its [credits](https://pokesymbols.com/about).
- [PokemonTCG reference data](https://github.com/PokemonTCG/pokemon-tcg-data), used where it supplied the exact symbol asset.

All symbols load from DogDex itself. No external symbol service is called while browsing.

## Installation

1. Close DogDex.
2. Extract **DogDex_UI_Update_1_8_8.zip** directly into the existing **J_DogDex** folder, accepting replacement of its included application files.
3. Start DogDex. If an old browser tab remains open, refresh it once.
4. Export the mobile view from Data health, then commit and push the changed `docs` folder with GitHub Desktop.

The patch contains no `data`, `my_collection`, `docs` or `runtime` replacements. Install only the patch for an existing setup. The full Windows package is the corresponding fresh-install alternative.

The public page inspected during this pass still displayed the older sidebar/logo layout and its 30 October snapshot with 132 collected targets. The local screenshot supplied for this change displayed 147 collected targets. A fresh export is required to publish the current local collection and layout.

## Review scope

This is a presentation and navigation update. It does not certify the factual accuracy of card metadata or alter printing identities. New symbols are not additional collectible targets.

The updated local UI could not be reached by the separate cloud browser. Interaction tests, static HTTP checks, export checks and CSS review were completed; a visual browser check of the patched desktop/mobile rendering remains a limitation.
