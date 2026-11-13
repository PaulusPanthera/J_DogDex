# DogDex 1.8.10 — UI validation

## Scope

Header/sidebar layout only. Application version: 1.8.10. Catalogue checkpoint:
1.8.9. No catalogue re-import, source restructuring or physical-printing changes.

## Checks completed

- **10 JavaScript DOM tests passed:** navigation/header placement, health access
  with the sidebar hidden, local/public status, exact 41-species/nine-generation
  grouping, independent category/species filters, saved preferences, sidebar
  focus/node preservation, mobile browsing, storage-failure handling, gallery
  printing/copy/price behaviour and the read-only GitHub project-subpath viewer.
- **Three Python publishing/preservation tests passed:** the public export uses
  the updated static assets and version without private copy details; backup
  roundtrip preserves every personal record and source cover; an older backup
  upgrades without changing keys. These use temporary test collections.
- JavaScript module syntax and the modified Python modules were checked.
- **3,742 catalogue/research/image files** match their 1.8.9 package SHA-256
  checksums exactly. No data file changed.
- Resolved target counts remain EN **1,707**, DE **1,451**, JA **847**, KO **530**:
  **4,535** total. Roster: **41**. These unchanged counts are a regression check,
  not a claim of factual completeness or accuracy.
- The full package passes SQLite integrity, ZIP CRC and per-file manifest checks.
  Applying the flat update to the previous 1.8.9 package reconstructs all files in
  the new full-package manifest. No personal collection, `docs`, runtime or data
  files are included in the UI patch.

## Layout limits

The desktop styles allocate 23 two-column species rows. Their height budget,
including generation headings, filters, the small title and outer spacing, is
approximately **902 CSS pixels**. This fits the roughly 925-pixel content height
in the supplied screenshot at normal scaling. Shorter windows and increased
browser zoom retain the existing vertical scroll fallback.

The layout budget was checked from the styles; no new live-browser screenshot
was captured in this environment. DOM tests do not measure rendered geometry.
The public/mobile export is generated locally and must be exported and pushed
by the user to update the live GitHub Pages site.
