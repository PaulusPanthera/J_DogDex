# DogDex 1.8.18 validation

Application version: 1.8.18. Catalogue data revision: 1.8.17.

## Automated checks

- Full Python discovery: **153 tests passed**, zero failures/errors/skips.
- Standard interface command: **44 tests passed**, zero failures/skips.
  This passed both with the existing test dependencies and with a clean
  installation from the new dependency lockfile.
- The review-archive scope regression was rerun after excluding Node dependency
  directories. Reference data and private files were not rewritten.
- Update integration: normal install, repeated install, changed-base rejection,
  corrupt-payload rejection and rollback after an injected validation failure.
  All five scenarios passed on a disposable copy of the supplied installation.
- Derived SQLite rebuild on temporary output: integrity/foreign keys passed;
  3,832 card identities and 4,594 raw printing records matched the current JSON.
- Git privacy checks: source/public viewer included; personal databases/photos,
  runtime, backups, review ZIPs, old-layout archives and dependency caches ignored.
- Workflow YAML parsed and its read-only repository permissions were checked.

## Catalogue and personal preservation

All 3,862 supplied data/research/image files remained byte-identical, including
both catalogue databases and the JSON. The default accepted catalogue remains
4,584 printing identities across four separate language ledgers. An individual
collection may have further manually confirmed printings.

All supplied personal files remained byte-identical. Installer tests compared
all personal tables, prices, notes, wishlist, manual metadata and image files;
validation used disposable database copies. Runtime, Git sentinels, unknown
root files and generated-viewer sentinels were preserved. The original catalogue
checkpoint retains SHA-256
`e79d48ff8d056d88fa0d6b1f0771f220d79f62d82797c886183e20ada9c22da0`.

Historical release tests are anchored to frozen inputs and independent golden
entry hashes. Current-release totals are asserted separately. Old research
expectations were not overwritten merely to accept today's totals.

## Practical limits

This run used Linux Python 3.12 and DOM tests with real local HTTP endpoints.
The embedded Windows executable and hosted GitHub Actions jobs were not run
here. The workflow prepares Python 3.12/3.14 checks on Linux/Windows and a Linux
interface job; they run after the user commits/pushes the source.

No native-browser visual pass is claimed. This release changes no UI layout,
card identity, printing fact, regional release date or marketplace price. These
mechanical checks are not a full factual printing audit. No Git commit, push or
website publication was performed.
