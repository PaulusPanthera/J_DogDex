# English/German database pass — 28 October 2026

The pass reviews the 85 English and 63 German identities without accepted printing choices in 1.2.0. It accepts explicit physical facts, corrects catalog identities/dates, and holds uncertain combinations rather than accepting generic source defaults.

| Change | Result |
|---|---:|
| New physical targets | 152 |
| Newly supported existing identities | 141 |
| Additional reference images | 112 (79 DE, 33 EN) |
| Individual card-date records reviewed/corrected | 87 |
| Set/source date changes | 15 |
| Duplicate imports merged | 2 |
| Wrong-form research entries retired | 2 |
| Additional Full Art identities | 5 |

## Evidence files

`western_reviewed_facts.json` contains the applied entry-level decisions, explicit printing tuples, language/identity selectors, source URLs, dates, alias/retirement decisions and remaining holds. `western_enrich.py` applies only those reviewed facts; ordinary source flags are never automatically accepted by the offline build. IDs for new printings are deterministic from physical identity.

`western_provider_snapshots.json` retains the fetched regional card metadata with retrieval hashes. `western_card_page_facts.json` records exact English page titles, dates, reference links and page hashes. `german_regional_date_facts.json` distinguishes the German flag dates from other regions on the same pages. Working article extracts and unrelated complete source sets are excluded from the release.

`western_gallery_candidates.json` records matched German gallery name/number pairs. `western_image_cache.json` identifies acquired image hashes and language checks, plus held/failed references. The native-name/KP check is conservative OCR, supplemented by visual samples; it is not proof of an exact foil/edition scan. Held references never become app images. Existing correct images and exact-printing overrides are retained. `western_tcg_reference_index.json` is a compact factual index of relevant source records and images.

## Important decisions

- The manufacturer describes 30th Celebration as entirely foil; generic normal placeholders are contradicted by that statement. Only a holo target is added per reviewed identity; no invented reverse set is generated. [Manufacturer announcement](https://press.pokemon.com/en-CA/MEDIA-ALERT-The-Pokemon-Company-International-Reveals-Product-Lineup-f).
- Detective Pikachu is also foil-only for these booster cards. A Common rarity and a Holo finish coexist; no automatic change to Holo Rare is made.
- German regional years for Expedition/Aquapolis and several EX releases come from the German flag/date column on Bisafans. Summer 2003 is stored as 2003 with its original qualifier in evidence. Ambiguous year ranges such as 2004/2005 are not promoted to exact dates.
- German McDonald's dates differ from the foreign references: [2021](https://www.bisafans.de/sammelkarten/sets/promos-specials/swsh-mcdonalds-2021.php) and [2022](https://www.bisafans.de/sammelkarten/sets/promos-specials/swsh-mcdonalds-2022.php). Regional availability and holo-only versus paired finishes are recorded separately.
- The exact English card date is applied to that card only. Later alternate artworks keep their 2017/2018 releases instead of inheriting a 2014/2016 expansion date. English dates are not copied wholesale into German records.
- [Delphox prerelease availability](https://www.pokemon.com/de/news/erhalte-fruehzeitig-eine-build-battle-box-mega-entwicklung-wachsendes-chaos-des-pokemon-sammelkartenspiels) is 9 May 2026, earlier than the wider expansion launch on 22 May. German Zacian MEP015 retains verified 2025 year precision while its earliest regional prerelease day remains unestablished here.
- Riolu BW33 has documented holo and non-holo product versions. Lillipup BW52 is the mirror reverse promo; conflicting 18/19 September date claims result in month precision. The provider's unsupported Ninetales ex cracked-ice pattern is not accepted; the ordinary EX holo is supported.
- Staff variants are accepted selectively. English Lucario SWSH186's later Staff distribution is dated 2023. Newly approved German records do not inherit the English Staff combinations automatically.
- Printed rarity is distinct from artwork: Delinquent 98b stays Uncommon and is Full Art. New full-art/secret choices use holo surfaces despite upstream normal defaults. My First Battle's 11–14 values are provider indexes, not printed collector numbers.
- Two Yellow A entries duplicate the exact Manectric/Lucario alternate artwork already filed under their printed expansions. One active identity remains per card, with both references retained. Zygarde EX 54a depicts Complete Forme; German Mega-Zygarde-ex 071 depicts Mega Zygarde. Both are outside the pre-existing 10%-only roster policy. Exact artwork was visually reviewed.

## Remaining work

There are 1 EN and 2 DE printing holds in the known catalog. The two Classic Collection Zacian V entries are research previews for a November 2026 product. German McDonald's 2011 Zorua remains a language/distribution hold: a translated API record and an English scan do not independently establish a physical German printing.

The catalog still has 212 missing pictures, 13 reference-only source dates and 23 unresolved source dates across all languages. A nearly empty EN/DE known-record printing queue is not a completeness guarantee; unknown identities and variants can still be absent. Historical Full Art classifications and shared-image edition accuracy remain open for individual review. JA/KO records were not researched in this pass.
