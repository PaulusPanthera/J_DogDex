# English/German coverage pass — DogDex 1.2.2

Reviewed 28 October 2026. English and German remain the priority. This pass adds actual missing identities and product variants; it does not equate low pending counts with a complete catalog.

## Results

| Change | Count |
|---|---:|
| New German card identities | 26 |
| New German source groups | 7 |
| Additional physical choices | 37 |
| Of those, jumbo choices | 9 |
| Individual card-date corrections | 15 |
| New German pictures | 47 |
| New English pictures | 2 |

The active catalog contains 3,636 identities and 4,229 printings, including 20 jumbo choices. Full Art remains 286 identities and cameos remain 116. The original 41-species scope remains in force, including the confirmed 10% Zygarde rule. Eevee and its evolutions, Shinx, Luxio and Luxray are not reintroduced. A genuine product name may still mention an excluded Pokémon.

## Missing German identities

| Source | Accepted cards | Numbered identities |
|---|---|---:|
| Trainer Kit Schwarz & Weiß — Stalobor | Yorkleff 1/27; Terribark 19 | 3 |
| Trainer Kit Schwarz & Weiß — Zoroark | Zorua 13/23; Zoroark 17/30 | 4 |
| XY Trainer Kit — Feelinara | Snubbull 11/27; Granbull 14/29; Coiffwaff 16/22 | 6 |
| XY Trainer Kit — UHaFnir | Coiffwaff 20 | 1 |
| Trainer Kit XY — Wrestler-Pikachu | Frizelbliz 11/28; Voltenso 13/22 | 4 |
| Trainer Kit Sonne & Mond — Wolwerock | Wuffels 14/29; Wolwerock 16/30 | 4 |
| Mein erstes Spiel — Glumanda deck | Vulpix, Vulnona, Fukano, Arkani | 4 unnumbered |

The native German deck lists enumerate the exact card names and numbers. Physical German product/card evidence corroborates release in the language. This is not an automatic translation of an English ledger. The selected number-30 Zoroark and Wolwerock face cards are holo; their separately numbered non-holo copies remain separate identities. The other numbered additions are fixed non-holo inserts. No reverse or first-edition alternatives are inferred.

“Mein erstes Spiel” cards have no printed collector number or rarity. Provider indexes 11–14 stay in `number_key` for sorting; they are not displayed as printed numbers. The Glumanda emblem stays on each physical printing. The manufacturer gives Q3 2023; the supported date field stores 2023, with the original quarter described in the evidence.

New sources expose their deck type, series, known 30-card half-deck totals and evidence links in Data Health. New printing-level products also retain dates and evidence links. Data Health counts a card linked through a printing under that product, while rejecting a language change for the linked source. “Mein erstes Spiel” has no asserted overall set total: the two 17-card mini-decks per product are not an expansion's unique-card count.

Native references:

- [Schwarz & Weiß trainer kit](https://www.pokewiki.de/Trainer_Kit_Schwarz_%26_Wei%C3%9F_(TCG)) and [German physical kit cards](https://recollectibles.de/collections/pokemon-bw-trainer-kit).
- [XY trainer kit](https://www.pokewiki.de/XY_Trainer_Kit_(TCG)).
- [Wrestler-Pikachu/Suicune deck list](https://www.pokewiki.de/Trainer_Kit_XY:_Wrestler-Pikachu_und_Suicune_(TCG)) and [German manufacturer page](https://www.pokemon.com/de/pokemon-sammelkartenspiel/Produktgalerie/trainer-kit-xy-wrestler-pikachu-und-suicune/).
- [Wolwerock/Alola-Raichu deck list](https://www.pokewiki.de/Trainer_Kit_Sonne_%26_Mond:_Wolwerock_%26_Alola-Raichu_(TCG)) and [German-language sealed product](https://www.wog.ch/de/index.cfm/details/product/56359-Pokemon-Sonne-und-Mond-Trainer-Kit-Wolwerock-Alola-Raichu).
- [Mein erstes Spiel native deck lists](https://www.pokewiki.de/Mein_erstes_Spiel_(TCG)) and [manufacturer release window](https://www.pokemon.com/de/pokemon-sammelkartenspiel/Produktgalerie/mein-erstes-spiel).

## Additional sizes and finishes

| Language | Identity | Additional size |
|---|---|---|
| English | Arcanine BREAK XY180 | Oversized holo |
| English | M Lucario-EX 55a | Oversized holo |
| German | Lucario-GX SM100 | Oversized holo |
| German | Zoroark-GX SM84 | Oversized holo |
| German | Bellektro-V SWSH219 | Oversized holo |
| German | Hisui-Zoroark-VSTAR SWSH298 | Oversized holo |
| German | Wolwerock-GX SM14 | Oversized holo |
| German | Mastifioso-ex SVP086 | Oversized holo |
| German | Mega-Lucario-ex MEP012 | Oversized, lenticular holo |

The English MEP012 jumbo already existed. Its ID is preserved while its label now exposes the lenticular effect. The German physical specimen and product are corroborated separately; no German jumbo is created solely because an English one exists. The new English 55a jumbo uses the retained canonical card identity from 1.2.1.

Alolan Ninetales SM128 additionally gains a standard-size holo in both languages. The English deck list describes Water Web foil; the German pattern remains unspecified. Deck positions 17 and 30 both retain the printed identifier SM128 and are modeled by non-holo/holo choices, not invented numbered cards.

Selected references: [Arcanine manufacturer box](https://www.pokemon.com/uk/pokemon-tcg/product-gallery/arcanine-break-evolution-box), [Mega Powers manufacturer collection](https://www.pokemon.com/uk/pokemon-tcg/product-gallery/mega-powers-collection), [German Lucario-GX manufacturer page](https://www.pokemon.com/de/pokemon-sammelkartenspiel/Produktgalerie/kollektion-lucario-gx), [German Bellektro-V manufacturer page](https://www.pokemon.com/de/pokemon-sammelkartenspiel/Produktgalerie/kollektion-bellektro-v), [German SVP086 oversized specimen](https://cardmex-shop.de/Mastifioso-EX-SVP-086-XXL-XXL-Pokemon-Jumbo-Karte-in-Deutsch/SVP-086-XXL), [German MEP012 oversized specimen](https://cardmex-shop.de/Mega-Lucario-EX-MEP-012-XXL-Jumbo-Pokemon-Promo-Karte-aus-Mega-Entwicklung-in-Deutsch/MEP-012-XXL), and [German SM128 holo specimen](https://www.ebay.de/itm/204405779436). Each complete source list is in `coverage_reviewed_facts.json`.

## Date corrections and source priority

Manufacturer product dates take precedence over conflicting card-index dates. Individual promo dates do not date every card in the surrounding promo series.

| Identity | Language | Accepted date | Precision |
|---|---|---|---|
| Lucario-GX SM100 | EN, DE | 2018-03-09 | Day |
| Zorua SM83; Zoroark-GX SM84 | EN | 2017-11-03 | Day |
| Zorua SM83; Zoroark-GX SM84 | DE | 2017 | Year |
| Bellektro-V SWSH219 | DE | 2022-04-22 | Day |
| Hisui-Zoroark-V SWSH297; VSTAR SWSH298 | DE | 2022 | Year |
| Wolwerock-GX SM14 | DE | 2017 | Year |
| Mastifioso-ex SVP086 | DE | 2024 | Year |
| Mega-Lucario-ex MEP012 | DE | 2025-11-07 | Day |
| Alolan Ninetales SM128 | EN | 2018-06-01 | Day |
| Alola-Vulnona SM128 | DE | 2018 | Year |
| Friedwuff-ex SVP162 | DE | 2024 | Year |

The previous English Lucario-GX date of 30 April 2018 conflicted with its already correctly dated jumbo and the [English manufacturer page](https://www.pokemon.com/uk/pokemon-tcg/product-gallery/lucario-gx-box). The previous English SM83/SM84 date of 26 November 2017 conflicted with the [manufacturer collection launch](https://www.pokemon.com/uk/pokemon-tcg/product-gallery/shining-legends-special-collection-zoroark-gx). German rows with uncorroborated exact days use years; they do not silently inherit the English day or the first date of an entire promo series.

For the 2017 Wolwerock trainer kit, a German-language Swiss retailer gives 10 May while the English launch is 21 April. The German source deliberately retains 2017. The 2014 and 2011 new kits also retain year precision; the 2016 kit uses the explicit German manufacturer's 27 April date.

## Picture checks

49 references are accepted: 47 German and two English. Limitless references require an exact localized name/collector route, a native image and, for German, a printed KP/name or distinctive German rule word. Cached files have content-derived names and source/image SHA-256 provenance. A visual sample includes German Lucario-GX, Zoroark-GX, Alola-Vulnona, Hisui-Zoroark-VSTAR and Wolwerock-GX. The new German Vulnona beginner-card picture was individually inspected.

The CardsRfun product labelled German Vulpix actually shows English HP and Will-O-Wisp. That image is rejected for German and accepted only for the English My First Battle Vulpix after visual identity/emblem checks. Its hold remains in `coverage_image_cache.json`; it never becomes the German card's image. This demonstrates why retailer language labels or `_DE` filenames alone are insufficient.

Images remain shared card references. An image does not by itself prove the owned edition, foil pattern or jumbo dimensions. Per-printing replacements remain available through the existing editor.

## Remaining holds and practical limits

- Existing EN/DE records without accepted printings: the two November 2026 Classic Collection Zacian V previews and German McDonald's 2011 Zorua. Their research-only status is unchanged.
- German Friedwuff-ex SVP162 oversized: conflicting retail announcements and an updated [regional release report](https://pokezentrum.de/pokemon-karten-news/pokemon-sammelkartenspiel-release-kalender-2024/) describe different distribution. The regular German card is corroborated, but this pass does not accept a German jumbo without a verified physical specimen.
- German M Lucario-EX 55a oversized: the English manufacturer evidence does not establish the German oversized release. No German tuple is copied.
- 189 pictures remain missing: EN 11, DE 137, JA 36, KO 5. Some newly added German identities have no accepted native reference yet.
- 651 active language/set groups have 615 accepted dates, 13 reference-only dates and 23 unresolved dates. Individual card dates remain absent for 124 records and reference-only for 68. Unknown precision remains visible.
- Japanese/Korean entry records are byte-equivalent under canonical JSON hashing to the prior release; no new research is performed for those languages.

## Reproducibility

`coverage_enrich.py` applies the explicit reviewed facts after the earlier western corrections and before rarity normalization. It checks identity keys, language boundaries, duplicate identities, printable tuple gates, image hashes and existing IDs. Offline builds need no research websites or Pillow. The immutable original database is never written.

Seven dedicated coverage tests exercise the new numbered/unnumbered identities, foil distinctions, date precedence, sizes/lenticular effect, rejected foreign-language picture, unchanged secondary languages and source-editor compatibility. Existing collector/editor/HTTP/backup and Node DOM tests also run. Exact test results and final packaging checks are recorded in `VALIDATION.md`.
