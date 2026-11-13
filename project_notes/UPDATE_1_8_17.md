# DogDex 1.8.17

The project root now contains launchers and a short README. Application modules
are in `dogdex/`, maintenance commands in `tools/`, and old release/audit notes
in `project_notes/history/`. The root `app.py` remains the stable launcher.
Existing personal files and generated viewer content are preserved.

The update adds 12 regional card identities and 22 accepted printing targets:
18 Delta Reign printings, two Classic Collection Zacian V printings, and two
previously provisional German 30th Lucario cameo printings. Existing 30th foil
targets are qualified with the visible anniversary mark while retaining IDs.
No unmarked duplicate is generated.

Classic Collection is an internal subset of 30th Celebration / 30 Jahre. Zacian
V uses its printed `138/202`, with provider checklist position `028` retained
separately. Main-set Lycanroc `138` remains a separate card. Numbered promos
stay in their own ledger.

The generated public viewer now includes the editor stub method expected by
1.8.16's selection UI. Optional selection synchronization also tolerates a
missing editor in read-only mode. English reference images used in German
entries are identified in the detail view.

`CREATE_REVIEW_ZIP.bat` creates a current private project snapshot without old
ZIPs, runtime files or generated viewer copies. It uses SQLite's backup API
rather than copying a live database/WAL pair. It includes personal purchase
notes, costs, edits and images, so it is intended for a private project review.

Use the update ZIP for an existing installation. Close the server, extract the
ZIP into the existing folder, run `UPDATE_DOGDEX.bat`, then start normally.
The full package is an alternative for a new installation, not a second update
that needs to be copied on top. Re-export the mobile viewer before publishing.
