# Bounded EN/DE new-set update, 11 November 2026

| Expansion | Regional release | Tracked identities per language | Accepted printings per language |
| --- | --- | ---: | ---: |
| 30th Celebration / 30 Jahre, main | 16 September 2026 | 12 primary + 2 Lucario cameos | 14 |
| Classic Collection, internal subset | 16 September 2026 | Zacian V, printed 138/202 | 1 |
| Delta Reign / Delta-Herrschaft | 6 November 2026 | 6 primary cards | 9 |

Delta's explicit inventory is Growlithe/Fukano 018 (normal and reverse),
Arcanine/Arkani 019 (holo and reverse), Zorua 066 (normal and reverse), Zoroark
ex 067 (holo), Growlithe/Fukano 106 (Illustration Rare, holo), and Zorua 112
(Illustration Rare, holo). The latter two have Full Art artwork classification;
the ordinary Double Rare Zoroark ex has Standard artwork.

[Manufacturer 30th release and all-foil announcement](https://press.pokemon.com/en-CA/MEDIA-ALERT-The-Pokemon-Company-International-Reveals-Product-Lineup-f)
and the [Classic Collection feature](https://www.pokemon.com/us/features/highlighting-10-cards-from-the-pokemon-tcg-30th-celebration-classic-collection)
corroborate the expansion/subset context. Native regional inventories and faces
are retained as evidence:

- [30 Jahre / 30th complete regional card list](https://www.card-corner.de/pokemon-30-jahre-30th-celebration-card-list)
- [Delta-Herrschaft / Delta Reign regional card list](https://www.card-corner.de/delta-herrschaft-kartenliste)
- [Printed German Delta checklist mirror](https://pokezentrum.de/wp-content/uploads/Pokemon-Delta-Herrschaft-Kartenliste-Checkliste-PDF-TCG-Deutsch.pdf)
- TCGdex native set and card JSON snapshots under `data/research/new_sets_1817/provider/`.
- Image source URLs, source hashes and cached image hashes in `image_receipts.json`.
- Explicit reviewed tuples in `facts.json`; before/after stable IDs in `id_reconciliation.json`.

The preceding research pass compared the complete inventories with the fixed
41-species roster and inspected Delta faces and crowded 30th artwork. This is
not an exhaustive background-character audit. Existing Lucario cameos on
Greninja ex 148 and Pikachu ex 150 are retained in both regional ledgers.

Provider generated variant booleans conflict with card-specific inventories;
they are not used to create printings. Some early Delta image previews show a
102 denominator while native release lists state 103; this is retained as a
source conflict rather than an invented extra printing. DE Growlithe 106 and
Classic Zacian V currently use identified English reference artwork.

Provider Cardmarket IDs on Illustration Rares repeat ordinary-card IDs. They
remain unconfirmed candidates and cannot automatically activate guide prices.
MEP095 Lucario remains in the numbered promo series. No retail distribution
creates a duplicate card. Japanese/Korean inventories and unrelated historical
card records are unchanged. This patch is not a new historical printing audit.
