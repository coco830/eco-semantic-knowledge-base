# pollutant_standard_link_map_v8_6

final_state: `NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY`
runtime_integration: `disabled`

v8.6 adds a candidate bridge from V8.5 pollutant-domain approved sources to scenario, industry, Score13, and graph-v0.6 surfaces. It does not mutate the V8.5 approved baseline CSV and does not promote runtime use.

## Truth Snapshot

- V8.5 source rows: 209
- Domain distribution: `{'air': 36, 'general_environmental_engineering': 2, 'hazardous_waste': 32, 'noise': 6, 'radiation': 26, 'solid_waste': 14, 'special_industry': 6, 'water': 87}`
- Source-role distribution: `{'EMISSION_STANDARD_SOURCE': 46, 'HAZARDOUS_WASTE_MANAGEMENT_SOURCE': 28, 'MONITORING_REQUIREMENT_SOURCE': 7, 'PERMIT_APPLICATION_AND_LEDGER_EVIDENCE_SOURCE': 4, 'POLLUTANT_DOMAIN_REFERENCE_SOURCE': 5, 'RADIATION_SAFETY_SOURCE': 26, 'SUPPORTING_REGULATION_SOURCE': 5, 'TREATMENT_TECHNICAL_SPEC_SOURCE': 88}`
- Content usability distribution: `{'OCR_REQUIRED_BEFORE_CLAUSE_OR_NUMERIC_ADOPTION': 9, 'SMALL_FILE_REVIEW_REQUIRED_POSSIBLE_TRUNCATION_OR_EXCERPT': 2, 'TITLE_LEVEL_AND_SOURCE_LOCK_READY': 198}`

The design draft expected `hazardous_waste=31` and `TITLE_LEVEL_AND_SOURCE_LOCK_READY=200`; the real repository data is `hazardous_waste=32` and `TITLE_LEVEL_AND_SOURCE_LOCK_READY=198`.

## Output Counts

`{'DOMAIN': 209, 'INDUSTRY': 27, 'SCENARIO': 479, 'SCORE13': 192, 'SOURCE_REVIEW': 11}`
