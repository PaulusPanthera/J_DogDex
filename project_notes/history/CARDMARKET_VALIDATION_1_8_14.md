# DogDex 1.8.14 — Cardmarket workflow validation

## Result

The targeted workflow and regression checks passed: **27 Python tests** and **23 JavaScript tests** across matching, catalogue rendering, picture coverage and publication. These are software checks, not an estimate of factual catalogue accuracy or filtered market valuations.

## Backend behaviour assessed

The existing 11 product-finder tests and nine additional related-product tests cover:

- Saved pretty URLs prefilling the finder without interpreting a trailing card number as a product ID.
- Recovering the existing Growlithe V1 reference for German Base Set #28, with the current saved listing retained.
- Reusing a newly saved collector confirmation from the merged catalogue, including another edition and the other Western ledger.
- A four-record Growlithe V1 batch spanning documented German and English entries, while both English Shadowless records remain outside that group.
- A separate two-record Shadowless V2 group, including First Edition and the unstamped printing, with no German V1 record included.
- Reverse-holo and regular guide series assigned independently under a common listing.
- An existing related printing's manually confirmed price-series choice remaining unchanged.
- Conflicting existing product IDs excluded from batch overwrite.
- Stale related identities and injected unrelated targets rejected before any write.
- Invalid hosts, online code products, unchecked confirmations and inappropriate reverse-series assignments rejected.
- Existing offline fallback, cache validation, cancellation/unlink, recovered Japanese references and same-day feed reuse retained.

Related-product tests use actual catalogue identities with isolated synthetic provider caches and personal records. Fixture prices are deterministic assertions, not newly researched valuations. The source snapshots are never promoted to factual printing evidence.

## End-to-end UI and export behaviour assessed

JavaScript checks include real HTTP interaction with the local Python server, rather than mocked matching results. They demonstrate:

1. A German Growlithe First Edition opens with its existing V1 URL already in the search field.
2. A product confirmed on the Unlimited printing appears first with **Reuse product**.
3. The selected product exposes four eligible V1 printing checkboxes and excludes Shadowless.
4. A single confirmation prices the selected records while retaining IDs, duplicate owned copies, costs, purchase notes and wishlists.
5. English First Edition opens V2 with English and First Edition filters; its confirmation list contains only the two Shadowless printings.
6. Minimum-condition changes update the link, persist in the browser and preserve keyboard focus, while the guide amount stays unchanged.
7. EN/DE/JA/KO language filters, First Edition yes/no, reverse-holo status and any-condition selection generate the expected query parameters.
8. Unrelated query parameters are retained, generic catalogue searches are not converted into exact offer links, and an untrusted imported canonical URL cannot become a JavaScript link.
9. Prices remain labelled **Guide**, with product-wide edition/language/condition scope in tooltips.
10. The existing Japanese Houndour search, confirmation, price, cancellation and unlink workflow continues over real HTTP.

The previous gallery/card-detail, chronology, printing-specific image selection and Data health missing-picture tests also pass. Public export checks cover the viewer at a GitHub project subpath, relative assets, sanitized publication fields, version 1.8.14, source covers, legacy collection upgrades, backup/restore and provider cache failure handling. Canonical listing URLs are retained in the published match metadata so the mobile viewer can generate the same filtered links without an editor or private API.

Commands:

```text
python -m unittest tests.test_marketplace tests.test_marketplace_groups tests.test_publishing
node --test --test-concurrency=1 tests/test_catalog.mjs tests/test_card_ui.mjs tests/test_image_fallback.mjs tests/test_marketplace_dom.mjs tests/test_marketplace_workflow.mjs tests/test_mobile_dom.mjs tests/test_publishing.mjs
```

Node DOM tests use the pre-existing jsdom development dependency. Python and JavaScript syntax checks passed. The package workflow checks SQLite integrity, ZIP CRC and file checksums; the patch overlay is compared against the complete generated bundle.

## Preservation

The original and derived catalogue databases, `data/catalog.json`, all research files and all 3,540 catalogue image assets remain byte-identical to the input 1.8.13 package. There are no catalogue additions, printing-ID changes, count changes or schema migrations. Personal matching changes occur only after the collector explicitly confirms selected targets in the existing finder. The patch contains no personal files, provider caches or generated mobile snapshot.

Tests exercise isolated fixture collections, not the collector's actual PC database. The public guide download does not provide filtered prices; no such figures are calculated or claimed here. Live Cardmarket offer-page requests were access-restricted in the preceding research and were not bypassed. A browser-binary download was unavailable in this environment, so no new pixel screenshot audit is claimed; interaction, templates, styles and public export were checked through DOM and real HTTP tests.
