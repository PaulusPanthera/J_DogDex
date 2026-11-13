# DogDex 1.8.5 — Source structure verification

Verified on 30 October 2026. Software checks establish preservation and behavior; they do not establish factual completeness of every printing.

## Results

| Check group | Result |
|---|---:|
| Node application/domain tests (real local HTTP + DOM) | 24 passed, 0 failed |
| Python source structure tests | 7 passed, 0 failed |
| Python collector, publishing and marketplace regressions | 37 passed, 0 failed |
| Python catalog editor regressions | 9 passed, 0 failed |
| Isolated full enrichment/import reruns | 2 passed |
| Python compile / JavaScript syntax | Passed |
| Complete source inventory | 994 original sources preserved; 1,015 rows with navigation metadata |
| Old/new printing ID reconciliation | 4,517 unchanged IDs |
| Accepted target reconciliation | 4,509 unchanged IDs |
| Original catalog JSON + both SQLite catalog hashes | All unchanged |

## Application behavior assessed

- Exactly one Crown Zenith/Zenit der Könige tile, 22 accepted printings: Main Set 16, Galarian Gallery 6.
- Shining Fates/Shiny Vault: one expansion, 15 accepted printings: Main Set 10, Shiny Vault 5.
- Four Trainer Gallery parent relationships, Hidden Fates parent with ten existing SV printings, and zero-card Celebrations Classic Collection metadata.
- Older RC/SH/RT/AR/SL numbering sections remain within their own expansion. Collector strings are not rewritten.
- SWSH Black Star Promos and McDonald's 2021 stay independent; Prize Pack Series 1/2/3 are separate distribution-series views over existing physical IDs.
- Card set-name and detail-header links open canonical expansion and correct section; EN↔DE keeps gallery scope, sorting and other compatible filters.
- Expansion/localized/subset search, explicit absent-language/section fallback, source filters, Data health and all four ledgers.
- Products have no completion bars. The CZ ETB shows its existing SWSH291 target, not a duplicate Crown Zenith booster card.
- Product finder, exact Japanese marketplace selection, price guides and the approved card/details UI still work.
- Read-only mobile export runs at a GitHub project subpath with relative assets and no edit controls.

## Saved-data verification

Upgrade/reopen, collection backup/restore, exact printing selection, source editing/removal/restore and FileReader picture/cover uploads were tested. Fixtures preserve copy IDs, two physical copies on one target, purchase costs, conditions, notes, dates, wishlist, manual cards/printings, source overrides and picture bytes. The structure upgrade creates a backup before writing only its version marker. A second open does not repeat the upgrade backup.

The user's actual PC collection database was not supplied. These are preservation checks on representative persisted test collections, combined with exact equality of all supplied catalog bytes and raw IDs. No ownership-bearing record was deleted or rekeyed.

## Browser visual check

The actual application was inspected in Chrome through the managed preview. Crown Zenith's combined tile and gallery navigation match the tested UI. A 390-pixel iframe yields a 375-pixel content viewport after its scrollbar: document width and scroll width both 375 pixels. All three section buttons fit within that width. Unowned previews remain gray; detail artwork retains color. This is a viewport check, not a physical Android-device test.

## Import check

Two complete enrichments ran in an isolated copy, using existing cached evidence. Each produced the same 4,517 raw printing IDs, 4,509 accepted IDs and Crown Zenith 22/22 EN/DE membership. Extra distribution provenance is attached to an existing normalized physical tuple, not copied into a new printing. No new factual printing audit or new variant evidence was applied to the released catalog.

## Reproduce

From the DogDex folder:

```
python -m unittest discover -s tests -p test_source_structure.py
python -m unittest discover -s tests -p test_collector.py
python -m unittest discover -s tests -p test_editor.py
python -m unittest discover -s tests -p test_publishing.py
python -m unittest discover -s tests -p test_marketplace.py
```

For UI checks, install the dev-only jsdom 26.1.0 dependency in `tests`, then run `npm test` there. The Windows application itself still needs only its bundled Python standard library.

`python source_inventory.py --user-dir my_collection --output source-review` produces an inventory containing the current collector's manual overlays and source records. It does not modify those records. `source_structure_build.py` reproduces the explicit 1.8.5 registry from its stored baseline and reviewed relationships.

Remaining structure questions (7 rows) and weaker card-level product assertions are listed in `data/research/sources_185/work_queue.json`. No global physical-variant completeness claim is made.
