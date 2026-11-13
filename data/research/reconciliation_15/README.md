# DogDex 1.5 reconciliation checkpoint

`baseline_140.json` is the immutable delivered 1.4 catalog. `baseline_inventory.json` and `current_inventory.json` contain complete language/species/set/source inventories. The original 1.4 research folder remains historical.

`reviewed_facts.json` drives `reconciliation_enrich.py` after all earlier stages. `field_verification_ledger.json` consolidates earlier facts and distinguishes populated data, provider assertions, prior review claims, inference, missing information and bounded field checks. A checked name does not verify the date, rarity, all printings or marketplace identity.

`carddex_reconciliation.json` retains 67 attempted native set inventories, 64 usable tables, 358 exact native name/set/number matches, 303 mappable rarity checks and two resolved rarity conflicts. Silver Star and broad Ultra Rare labels are not blindly collapsed into another era taxonomy. Carddex is an independent editorial source, unlike sites that reproduce TCGdex.

`inventory_reconciliation.json` repeats all 41 species against the same 957 cached PokéWiki international primary rows, with per-language exclusions and unresolved regional availability. It is not a complete cameo or physical-variant census.

`sample_plan.json` freezes seed 20261029 before changes: eight randomly selected records per language and five year strata, 80 total, excluding the previous sample. `sample_audit.json` records exactly which fields were assessed. Two missing pictures remain unassessed. There is no population accuracy estimate.

`work_queue.json` is the continuation point. Read resolved items before researching again. `source_acquisition.json` records failed successor publisher links; an access failure is never proof that a card did not exist. `evidence_log.json` links decisions and source families.

Rebuild offline with `python catalog_enrich.py`, then refresh this audit with `python reconciliation_audit.py`. Rebuilds preserve old IDs, including withdrawn targets kept in retired_entries. Never overwrite a personal my_collection folder.

The separate DogDex_Research_Evidence_1_5.zip contains source preparation scripts, cached native HTML, earlier publisher PDFs and source hashes. Source acquisition is not needed to run the collector. Collection and QA records are excluded from all deliverables.
