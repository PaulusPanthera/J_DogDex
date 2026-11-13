# DogDex 1.8.9 identity correction validation

34 distinct UI checks, 3 focused identity/preservation checks and 17 existing Python regression checks passed. Five existing identities changed; all prior IDs, archived entries and Japanese/Korean records are preserved. See IDENTITY_VALIDATION_1_8_9.md for evidence, logs and limits.

# DogDex 1.8.8 UI validation

33 UI regression tests and 3 collection/export checks passed. Set assets are included in local and mobile builds. Catalogue files are byte-for-byte unchanged. See UI_VALIDATION_1_8_8.md for logs, scope and the visual browser limitation.

# UI release 1.8.7

Current checks: UI_VALIDATION_1_8_7.md — 27 JavaScript/DOM tests and one Python export test passed; unchanged catalog data. Visual browser preview unavailable in this environment. Historical validation follows.

# Printing correction release 1.8.6

Current checks: PRINTING_VALIDATION_1_8_6.md — 69 Python and 24 JavaScript/DOM tests passed, reproducible correction delta, preserved original IDs and representative collection upgrades. Earlier sections below describe historical releases.

# Source structure release 1.8.5

See SOURCE_VALIDATION_1_8_5.md for the current source/navigation and collection-preservation checks. All catalog bytes and printing IDs remain unchanged from the underlying 1.8.4 checkpoint. Earlier validation follows.

# DogDex 1.8.4 validation

## Software and collection preservation

- The 96 existing Python regression checks were exercised. After fixing the image-only overlay and legacy validation exception handling, the affected collector/HTTP (19), completion/upgrade (7) and regional-research (8) suites were rerun successfully. Other suites had passed in the full run. Nine new printing-system tests also passed after those fixes.
- New tests cover the bounded data delta, exact preservation of every unreviewed entry hash and old ID, JA/KO facts, idempotence, synonym duplicate rejection, distinct Energy/Friend Ball IDs, separate evidence states, stable copy IDs/costs/wishes, printing-specific image preservation, invalidated stale photo/price checks, equivalent manual records, automatic pre-upgrade backup and v4 restore, unsupported modern edition/layout rejection, and the diagnostic severity split.
- Existing 19 JavaScript/DOM checks passed across catalogue, card UI, editing, mobile, prices/rarity and Cardmarket finder. The large editor flow passed separately after increasing its test timeout for this environment; its real HTTP uploads and backup restore completed successfully. The test command now runs suites sequentially to avoid competing fixture servers.
- Three new JavaScript checks passed: pure localized identity matching, physical completion deduplication, and a real HTTP/DOM flow through prefix/source/flag switching, missing card/printing/regional fallbacks, contextual pattern/source controls, two separately added reverses, duplicate rejection, independent image controls, preserved ownership and server restart. Expanding source choices remains language-specific.
- Python syntax and JavaScript syntax checks passed. The full offline rebuild reproduces catalogue JSON and derived SQLite byte-for-byte. The original SQLite checkpoint remains `e79d48ff8d056d88fa0d6b1f0771f220d79f62d82797c886183e20ada9c22da0`.
- The Windows runtime is retained. Native Windows execution cannot be tested in this Linux environment. Local HTTP tests use isolated temporary collection folders, not the user's PC collection.

## Factual scope, measured separately

- Ten existing ASC identities in English and ten in German were reconciled against a manufacturer-branded checklist, card-specific release notes, set reporting and native German inventories. The reviewed expected regular-printing denominator is 22 per language. Twenty existing base printing IDs remain; 24 named reverses were added. Ex/illustration identities received no inferred reverses. Okidogi retains Rare + base Holo.
- The mirrored checklist was visually assessed for numbering/rarity/base holo; it contains no reverse-pattern columns. Pattern evidence was evaluated separately. Source lineage, retrieved observations and access limits are in `approved_variants.json`. No personal specimen inspection or exact foil-image verification is asserted.
- The saved-claim scan covers 3,820 records across 41 roster species and four ledgers. It retains 514 unresolved active claims and 771 review findings. There are 9,018 image/market information findings and zero confirmed structural/specification findings in the stock catalogue after correction. These figures are not a worldwide coverage denominator or accuracy estimate.
- All pre-existing raw printing IDs remain. All raw JA/KO entries and every unreviewed entry hash match 1.8.3. No automatic Cardmarket confirmation is added. Provider candidate IDs remain suggestions.

## Visual and package checks

- Desktop and 390 px layouts were inspected through the supported browser preview: card details, language flags, compact physical selection, prominent owned copy, grouped printing form, contextual sources and separate verification controls. The Data health diagnostics distinguish information from confirmed problems and show the reviewed 22/22 scope explicitly. Layout snapshots use example QA copies; functional checks use real HTTP separately.
- Mobile export remains read-only, works at a GitHub project subpath, and strips purchase costs, private copy notes, evidence URLs, tokens, local database/cache and editor/finder implementation. It includes canonical source keys and normalized public physical keys for the same navigation and counting behavior.
- Full/patch packaging verifies CRC and per-file hashes. Patch equivalence is checked against the authoritative 1.8.3 full package. The data-bearing patch excludes the original SQLite checkpoint, unchanged runtime/images, all personal collections and temporary QA files. The full package contains the same update.

Software tests and populated fields do not establish factual catalogue accuracy. There is no global completeness or accuracy percentage in this release.

## Historical validation records

# DogDex 1.8.3 validation

- 19 JavaScript/DOM checks passed across the catalogue, price/rarity, card UI,
  editor, mobile and new product-finder suites. The finder test uses a real local
  HTTP server: native Japanese reference recovery, explicit selection/confirmation,
  regular holo price series, saved prices, pretty URLs, cancellation, unlink and
  retained copy IDs/costs/notes/wishlist. Candidate labels are HTML escaped.
- 27 Python checks passed across publishing/price (7), editor (9) and product
  lookup (11). Coverage includes daily atomic caching, failed-refresh retention,
  stale identity rejection, non-holo/reverse distinction, no automatic promotion,
  excluding code-card products, existing overrides and fresh matches in v4 backup
  round-trips. Factual database accuracy is not inferred from these checks.
- Live official downloads succeeded: 75,066 product rows (source catalogue dated
  2026-10-29T14:18:13+0100) and 80,170 guide rows. Japanese Houndour SV3 #115
  surfaces candidate 724971; German Rockruff TG07 surfaces compatible Western
  reference 682271. Feed size is not matched coverage or verified card identity.
- Rendered desktop and 390 px layouts inspected through the supported preview:
  larger gallery, wrapped set names, header metadata, prominent owned records,
  compact market amount, candidate results and separate confirmation step.
  Preview used isolated QA records; functional interaction checks are separate.
- Mobile export remains read-only and omits the editor/finder implementation,
  lookup cache, ownership notes and paid costs. Confirmed price snapshots export.
- Catalog JSON and both SQLite checkpoints remain byte-identical to 1.8.2. The
  41-species roster, all card/printing IDs and accepted-target counts are unchanged.
- Release packaging checks full/patch CRC, per-file hashes and cumulative patch
  equivalence against 1.8, 1.8.1 and 1.8.2. No catalog data, runtime, evidence archive
  or user collection/cache is in the patch. Native Windows execution remains
  untested in this Linux environment; the existing Windows runtime is retained.

# DogDex 1.8.2 validation

- 18 JavaScript checks passed: catalog behavior, regional/era rarity presentation,
  per-printing guide price selection and fallbacks, desktop card UI, copy editing,
  full-color detail/grayscale overview, read-only GitHub-subpath viewer, and the
  complete editor/picture/backup workflow over a real local HTTP server.
- 7 Python publishing/price checks passed, including identity-bound price mapping,
  cache behavior, mobile export and collection preservation.
- Visually inspected rendered application markup at desktop and 390 px widths
  through the supported preview. Included owned Rockruff, rarity/finish badges,
  collapsed prices and responsive gallery/detail layout. Browser preview used
  isolated QA records; functional interactions were checked by the HTTP/DOM tests.
- The three catalog checkpoints are byte-identical to 1.8.1. No owned records,
  manual overrides, wishlist, picture assets or price cache is shipped in the patch.
- Full package and small-patch CRC/checksum checks and patch-to-full equivalence
  are verified during release packaging. No factual database accuracy is inferred
  from these software/layout checks.

# DogDex 1.8.1 UI validation

- 17 JavaScript/DOM tests passed across the existing 16-check suite and one new
  card interaction/search regression. They cover the German Vulpix 91 caption,
  exact printing selection, ownership/cost associations, image loading priority,
  grayscale previews/full-colour details, source-cover backup/restore and mobile
  read-only operation. Search results match the previous per-field behavior
  across every catalog printing for six representative queries.
- Date-label microbenchmark, 400 month/day labels, three runs: previous code
  69.05/74.33/72.36 ms; cached formatter 1.51/1.54/1.24 ms in this runtime. This
  measures date formatting only, not page load, browser paint or end-to-end speed.
- Catalog JSON and both SQLite catalog files are unchanged from 1.8. No personal
  schema, collection storage, IDs, costs, wishlist or picture overrides change.
- A native browser visual pass could not be completed: the browser cannot reach
  this workspace's localhost and its policy disallows file-protocol previews.
  No browser-policy workaround was attempted. DOM/CSS checks and the normal
  real-HTTP interaction suite provide the available verification; final native
  appearance should be checked on the user's desktop/mobile browser.
- Bundle packaging verifies ZIP CRC and manifest checksums. The small update
  contains application, documentation and test files only, with no data or
  my_collection paths. Native Windows execution remains untested here.

Previous validation follows.

# DogDex 1.8.0 software validation

This release changes usability and publishing, not the factual catalog.

- 85 unique Python checks passed across the full run and targeted follow-ups.
  The first 84-test run passed 83: the remaining test still asserted the old v3
  backup version. Its expectation was updated to v4 and the complete round-trip
  test passed on rerun. The six initial publishing checks passed, followed by a
  seventh explicit price-mapping/identity-change check. Functional preservation
  assertions were retained.
- 16 JavaScript/DOM tests passed, including a real localhost HTTP session and a
  read-only viewer at a GitHub project subpath. Coverage includes no mobile edit
  controls or mutation requests, ownership quantities, relative asset paths,
  source groups, Cardmarket queries, price labels and manual override priority.
- Upgrade/backup checks retain original copy IDs, costs, wishes, card/printing
  corrections, manual sources and image overrides. New source covers survive v4
  round-trips. Legacy v3 backups upgrade without changing copy IDs.
- Export checks use the merged catalog, omit private record fields and databases,
  include custom source images, support repeat exports, and refuse to overwrite
  an unrelated docs folder. No editing API, token or editor implementation is
  exported. Public hosting is configured by the user in GitHub Desktop/Pages;
  no GitHub repository or live deployment was created during these checks.
- A real official price-guide download succeeded: 80,170 product rows, source
  timestamp 2026-10-29T02:52:59+0100. This count is feed size, not matched DogDex
  coverage. The unchanged catalog initially has zero explicit 1.8 price-series
  confirmations; quarantined candidates are not automatically priced. Mocked
  confirmed mappings verify price display; malformed refreshes retain old cache.
- catalog.json, original SQLite and derived SQLite are byte-for-byte identical
  to the delivered 1.7 package. All identities, physical IDs and factual research
  remain unchanged. These software checks are not new factual accuracy findings.
- Bundle checks verify manifest hashes and ZIP CRC. Native Windows runtime
  execution and actual GitHub deployment are not performed in this environment.

Current catalog JSON SHA-256:
`4fb01790630a2a15312c2cb31f26de7720f78f3ee577bb3b771eeb5bcd50a6f3`.

Previous release validation follows.

# DogDex 1.7.0 software validation

Factual specimen review and source coverage are reported separately in DATA_AUDIT_1_7.md.

- 78 Python tests passed across the full suite and targeted reruns. The first full run passed 74; four historical no-JA/KO-change guards were then scoped to the immutable 1.6 boundary and all four passed on rerun. Their original expected hashes were retained. The authorized 1.7 changes are protected by new strict EN/DE and stable-ID checks.
- 12 JavaScript/DOM tests passed with real local HTTP. The scenarios include visible Japanese provisional tiles and documented Korean identities without a known finish, research visibility toggles, evidence links, the approved sidebar, gray unowned previews and full-colour details.
- The six new JA/KO regression tests cover all previous active/retired IDs, no cross-language physical generation, no printed-rarity inference from Korean S12a catalog tiers, Mega marks, primary hosts versus cameo-only cards, and promotion of an incomplete identity without making a second ID.
- A 1.6-to-1.7 fixture retains owned copies, EUR costs, wishlist, manual names, source corrections, explicit printing corrections and exact picture overrides. A collector's saved printing correction takes precedence over a new catalog foil qualification.
- Two final offline builds have identical catalog JSON and derived SQLite bytes. The immutable original SQLite remains unchanged. Integrity and foreign-key checks pass.
- 3,820 visible identities/claims, 4,493 raw physical IDs, 4,485 accepted targets and eight held physical claims. Provisional entries do not increase confirmed totals. These are software invariants, not a factual accuracy estimate.
- package.py checks every manifest hash and ZIP CRC. A separate fresh-extraction HTTP check is recorded in the companion evidence receipt.
- The bundled Windows x64 Python runtime and launcher are retained. Native Windows execution was not performed in this Linux environment.

Final catalog JSON SHA-256: `4fb01790630a2a15312c2cb31f26de7720f78f3ee577bb3b771eeb5bcd50a6f3`.
Final derived SQLite SHA-256: `b9c9563bda21ed4d4742748a68ba0c041bbdd96cd21bb6959c3c23e3429ca14c`.
Original SQLite SHA-256: `e79d48ff8d056d88fa0d6b1f0771f220d79f62d82797c886183e20ada9c22da0`.

Previous release validation follows.

# DogDex 1.6.0 software validation

Software and collection-upgrade checks are separate from factual assessment in DATA_AUDIT_1_6.md.

- 72 Python tests passed; 12 JavaScript/DOM tests passed, including a real local HTTP server.
- Every prior active or retired identity and physical ID remains addressable. The 41-species roster and JA/KO canonical entries are unchanged.
- Upgrade fixtures preserve owned copies, prices, wishlist, manual name/identity corrections, older explicit printing confirmations, shared pictures and exact printing picture overrides.
- A disputed physical ID remains editable, accepts additional picture evidence and can be promoted without making a duplicate. It does not count as confirmed. Existing paid cost remains in collection totals.
- Visible provisional tiles can be searched and hidden through the research control. Evidence links are rendered in the existing editor.
- Two offline builds produced identical catalog JSON and derived SQLite bytes. Both databases passed integrity and foreign-key checks.
- The original research SQLite remains e79d48ff8d056d88fa0d6b1f0771f220d79f62d82797c886183e20ada9c22da0.
- The approved dark layout is retained. Unowned overview pictures remain gray; details remain full colour.
- package.py verifies manifest hashes and ZIP CRC before delivery. A fresh extraction is then checked through local HTTP; its receipt is in the research evidence archive.

Catalog JSON SHA-256: `4af5d62d42d6e0c69f952121accca3adcf0b14d50947ac70c25637a9c34191fe`.

The included Python 3.14.10 Windows x64 runtime and launcher are retained. Native Windows execution was not performed in this Linux environment. Test success is not an overall database accuracy percentage.
