# Regional products and physical printings audit — 1.3.2

Observed 28 October 2026. English and German are the research priority. This pass follows the 1.3.1 scope: 41 species, all original identities and printing IDs retained, Eevee/Shinx families excluded. No Japanese or Korean card record changes.

## Results

- 43 physical printing targets added to existing identities: 34 English World Championships replicas, three English STAFF promos, English Rockruff Sequin Holo, two English Pixel Cosmos promos, English Riolu Pokémon Center stamp, and English/German oversized Charizard & Braixen-GX SM230.
- 19 existing promo targets corrected from non-holo to holo, including the German textured SM230. Six existing SM95/118/130 participation cards also gain their visible expansion-logo stamp. All existing IDs survive.
- English SVP011 and SVP024 general Cosmos targets are refined to Smooth Cosmos in place. Their documented Pixel Cosmos papers have separate targets. German paper types and STAFF cards are not multiplied from English evidence.
- 26 card dates changed: 10 English and 16 German. Thirty-two card-date facts are reviewed in total. German Mega-Entwicklung source chronology gains manufacturer evidence; its already-correct expansion date is unchanged.
- Seven German pictures filled: Zorua SM83, Mega-Lucario-ex MEP012, Fiffyen GG33, Riolu GG26, Rutena TG01, Kleptifux SV081 and Zamazenta-V GG54. Native printed names, rules/KP and exact identifiers were visually checked. The gallery pictures also directly verify three previously unclassified German Full Art cards; Zamazenta GG54 now has direct German visual evidence.
- 41 conflicting English marketplace product references rejected. Examples: Arcanine 1 was mislabeled Fan Rotom; Team Aqua's Manectric 4 was mislabeled Dusclops; Lillipup trainer-kit records pointed to Purrloin/Energy Search. Their physical IDs are retained, and searches use the accepted card name. `catalog_enrich.market` now checks marketplace names against the accepted English identity before attaching product metadata.

## Evidence and decisions

`regional_reviewed_facts.json` retains each exact identity, accepted physical tuple, source URLs, supported date precision, evidence and pending holds. Its 80-deck audit has a SHA-256 for each retrieved retail-deck page. Native scans and source hashes are in `regional_image_cache.json`. `regional_upgrade_baseline.json` checkpoints all pre-update IDs plus canonical Japanese/Korean hashes. Full downloaded article bodies and QA collections are excluded from the distributed app.

World Championships replicas are official commemorative products with printed player signatures and a different card back. They are non-holo and not tournament legal. They are separate physical targets under the original card identity, with their own source deck and product date. They are not ordinary pack printings, and ownership of an ordinary card does not count as ownership of a replica. Different players' signatures on N in the same year remain distinct targets. The retail replica deck list takes precedence over the competitor's original tournament list when selecting the reproduced number/artwork.

For 2018, the [manufacturer launch](https://www.pokemon.com/uk/pokemon-tcg/product-gallery/2018-pokemon-tcg-world-championships-decks) is 16 November, overriding 14 November on the secondary deck pages. For the 2023 event, the retail deck date is March 2024, supported by the [manufacturer announcement reproduced contemporaneously](https://pokemonblog.com/2024/01/18/full-content-details-and-release-date-revealed-for-the-new-2023-pokemon-tcg-world-championships-decks/). Month-only dates for older products remain month-only. Pre-2022 World Championships decks were English-only; they are not translated into the German ledger.

German product evidence is independent. The native [Zoroark collection](https://www.wog.ch/en/index.cfm/details/product/60434-Pokemon-Schimmernde-Legenden-Zoroark-GX), [Zoroark pin collection](https://www.wog.ch/en/index.cfm/details/product/61509-Pokemon-Schimmernde-Legenden-Zoroark-Pin-Kollektion), [Spring 2018 chest](https://www.wog.ch/de/index.cfm/details/product/63914-Pokemon-Sammelkoffer-Fruehling-2018) and [TAG TEAM Generations box](https://www.wog.ch/de/index.cfm/details/product/89504-Pokemon-Tag-Team-Generationen-Premium-Kollektion) do not justify copying the international sale day when the retailer gives another day. These use supported month precision. The [German manufacturer Mega-Entwicklung announcement](https://www.pokemon.com/de/news/neue-karten-der-pokemon-sammelkartenspiel-erweiterung-mega-entwicklung) and [German ETB product](https://www.man-of-games.de/p/pokemon-mega-entwicklung-meg-top-trainer-box-deutsch) establish 10 October 2025 for German Riolu MEP010, distinct from the English 26 September launch.

Prerelease promos use documented early distribution, not the later expansion day. The [English Brilliant Stars manufacturer announcement](https://www.pokemon.com/us/pokemon-news/get-the-pokemon-tcg-sword-shield-brilliant-stars-build-battle-box-early/) dates Lucario SWSH186 to 12 February 2022; its retroactively distributed STAFF copy correctly remains dated 2023. The German card retains February precision from contemporary native reports. The [German Kampfstile early-sale announcement reproduced by a retailer](https://www.multi-music-corner.de/pokemon-kampfstile/) establishes 6 March 2021 for the Build & Battle promo.

The ordinary non-holo Snubbull SM200 and Alolan Ninetales SM128 deck variant remain valid. A shared artwork or Japanese non-holo with a different identifier never proves that the English/German promo is non-holo. Rarity, artwork, finish, foil pattern, stamp and physical size stay separate.

## Changed card dates

| Ledger | Card | Previous | Reviewed |
|---|---|---|---|
| EN | Rockruff SM06 | 2017-02-05 | 2017-02-03 |
| EN | Lucario SM95 | 2018-02-02 | 2018-01-20 |
| EN | Lycanroc SM105 | 2018-05-07 | 2018-03-23 |
| EN | Lycanroc SM118 | 2018-05-07 | 2018-04-21 |
| EN | Manectric SM130 | 2018-08-04 | 2018-07-21 |
| DE | Zorua SM83 | 2017 | 2017-11 |
| DE | Zoroark SM89 | 2017-02-03 | 2017-12 |
| DE | Wolwerock SM105 | 2017-02-03 | 2018-03 |
| DE | Wolwerock SM118 | 2017-02-03 | 2018-04 |
| DE | Voltenso SM130 | 2017-02-03 | 2018-07-21 |
| DE | Zoroark GX SM84 | 2017 | 2017-11 |
| EN | Lucario & Melmetal GX SM192 | 2019-08-23 | 2019-09-06 |
| DE | Lucario & Melmetal GX SM192 | 2017-02-03 | 2019-09-06 |
| DE | Glurak & Rutena GX SM230 | 2017-02-03 | 2019-11 |
| DE | Zacian SWSH033 | 2019-11-15 | 2020-08-14 |
| DE | Zamazenta SWSH034 | 2019-11-15 | 2020-08-14 |
| EN | Snubbull SM200 | 2019-05-18 | 2019-05-10 |
| DE | Snubbull SM200 | 2017-02-03 | 2019 |
| DE | Fukano 024 | 2023-03-31 | 2023-06 |
| EN | Houndstone 042 | 2023-08-12 | 2023-08-11 |
| DE | Friedwuff 042 | 2023-03-31 | 2023-08-11 |
| DE | Riolu 010 | 2025-09-26 | 2025-10-10 |
| EN | Lucario SWSH186 | 2022-02-25 | 2022-02-12 |
| DE | Lucario SWSH186 | 2019-11-15 | 2022-02 |
| EN | Houndoom SWSH090 | 2021-03-19 | 2021-03-06 |
| DE | Hundemon SWSH090 | 2019-11-15 | 2021-03-06 |

## Accepted World Championships physical targets

| Event | Original card identity | Printed signature | Retail product date |
|---|---|---|---|
| 2004 | Pokémon Fan Club 130 | Reed Weichler | 2004-11 |
| 2004 | Team Aqua's Manectric 4 | Chris Fulop | 2004-11 |
| 2004 | Team Aqua's Electrike 53 | Chris Fulop | 2004-11 |
| 2006 | Electrike 60 | Jason Klaczynski | 2006-10-31 |
| 2006 | Manectric ex 101 | Jason Klaczynski | 2006-10-31 |
| 2009 | Poké Drawer + 89 | David Cohen | 2009-10-28 |
| 2009 | Lucario GL 8 | Tsubasa Nakamura | 2009-10-28 |
| 2010 | Lucario GL 8 | Yuta Komatsuda | 2010-11 |
| 2012 | Smeargle 8 | Igor Costa | 2012-11 |
| 2012 | Smeargle 21 | Chase Moloney | 2012-11 |
| 2012 | Smeargle 21 | Zachary Bokhari | 2012-11 |
| 2015 | Lucario EX 54 | Rowan Stavenow | 2015-11 |
| 2015 | Manectric EX 23 | Patrick Martinez | 2015-11 |
| 2016 | N 105 | Jesper Eriksen | 2016-11 |
| 2016 | N 105 | Shintaro Ito | 2016-11 |
| 2016 | N 105 | Shuntu Sadahiro | 2016-11 |
| 2016 | N 105 | Cody Walinski | 2016-11 |
| 2017 | Alolan Ninetales GX 22 | Zachary Bokhari | 2017-11-17 |
| 2017 | Alolan Vulpix 21 | Zachary Bokhari | 2017-11-17 |
| 2017 | N 105 | Zachary Bokhari | 2017-11-17 |
| 2017 | Alolan Vulpix 21 | Diego Cassiraga | 2017-11-17 |
| 2017 | N 105 | Diego Cassiraga | 2017-11-17 |
| 2017 | N 105 | Naoto Suzuki | 2017-11-17 |
| 2017 | N 105 | Kabu Fukase | 2017-11-17 |
| 2018 | Zoroark GX 53 | Robin Schulz | 2018-11-16 |
| 2018 | Zorua 52 | Robin Schulz | 2018-11-16 |
| 2018 | N 105 | Robin Schulz | 2018-11-16 |
| 2018 | N 105 | Magnus Pedersen | 2018-11-16 |
| 2018 | Lycanroc GX 74 | Naohito Inoue | 2018-11-16 |
| 2018 | Rockruff 75 | Naohito Inoue | 2018-11-16 |
| 2018 | N 105 | Naohito Inoue | 2018-11-16 |
| 2019 | Ninetales 16 | Kaya Lichtleitner | 2019-11-22 |
| 2019 | Vulpix 15 | Kaya Lichtleitner | 2019-11-22 |
| 2023 | Zacian V 16 | Tord Reklev | 2024-03-01 |

## Honest limits

There are 3,648 active identities and 4,288 physical targets: English 997/1,588, German 897/1,407, Japanese 965/793 and Korean 789/500. Missing pictures fall from 119 to 112 (EN13, DE58, JA36, KO5). There are 343 Full Art identities, 93 cameo-only identities and 27 oversized/metal targets. The 551 printing-research records and 124 undated records remain; reference-only card dates fall from 38 to 23. Of 655 language/set groups, 620 dates are accepted, 12 reference-only and 23 unresolved.

Remaining holds include German SM06/54/95/120 original sale days, German STAFF specimens, German Smooth/Pixel paper variants and later German Worlds cards. English Growlithe SVP024 Pixel Cosmos has no independently established first-sale day: its parent-card date is explicitly marked approximate and explained in detail. Thirty-five historical German image requests were unavailable; no foreign-language replacement was used. Shared pictures can still depict a different finish, signature or back; exact printing pictures remain replaceable in Data health.

The marketplace name check prevents clear card-name conflicts; it does not prove every same-name set, number, finish or signature mapping. Stock and prices are not synchronized. This is expanded verified coverage, not an exhaustive completeness claim.
