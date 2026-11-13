# DogDex 1.8.12 — Validation

## Exact bounded delta

- **27** accepted English Unlimited physical printings across Gym Heroes/Challenge and Neo Genesis/Discovery/Revelation/Destiny. They include both Snubbull reports and all five Vulpix cases. No new card identity is created.
- **32** existing First Edition-era identities reconciled against explicit edition/finish labels: 27 newly documented Unlimited tuples and five already indexed controls. Source-specific denominator and original labels are in the persistent edition matrix. This does not claim every possible cameo identity or paper variant is known.
- The German Skyridge release and its eight tracked identities select
  `2003-08-15`, with `sourced_regional_date_conflict` and retained historical
  Bisafans evidence. This is one unresolved source conflict affecting eight
  existing entries, not eight independently confirmed date facts.
- All **4,545** previous physical-printing records and IDs are unchanged.
- No unrelated card record changes. All **1,861** Japanese/Korean entries are
  identical to the previous catalogue. The 41-species roster is identical.
- Original `data/catalog.sqlite3` and all **3,540** cached catalogue images are
  unchanged. Existing image references are not promoted to exact Unlimited
  specimen verification.

Complete before/after records, new IDs and assertions are saved under
`data/research/corrections_1812/`. The date-resolution and optional exact-image
blockers are in its `work_queue.json`.

## Software and preservation

**15 JavaScript checks passed.** These cover the new printings in gallery and
details, German Skyridge's year-only gallery and full detail date, date-conflict
visibility in Data health, its historical Evidence tab, existing captions,
printing-specific Wishlist, date sorting, marketplace selection and 1.8.9 scope
corrections. Browsing the tested corrections makes no mutation request.

**Eight Python checks passed.** Four correction checks cover exact/idempotent
changes, selected/conflicting date evidence, the complete 32-row cached edition matrix, and a saved-collection upgrade with manually created Unlimited versions for Snubbull, Vulpix and Holo Ninetales. Four preservation/public-export checks
also pass, including the earlier German stadium and Zygarde corrections.

The upgrade fixture contains three manually created Unlimited identities across non-holo and holo finishes, duplicate physical copies, purchase costs, notes,
misprint notes, wishlists, manual identity edits and per-printing pictures. State
and image bytes remain identical after replacing the catalogue. Matching new
default IDs alias to matching pre-existing manual IDs without double-counting.
A backup/restore roundtrip retains those records as well. These checks use
temporary collections, not the user's actual PC collection.

Syntax checks passed for changed Python and JavaScript modules. The approved
1.8.11 layout, Growlithe logo, flags and rarity systems are retained.

## Reproducibility and package

The full offline `catalog_enrich.py` pipeline produces the same corrected
catalogue records as the targeted application. A repeat full rebuild produces
byte-identical JSON and derived SQLite files:

- JSON SHA-256: `11633264b9a74df87e99a938811790114f6834173cde51c020872ddcf5b34c32`
- SQLite SHA-256: `96e661dc8e6942c53173d5b886eb4e0ee5e927db172cb4baf5117f48875d8b60`

The full bundle passes the existing SQLite integrity, foreign-key, ZIP CRC and
per-file manifest checks. Applying the flat patch to the preceding 1.8.11
package reproduces the new full-package manifest. No `my_collection`, generated
`docs` or runtime replacement is included in the patch.

## Factual limits

The additions are inventory-supported physical-printing records. Provider and
downstream mirror assertions are not counted as independent confirmations.
The two inspected Snubbull scans show 1st Edition. Existing images for all 27 additions remain
unverified shared references. German Skyridge retains the incompatible native
winter-period claim; no contemporary manufacturer evidence resolving it was
located. Software checks and the 27 added targets are not an overall dataset
accuracy or completeness estimate. No new pixel-geometry browser audit was
performed for this data-focused release.
