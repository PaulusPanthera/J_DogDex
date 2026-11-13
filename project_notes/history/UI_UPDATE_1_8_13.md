# DogDex 1.8.13 — Data health picture coverage

The German Grundset Ninetales #12 report exposed a presentation error: both printing pictures could be saved and displayed correctly in the gallery, while Data health still showed a blank thumbnail and listed the card under Missing pictures. The health page only inspected the optional shared reference image.

## Corrected behaviour

- A card leaves **Data health → Missing pictures** when each indexed printing has an available picture, either its own printing image or the shared card reference.
- An available picture for one printing does not conceal a genuinely missing picture for another printing.
- For a card without indexed printings, picture coverage is checked against its shared reference. Recorded printing claims are checked separately when present.
- Data health thumbnails prefer the shared reference, then a picture from that same card's accepted printings, then its recorded printing claims. This is a display fallback, not a new shared image assignment.
- The Picture tab's empty shared slot says **No shared reference saved**. If an overview can use a printing image, the editor identifies that fallback. Uploading a duplicate shared picture is unnecessary.
- Existing exact printing pictures continue to display on their own gallery rows and detail views. No sibling printing or other language is substituted for a missing exact printing image.

## Verification remains independent

Picture availability resolves a missing-picture issue. It does not mark a representative picture as a verified specimen, confirm a physical finish, or alter the separate printing-image audit. Existing image kinds, exact-image verification, provenance and historical findings are retained.

## Scope and preserved records

No catalogue records, printing IDs, collection data, pictures or database schemas change in this patch. The 1.8.12 English Unlimited additions and selected German Skyridge date remain unchanged. No shared picture is written automatically. Ownership, costs, wishlists, manual corrections, source covers and all existing picture overrides remain stored as before.

Updated modules: `static/catalog.mjs`, `static/editor-ui.mjs`, `static/app.js`, and cache versions in `static/index.html`. Export metadata and the package builder advance to 1.8.13. The mobile export continues to copy each existing printing picture under its original file name.

## Installation

Close DogDex, extract **DogDex_UI_Update_1_8_13.zip** directly into **J_DogDex**, and merge/replace the supplied files. Restart DogDex and refresh the browser. The patch contains no `my_collection`, `data` or `docs` replacements. No picture reuploads or manual data repair are needed for the reported case. Re-export the mobile view and commit/push `docs` if publishing the updated viewer.

See `UI_VALIDATION_1_8_13.md` for the reproducible checks.
