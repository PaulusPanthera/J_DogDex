# Resume the systematic English/German audit

Start with `work_queue.json`, not another broad discovery search. Scope remains 41 species, with the agreed excluded families/forms. EN/DE are the priority; JA/KO entry records are unchanged.

- `baseline_inventory.json`: frozen 1.3.2 measurements, all-language card inventory, per-species, per-release and per-source groups; later detectors were also applied to the same frozen input.
- `current_inventory.json`: same measurements after 1.4.0.
- `inventory_reconciliation.json`: all 957 cached international species rows compared with each western ledger; native availability and scope exclusions are separate from identity matching.
- `cameo_reconciliation.json`: existing English cameo source pool compared with German identities. This is a candidate queue, not a universal external cameo denominator.
- `manufacturer_checklists.json` and `publisher_evidence.json`: language-specific publisher URLs, response hashes, compact factual rows, extracted rarity symbols and own-PDF checkbox legends/geometry. Do not treat an empty or unavailable checklist as proof of absence.
- `native_cameo_evidence.json`: native API records and exact image hashes. A translated API listing alone was insufficient; accepted additions also required reviewed German images and publisher printing evidence.
- `reviewed_facts.json`: explicit changes and accepted physical tuples. Source type and uncertainty remain attached. Do not generate variants from rarity or from another language.
- `evidence_log.json`: evidence pointers used by the current reviewed changes.
- `sample_plan.json` and `sample_audit.json`: fixed 80-record sample; unassessed fields do not count as correct. No whole-catalog accuracy estimate.
- `upgrade_baseline.json` and `upgrade_test_fixture.json`: stable identity/secondary-language checks and an upgrade fixture; neither contains user collection data.
- `audit_summary.json`: machine-readable before/after changes, counts and limitations.
- `software_validation.json`: software results, separate from source-based factual validation.

Offline reproduction from the bundled immutable database and cached facts:

```sh
python catalog_enrich.py
python reconcile_catalog.py
python -m unittest discover -s tests -p 'test_*.py'
```

New research should add a dated evidence assertion, resolve or retain its queue item, then rebuild. Keep original IDs and all personal overlays. Raw HTML/PDF download caches are not part of the app package; compact factual evidence, document hashes, source URLs and exact native images used by accepted entries are retained. Do not claim that separate websites are independent when they reuse the same upstream dataset.

The full publisher PDF cache and source-preparation scripts are retained separately as DogDex_Research_Evidence_1_4.zip. Its folder structure restores systematic_audit/work and the frozen baseline; place the app from the main bundle under systematic_audit/DogDex to reuse the cached preparation scripts.
