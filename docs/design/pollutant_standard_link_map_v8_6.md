# pollutant_standard_link_map_v8_6

final_state: `NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY`
runtime_integration: `disabled`

v8.6 adds a candidate bridge from V8.5 pollutant-domain approved sources to scenario, industry, Score13, and graph-v0.6 surfaces. It does not mutate the V8.5 approved baseline CSV and does not promote runtime use.

## Truth Snapshot

- V8.5 source rows: 209
- Active source rows emitted as `PollutantStandardSource`: 203
- Obsolete source rows excluded from candidate graph: 6
- Domain distribution: `{'air': 36, 'general_environmental_engineering': 2, 'hazardous_waste': 32, 'noise': 6, 'radiation': 26, 'solid_waste': 14, 'special_industry': 6, 'water': 87}`
- Source-role distribution: `{'EMISSION_STANDARD_SOURCE': 46, 'HAZARDOUS_WASTE_MANAGEMENT_SOURCE': 28, 'MONITORING_REQUIREMENT_SOURCE': 7, 'PERMIT_APPLICATION_AND_LEDGER_EVIDENCE_SOURCE': 4, 'POLLUTANT_DOMAIN_REFERENCE_SOURCE': 5, 'RADIATION_SAFETY_SOURCE': 26, 'SUPPORTING_REGULATION_SOURCE': 5, 'TREATMENT_TECHNICAL_SPEC_SOURCE': 88}`
- Content usability distribution: `{'OCR_REQUIRED_BEFORE_CLAUSE_OR_NUMERIC_ADOPTION': 9, 'SMALL_FILE_REVIEW_REQUIRED_POSSIBLE_TRUNCATION_OR_EXCERPT': 2, 'TITLE_LEVEL_AND_SOURCE_LOCK_READY': 198}`
- Source recovery actions: `{'CONFIRMED_UNBLOCK_CURRENT_STANDARD': 5, 'OBSOLETE_EXCLUDE_NO_ACTIVE_REPLACEMENT': 3, 'OBSOLETE_EXCLUDE_REPLACEMENT_GOVERNANCE': 3}`
- Standard lifecycle statuses: `{'CURRENT': 5, 'OBSOLETE_NO_ACTIVE_REPLACEMENT': 1, 'OBSOLETE_NO_EXACT_REPLACEMENT': 1, 'OBSOLETE_REPLACED': 3, 'OBSOLETE_REPLACED_THEN_REPLACEMENT_OBSOLETED': 1}`

The design draft expected `hazardous_waste=31` and `TITLE_LEVEL_AND_SOURCE_LOCK_READY=200`; the real repository data is `hazardous_waste=32` and `TITLE_LEVEL_AND_SOURCE_LOCK_READY=198`.

## Output Counts

`{'DOMAIN': 203, 'INDUSTRY': 27, 'SCENARIO': 490, 'SCORE13': 197, 'STANDARD_LIFECYCLE': 6}`

## Human Review Overlay

- Overlay rows: 698
- Decisions: `{'ACCEPT': 412, 'REJECT': 286}`
- Overlay status: `{'BLOCKS_RUNTIME': 286, 'FORMALIZATION_CANDIDATE': 412}`
- Rejected deep links remain auditable in `pollutant_standard_link_map_v8_6.csv` with `human_review_label=REJECT_CANDIDATE`; they are not emitted as graph-v0.6 traversal edges.

## Source Recovery Overlay

- Source recovery rows: 11
- Source-recovery-confirmed deep links: 16
- Replacement standard governance candidates: 3
- Obsolete source rows use `STANDARD_LIFECYCLE` audit links only and are not emitted as `PollutantStandardSource` graph nodes or old-standard traversal edges.
