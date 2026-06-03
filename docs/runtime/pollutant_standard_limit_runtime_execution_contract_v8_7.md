# pollutant_standard_limit_runtime_execution_contract_v8_7

contract_version: `v8.7-standard-limit-runtime-execution-contract`
source_contract_version: `v8.7-standard-limit-runtime-import-contract`
approval_id: `CANDY-APPROVAL-STANDARD-LIMIT-RUNTIME-IMPORT-2026-06-03`
final_state: `APPROVED_STANDARD_LIMIT_RUNTIME_EXECUTION_CONTRACT_TESTED`
runtime_status: `DOWNSTREAM_IMPORT_CONTRACT_TEST_EXECUTION_PASS`
runtime_integration: `approved_standard_limit_profile_import_contract`
execution_action: `DOWNSTREAM_RUNTIME_IMPORT_CONTRACT_TEST_EXECUTED`
execution_mode: `DRY_RUN_MATERIALIZATION_ONLY`

This contract connects the 74 approved standard-limit runtime import rows to downstream test execution by producing a lookup-only dry-run snapshot.

Hard rules:
- This execution contract materializes standard-limit lookup entries only.
- Execution mode is dry-run materialization in this knowledge-base package.
- Downstream EcoCheck import can consume the snapshot only after its own runtime tests pass.
- This package must not create ConfirmedDataset, run formal emission-right calculation, auto-select coefficients, mutate coefficient selectors, or enable all-industry radiation defaults.
- This package must not generate formal permit_type, formal inspection templates, automatic deduct values, or formal compliance conclusions.
- Every lookup entry must preserve source_profile_id, raw_fragment, source_page, rollback_manifest_id, and approval_id.

Test cases:
- `PSLRT-EXEC-TC-001` runtime_import_row_count: PASS
- `PSLRT-EXEC-TC-002` runtime_import_required_fields: PASS
- `PSLRT-EXEC-TC-003` unique_runtime_and_lookup_ids: PASS
- `PSLRT-EXEC-TC-004` source_import_contract_state: PASS
- `PSLRT-EXEC-TC-005` lookup_snapshot_materialization: PASS
- `PSLRT-EXEC-TC-006` runtime_effect_lookup_only: PASS
- `PSLRT-EXEC-TC-007` forbidden_runtime_actions_remain_blocked: PASS
- `PSLRT-EXEC-TC-008` source_traceability_preserved: PASS
- `PSLRT-EXEC-TC-009` runtime_scope_coverage: PASS
- `PSLRT-EXEC-TC-010` standard_coverage: PASS
