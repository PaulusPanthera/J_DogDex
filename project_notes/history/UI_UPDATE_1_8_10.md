# DogDex 1.8.10 — More room for the species list

Data health and the save/publication status now live in the main header. The
sidebar contains a compact DogDex title, category filters and the species list.
Its footer has been removed and its outer spacing reduced.

- All 41 species and the nine generation dividers remain in the same order.
- The desktop layout is sized to fit the complete list at the viewport height
  shown in the supplied screenshot. Shorter windows retain a scrollable list.
- Data health remains available with the sidebar hidden. The existing sidebar
  visibility preference, combined species/category filters and gallery are kept.
- The mobile picker no longer reserves space for the old health button.
- The public viewer shows its read-only/update status in the header and exposes
  no Data health or editing controls. The small sidebar title is desktop only.

## Install

1. Close DogDex.
2. Extract **DogDex_UI_Update_1_8_10.zip** directly into **J_DogDex**, replacing
   matching application files. The patch is flat; do not create another DogDex
   subfolder. It updates an existing 1.8.9 installation.
3. Start DogDex and refresh the page (Ctrl+F5 if the previous layout is cached).
4. To update GitHub Pages, export the mobile viewer from DogDex, then commit and
   push the generated `docs` changes through GitHub Desktop.

The full Windows package contains the same UI update and the existing 1.8.9 data
corrections. Updating an existing folder only needs this patch. Neither the patch
nor the full application package supplies personal collection files.

## Data preservation

No catalogue or research file is changed. The patch contains no `data`,
`my_collection`, `docs` or `runtime` directory. Ownership, duplicate physical
copies, purchase costs, wishlists, manual edits and image overrides remain in
the existing collection. No collection schema or printing-ID migration is added.

Validation and its limits are recorded in **UI_VALIDATION_1_8_10.md**.
