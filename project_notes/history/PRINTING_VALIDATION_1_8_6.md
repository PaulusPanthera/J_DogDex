# DogDex 1.8.6 — Validierung

Geprüft am 30.10.2026. Ausgangspunkt: veröffentlichtes 1.8.5-Paket,
SHA-256 `ab16d9a526edbf5956dfb37efb8bcf97e9e4bea12fcc867456731aba75560aa0`.

| Prüfumfang | Ergebnis |
|---|---|
| Python: Korrekturen, physische Identität, Sources, Sammlung, Editor, Veröffentlichung, Marketplace | **69 Tests bestanden**, 0 Fehler (419,503 s) |
| JavaScript / DOM / echte lokale HTTP-Abläufe | **24 Tests bestanden**, 0 Fehler (140,049 s) |
| Python-/JavaScript-Syntax der geänderten Dateien | Bestanden |
| Delta erneut auf unverändertem 1.8.5 angewendet | Exakt gleiche JSON- und abgeleitete SQLite-Datei |
| Delta auf 1.8.6 nochmals angewendet | Keine zusätzlichen IDs; Kataloginhalt unverändert |
| Ursprüngliche physische IDs / normalisierte Schlüssel / Bild- und Marktreferenzen | Alle 4.517 erhalten |
| Arten / Kartenidentitäten | 41 / 3.820 unverändert |
| JA/KO-Kartenarrays | Inhaltsgleich zum Ausgangsstand |
| Physische Duplikate im gesamten Rohkatalog | Keine gleichen normalisierten Schlüssel innerhalb einer Kartenidentität |
| Bestand | 4.543 Roh-IDs, davon 4.535 akzeptierte Ziele; 8 vorherige zurückgehaltene Claims unverändert |

Gezielte neue Prüfungen decken alle 20 White-Flare-Muster, gewöhnliche Reverse-Drucke,
Logo-Zoroark genau einmal, Seltenheit getrennt von Finish, Mirage/Kürbisstempel,
Cosmos Parallel, Produkttermine, vier unbestätigte deutsche Varianten, Speicherung
und Neustart ab. Die zusätzliche Browserprüfung verwendet tatsächliche White-Flare-
Karten für Galerie-Badges, korrektes Datum, Farbdarstellung im Detail und den
exakten Master-Ball-Wechsel EN ↔ DE.

Ein Upgrade-Test legt vorab manuelle Varianten, mehrere Käufe mit Kosten,
Wünsche, persönliche Metadaten und ein Bild an. Der neue Standarddruck wird als
Alias dem bestehenden manuellen Druck zugeordnet. Alte persönliche Tabellen und
Bilddateien bleiben unverändert; die automatische Sicherung entsteht genau einmal.
Andere bestehende Tests decken Wiederherstellung, Quelle-/Druckänderungen,
Marktzuordnungen, Veröffentlichung und Original-ID-Referenzen ab.

Die Strukturmodule und die Sources-/Galerie-UI sind bytegleich zu 1.8.5:
`source_structure.py`, `source_structure_build.py`, `source_inventory.py`,
`static/source-ui.mjs`, `static/app.js`, `static/app.css` und die 1.8.5-Relationsdatei.
Lediglich die Startseite erhält den aktuellen Versionsparameter.
Die Quellen-Regression bestätigt Crown Zenith 22 (Main 16 + GG 6), Shining Fates
15 (Main 10 + Shiny Vault 5), unabhängige Promoserien und Products ohne zusätzliche
Sammelbalken. Der zusätzliche DE Prize-Pack-Serienkontext verteilt vorhandene
physische Identitäten und erzeugt keine Kopie desselben Drucks.

Die ursprüngliche SQLite bleibt unverändert:
`e79d48ff8d056d88fa0d6b1f0771f220d79f62d82797c886183e20ada9c22da0`.

Softwaretests sind keine zusätzliche Faktenbestätigung. Die 20 Musterbefunde
stammen aus dem bereits abgeschlossenen manuellen Audit; Quellen und Herkunft
stehen in corrections.json und evidence_ledger.json. Vier DE-Varianten und das
englische Zacian-Cosmos-Produktdatum sind ausdrücklich offen. Es wird weder eine
weltweite Vollständigkeit noch eine Gesamtfehlerquote behauptet.

Deine tatsächliche PC-Sammlung lag nicht vor. Erhaltung und Upgrade wurden an
isolierten repräsentativen Sammlungen getestet. Die Windows-Laufzeit bleibt im
Paket; native Windows-Ausführung ist in dieser Linux-Umgebung nicht getestet.

Ausführbare Befehle und vollständige Testprotokolle:
`data/research/printing_186/validation.json`, `python_validation_186.log` und
`node_validation_186.log`. Archiv- und Patchprüfung stehen in der Release-Quittung.
