# DogDex 1.8.20 validation

The shared catalogue adds seven entries, promotes four research identities in
place, adds 12 physical printings and repairs eight species links. Every one of
the 3,832 previous entry IDs and 4,615 previous printing IDs survives. All prior
physical keys and complete printing-field hashes match the 1.8.19 checkpoint.
The roster, original SQLite checkpoint and all JA/KO entries remain hash-identical.

The positive coverage registry checks 153 EN/DE host/species/language cases and
12 explicit new physical identities. Mutation tests check dropped hosts, missing
links, duplicate canonical identities, lost STAFF stamps and unreviewed provenance
drift. The import stage refuses unreviewed collisions and does not generate reverse,
regional or placement variants from provider defaults.

The source pipeline reproduces the final catalogue semantically from the original
checkpoint and frozen facts. JSON object key order can differ between a rebuild
and applying a patch to the published catalogue; records and values agree.

Mechanical checks cover SQLite integrity, unique IDs/physical tuples, JSON/index
agreement and 3,566 cached references. The supplied private snapshot is checked
on disposable copies: active copies, wishlist, prices, edits, images and every
original private file remain unchanged. Temporary SQLite WAL/SHM bookkeeping
files are excluded from that file comparison. Private counts and personal audit
results are kept out of the public release bundle.

Generic accepted targets: EN 1,763; DE 1,477; JA 847; KO 530; total 4,617.
Raw printing records: 4,627. Entries: 3,839. A personal manual printing can increase
the displayed total.

Regression results: 172 Python checks pass, with a final focused run of all
14 cameo checks after the finish-conflict correction. All 44 DOM/interface checks
pass, including the actual exported viewer. Six updater scenarios pass: ordinary
installation, idempotent repeat, unexpected catalogue rejection, older application
rejection, damaged payload rejection before mutation and rollback after an injected
post-install failure. The final archive is checksum-verified and installation is
rechecked against the packaged payload. Native Windows startup and hosted GitHub Actions are not run in this
preparation environment. No repository commit, push or publication is performed.
Software tests protect implementation and accepted facts; unresolved physical
and regional claims remain documented and do not imply complete population coverage.
