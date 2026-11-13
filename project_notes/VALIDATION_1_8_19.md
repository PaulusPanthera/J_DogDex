# DogDex 1.8.19 validation

- 158 Python regression checks pass, including the bounded 21-printing delta,
  deterministic replay, frozen historical boundaries, current release totals,
  physical-key deduplication and collection preservation.
- 44 DOM/interface checks pass with the pinned dependency lockfile.
- Final focused reference/finder runs pass: 5 reference tests and 20 marketplace
  tests. They check pattern/stamp/size isolation, native type normalization,
  unchanged confirmation rules, saved-link reuse and separate Base Shadowless.
- Six updater scenarios pass: normal install, idempotent repeat, unexpected
  catalogue rejection, older application with the same catalogue rejection,
  damaged payload rejection before mutation, and rollback after an injected
  post-install validation failure. Runtime, existing viewer, Git sentinel and
  unknown root files remain intact. Personal table rows and files are unchanged.
- Mechanical project diagnostics pass: SQLite integrity, unique IDs/tuples,
  JSON/index agreement, 3,554 cached image files, and resolving owned IDs.
- All 3,832 existing entry IDs and 4,594 existing raw printing IDs/physical keys
  survive. No existing non-candidate printing field changes. JA/KO catalogue
  records and the original SQLite checkpoint are byte/hash anchored unchanged.
- New raw total: 4,615. Generic accepted total: 4,605 (EN 1,757; DE 1,471;
  JA 847; KO 530). A personal manual printing may add one to that denominator.
- No ownership, price, manual metadata or image replacement is shipped in the
  public release. The personal review and its open questions are separate.

Checks ran in the preparation environment. Native Windows startup and hosted
GitHub Actions were not run. Software tests verify implementation and retained
facts, not population-wide catalogue accuracy. Specimen images remain outside
this review. No repository write or public deployment was performed.
