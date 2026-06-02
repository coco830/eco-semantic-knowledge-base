# FINAL POLLUTANT STANDARD LINK GRAPH v8.6

Final state: `NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY`
Runtime integration: `disabled`

## Delivered

- Built `pollutant_standard_link_map_v8_6.csv` as the candidate bridge over V8.5.
- Applied the v8.6 human review overlay: `{'ACCEPT': 412, 'REJECT': 286}`.
- Built `graph_nodes_v0_6.jsonl` and `graph_edges_v0_6.jsonl.gz`.
- Omitted human-rejected deep links from graph-v0.6 traversal edges while preserving them in the auditable link CSV.
- Preserved candidate-only/runtime-disabled boundaries on every new link and graph edge.
- Kept the original V8.5 baseline CSV unchanged.

## Counts

- Link rows by target kind: `{'DOMAIN': 209, 'INDUSTRY': 27, 'SCENARIO': 479, 'SCORE13': 192, 'SOURCE_REVIEW': 11}`
- Graph nodes by type: `{'ApplicabilityRelation': 22815, 'Industry': 1382, 'InspectionCandidate': 22, 'KnowledgeBaseManifest': 1, 'OpenQuestion': 19, 'PermitCatalogEntry': 112, 'PermitCondition': 336, 'PollutantDomain': 8, 'PollutantStandardSource': 209, 'RiskAcceptance': 9, 'ScenarioTemplate': 28, 'Score13Dimension': 13}`
- Graph edges by type: `{'CANDIDATE_APPLICABILITY': 22815, 'HAS_APPLICABILITY_RELATION': 22815, 'HAS_CONDITION': 336, 'HAS_INSPECTION_CANDIDATE': 22, 'MAPS_TO_SCORE13': 48, 'RELATED_TO_SCENARIO': 119193, 'RISK_LINKED_TO_OPEN_QUESTION': 12, 'STANDARD_APPLIES_TO_INDUSTRY': 17, 'STANDARD_GOVERNS_SCENARIO': 206, 'STANDARD_IN_DOMAIN': 209, 'STANDARD_SUPPORTS_SCORE13': 189}`
- V8.5 domains: `{'air': 36, 'general_environmental_engineering': 2, 'hazardous_waste': 32, 'noise': 6, 'radiation': 26, 'solid_waste': 14, 'special_industry': 6, 'water': 87}`
- V8.5 source roles: `{'EMISSION_STANDARD_SOURCE': 46, 'HAZARDOUS_WASTE_MANAGEMENT_SOURCE': 28, 'MONITORING_REQUIREMENT_SOURCE': 7, 'PERMIT_APPLICATION_AND_LEDGER_EVIDENCE_SOURCE': 4, 'POLLUTANT_DOMAIN_REFERENCE_SOURCE': 5, 'RADIATION_SAFETY_SOURCE': 26, 'SUPPORTING_REGULATION_SOURCE': 5, 'TREATMENT_TECHNICAL_SPEC_SOURCE': 88}`
- V8.5 content usability: `{'OCR_REQUIRED_BEFORE_CLAUSE_OR_NUMERIC_ADOPTION': 9, 'SMALL_FILE_REVIEW_REQUIRED_POSSIBLE_TRUNCATION_OR_EXCERPT': 2, 'TITLE_LEVEL_AND_SOURCE_LOCK_READY': 198}`
- Review overlay decisions: `{'ACCEPT': 412, 'REJECT': 286}`

## Known Gaps

- Accepted title-level links remain candidate-only and still require runtime promotion review before any operational use.
- OCR and small-file rows are intentionally blocked from scenario, industry, and Score13 linking.
- This package is graph/RAG candidate scaffolding only; no EcoCheck runtime mutation or formal compliance conclusion is authorized.
