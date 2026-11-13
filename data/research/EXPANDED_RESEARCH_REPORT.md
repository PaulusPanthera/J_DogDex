# Expanded English/German audit — 28 October 2026

This pass builds on version 1.3.0. It preserves every previous active entry and printing ID and performs no new Japanese/Korean research. The 41-species roster and excluded-family policy are unchanged.

## Discovery and acceptance

`expanded_species_index.json` records 957 numbered international paper-card rows across all 41 native species pages, with source URLs and response hashes. This is a discovery list, not proof that each card exists in German, or an exhaustive list of physical finishes. Pocket cards are excluded. New entries are reviewed individually against exact numbers, native specimens and regional product information. English-only products, French McDonald's releases, excluded Zygarde forms and uncertain editions are not automatically imported.

`expanded_reviewed_facts.json` contains 10 new entries, four new regional sources, two existing-source corrections, 58 existing-card metadata/artwork corrections, ten individual-date corrections, two extra physical-printing records and one printing refinement. The two source-date corrections also change the inherited dates of English Lucario 3/11 and German Zorua 9/12, giving **12 corrected existing card dates** in total.

## Accepted identities and physical distinctions

| Language | Source / number | Result |
|---|---|---|
| German | XY Promos XY02 | Fynx, foil, Promo; 2013 year retained |
| German | XY Promos XY19 | Fennexis-EX, foil, standard artwork; September 2014 |
| German | BW Promos BW19 | Zoroark, standard foil; German year 2011, no German jumbo inferred |
| German | Guardians Rising 21a | Alola-Vulpix alternate artwork, foil, Common; 2018 |
| German | Shining Legends 77a | Zoroark-GX, foil, Ultra Rare and Full Art; 2019 |
| German | DP Trainer Kit 3/11 | Lucario fixed holo without printed rarity; 2007 year |
| German | MEP095 | Lucario anniversary foil; October 2026 month |
| English | Plusle EX Trainer Kit 2/12 | Electrike fixed non-holo without printed rarity; March 2006 |
| English | Lucario DP Trainer Kit 6/11 | Riolu fixed non-holo without printed rarity; 24 September 2007 |
| English | MEP095 | Lucario anniversary foil; US launch 16 September 2026 |
| German, existing identity | McDonald's 2011 Zorua 9/12 | Hold resolved: native confetti holo, actual regional date 9 March 2012 |
| English, existing identity | BW19 Zoroark | Separate oversized lenticular card; existing regular holo refined to Cosmos in place |

The German McDonald's date is corroborated by a contemporary manufacturer announcement reproduced by [Brandora](https://www.brandora.de/de/archiv/spielwaren-insights/pokemon-startet-diesen-maerz-mit-der-mcdonald-s-happy-meal-aktion-in-deutschland), the native [checklist](https://www.pokewiki.de/McDonald%E2%80%99s_Kollektion_2011_(TCG)) and an exact German 9/12 specimen. Its printed 2011 copyright is not used as its German release date. The older research-only hold in historical files is superseded.

German XY19 uses the [native manufacturer's September 2014 tin date](https://www.pokemon.com/de/pokemon-sammelkartenspiel/Produktgalerie/xy-tin-box-kalos-kraftpaket), rather than its earlier English distribution. English MEP095 uses the [US manufacturer](https://www.pokemon.com/us/pokemon-tcg/product-gallery/30th-celebration-tech-sticker-collection); German MEP095 uses the [German October product announcement](https://www.pokemon.com/de/news/wirf-einen-blick-auf-alle-pokemon-sammelkartenspiel-produkte-die-im-oktober-2026-veroeffentlicht-werden). A documented German delay and later UK listing prevent treating September 16 as one universal English/German launch.

Other specific corrections include EN/DE Zacian SWSH018 and Zamazenta SWSH019 (22 May 2020); DE SWSH076/077 (20 November 2020), Bellektro SWSH085 (19 February 2021), Wolwerock SWSH199 (25 February 2022), Arkani Wizards 6 (March 2000) and Farbeagle Wizards 32 (March 2001). Exact source links and evidence accompany each record. Partial precision is deliberate.

## Artwork, rarity and pictures

Fifty-five previously unclassified Ultra Rare candidates were visually reviewed. **37** use Full Art; **18** ordinary EX/GX/BREAK cards use Standard. German Zamazenta GG54 is an explicitly labeled localized-artwork inference from the same numbered English artwork; no English illustration is published as its German picture. The new German Zoroark 77a also uses Full Art. Printed rarity is preserved independently.

Exact native Wizards Arkani 6 and Farbeagle 32 have Black Star PROMO symbols. Their previous Common classifications are corrected to Promo without changing printing IDs.

`expanded_image_cache.json` records accepted and held candidates, language/number checks, source hashes and content-addressed filenames. **80 pictures** are applied: 72 to previously missing German records and eight to new identities. German script-based checks require native KP/rules text as well as an exact source/number match; accepted images were also visually reviewed in contact sheets. The small Lucario 3/11 specimen was reviewed manually where OCR failed. The English MEP095 picture comes from the exact English Limitless reference. Native scans are never replaced with a differently localized preview merely because a page has a translated title.

Two new English trainer-kit records have no exact cached picture. Shared references can still show another physical edition, stamp or finish. Local per-printing replacement remains available.

## Preservation and limits

`expanded_upgrade_baseline.json` preserves the pre-update entry/printing ID map and canonical Japanese/Korean hashes for regression checks. Every original active ID survives. The original SQLite checkpoint remains immutable. One existing BW19 physical tuple is refined to Cosmos while keeping the owned ID; the new jumbo uses a distinct ID.

Uncertain German BW09, XY161, XY180, SWSH304 and additional early trainer-kit candidates remain outside accepted targets pending appropriate native proof. Historical November Classic Collection Zacian previews remain research-only. Few printing holds do not prove exhaustive coverage.

Final totals: **3,648 identities / 4,245 printings**, including **997/1,546 English** and **897/1,406 German**. German pictures missing fall from 137 to 65; English missing rises from 11 to 13 because two missing historical cards are now honestly cataloged. Across all ledgers 119 pictures and 124 dates remain absent, and 38 card dates are reference-only. Source dates are accepted for 620 of 655 regional groups, with 12 reference-only and 23 unresolved.
