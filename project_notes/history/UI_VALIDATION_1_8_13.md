# DogDex 1.8.13 — Picture coverage validation

## Reproduction and result

The supplied screenshots show German Grundset Ninetales #12 with a First Edition picture and a separate Unlimited picture, but no shared reference. In 1.8.12 the Cards page rendered only `entry.image` and used `!entry.image` for its Missing pictures filter. This produced a false flag despite both gallery rows having usable printing images.

The corrected health filter evaluates picture availability for each indexed printing, including a shared reference as a permitted fallback. The entry thumbnail can use a same-entry printing image. The saved shared reference remains empty unless the collector uploads one explicitly.

## Automated checks passed

**17 JavaScript checks** passed: two targeted image-fallback tests plus the 15 existing catalogue, card UI, real HTTP editor and mobile-viewer tests. **One Python public-export check** also passed.

The targeted test uses the actual German Ninetales #12 catalogue entry and two different files uploaded through `Collection.mutate('catalog/image', ...)`. These fixture files test distinct image associations; they are not factual specimen evidence. Assertions cover:

- Two printing uploads and no shared image: Data health displays a thumbnail and omits the card from Missing pictures.
- Switching the Picture target selects the correct saved printing picture. The empty shared target is labelled explicitly.
- An explicit shared reference still takes priority in entry-level thumbnails, without overriding either printing-specific image.
- Removing one printing image restores the missing-picture flag, while the thumbnail may use the other printing's image.
- A missing Unlimited image is never filled with its sibling First Edition picture in the gallery or card details.
- Research-only and empty entries are handled without promoting claims or changing data.
- Viewing, filtering and opening editors performs no POST requests and leaves copies, costs, wishes, printing IDs, physical keys and image associations unchanged.
- A backup/restore round trip preserves both printing uploads and all fixture records without synthesizing a shared image override.
- The real mobile exporter copies both uploaded files byte-for-byte. The read-only viewer uses the correct project-relative image URLs for each printing.

Existing regression checks cover exact printing selection, ownership colour, price presentation, wishlist behaviour, chronology, card/source editing, real FileReader uploads, stable printing IDs, source covers, backup/restore and the public viewer at a GitHub project subpath. The separate Python export test confirms private copy metadata is omitted and the exported application version is 1.8.13.

Commands (Node tests require the existing jsdom development dependency):

```text
node --test --test-concurrency=1 tests/test_image_fallback.mjs tests/test_catalog.mjs tests/test_card_ui.mjs tests/test_editor_dom.mjs tests/test_mobile_dom.mjs
python -m unittest tests.test_publishing.PublishingTests.test_public_snapshot_uses_merged_data_and_only_public_ownership
```

JavaScript and Python syntax checks passed. Full-package SQLite checks, ZIP CRC/checksums and patch-overlay checks are performed by the release packaging workflow.

## Preservation and limits

Compared with the input 1.8.12 package, `data/catalog.json`, the original `data/catalog.sqlite3`, the derived `data/catalog-collector.sqlite3`, and all catalogue image assets remain byte-identical. The patch contains no `my_collection`, catalogue data, uploaded pictures or generated `docs`. There is no database migration.

Tests used isolated fixture collections, not the collector's current PC database. No live pixel-layout audit was required: this changes image selection and issue detection, with the existing layout retained. Image availability is not image authenticity, exact specimen verification, printing verification or factual catalogue validation. Those states and their audit findings remain separate.
