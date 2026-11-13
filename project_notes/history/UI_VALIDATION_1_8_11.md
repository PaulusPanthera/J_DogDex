# DogDex 1.8.11 — Validation

## Scope

Application version 1.8.11; catalogue checkpoint 1.8.9. This is a presentation
update. No catalogue rebuild, card/printing research or personal schema change.

## Functional checks

**27 distinct JavaScript checks passed**, covering:

- Compact captions: name/number grouping, symbol/set/year placement, add button
  beside classification tags, reference price in the identity row and absence of
  gallery ownership/wishlist overlays. Owned/unowned colour behaviour is kept.
- Full date precision in details; partial and approximate years; printing-specific
  product dates; unresolved product dates; regional periods spanning two years.
  The underlying full-date sort remains covered.
- The moved Wishlist toggle saves the selected printing ID, reports its selected
  state, updates when changing printings and retains keyboard focus after save.
  Toggling it leaves duplicate-copy records, costs and notes unchanged.
- Clicking the gallery set name still navigates to the canonical source.
- Public GitHub project-subpath loading, local asset URLs, absence of public edit
  controls and no public purchase-cost disclosure.
- Persistent sidebar, 41-species/nine-generation groups, combined category/species
  filters, language switching, symbols and independent Western/Asian rarity data.
- The 1.8.9 German stadium and Zygarde exclusions remain effective. Retained owned
  copies of excluded forms remain visible and correctly labelled.

The caption check was rerun after the final changes; it also exercises the
source-link click and roundtrip wishlist changes, with two retained copy records.

**Three Python publishing/preservation checks passed:** public export includes
the updated assets and Growlithe SVG; a backup roundtrip preserves every personal
record and source cover; an older backup upgrades without rekeying its records.
Checks use temporary fixture collections, not the user's PC collection.

JavaScript syntax and modified Python modules were checked. The updated catalogue
module URL is versioned to avoid an older cached module missing the new year
formatter after updating GitHub Pages.

## Data and package preservation

- All **3,742** existing catalogue/research/image files match the 1.8.10 package
  SHA-256 values exactly. Zero data files changed.
- Confirmed targets remain EN **1,707**, DE **1,451**, JA **847**, KO **530**:
  **4,535** total, with the same **41** species. These unchanged counts are a
  software regression check, not a completeness or factual-accuracy estimate.
- The full package passes the existing SQLite integrity, ZIP CRC and per-file
  manifest checks. The patch overlay reproduces the new full-package manifest.
- The patch has no `data`, `my_collection`, `docs` or `runtime` replacement files.
  No collection-ID, wishlist, cost, manual correction or image migration is added.

## Visual and asset limits

The supplied screenshots were the layout baseline. DOM checks verify structure,
interactions and selected computed styles; no new live-browser screenshot was
captured here, so they do not establish pixel-perfect desktop/mobile geometry.
Long names and tag groups wrap; cameo/research/distribution context can add lines.

The unmodified Growlithe SVG was rendered and inspected, checked for active or
external embedded content, and bundled with source attribution in
`static/brand/CREDITS.txt`. No runtime external image request is required.
The existing compact desktop brand height is preserved.

GitHub Pages is updated by exporting the mobile view and committing/pushing the
generated `docs` folder. This delivery does not publish to the user's repository.
