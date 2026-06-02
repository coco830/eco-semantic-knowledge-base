# V8.5 Pollutant Domain Approved Baseline

This package backfills the manually approved Semantic Profile Lab V8.5 pollutant-domain source baseline into `coco830/eco-semantic-knowledge-base`.

## Scope

- Approved entries: 209
- P1 excluded entries: 6
- Approval authority: `CANDY_OWNER_L5_APPROVAL`
- Approval date: `2026-06-02`
- Source Semantic Profile Lab commit: `5ae1225663dd9d4035918c89383a2342c853ed7d`
- Source package scope: `DOWNSTREAM_KNOWLEDGE_BASE_STAGING_ONLY`
- Knowledge-base final state: `APPROVED_POLLUTANT_DOMAIN_BASELINE_KNOWLEDGE`
- Runtime integration marker: `approved_baseline_export_ready`

The source candidate boundary is preserved on every row as `source_runtime_status`, `source_final_state`, and `source_runtime_integration`.

## Domain Distribution

- `air`: 36
- `general_environmental_engineering`: 2
- `hazardous_waste`: 32
- `noise`: 6
- `radiation`: 26
- `solid_waste`: 14
- `special_industry`: 6
- `water`: 87

## P1 Exclusions

- `PDS-V8_0-0079`: REJECT_DUPLICATE_HASH (Byte-identical duplicate of PDS-V8_0-0017; keep one source snapshot only for L4 semantic subset.)
- `PDS-V8_0-0081`: REJECT_SUPERSEDED (GB 21523-2008 is superseded by current GB 21523-2024; reject old version for L4 semantic subset.)
- `PDS-V8_0-0150`: REJECT_DUPLICATE_HASH (Byte-identical duplicate of PDS-V8_0-0149; filename separator differs only.)
- `PDS-V8_0-0165`: REJECT_DUPLICATE_HASH (Byte-identical duplicate of PDS-V8_0-0164; filename separator differs only.)
- `PDS-V8_0-0169`: REJECT_DUPLICATE_HASH (Byte-identical duplicate of PDS-V8_0-0168; filename spacing/separator differs only.)
- `PDS-V8_0-0194`: REJECT_SUPERSEDED (GB 13600-92 is superseded by current GB 13600-2024; reject old version for L4 semantic subset.)

## Guards

- `ConfirmedDataset` is still `NOT_CREATED`.
- Formal emission-right calculation is still `NOT_AUTHORIZED`.
- `radiation_all_industry_default` remains blocked.
- This backfill does not mutate EcoCheck runtime code, `ReviewField`, or `CoefficientSelector`.
