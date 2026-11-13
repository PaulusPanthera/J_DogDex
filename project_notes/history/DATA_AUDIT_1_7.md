# DogDex 1.7 — Japanese/Korean focused reconciliation

Cutoff: 2026-10-29. English/German entries and releases are byte-for-byte equivalent JSON values to 1.6. The 41-species roster, all earlier entry/printing IDs and the approved UI remain in place.

## Result

| Measure | Japanese before → after | Korean before → after |
|---|---:|---:|
| Visible catalog identities/claims | 965 → 1059 | 789 → 802 |
| Documented identities | 950 → 960 | 789 → 802 |
| Provisional identities | 15 → 98 | 0 → 0 |
| Accepted physical printings | 793 → 847 | 500 → 530 |
| Identities without accepted printings | 244 → 290 | 305 → 288 |

Added 107 identities: 19 documented (6 JA, 13 KO) and 88 provisional Japanese claims. Added 84 supported physical targets. These counts are change measures, not completeness or accuracy estimates. Unknown fields do not block inclusion; provisional identities and speculative variants do not count as confirmed targets.

Examples: Korean S12a art cards 192, 201, 208, 225, 226, 232 and 234; Korean MEZ numbered deck identities 006, 007 and 020; Japanese PCG-P Lucario promos; historical Japanese provider claims and cameo hosts. Missing foil details on a documented identity remain explicit, with no invented Normal target.

## Corrected recurring causes

- Japanese Mega marks: replaced importer literal mega text with the manufacturer’s exact Japanese alternate label: **11** change events.
- Korean promo records: corrected misleading single-product/XY group titles while keeping source IDs: **9** change events.
- Removed unsupported individual-card dates inherited from promo-series launches: **13** change events.
- Protected previously undated promos against inheriting a source-series date: **96** change events.
- Selected product-specific dates with source precision and an earliest-documented-product qualification: **97** change events.
- Qualified generic Korean mirror records as Poké Ball foil from exact native specimens, keeping IDs: **8** change events.
- Refined inherited blank stamp fields from exact product evidence without inventing another unstamped issue: **2** change events.
- Promoted existing Japanese review identities after exact native comparison: **4** change events.
- Excluded the inherited Zygarde GX claim from canine collection targets; its old identifier remains unverified: **1** change events.
- Selected individual dates on already existing physical IDs: **2** change events.
- Kept appearances on tracked primary hosts without separate cameo-only identities: **1** change events.

42 distinct existing records received a corrected label/date/scope or a more specific physical qualifier. Product-date additions to previously empty fields are reported separately. No generic Normal, rarity code, shared artwork or Japanese release creates a Korean physical variant. Korean S12a catalog tiers are retained as claims where specimens show no printed symbol.

## Retrieved reference inventories

| Inventory family | Rows | Dispositions |
|---|---:|---|
| official_ja | 1080 | matched_identity: 984, excluded_outside_roster: 66, excluded_form: 30 |
| official_ko | 944 | matched_identity: 834, excluded_outside_roster: 71, newly_documented: 13, excluded_form: 26 |
| tcgdex_authored_asia | 562 | matched_authored_identity: 474, excluded_form: 12, provisional_inventory_identity: 65, excluded_other_language: 11 |
| pokumon_regional_product | 128 | newly_documented_printing: 78, provisional_printing_claim: 31, matched_default_stamp_refined: 2, excluded_form: 5, matched_identity_family_multiple_artworks: 12 |
| pokecameos_recovered | 22 | provisional_cameo_identity: 14, matched_primary_card_no_separate_cameo: 1, provisional_primary_host_identity: 1, matched_cameo_identity: 5, excluded_other_language: 1 |

184 paginated native requests cover all 41 Japanese and all 41 Korean species queries, plus Japanese positive mirror filters. The 2,024 native records include variants and false keyword hits; they are not 2,024 distinct card identities. All rows have a recorded disposition. The Asia repository includes 11 Chinese rows; these were excluded, not translated into Japanese releases. TCGdex repository and TCGdex APIs are one upstream family.

Native manufacturer searches are strong for their indexed eras. They do not establish pre-DP Japanese coverage or every regional promo. Pokumon contributes 98 JA and 30 KO product pages; PokéCameos contributes 22 recovered appearance rows, including one explicitly Chinese-only contradiction. These inventories are useful denominators for this pass, not worldwide totals.

## Evidence and remaining work

The editor exposes new native comparisons, product claims and recovered source assertions. 2770 evidence items were newly indexed/compared during this pass; 1776 are explicitly recovered prior evidence, not fresh independent confirmations. Original source labels, variant assertions, source families, URLs and available retrieval metadata remain separate from selected values. Old raw bodies that were never supplied cannot be recreated from a stored hash.

- 65 historical Japanese authored inventory identities remain provisional, including uncertain printed numbering and inaccurate provider name translations. They are searchable research tiles, not invisible queue rows.
- Other provisional Japanese hosts/products retain their source claims. Ambiguous unnumbered design-contest pages point to existing artwork families instead of adding duplicate identities.
- Exact stamp, edition, foil subtype, language-specific availability and individual-date conflicts remain in work_queue.json. Native all-foil statements for Korean products remain positive foil-presence claims until the subtype is supported.
- No new marketplace product ID was attached. Artwork and broad picture acquisition were outside this focused pass.
- The 82-cell species/language matrix and the complete set/source inventory distinguish this bounded reconciliation from unchecked historical/product families.

## Factual specimen sample

Independently viewed **18 exact manufacturer specimens** (10 JA, 8 KO), selected reproducibly across available eras and promos. Names, printed identifiers, primary species, native language and printed rarity/no-symbol state agreed after review. The sample additionally exposed two inherited promo-date assertions and one TANTO stamp omission; those were removed/replaced or qualified. The physical-stamp denominator is one, not 18 complete variant audits.

No global accuracy estimate is inferred. Pre-DP Japan and Korean DP/BW main sets are outside this native sample frame; complete physical variants, other dates, artwork and marketplace identity were not assessed by this sample.

## Rebuild and verification

Run `python catalog_enrich.py`, then `python asia_audit.py`. These are offline and use frozen reviewed facts. Software migration/HTTP/DOM checks are recorded separately in VALIDATION.md. The evidence ZIP contains acquisition scripts, cached native responses/specimens, source-specific reconciliation, the field ledger, matrix and resumable queue.
