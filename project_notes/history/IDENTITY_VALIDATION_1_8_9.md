# DogDex 1.8.9 validation

## Factual review

The focused pass assessed five existing EN/DE identities: German Illumina City 077 and English/German Mega Zygarde ex 104 and 120. It completed the German stadium's documented identity and physical printings, excluded 104's non-canine forms from completion, and retained 120's canine cameo.

Facts, source lineage, original assertions, cached provider rows, exact selected changes and remaining limits are in `data/research/identity_189/`. This is not a catalogue-wide accuracy estimate.

## Software and collection checks

- **34 distinct JavaScript/DOM/real HTTP checks passed**, completed across the regression run and focused finishing batches. These cover the existing UI, search/product confirmation, source/subset/product navigation, editor, printing selection, language boundaries, mobile viewer and new card/form outcomes. `ui_summary.json` lists the distinct check names and contributing logs.
- **3 focused Python checks passed**: idempotent data corrections, exact form-scope matching without regional inference, and a simulated pre-update collection upgrade.
- **17 existing Python regression checks passed**, covering previous printing corrections, source structure, backup/restore and mobile export. The historical exact-delta expectations were extended by the five reviewed identities and two restored printing IDs; unrelated changes still fail those assertions.
- The preservation fixture includes duplicate physical copies, misprint notes, prices paid, wishlists, a manual label, a pre-existing manual 077 printing, and printing-specific picture overrides. The update leaves their stored rows and image bytes unchanged. Matching the full physical tuple suppresses the new derived normal-printing default in favour of the existing manual ID.
- Owned excluded 104 copies remain visible, editable and recoverable through backup restore. They are excluded from completion. The mobile snapshot retains their ownership and the reason for exclusion while keeping private costs/notes out of the public export.
- Python and JavaScript syntax checks passed.

Logs are under `tests/results_1_8_9/`. The first broad JavaScript log has no suite footer; the remaining cases were completed in separate batches, with all 34 distinct checks accounted for. An initial pair of obsolete historical-baseline assertions was updated to reflect the reviewed delta, then the 17-check Python regression run passed.

## Dataset preservation

- All **3,820 existing active identity IDs** and all **4,543 previous physical printing IDs** remain stored. Exactly **five existing identities** changed.
- Two printing IDs were added to the existing German 077 identity; no duplicate identity was created.
- Every JA/KO entry is unchanged. Archived/retired entries are unchanged.
- Of the original manifest's data files, only `data/catalog.json` and its derived `data/catalog-collector.sqlite3` changed. The original `data/catalog.sqlite3` and all prior research/image files retain their SHA-256 values.
- The shared catalogue gains one native German illustration and the focused evidence checkpoint. The update ZIP contains no `my_collection/`, `docs/` or `runtime/` replacement.
- Confirmed totals are EN **1,707**, DE **1,451**, JA **847**, KO **530**: **4,535** in total.

The generated full ZIP is checked for CRC errors and per-file SHA-256 consistency. The update ZIP is checked against the full release and for prohibited personal-data paths.

## Limits

Native German images and the manufacturer checklist were visually inspected. The reverse printing has a direct German merchant assertion and explicit native provider tuple, but no exact reverse physical specimen image was inspected. No foil pattern beyond unspecified reverse holo is claimed.

No current user PC collection dump was supplied. Preservation checks use representative fixtures, not the user's actual current collection database. No new visual browser verification of the application is claimed in this data release.
