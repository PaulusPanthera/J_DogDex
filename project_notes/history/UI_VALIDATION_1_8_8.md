# DogDex 1.8.8 validation

## Software checks

- Full JavaScript/DOM/real HTTP regression suite: **33 tests passed, 0 failed**. Covers catalogue navigation, the editor, ownership, costs, image uploads, backup restore, market matching, language boundaries, printings, source/subset/product navigation, read-only export, generation groups and sidebar visibility.
- Three Python checks passed: v4 backup round trip, v3 upgrade without rekeying, and public export with merged catalogue overlays, duplicate-copy quantities and custom source pictures.
- The public-export check verifies that the symbol module and every symbol asset are copied byte-for-byte into the generated website. Its existing checks confirm that ownership is exported, personal costs and notes are not published, and repeated exports preserve the local collection.
- Five HTTP checks passed: index, application script, symbol module, asset provenance and a WebP symbol. The server returns the expected MIME types.
- Python and JavaScript syntax checks passed.
- The final caption/navigation check also exercises cameo-credit placement above the aligned footer.

Logs are in `tests/results_1_8_8/`.

## Preservation checks

All **3,734 pre-existing files under data/** retain their SHA-256 values, including all **3,732 data files in the original bundle manifest**. There are no added or modified catalogue/research/image files under data/. The current accepted target count remains **4,535**.

The UI update ZIP contains no `data/`, `my_collection/`, `docs/` or `runtime/` replacement. Collection IDs, owned quantities, prices paid, wishlists, manual corrections, image overrides, printings and source relationships are unaffected by patch installation.

The full bundle is checked for ZIP CRC errors and against its per-file SHA-256 manifest. Applying the patch over the original 1.8.7 bundle must reproduce the corresponding files in the full 1.8.8 bundle.

## Visual and factual limits

The supplied 1.8.7 local screenshot and the existing public GitHub page were inspected for appearance and navigation. The cloud browser cannot reach the patched local server, so **the patched desktop/mobile rendering has not had a visual browser verification**. Responsive CSS and DOM behavior were reviewed and tested; those checks do not establish pixel-level layout quality.

Symbols are presentation metadata. Their presence does not verify rarity, finish, dates, marketplace identity or regional card availability. The native JA/KO text marks are explicitly set identifiers, not substituted English symbol images. Three English source families and original Base Set intentionally have no added symbol; unresolved/custom sources also stay blank.

No individual-card factual audit was performed or claimed in this UI release.
