# DogDex 1.8.7 UI validation

Checked 31 October 2026 against app package 1.8.6.

- **24 existing JavaScript/DOM/HTTP tests passed** (148.379 seconds). These cover catalog filtering, the real editor/backup workflow, product confirmation, read-only publishing, printing controls, language navigation, Sources/subsets, owned copies and costs.
- **3 new navigation tests passed** (6.788 seconds): header order and logo removal; category/species intersections and independent clearing; preference reload and read-only language switching. No POST mutations occur while browsing.
- **1 focused Python mobile-export test passed** (9.555 seconds): merged snapshot, private-copy fields excluded, image export and repeated managed export. Export metadata is app version 1.8.7.
- Syntax checks passed for changed JavaScript and Python files.
- Every original `data/` file (3,732 catalog, research and image files) retains its 1.8.6 SHA-256 checksum. No card/printing IDs, rarity facts, physical variants or collection schema changed. Accepted targets remain 4,535.
- The UI patch excludes `data`, `my_collection`, runtime, pictures and any prebuilt public snapshot. Mobile publication uses the user's current PC collection when Export mobile view is run.

The desktop CSS uses a 280px two-column species sidebar with 28px rows and a separate top navigation/header. This is designed to show all 41 species in a 1080p desktop window. Shorter windows retain scrolling. Mobile uses a collapsible picker and stacked filter controls.

The cloud browser could not connect to the local preview. Opening the synchronized file preview was denied by browser URL policy. No workaround was attempted. Therefore **visual Chrome/Android rendering was not verified**; layout review used DOM structure and the responsive CSS. The unavailable preview is a validation limit, not a claim that the user's local browser is blocked.

Logs are in `tests/results_1_8_7`. The package/patch builder also checks ZIP integrity and that applying the patch to 1.8.6 reconstructs every file in the full 1.8.7 package.
