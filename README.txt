DogDex 1.8.19

Start with START_DOGDEX.bat. The full Windows package includes Python.

This release repairs maintenance commands, separates historical audit tests from
current-release checks, adds CHECK_DOGDEX.bat and prepares source tracking and
GitHub checks. Catalogue facts remain at data revision 1.8.17, including the
30th Celebration / 30 Jahre and Delta Reign / Delta-Herrschaft additions.

Folder guide
  app.py, START_DOGDEX.bat    Application launchers.
  CHECK_DOGDEX.bat            Read-only project and collection diagnostics.
  dogdex/                    Application code.
  static/                    Interface, flags, symbols and logo.
  data/                      Shared catalogue, images and source evidence.
  my_collection/             YOUR collection, prices paid, edits, pictures, backups.
  runtime/                   Bundled Windows Python. Keep this folder.
  docs/                      Generated read-only GitHub Pages viewer.
  tools/                     Maintenance, audits, packaging and review ZIP tool.
  tests/                     Automated regression checks.
  project_notes/             Current notes; historical notes are in history/.

Update an existing installation
  1. Close the DogDex server window.
  2. Extract the UPDATE ZIP directly into your existing DogDex folder.
  3. Run UPDATE_DOGDEX.bat, then start DogDex normally.

The updater backs up changed managed files and a coherent personal SQLite copy
under my_collection/backups/. It archives the known old root modules and notes,
keeps unknown files, checks that personal records are unchanged, and validates
owned printing IDs on a temporary database copy. It does not replace your
runtime, docs export, collection or Git folder. In-app personal edits are
supported; a different manually modified base catalogue stops the installer
for reconciliation. Do not copy an older full package over this update.

Backups and future reviews
  Use Backup & Trash in DogDex for collection backups. Keep another copy outside
  this folder. CREATE_REVIEW_ZIP.bat creates a review ZIP beside the DogDex folder.
  It includes code, catalogue, research, collection, manual edits and pictures.
  Runtime, generated docs viewer, Git history, old ZIPs, caches and backups are
  omitted. The review ZIP contains private purchase costs and notes. Share it
  only for the intended project review.

GitHub Pages
  Use Export mobile view again after updating, then commit and push docs through
  the existing GitHub workflow. Nothing is published automatically. The viewer
  contains ownership counts and wishlist entries, not private copy notes/costs.
  Ignore rules now also allow the public app source and automated checks.
  Review git status before committing; collection data remains excluded.
  This update does not stage, commit, push or publish files. See DEVELOPMENT.md.

Developer commands, from the DogDex folder
  python app.py --no-browser
  python tools/build_index.py
  python tools/check_project.py
  python tools/audit_catalog.py --help
  python tools/create_review_zip.py
  python tools/package.py
  python -m unittest discover -s tests -v

The application/updater use Python's standard library. Preparing reference
images also needs Pillow; DOM tests need Node and jsdom; browser smoke checks additionally need Playwright.
Those are development dependencies, not application requirements.

Artwork currently has Standard and Full Art classifications. Illustration Rare
and Special Illustration Rare are rarities; holo and reverse holo are finishes.
Japanese and Korean rarity codes remain independent of Western rarity labels.

See DEVELOPMENT.md and project_notes/UPDATE_1_8_19.md.
Catalogue evidence is recorded in project_notes/DATA_SOURCES_1_8_17.md.
