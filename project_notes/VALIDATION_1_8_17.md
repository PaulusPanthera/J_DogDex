# Validation: DogDex 1.8.17

## Catalogue and identity reconciliation

- Original immutable catalogue SQLite hash is unchanged:
  `e79d48ff8d056d88fa0d6b1f0771f220d79f62d82797c886183e20ada9c22da0`.
- Raw card identities: 3,820 → 3,832. Raw printing records: 4,572 → 4,594.
- Twelve new regional identities and 22 new accepted physical targets.
- Every prior card and printing ID is retained. The 3,790 unrelated card records
  are field-for-field identical. Japanese and Korean entries are identical.
- Original printing IDs remain attached to qualified 30th anniversary targets.
  No unmarked duplicate is added.
- The new-set stage is idempotent. A complete rebuild from the immutable input
  and source facts reproduces the same catalogue records and values.
- Both SQLite integrity checks pass; the resolved catalogue has no foreign-key
  violations. Source inventories group the main and Classic Collection targets
  under one expansion per language while retaining the internal subset.
- Per-card before/after IDs and actions are in
  `data/research/new_sets_1817/id_reconciliation.json`.

## Functional regression checks

Passed checks cover:

| Area | Individual automated tests |
| --- | ---: |
| New-set identity, finish, idempotence, image receipts | 4 |
| Individual visual selection and bulk editing | 7 |
| Collection backups, public export and privacy | 7 |
| Shared Cardmarket products, filters and workflow | 9 |
| Coherent review ZIP with committed WAL data | 1 |
| UI, source navigation, symbols, mobile and marketplace DOM tests | 16 |
| Actual generated public viewer and editor stub | 1 |

The final generated-viewer regression loads the exported files, including the
actual no-op editor stub. It checks German Delta's nine targets, two ordinary
Growlithe finishes, the English reference caption, one 30th expansion tile,
15 combined targets, its one-card Classic subset, correct Zacian number/date,
and absence of private editing APIs. Existing private-gallery and public-viewer
checks are also rerun after the reference-caption change.

These are software and bounded inventory checks, not a fresh factual audit of
all historical printings. The full legacy audit suite contains assertions tied
to earlier catalogue totals and is not claimed to pass as a whole.

## Installer integration

The standard-library installer was tested against an untouched extraction of
the supplied 1.8.16 project. Tests cover a normal upgrade, repeat installation,
rejection of an independently modified base catalogue, rejection of a corrupt
payload before mutation, and restoration after an injected post-install import
failure. All personal tables/files remain unchanged. Existing generated docs,
Git/runtime sentinels and an unknown root file are preserved. A repeat
installation changes zero managed files.

The integration runner is `tests/integration_installer.py`. It accepts a prior
project ZIP, an update ZIP and an output directory; it never changes its input
archives. The Windows batch wrapper is not executed on Windows in this test
host; its Python installation logic is exercised directly.

## Rendering limits

A native Chromium smoke run could not launch because this execution environment
blocks its Unix process-singleton socket. No native-browser visual result is
claimed. The existing CSS layout is unchanged; interaction and generated-viewer
behavior are verified through DOM tests.

## Packaging boundary

The public full bundle and update payload exclude personal databases, purchase
records, custom collection images, generated personal viewer output, Git history
and personal audit reports. The update also excludes the existing runtime. ZIP
CRC and payload SHA-256 checks run during packaging and installer preflight.
