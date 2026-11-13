# DogDex 1.8.9 — Illumina City and Zygarde forme corrections

This is a focused data correction to the 1.8.8 application. The 41-species roster and the approved UI are preserved. Japanese/Korean records are unchanged.

| Existing identity | Before | Selected outcome |
|---|---|---|
| DE Illumina City, Optimale Ordnung 077/088 | Documented identity, no picture, no accepted physical printings | Same entry ID; native German picture; Thievul cameo on the right-hand shop billboard; Non-holo and Reverse Holo printings; Uncommon rarity and standard artwork |
| EN Mega Zygarde ex, Perfect Order 104/088 | Accepted as a primary Zygarde target | Excluded from completion: Mega Zygarde with a Complete Forme silhouette, without the 10% dog. Record and printing ID retained |
| DE Mega-Zygarde-ex, Optimale Ordnung 104/088 | Accepted as a primary Zygarde target | Same exclusion and preservation as the English identity |
| EN Mega Zygarde ex, Perfect Order 120/088 | Accepted as a primary Zygarde target | Same physical printing, reclassified as a cameo because the artwork includes Zygarde 10% |
| DE Mega-Zygarde-ex, Optimale Ordnung 120/088 | Accepted as a primary Zygarde target | Same physical printing and 10% cameo classification |

The 120 artwork contains the canine 10% Forme outline at the lower left. It should remain collectible under **Cameos → Zygarde**. The 104 background silhouette is Complete Forme, which is outside the agreed dog scope.

## Evidence and limits

- The native German image and the user-supplied Card-Corner gallery establish the regular 077 identity and billboard cameo. The manufacturer's German checklist confirms its number, Uncommon symbol and standard non-holo release.
- A direct German merchant listing explicitly documents the Reverse Holo printing. The native TCGdex record also contains explicit Normal/Standard and Reverse/Standard physical tuples. The printings are not generated from rarity, another language, or a generic API Normal default.
- An exact physical reverse specimen was not inspected. The new picture is the shared native German card illustration; no special reverse foil pattern is claimed.
- The manufacturer preview, native card images, and form-specific cameo inventories distinguish 104 from 120. Generic `dexId`/`cameoDexIds` value 718 does not identify a Zygarde forme. That species-only interpretation caused the incorrect inclusion/classification.
- Illumina City 111 is a different illustration. The 077 cameo is not automatically copied onto it.
- The expansion release remains **27 March 2026**. An entry/evidence timestamp of 31 October is not a release date.

References and source lineage:

- [User-supplied German gallery](https://www.card-corner.de/optimale-ordnung-kartenliste?karte=77).
- [Native German 077 provider record](https://api.tcgdex.net/v2/de/cards/me03-077) and its native card image are one TCGdex source family.
- [Manufacturer German checklist, retailer-hosted mirror](https://pokezentrum.de/wp-content/uploads/Pokemon-Mega-Entwicklung-Optimale-Ordnung-Kartenliste-Checkliste-PDF-TCG.pdf), page 1, middle column 077. The mirror is not an independent second manufacturer source.
- [Direct German Reverse Holo listing](https://cardmex-shop.de/Illumina-City-POR-077-Reverse-Pokemon-Reverse-Holo-Karte-aus-Optimale-Ordnung-in-deutsch/POR-077-Reverse).
- [Manufacturer artwork preview](https://www.pokemon.com/uk/news/rosas-encouragement-mega-zygarde-ex-and-more-from-mega-evolution-perfect-order).
- [Complete Forme cameos](https://cardcameos.com/zygarde-complete-cameo-cards/) and [10% Forme cameo](https://cardcameos.com/zygarde-10-cameo-cards/) are one reference family.

The evidence checkpoint is `data/research/identity_189/`: selected facts, cached native provider records, the supplied gallery, exact before/after identity records and a resolved work queue. Earlier claims remain in the evidence history; the correction does not silently erase them.

## Counts and preservation

| Confirmed completion targets | Before | After |
|---|---:|---:|
| English | 1,708 | 1,707 |
| German | 1,450 | 1,451 |
| Japanese | 847 | 847 |
| Korean | 530 | 530 |
| Total | 4,535 | 4,535 |

Two German printings were restored, while one 104 printing was excluded from each Western ledger. This unchanged total describes the correction; it is not a completeness or accuracy estimate.

All 3,820 existing identity IDs and all 4,543 existing physical printing IDs remain stored. Two new printing IDs complete the existing German 077 entry. No identity was duplicated or deleted, and no existing physical identity was rekeyed. The underlying 104 printings remain stored as excluded claims, not confirmed targets.

Owned 104 copies, costs, notes, wishlists and picture overrides remain accessible. Existing copies show **Out of scope** in My collection; the catalogue record and evidence remain in **Data health → Excluded**. Their ownership history is retained while their completion eligibility changes.

A pre-existing manual printing on the same 077 identity is matched by its full physical tuple. Its ID and ownership win over the newly supplied default, preventing a duplicate collectible.

No current PC collection dump was supplied. Preservation was tested with a representative pre-update collection containing duplicate owned copies, misprint notes, costs, wishes, manual labels and picture overrides.

## Install and publish

Close DogDex. Extract **DogDex_Data_Update_1_8_9.zip** directly into **J_DogDex**, accepting replacements of included application and shared catalogue files. Restart and refresh the browser tab.

The update includes the current UI files and symbols. It contains no `my_collection`, `docs`, `runtime` or original `data/catalog.sqlite3` replacement. The full Windows package is the corresponding fresh-install alternative; an existing installation needs only this update.

Export the mobile view again, then commit and push `docs` through GitHub Desktop. Publication remains an explicit export, not an automatic live sync.
