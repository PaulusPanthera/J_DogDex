# Working on DogDex

The Windows app uses Python's standard library. With an installed Python 3.12
or 3.14, run these commands from the project folder:

```sh
python tools/build_index.py
python tools/check_project.py
python app.py --no-browser
```

`build_index.py` rebuilds only `data/catalog-collector.sqlite3` from the current
reviewed JSON. It does not rerun research stages or replace catalogue facts.
The immutable `data/catalog.sqlite3` is an original checkpoint; do not edit it.
The application and current catalogue data revision are 1.8.19.

## Tests

```sh
python -m unittest discover -s tests -v
npm ci --prefix tests
npm test --prefix tests
```

Python tests need no pip packages. Interface tests need Node 24 and the pinned
jsdom dependency. `tests/package-lock.json` fixes transitive dependencies.
Pillow is needed only for image preparation, outside the ordinary app/tests.

Historical audit boundaries use frozen catalogue inputs and reconstructed
stages in `tests/catalog_history.py`. Independent, frozen golden hashes verify
those reconstructions. Current behaviour and release totals are checked
separately. A newer fact must not silently rewrite an older audit expectation.

The GitHub workflow checks Python 3.12/3.14 on Linux and Windows, and DOM
behaviour on Linux. These jobs start only after the files are committed/pushed.
No deployment or publication step is included.

## Source control and private data

The ignore rules now allow application source, tests, public catalogue/evidence,
interface assets, project notes and the existing `docs/` viewer. They exclude
`my_collection/`, the embedded runtime, review ZIPs, backups, generated SQL,
previous-layout archives, caches and unknown root files. Existing tracked files
are unaffected by ignore rules: review `git status` and the proposed diff
before committing. Never use `git add -f` on private data.

The original SQLite checkpoint is just below GitHub's per-file limit and must
stay immutable. Do not add new database dumps to Git. The bundled Windows
runtime stays in the download package, not the source repository.

This release does not stage, commit, push or publish anything. The public
viewer still updates through DogDex's Export mobile view command and your
existing Git workflow. It exposes ownership/wishlist data as before.

## Project checks and review archives

`CHECK_DOGDEX.bat` checks catalogue identities, physical tuples, cached images,
SQLite integrity and owned IDs. Its summary is saved under
`my_collection/checks/latest.json`. Personal database validation runs against a
temporary copy. These mechanical checks do not verify every factual printing.

`CREATE_REVIEW_ZIP.bat` includes source, catalogue/evidence and private collection
records/images. Runtime, generated viewer, Git history, backups and old ZIPs
are omitted. Share a review archive only for the intended review.

Maintenance scripts under `tools/` can be imported or called with `--help`
without regenerating evidence. Running an audit without `--help` can still
write audit outputs; use a disposable checkout when reproducing old audits.
