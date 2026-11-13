# DogDex 1.8.11 — Unified gallery tiles

Each gallery tile now contains its image and caption within one subtle panel.
The usual caption has three rows:

1. Pokémon name and collector number together; cached reference price at right
   when one is available.
2. Set symbol, clickable set name and year.
3. Rarity, finish and edition tags; add/review button at right.

Long names and tags wrap. Cameo credits, research status and unverified
distribution notes remain visible where applicable. Missing prices have no
empty placeholder. Rarity systems and physical classifications are unchanged.

The gallery has no owned-count badge or wishlist heart on the artwork. Owned
cards retain their full-colour images and use a subtle lavender tile tint and
accent border. Unowned cards retain gray previews. Quantity is available in
details and accessible ownership labels.

Wishlist is beside the Printing heading in details and applies to the selected
printing. Its selected state updates when switching printings. Saving the toggle
keeps keyboard focus on it. Full-colour detail images have no heart overlay.

The gallery shows years only; details retain the full supported date precision.
Approximate years remain marked. An unresolved product date does not borrow an
expansion year. A documented period spanning two years remains a year range.
Date sorting is unchanged and still uses the complete underlying dates.

The compact sidebar title now uses a locally bundled Growlithe illustration
instead of the abstract mark. Asset source and credits are in
`static/brand/CREDITS.txt`; public exports include it without external requests.

## Install

Close DogDex. Extract **DogDex_UI_Update_1_8_11.zip** directly into **J_DogDex**,
replacing matching application files. The patch is flat: do not create another
DogDex subfolder. Restart and press Ctrl+F5 if the previous layout is cached.
It updates the current 1.8.10 installation and includes that UI in its complete
application files.

For GitHub/mobile, export the mobile viewer from DogDex, commit the generated
`docs` changes through GitHub Desktop and push. Your existing folder only needs
this UI patch; the full Windows package contains the same update.

No catalogue, image reference, printing ID, personal collection database or
schema changes. Ownership quantities, misprints, purchase costs, wishlists,
manual corrections and picture overrides stay in the existing collection.
The patch contains no `data`, `my_collection`, `docs` or `runtime` replacements.

Validation: **UI_VALIDATION_1_8_11.md**.
