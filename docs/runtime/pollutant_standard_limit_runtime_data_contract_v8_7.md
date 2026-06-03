# pollutant_standard_limit_runtime_data_contract_v8_7

contract_version: `v8.7-standard-limit-runtime-import-contract`
approval_id: `CANDY-APPROVAL-STANDARD-LIMIT-RUNTIME-IMPORT-2026-06-03`
final_state: `APPROVED_STANDARD_LIMIT_PROFILE_RUNTIME_IMPORT_CONTRACT`
runtime_status: `APPROVED_FOR_IMPORT_PENDING_TESTS`
runtime_integration: `approved_standard_limit_profile_import_contract`
import_action: `APPROVED_FOR_RUNTIME_IMPORT_CONTRACT`

This contract promotes the 74 approved standard-limit profile rows into a runtime import contract for standard-limit lookup only.

Required fields:
- `runtime_import_id`
- `source_profile_id`
- `approval_id`
- `replacement_standard_no`
- `obsolete_source_id`
- `replacement_standard_title`
- `profile_family`
- `standard_limit_target`
- `medium`
- `table_or_clause_ref`
- `source_page`
- `source_table_index`
- `source_row_index`
- `pollutant_item`
- `standard_limit_metric`
- `metric`
- `operator`
- `value`
- `unit`
- `lower_value`
- `lower_unit`
- `lower_inclusive`
- `upper_value`
- `upper_unit`
- `upper_inclusive`
- `equivalent_value`
- `equivalent_unit`
- `limit_context`
- `monitoring_location`
- `raw_fragment`
- `source_evidence_ref`
- `adapter_mapping_basis`
- `human_review_status`
- `runtime_scope`
- `runtime_status`
- `runtime_integration`
- `runtime_effect`
- `import_action`
- `forbidden_runtime_actions`
- `rollback_manifest_id`
- `contract_version`
- `final_state`

Hard rules:
- This contract imports standard-limit lookup profiles only.
- It must not create ConfirmedDataset.
- It must not run formal emission-right calculation.
- It must not auto-select or mutate coefficient selection.
- It must not enable all-industry radiation defaults.
- It must not generate formal permit_type.
- It must not generate formal inspection templates.
- It must not generate automatic deduct values.
- It must not make formal compliance conclusions without downstream runtime tests and enterprise evidence.
- Every row must preserve source_profile_id, raw_fragment, source_page, approval_id, and rollback_manifest_id.
