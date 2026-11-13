# DogDex 1.6.0 — English/German completion pass

Baseline: delivered 1.5.0. Evidence cutoff: 29 October 2026. The 41-species roster is unchanged. This release completes a systematic pass through the inventories named below. It does **not** establish that every physical variant worldwide is known.

## What changed

- **51 new identities:** English 8 (2 documented, 6 provisional); German 43 (14 documented, 29 provisional). Unknown rarity, artwork, finish, image or date no longer hides a credible identity.
- **Three original IDs restored:** German Shaymin-EX 77a is a visible provisional availability claim. German M Manectric-EX 24a and M Lucario-EX 55a remain explicit exclusions, accessible with their evidence in Data health. Their historical physical IDs and all personal records survive.
- **85 supported physical targets added:** 84 English and one German, mostly product variants of existing identities. Product-row reconciliation contributes 83 new targets; two exact Cynthia SV82 foil specimens contribute the other two. Fifty existing physical IDs gain source-named foil-pattern detail without creating additional targets. Product provenance is attached to 117 matched inventory rows; 25 existing physical targets receive product-year precision or an explicit unknown product date instead of inheriting an expansion day.
- **Existing errors and unsafe certainty corrected:** Dark Houndoom EX Team Rocket Returns 5 is Holo Rare; Hisuian Zoroark VSTAR Lost Origin 203 is Rainbow Rare; English Lucario 122 gains its omitted LV.X name marker. Seven remaining promo-series date inheritances are removed: three retain dates supported by exact product references and four German dates become explicitly unresolved.
- **Five disputed physical targets across four existing cards leave confirmed progress**, while copies, costs, wishes and picture overrides remain addressable. Uncertainty is retained as evidence, not silently deleted.
- **1,334 previously missing artwork fields assessed** from exact cached faces: 48 Full Art and 1,286 Standard. Four horizontal BREAK layouts remain ambiguous and 50 old records have no exact face to assess. These are metadata fills, not 1,334 demonstrated prior errors.
- **20,739 field/source claims consolidated** across current EN/DE identities. Original provider assertions, previous reviews, rejected defaults, contradictions and superseded values are kept distinct from the selected current value. Reindexing old evidence is not counted as new verification.

The layout remains charcoal, with gray unowned overview images and full-colour details. Small additions provide a research badge, identity evidence status and an Evidence tab. A documented identity can have no accepted printings; an exact physical printing can have unknown rarity, date or picture. Promotion edits the same ID.

## Before and after — identities and physical records

| Ledger | 1.5 identities | 1.6 identities | 1.5 physical IDs | 1.6 physical IDs retained | 1.6 confirmed targets |
|---|---:|---:|---:|---:|---:|
| EN | 997 | 1005 | 1598 | 1682 | 1681 |
| DE | 908 | 954 | 1430 | 1434 | 1427 |
| JA | 965 | 965 | 793 | 793 | 793 |
| KO | 789 | 789 | 500 | 500 | 500 |

Physical IDs retained includes held historical targets. Confirmed targets excludes provisional/disputed/excluded identities and unsupported physical claims. JA/KO canonical entries are byte-equivalent under canonical JSON to 1.5; their research was not expanded. No owned data is bundled.

## Named inventories and coverage denominators

Every extracted row has a persistent disposition and source link. The pools overlap, so their row counts must not be added into a global denominator. A matched inventory identity does not verify its date or every physical variant.

| Source pool | Extracted rows in this comparison | Disposition |
|---|---:|---|
| Pokémon TCG API / pokemon-tcg-data English primary inventory | 911 | 889 matched; 21 excluded Zygarde forms; one disputed Classic Zacian identifier |
| Serebii Cardex pages for all 41 species | 942 | 791 matched; 143 other/unconfirmed-language rows; seven excluded forms; one disputed Zacian subset identifier |
| CardCameos species inventories | 77 | 70 matched; seven admitted identity claims, with later field-specific promotions recorded separately |
| PokéCameos available species inventories | 103 | 67 EN matches; 36 outside EN/DE or language unconfirmed |
| Pokumon exact language/product pages | 271 | 220 in-scope EN rows: 117 existing targets, 83 new targets, 20 incomplete physical claims; 37 native-DE products outside the roster and 14 excluded Zygarde forms |
| Additional native Bisafans checklists, 22 sets | 216 in-scope rows | 214 exact DE name/set/number matches, including 11 newly admitted identities; 205 mappable rarity labels, nine raw/unmapped labels; two excluded forms |
| Prior PokéWiki primary species pool | 957 source rows evaluated separately for EN and DE | All earlier rows retain their disposition; all 13 previously withheld German primary candidates are now visible without invented finishes |
| Prior manufacturer checklists and Carddex inventories | 133 PDFs; 64 usable Carddex inventories out of 67 attempts | Existing 856 manufacturer identity matches and 358 native Carddex identity matches are reused, not freshly retrieved or universally verified |

Source lineage: GitHub pokemon-tcg-data and its Pokémon TCG API are one family. TCGdex and sites reproducing TCGdex are one family. Cameo inventories have uncertain/shared lineage and are not treated as two independent confirmations. Bisafans/Carddex native editorial lists, manufacturer documents and physical specimens are used according to their field. A native provider listing is a positive claim, not proof of every localized physical edition.

The 82-cell species/language matrix records primary expansions, promos/products, decks/alternates, cameos/items, jumbo/special cards and known replicas. Existing entries absent from the new inventories are listed rather than deleted. Each cell identifies source coverage and limits. Earlier individually documented championship replicas and their deck evidence remain intact; a new exhaustive replica/event census was not available.

## Field checks, missing information and conflicts

Fresh inventory tuple comparisons agree for **1,164 existing EN/DE identities** after explicit prefix/SP-label normalization. This is name/number/set comparison coverage; it is not a count of fully verified cards. The native Bisafans checks cover 203 existing and 11 newly admitted DE identities, with 205 mappable rarity checks across that group. See `field_comparisons.json` for the actual compared values and source family.

The original 1,388-field artwork backlog has **54 old-record gaps** remaining (50 missing faces and four ambiguous BREAK layouts). New incomplete identities and the three restored claims add their own unknown fields. Current EN/DE totals have 105 unclassified artwork fields and 39 unknown rarity fields. Rising missing-field counts from newly visible claims are not evidence of a regression in factual accuracy.

Known open conflicts include German Manectric EX Emerald 7 non-holo, German Zoroark Black & White 71 non-holo, English Lucario GL Rising Rivals 8 non-holo, and two German Eldegoss Evolving Skies 16 non-holo/stamped claims. Their complete old records remain held. The Classic Zacian V claims use 028, original 138/CC-138 and Serebii SH26/H26 labels; their relationship and product chronology remain disputed under the existing research ID. An ordinary Lycanroc 138 can never satisfy that match.

Product claims without an accepted tuple remain visible, including the Kalos First Partner jumbo Fennekin XY02: oversized identity, anniversary logo and product date are documented, while the base finish stays unknown. Two newly admitted German lettered alternates do not inherit the ordinary expansion day. The two conclusive German alternate exclusions retain their historical dates as superseded evidence rather than selected release facts.

**923 quarantined Cardmarket IDs remain quarantined.** The current primary bulk catalog was downloaded and all 923 were re-screened. It supplies a name and expansion ID, but no exact collector number, language or physical variant; it cannot resolve the matching question. Generic search links remain labelled as searches. An inaccessible exact listing is not negative evidence for a card.

Acquisition log: 448 successful cached documents and 47 failed/unavailable requests. Individual failure URLs and reasons are retained. Missing pages are not interpreted as nonexistence. Native German product evidence remains narrower than English; obscure paper variants, some regional distributions, ambiguous layouts and replica/event coverage are named limits.

## Recurring causes addressed

| Cause | Implemented result |
|---|---|
| Metadata completeness used as admission gate | Provisional/documented identity and physical evidence are separate. Unknown fields do not remove a credible card. Research tiles and Data health show the same ID. |
| Generic Normal or rarity used as physical proof | Only exact reviewed physical tuples enter confirmed progress. Five unsupported old targets are held; known deck exceptions carry their own provenance. |
| Promo-series or original expansion date copied to a product | Seven remaining existing promo inheritances cleaned; new promos and lettered alternates use individual supported dates or unknown. Precision is preserved. |
| Printed rarity, artwork and foil collapsed | Exact rarity corrections, independent visual artwork assessment and source-specific foil/stamp tuples remain separate fields. No absent Full Art label implies Standard. |
| Card number alone matched across subsets | Species constraint plus explicit disputed Zacian subset relation prevents a wrong cross-species match. Old IDs remain unchanged. |
| Broad foil patterns created duplicate targets | Specific pattern refines an existing compatible target. Existing smooth/pixel Cosmos and lenticular jumbo details are preserved. |
| Existing primary canine also shown as a cameo card | Background associations remain evidence on the primary identity; Cameos includes only cards without a tracked primary. |
| Historical assertion overwritten by selected value | Original labels, lineage, locators, URLs and known dates/hashes remain in history; current selection is separate. |

## Fresh factual sample — separate from software tests

Frozen seed 20261030; **79 existing records**, English 40 and German 39, across five eras. It excludes the previous 160 sampled IDs. Eight per cell were requested; only seven early-DE records remained, and all seven were taken. Unknown-year records are outside this sample design.

Name/number comparison was assessable on 61 records; 18 had no suitable comparison in the selected references. A separate visual check assessed 74 shared faces; five missing faces were unassessed. **Zero discrepancies were observed in those assessed sample fields.** This does not assess every finish, language-specific product, date or marketplace ID. No overall accuracy percentage or confidence claim is derived. The two broader rarity corrections came from the systematic comparison, not this sample.

## Resume without repeating discovery

The work queue contains 304 items, including grouped blockers and diagnostic flags; it is not a count of proven errors. Resume in priority order: exact regional/identity conflicts, incomplete physical tuples, exact marketplace metadata, remaining image/layout ambiguity. Every one of the 118 original research leads has a recovered disposition; excluded families and JA/KO observations remain outside this research pass.

- Application: `DogDex_Local_Collector_Windows.zip` contains the code, selected catalog, historical source SQLite, evidence tables, matrix and audits.
- Evidence archive: `DogDex_Research_Evidence_1_6.zip` contains this application research, preparation scripts, raw acquisition caches and the earlier 1.5 working evidence. It is the research checkpoint.
- Rebuild offline from selected facts with `python catalog_enrich.py`. Research extraction uses `work/completion_16/prepare16.py` with lxml/Pillow; the normal app has no such dependency. Do not run old report generators over a new catalog or replace the frozen 1.5 baseline.
- Read `work_queue.json`, `field_verification_ledger.json`, `field_comparisons.json`, `inventory_reconciliation.json`, `product_reconciliation.json`, `original_evidence_archive.json` and `source_acquisition.json` before fetching again.

## Software and upgrade validation

See `VALIDATION.md` and `software_validation.json`. Tests, stable IDs, database integrity, offline rebuild hashes and package checks are independent from factual validation. Native Windows execution is not performed in this Linux environment.
