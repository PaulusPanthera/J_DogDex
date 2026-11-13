# DogDex 1.8.16 - Bulk card classifications

Data health now offers an explicit visual card picker. The ordinary list keeps its Edit
and Remove controls. Select cards switches to larger, full-colour reference thumbnails
with individual checkboxes; it starts with nothing selected. Optional Select all matching
cards includes results beyond the visible page and allows individual exceptions.
Changing the view, ledger, issue, search or species/category/source scope clears selection.

Set artwork and Set rarity open a compact value chooser followed by a before/after review.
Only unclassified cards are changed by default. Already classified / unchanged cards are
listed as skipped; the collector can explicitly permit replacements. No installation-time
classification or automatic inference from names, rarity or card type is performed.

## Scope

- Artwork: Standard artwork or Full Art.
- Card rarity: current ledger options, including No printed rarity. EN/DE use western
  codes; JA and KO use their separate codes, with legacy Special Rare (LV.X) S preserved.
- Explicit printing-specific rarity overrides take priority and are never replaced.
- Card identity, existence evidence, physical finishes, edition/stamp/foil distinctions,
  dates, images, marketplace mappings, ownership and costs are outside the batch.
- A shared release date is still best corrected on its set/source. Missing pictures and
  printing existence need individual evidence rather than clearing a health flag in bulk.

## Transactions and Undo

Review has no database side effects. A review fingerprint binds the exact card identities
and current selected field values; a stale review rejects the whole batch. Writes use one
SQLite transaction, retain unrelated overrides and create one batch audit record. No new
collection identity or target is created. Undo validates every edited field before restoring
any, preserves unrelated later edits and refuses to overwrite a newer classification.
The normal version-4 collection backup carries batch edits and Undo history; no schema
migration is needed. Recent bulk edits are available in Backup & Trash after restart.

## Files

| File | Change |
| --- | --- |
| bulk_edit.py | Preview, atomic apply, field-scoped Undo and ledger validation |
| collector.py / app.py | Local authenticated batch routes; preview returns no mutated state |
| static/editor-ui.mjs | Visual selection, scoped controls, review and Undo history |
| static/app.js / static/app.css | Selection reset and responsive picker styles |
| static/index.html / mobile_export.py | Updated asset versions and read-only export version |
| tests/test_bulk_edit.py / tests/test_bulk_edit_dom.mjs | Transaction, preservation and UI workflow checks |

The patch also includes the earlier 1.8.15 caption/order files, so it can be overlaid on
1.8.14 or 1.8.15. It contains no replacement catalogues, personal databases, images,
Windows runtime or generated public viewer.

## Validation

- Seven backend bulk tests: exact selected IDs, no-write review, classified-value skipping,
  invalid/mixed-language/deleted targets, whole-batch stale-review rejection, rollback on
  failure, independent artwork/rarity and identity states, explicit printing rarity,
  JA/KO S namespaces, backup/restore and field-scoped/conflict-aware Undo.
- Four existing Python editor / public-export checks passed.
- Thirty-one JavaScript checks passed, including visual individual selection and deselection,
  optional all-filtered selection beyond pagination, filter/language selection reset,
  review without mutation, real HTTP save/Undo, regional rarity choices and skipped cards.
- Existing gallery, printing order, image fallback, sidebar and Cardmarket workflows passed.
- Python / JavaScript syntax checks and bundle SQLite, ZIP CRC, checksum and overlay checks.

DOM and real HTTP were exercised; a pixel-level browser screenshot audit was not performed.
These software checks do not constitute a new factual audit of the catalogue.
