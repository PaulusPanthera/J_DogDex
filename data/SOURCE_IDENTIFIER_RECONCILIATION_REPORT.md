# DogDex remaining source and identifier reconciliation

27 October 2026. This is a validated local database checkpoint with evidence, catalog pictures and manual research queues. It is not a Windows collector launcher or completed website.

**All 59 previously held source records are reconciled:** 57 bind to verified local identities, and two are excluded from collection scope. The pass adds **35 identities** (26 Japanese, six German, three English), **14 supported printing choices**, and four H-series display-number corrections. Six current German provider snapshots corroborate the old archived records.

## Current totals

The catalog contains **5,299 visible identities** and **5,625 accepted physical printing choices**. **4,096 identities have at least one printing**; **1,203 still need printing or metadata research**. The five earlier unknown-rarity cases are unchanged.

| Language | Visible identities | With a printing | Without a printing |
|---|---:|---:|---:|
| DE | 1,279 | 1,175 | 104 |
| EN | 1,408 | 1,282 | 126 |
| JA | 1,454 | 950 | 504 |
| KO | 1,158 | 689 | 469 |

The source inventory's held queue is now empty. That closes the already discovered records in this workflow; it does not prove a globally complete card list or complete enumeration of every finish, edition, stamp and reissue. Other data-health issues remain, including product introduction dates and exact foil patterns.

## Identity corrections

- Aquapolis Arcanine H2/H32 and Espeon H9/H32, and Skyridge Arcanine H2/H32 and Flareon H7/H32, retain their stable entry and variant IDs. Displayed provider padding H02/H09/H07 becomes the printed H2/H9/H7. H-series cards remain separate from ordinary-number cards.
- Fourteen shiny-vault observations were filed under original Sun & Moon expansions. Thirteen attach to their existing English Hidden Fates Shiny Vault identities. Zygarde-GX SV65 depicts the other form and its existing research entry is held from collection progress. It had no accepted printing or owned copy.
- Three Silver Tempest Trainer Gallery observations attach to the correct subset rather than the main expansion.
- Restore the Yellow A alternate-art cards Sylveon-GX 92a/145, Zoroark-GX 77a/73 and Eevee 101a/149. Printed letter suffixes and distinct artwork are not merged into the original-number cards. Each gets its positively supported English holo printing. The original expansion date is not verified as the introduction date of this later artwork: separate product/date claims remain in research. The Eevee archive date and UK product listing differ; no exact launch date is promoted automatically.
- Restore six German Ultimative Sieger identities: Fukano 108, Sheinux 126, Arkani G 15, Lucario C 31, Arkani 50 and Voltenso G 66. Their German scans show /147, while the old archive's 153 is the total catalog count. The current localized set response confirms official 147 and total 153. No German release day is copied from an English date.
- Vulpix δ 70 and Ninetales δ 8 retain their existing Dragon Frontiers identities. The delta symbol is a scoped name representation difference. Five shiny-card provider records omit printed +/× damage suffixes; individually reviewed suffix observations reconcile those formats without changing any raw source.
- The Korean source labeled as species 676 actually depicts Archeops, not Furfrou. The incorrect inherited species value remains in its original source, with an explicit excluded-source review and before/after history. No Archeops card is added to the canid catalog.

## Valid unnumbered Japanese identities

26 manufacturer records now have an explicit **unnumbered** identifier namespace and display “Unnumbered.” Website IDs distinguish internal records and never appear as fabricated collector numbers. Each card's exact manufacturer page, image, illustrator and product context are retained. Distinct design-contest artworks remain separate even when their attacks are identical.

These include Shinx and Lucario LV.X from Secret of the Lakes; Leafeon LV.X and Glaceon LV.X from Dawn Dash; seven starter/Temple of Anger records using the broad DP5 logo; Electrike and Manectric from Entry Pack ’08 / DX; 12 Illusion's Zorua/Zoroark contest artworks; and the movie-anniversary Lucario sheet card. Source-product links preserve the actual starter, expansion, contest category and sheet context instead of treating a broad regulation logo as one booster. These links cover this reviewed batch, not every older catalog entry.

The primary manufacturer originals for these legacy cards are only 162×226 pixels. They identify the artworks and layouts; they are not detailed physical scans and do not justify a full finish or edition list. Historical manufacturer S rarity is retained in an explicit legacy namespace for LV.X cards; it is not silently relabeled as modern shiny rarity. No printed rarity is distinct from unknown rarity.

**All 26 new Japanese entries still need finish/edition/stamp research.** Their identities are restored without making up a normal, holo, reverse or first-edition choice. Therefore the open printing queue rises from 1,178 to **1,203**: 26 real entries become visible, and one out-of-scope Zygarde research entry leaves collection totals. The nine other restored entries have supported choices.

## Printing evidence

11 choices use explicit non-generated tuples in the exact current German Ultimative Sieger card records, corroborated by local set membership and reviewed German faces. The scoped modern product rule resolves edition applicability; it does not create a finish from source booleans, rarity, scan brightness or foreign marketplace prices. Arkani G's league-pattern reverse and Kosmos holo tuples remain two explicit research claims until their localized products/patterns are verified. No generic reverse is substituted for the named league version.

Three choices use positive Holofoil quotes for exact numbered English Alternate Art Promos products. Product IDs, denominator, HP, title and set context must all agree; similarly numbered Trainer or other-set cards are rejected. Conditions do not create additional printings. Quote values are availability evidence and are not imported as live personal valuations or purchase prices.

## Preservation and recovery

**226 database/evidence checks and 29 boundary tests passed.** Exact replay changes no persisted table, source history, owned record or collection target. All prior source records, physical tuples and available choices remain intact. Corrected display numbers preserve stable IDs. Original sources, including incorrect claims, are retained.

The checkpoint includes all 59 reviewed catalog images/previews, 74 newly registered evidence blobs, the current SQLite database, the preceding Phase 12 database, current research queues and review receipts. `source_reconciliation_history` also handles excluded sources that have no collection entry; `identifier_observations` distinguishes unnumbered identities and printed denominators; `source_products` and `entry_source_products` retain this batch's distribution contexts and unverified date claims. Source code remains in Git at the manifest's commit and is not duplicated here.

Use `data/catalog.sqlite3` as current and `checkpoints/phase12_catalog.sqlite3` for rollback. Retain the preceding English Set Reconciliation archive and its pinned dependencies for earlier evidence and images.

## Next implementation step

This checkpoint can support the local collector interface while remaining research is handled in one Data Health tab. The interface must display unnumbered cards correctly, expose only accepted printing choices, and allow explicit manual research for the 1,203 entries without a choice. An empty source intake queue must never be presented as complete printing coverage.

The agreed collector remains a local Windows PC app: separate EN/DE/JA/KO ledgers; All cards, My collection, Wishlist and booster/source views; every physical printing counts; jumbo/cameo categories included in overall progress; simple release-year/Pokedex/rarity sorting; grey unowned cards; owned copies with price and condition; standard catalog images only; data health confined to one tab.
