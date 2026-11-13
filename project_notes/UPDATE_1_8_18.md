# DogDex 1.8.18 — reliability and source tracking

Application code is 1.8.18. Catalogue facts stay at revision 1.8.17: no card,
printing, rarity, date, image or distribution identity is changed by this update.

- Repaired imports in the relocated reconciliation/completion audit commands.
- Made maintenance imports and `--help` safe: source-structure generation no
  longer runs merely because its module is imported.
- Made text reads/writes explicitly UTF-8 for German/Japanese/Korean data on
  Windows, including maintenance commands and fixtures.
- Historical tests now check their original release boundaries. Frozen inputs
  and independent golden hashes anchor reconstructed releases; current data
  has a separate release contract. Superseded 30th estimates remain in history.
- The standard DOM command now includes image fallback and shared-product
  Cardmarket workflow checks. Public exports use the application's version.
- Added CHECK_DOGDEX.bat and tools/check_project.py for mechanical diagnostics.
  Personal validation runs on a temporary database copy. A report is written
  only when requested, under my_collection/checks/ in the Windows launcher.
- Added a pinned interface-test dependency lockfile, source tracking rules,
  DEVELOPMENT.md and a read-only GitHub Actions check workflow. No files are
  staged, committed, pushed or published by the installer.

Install only the update ZIP into an existing 1.8.17 installation, close DogDex
and run UPDATE_DOGDEX.bat. The installer backs up changed managed files and a
coherent collection database, validates owned IDs on a disposable copy and
rolls back managed files if validation fails. The full Windows ZIP is a fresh
installation package; it is not a second required update.

All personal table rows, images, metadata and prices were compared before and
after installation. The installer supports further collection edits made after
the review; no ownership or wishlist total is hardcoded.

After installation, run CHECK_DOGDEX.bat. Export the mobile viewer again when
you want the public view to reflect this application version. Review Git's
proposed changes before committing the newly tracked source.

This release does not claim a full factual audit of all collectible printings
or all regional artwork images. That remains separate from software tests.
