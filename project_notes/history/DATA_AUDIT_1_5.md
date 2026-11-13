# DogDex 1.5 — dataset reconciliation

Baseline: delivered **1.4.0**, frozen before research. Research date: **29 October 2026**. The collecting roster remains 41 species; previous family/form exclusions and the approved UI remain unchanged. English and German were researched. Japanese and Korean records were not changed.

## What changed

**Nine existing records have factual value/precision corrections; three unsupported German identities were withdrawn from active targets.** Four German identities and one specifically documented English foil printing were added. Another 63 previously missing artwork classifications were filled by reading the exact cached card faces. These are missing-field additions, not 63 previously erroneous values.

| Measure | 1.4 baseline | 1.5 |
|---|---:|---:|
| English active identities | 997 | 997 |
| German active identities | 907 | 908 |
| English catalog printings | 1,597 | 1,598 |
| German catalog printings | 1,429 | 1,430 |
| English unclassified artwork | 791 | 758 |
| German unclassified artwork | 658 | 630 |
| German primary candidates awaiting availability proof in the named inventory | 24 | 13 |
| Original nine finish alerts with a documented exception | 0 recorded in this audit | 4 |

Counts are catalog targets, not evidence of factual accuracy or overall completeness. The modest net count increase includes withdrawals: adding records indiscriminately would conceal the underlying errors.

## Reference inventories and coverage

**PokéWiki primary-species inventories:** all 41 species were compared again against the same 957 cached international reference rows, separately for each language. These are bounded discovery inventories, not a census of cameos, product reprints or every printing.

| Reference-row outcome | English | German |
|---|---:|---:|
| Matched active identity | 927 | 869 |
| Documented absence of German release | — | 45 |
| German availability unresolved | — | 13 |
| Other-language-only rows | 6 | 6 |
| Announced/unreleased reference rows | 2 | 2 |
| Excluded Zygarde forms | 22 | 22 |

A matched international row is **not** independent proof of German availability. English has no unmatched primary identity in this particular reference inventory; substantial uncertainty remains outside its scope.

**Independent native Carddex batch:** 67 set inventories attempted, 64 accessible, **358 existing German cards** matched on native name, set and printed number. Of those, **303 rarity categories** were specific enough to compare with the current taxonomy: 301 agreed and two required corrections. The other 55 categories remain unmapped where labels such as Silver Star or Ultra Rare are broader than DogDex's era-specific distinctions. Those differences were not automatically counted as errors. Three unavailable native tables remain logged.

Carddex is a separate editorial source. TCGdex-backed pricing sites and translated marketplace pages were not counted as independent confirmations. The earlier 133 publisher PDFs and their bounded 856 identity checks remain available; this release does not present them as new research.

## Corrected existing data and recurring causes

* **Two German rarity errors:** Team Up Zoroark 91 and Alolan Ninetales 111 were ordinary Rare instead of Holo Rare. The native Carddex inventory, native Bisafans checklist and localized specimens support the correction. The earlier German publisher PDF has outlined text and was not machine-readable. Existing physical finishes were preserved.
* **Seven English date/precision corrections:** three Minun-deck cards lose the unsupported March 1 day and retain March 2006. Delphox-EX XY19 retains the manufacturer's June 2014 month rather than an unsupported June 30. Shaymin-EX 77a and Delinquent 98b use their 2017 product distribution instead of their original expansion dates. Delinquent 98a uses its actual September 2018 product release.
* **Three German regional targets withdrawn:** M Manectric-EX 24a and M Lucario-EX 55a were English-only Mega Powers alternates represented by translated records and pictures of the ordinary originals. Shaymin-EX 77a is retained as an inactive, unsubstantiated regional claim: its German record also uses the ordinary original picture, and no exact German alternate specimen establishes availability. This third decision does not claim proof of universal non-existence.

The new build stage applies exact reviewed identities and preserves all IDs, including inactive records in `retired_entries`. A general guard prevents lettered alternate cards from inheriting the original expansion's date without their own product/card evidence. It does not copy another language's product date. The field ledger also prevents an inaccessible or undecoded reference from being interpreted as a successful check.

For the 2017 Premium Trainer collection, October 20 hobby-store availability and November 17 general retail launch are stored separately. Delinquent 98a illustrates why conflicting histories need a timeline: its proposed 2017 product was cancelled, but the card was released in a different product in 2018. It was kept, not deleted on the strength of the earlier cancellation report.

## Accepted additions and finish decisions

Four **German EX Trainer Kit 2** identities were missing: Minun-deck Arkani 1, Fukano 4 and Vulpix 7; Plusle-deck Frizelbliz 2. The native numbered Carddex inventory, explicit German kit-language history and exact German specimen listings establish the product family. Only the ordinary non-holo inserts were added. No rarity symbol is printed. The supported German date is **2006**; no English month/day was transferred. Usable native pictures remain missing.

English **Delinquent 98a Sheen Holo** is added for the specifically documented Mega Blastoise Battle Arena deck. Its existing non-holo printing and ID remain separate.

All nine original foil-rarity/non-holo alerts were examined. Four English exceptions now have explicit evidence attached: Arcanine HGSS 1, Manectric Emerald 7, unstamped Eldegoss Evolving Skies 16 and its Play! stamped non-holo. The stamped evidence includes a secondary reproduction of the publisher checklist; the original PDF is currently inaccessible.

Five alerts remain unresolved: German Manectric Emerald 7, German Zoroark BW1 71, ordinary English Lucario GL 8 and the two German Eldegoss targets. The German Lauffeuer inventory calls its Manectric copy Holo, while English Wildfire histories document non-holo. That conflict is retained explicitly. Separately documented World Championships Lucario replicas do not establish an ordinary non-holo version. Existing special variants and their IDs remain intact.

## Fresh sample and limits

A new **80-record diagnostic sample** was frozen before corrections, seed **20261029**: 40 English and 40 German, eight random records per language in each of five year strata. The previous 80 records were excluded and remain a regression sample. Unknown-year records are outside this sample design.

**78 cached card faces were reviewed; two missing pictures were unassessed.** One wrong alternate picture/unsupported German identity was found, plus one unsupported exact promo date: **two records with observed problems**. The former was withdrawn with IDs preserved; the latter was corrected to the supported month. Native inventory evidence assessed rarity for 36 sample records; the other 44 rarity fields were unassessed in this fresh sample. Most sample dates, all editions/paper variations and marketplace variants were not independently audited in this sample.

This does **not** establish a population error rate or an overall accuracy percentage. A correct-looking shared card picture does not prove that every language, finish, edition or marketplace product exists. Missing artwork labels are recorded separately from incorrect populated labels.

## Remaining work and continuation

The 13 German primary candidates are ten promo identities and three McDonald's identities. Explicit release-language histories exclude the 2014/2015 McDonald's and Rumble candidates. The 2016/2018 histories list German, but targeted research did not obtain exact native specimens for the three tracked cards, so they remain candidates rather than new accepted targets. Localized manufacturer card descriptions and translated prices alone are insufficient.

Modern successor checklist links were discovered, but returned inaccessible/non-PDF responses. The failures and exact published URLs are cached; no access-wall workaround or repeated blind retries were used. Exact marketplace expansion/number/variant checks, further native cameo proof and 1,388 unclassified EN/DE artwork fields remain open. The 923 provider marketplace IDs quarantined in 1.4 remain candidates, not 923 proven mismatches.

Resume from `data/research/reconciliation_15/work_queue.json`: 15 previous tasks resolved, 106 remaining queue items, including grouped work lists. The field ledger covers all **1,905 active EN/DE identities**, with separate provider assertions, prior review claims, inferred values, missing information and current field checks. It supplies field-specific progress; it does not label whole records verified.

## Software and collection safety

65 Python tests and 12 JavaScript/DOM tests check the collector separately from factual research. Every 1.4 entry and printing ID remains addressable. Upgrade/restore checks include a withdrawn target with owned copies, costs, wishlist, manual name and printing-specific picture override. Japanese/Korean canonical entries, the roster and approved static UI files are unchanged. Offline rebuilds and package/SQLite checks are recorded in `software_validation.json`. Native Windows execution remains untested in this Linux environment.

To update, close the old app, extract the new package to a separate folder and copy the existing `my_collection` folder beside the new `app.py`. Keep the old folder and a backup until the updated app is checked.

## Principal evidence

* [Carddex EX Trainer Kit 2 native inventory](https://www.carddex.net/index.php?page=DB_SERIE&suche=151) and [explicit language/deck history](https://bulbapedia.bulbagarden.net/wiki/EX_Trainer_Kit_2_(TCG)).
* [Carddex Team Up native inventory](https://www.carddex.net/index.php?page=DB_SERIE&suche=288) and [Bisafans native checklist](https://www.bisafans.de/sammelkarten/sets/sm/teams-sind-trumpf/kartenliste.php).
* [Manufacturer Mega Powers contents/date](https://www.pokemon.com/uk/pokemon-tcg/product-gallery/mega-powers-collection) and [native editorial documenting the English-only alternate](https://pokezentrum.de/blog/die-10-wertvollsten-pokemon-karten-aus-xy-phantomkraefte/).
* [Manufacturer Premium Trainer dates and contents](https://www.pokemon.com/us/pokemon-tcg/product-gallery/premium-trainers-xy-collection/), [firsthand 2017 product photos](https://www.pokebeach.com/2017/10/xy-premium-trainers-kit-product-and-promo-photos) and [2018 Battle Arena product report](https://www.pokebeach.com/2018/07/new-configuration-for-charizard-blastoise-battle-arena-decks-delinquent-professors-letter-promos).

All individual decisions and additional links remain in the JSON evidence files. Cached raw source material and preparation scripts are supplied in the separate research evidence package.
