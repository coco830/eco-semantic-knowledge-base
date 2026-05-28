# process_evidence_gate_report_v1_1

final_state: `NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY`

- runtime_integration: disabled
- process_triggers: 10
- activation_rows: 34
- sample_evidence_rows: 6
- overlay_rows: 16
- not_apply_scope_gate: PROCESS_ONLY required for process negation.
- conflict_gate: same enterprise + scenario confirmed/not_apply requires explicit process-only scope.
- boundary_fields_gate: runtime_status/final_state/runtime_integration are row-level fields.
- hard boundary: candidate process evidence only; no EcoCheck runtime effect.
