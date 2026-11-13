# DogDex 1.8.6 — Druckvarianten-Korrektur

Ausgangsstand: vollständiges Paket 1.8.5. Kein UI-Umbau und keine erneute Vollprüfung der 48 Fälle.

**26 neue Druck-IDs; alle 4.517 bisherigen IDs erhalten.** Die 3.820 Kartenidentitäten und die 41 Arten bleiben bestehen. JA/KO-Kartenrecords sind unverändert.

| Bereich | EN vorher → nachher | DE vorher → nachher |
|---|---:|---:|
| White Flare / Weiße Flammen (10 Identitäten) | 15 → 26 | 15 → 25 |
| Hisui-Arkani, Verlorener Ursprung 084 | 4 → 4 | 2 → 3 |
| Zacian, Paradox Rift 136 | 2 → 3 | 2 → 2 |
| Zacian, Phantasmal Flames 045 | 3 → 4 | 2 → 2 |
| Houndoom, Scarlet & Violet 034 | 2 → 3 | 2 → 2 |
| Fidough, Paldean Fates 038 | 2 → 3 | 2 → 2 |

| Gesamtmaß | Vorher | Nachher |
|---|---:|---:|
| Physische IDs einschließlich 8 zurückgehaltener Alt-Claims | 4.517 | 4.543 |
| Bestätigte Sammelziele | 4.509 | 4.535 |
| Davon EN | 1.693 | 1.708 |
| Davon DE | 1.439 | 1.450 |
| Davon JA / KO | 847 / 530 | 847 / 530 |

Diese Zahlen messen diesen abgegrenzten Änderungsumfang, keine globale Vollständigkeit oder Fehlerquote. Vier neue unbestätigte DE-Variantenclaims werden nicht zu Sammelzielen.

## Umgesetzte Korrekturen

- 20 Poké-Ball-/Master-Ball-Reverse-Drucke für 074, 075, 076, 061 und 062 in EN und DE. Gewöhnliche Reverse-Drucke bleiben erhalten; keine neuen Illustration-Rare-Identitäten.
- EN Zoroark 062: Holo mit White-Flare-Logo, US Costco Unova Heavy Hitters; 20.11.2025.
- DE Hisui-Arkani 084: Play!-Pokémon-Non-Holo. Nachweis umfasst German-SKU 728209.German; die Händlerbezeichnung „Promo“ ersetzt nicht die gedruckte Seltenheit.
- EN Zacian 136: Melmetal-Deck-Non-Holo, 05.04.2024.
- EN Zacian 045: Cosmos-Holo aus Chaos-Rising-Blister. Nummer 045, nicht die fehlerhafte 044 aus einer externen Tabelle. Exaktes Produktdatum bleibt offen.
- EN Houndoom 034: Mirage-Holo mit Pikachu-Kürbisstempel, Trick or Trade 2023, 01.09.2023.
- EN Fidough 038: Cosmos Parallel Holo = Reverse Holo + Cosmos, Costco Mini-Tin-5-Pack, Oktober 2024 mit Monatspräzision. Keine Verwechslung mit SVP 069.
- EN White Flare: Herstellerdatum 18.07.2025 statt 17.07.2025. Der falsche Tag stand wörtlich in den Providerdaten; die bestehende UTC-Datumsanzeige ist korrekt. Historisches Referenzdatum bleibt als alter Claim erhalten. Produktdaten werden separat behandelt.
- DE Setname zentral auf Obsidianflammen korrigiert, alter Name Obsidian Flammen als Suchalias erhalten.
- Kontrollierte Bezeichnung Mirage und lesbare Stempelnamen ergänzt; IDs und physische Vergleichsschlüssel unverändert.

## Bereits vorhanden — nicht nochmals angelegt

| Bestehender Druck | Erhaltene ID | Änderung |
|---|---|---|
| EN Hisui-Arkani 084, B&B Non-Holo | `research_printing_29d38408e8c553dc85802e38778e515f` | Datum von 2022 auf 27.08.2022 präzisiert; Prerelease vs. Expansion getrennt |
| EN Hisui-Arkani 084, Play! Non-Holo | `research_printing_bc0f6351aff85a3fbaa44804395a43df` | Datum von 2023 auf 11.08.2023; frühe League-Verteilung 11.–13.08., allgemein 14.08.; Quellenlabel normalisiert |
| EN Zacian 045, Non-Holo | `variant_329df756e0de5185be7a6a5e90b28fe3` | Mega-Diancie-Deck und B&B als zwei Distributionen desselben Drucks; Erstverfügbarkeit 24.10.2025 |

Mightyena 114, Poochyena 128 / Ascended Heroes und die White-Flare-Illustration-Rares wurden nicht erneut auditiert oder dupliziert.

## Offene Fragen

| Sprache / Karte | Offene Variante / Feld | Grund |
|---|---|---|
| DE swsh11 084 | non_holo / none | Exact German Build & Battle Non-Holo specimen/language proof remains absent; English documented, not automatically German. |
| DE sv04 136 | non_holo / none | German Melmetal deck exists, but native exact Non-Holo Zacian 136 physical card remains unverified. |
| DE me02 045 | non_holo / none | Need native German Non-Holo 045 specimen or explicit language/finish contents for Mega Diancie / Build & Battle. |
| DE me02 045 | holo / cosmos | A German-localized price page does not prove a German-language Cosmos specimen. Existing English/Italian listings cannot establish German availability. |
| EN me02 045 | first_availability_date | Exact first availability of the English Chaos Rising Zacian Cosmos blister is not established. Do not inherit the original expansion date. |

Die vier DE-Claims stehen mit Quellen in der bestehenden Data-health-Druckprüfung und Kartenevidenz, zusätzlich in `data/research/printing_186/work_queue.json`. Ihr Fehlen als bestätigter Druck ist keine Aussage, dass diese Varianten nicht existieren.

## Neue Druck-IDs

| Sprache | Set / Nummer | Druck | Stempel | ID |
|---|---|---|---|---|
| DE | sv10.5w / 061 | reverse_holo · master_ball | — | `research_printing_831a483552d255099314b6e33b295adf` |
| DE | sv10.5w / 061 | reverse_holo · poke_ball | — | `research_printing_848c81578a7250df8227ae5f667e8c00` |
| DE | sv10.5w / 062 | reverse_holo · master_ball | — | `research_printing_b09eec275e0a56188d2a3a19f039b499` |
| DE | sv10.5w / 062 | reverse_holo · poke_ball | — | `research_printing_ec65c2ec23a35668803c4efc2a40c4c0` |
| DE | sv10.5w / 074 | reverse_holo · master_ball | — | `research_printing_2f87f1237539526d8a91212ecb157d1f` |
| DE | sv10.5w / 074 | reverse_holo · poke_ball | — | `research_printing_69ded7e76f4e56cf81f40b9f3be5f52d` |
| DE | sv10.5w / 075 | reverse_holo · master_ball | — | `research_printing_345ce600ca315a3b842cfe22dd82558d` |
| DE | sv10.5w / 075 | reverse_holo · poke_ball | — | `research_printing_2ed8a01de98b5b85aa9e2b0e834dfa81` |
| DE | sv10.5w / 076 | reverse_holo · master_ball | — | `research_printing_81348b98da7557a29f94dc3fbe4d1791` |
| DE | sv10.5w / 076 | reverse_holo · poke_ball | — | `research_printing_c624bd1f8eed509fbeb61765270f107d` |
| DE | swsh11 / 084 | non_holo · none | play_pokemon | `research_printing_fdd35c090aba5711889a1c9a0634400f` |
| EN | me02 / 045 | holo · cosmos | — | `research_printing_1042452bcf835dc88a03645e0aa658cb` |
| EN | sv01 / 034 | holo · mirage | pikachu_jack_o_lantern | `research_printing_f99de017de5a5358b50e75104e157a28` |
| EN | sv04 / 136 | non_holo · none | — | `research_printing_a93615598fdc5b3686dc73c966df9aa3` |
| EN | sv04.5 / 038 | reverse_holo · cosmos | — | `research_printing_ff7f761dbfa75f6ca82db49729b47a1b` |
| EN | sv10.5w / 061 | reverse_holo · master_ball | — | `research_printing_402ebc6fdba150e1bd3be17099a06705` |
| EN | sv10.5w / 061 | reverse_holo · poke_ball | — | `research_printing_9bfed61221bf5a0c9296d59c5bcebfb1` |
| EN | sv10.5w / 062 | reverse_holo · master_ball | — | `research_printing_70fce5d431c65382b56f6506638c7be4` |
| EN | sv10.5w / 062 | reverse_holo · poke_ball | — | `research_printing_d90c011467bd52cfab21c535fea41352` |
| EN | sv10.5w / 062 | holo · unspecified | white_flare | `research_printing_4f6b0dbe822e5402878f985c7faadbf4` |
| EN | sv10.5w / 074 | reverse_holo · master_ball | — | `research_printing_14574922062e511091357a06a40aa600` |
| EN | sv10.5w / 074 | reverse_holo · poke_ball | — | `research_printing_ea74897cc8915f9c91210a012ccccf88` |
| EN | sv10.5w / 075 | reverse_holo · master_ball | — | `research_printing_dc3b8cbf766f5b51b4a4ebb9ecb047b7` |
| EN | sv10.5w / 075 | reverse_holo · poke_ball | — | `research_printing_7f8262003b3053f9ba9ce9aae272224c` |
| EN | sv10.5w / 076 | reverse_holo · master_ball | — | `research_printing_14acc457567e5cd4bcbf346593125123` |
| EN | sv10.5w / 076 | reverse_holo · poke_ball | — | `research_printing_035f772ce5e8571bb6fb0247ce6ba2b4` |

## Nachvollziehbarkeit und Wiederaufnahme

- `data/research/printing_186/corrections.json`: explizite, wiederholbar anwendbare Fakten. 27 Druckzuordnungen = 26 neue plus 1 schon vorhandener Druck.
- `new_printing_ids.json`, `before_after.json`, `changed_entry_ids.json`, `baseline_185.json`: exakte IDs, Abgrenzung und Ausgangsprüfsummen.
- `evidence_ledger.json`: übernommene Auditbefunde, Quellenfamilien, ausgewählte Korrekturen und offene Sprachclaims. Übernommene Befunde sind als solche gekennzeichnet; keine neue unabhängige Prüfung aller 20 Muster behauptet.
- `work_queue.json`: vier DE-Varianten und ein Produktdatum; hier fortsetzen, keine erneute Vollrecherche.
- `printing_corrections.py --apply`: idempotenter, expliziter Delta-Schritt; auch in `catalog_enrich.py` nach den bisherigen Importen eingebunden.

## Installation

1. DogDex und das zugehörige Konsolenfenster schließen. Bei Bedarf zusätzlich die vorhandene Sammlung über Backup & Trash sichern.
2. Den Inhalt von **DogDex_Update_1_8_6.zip direkt in J_DogDex** entpacken und Programmdateien überschreiben. Nicht nochmals einen DogDex-Unterordner erzeugen.
3. **my_collection behalten.** Der Patch enthält weder deine Sammlung noch Ersatzbilder für deine eigenen Bilddateien. Keine alten Ordner löschen.
4. START_DOGDEX.bat starten. Der erste Start mit einer bestehenden 1.8.5-Sammlung legt automatisch ein `before-printing-corrections-1.8.6-*.zip` unter `my_collection/backups` an.
5. Falls ein äquivalenter manueller Druck bereits existiert, gewinnt seine alte ID; Bestände, Wünsche, Preisangaben und Bilder bleiben daran hängen. Neue Distributionsevidenz wird in der Ansicht ergänzt.
6. Für GitHub/mobile anschließend den öffentlichen Leseexport neu erzeugen, Commit und Push. Kein Preis- oder Sammlungs-Sync allein durch Ersetzen der Programmdateien.

Das vollständige Paket ist eine Alternative für eine neue Installation. Bei einer bestehenden Installation genügt der Update-Patch; nicht beide ZIPs nacheinander installieren.

Die Sicherungs- und Erhaltungstests verwenden repräsentative isolierte Sammlungen. Deine tatsächliche PC-Sammlung wurde nicht übermittelt und daher nicht direkt geprüft. Der Windows-Laufzeitordner bleibt erhalten; native Windows-Ausführung ist in der Linux-Testumgebung nicht möglich.

Testergebnisse: siehe `PRINTING_VALIDATION_1_8_6.md`.
