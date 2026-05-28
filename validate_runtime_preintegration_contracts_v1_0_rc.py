import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FINAL_STATE = "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"
RUNTIME_INTEGRATION = "disabled"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def fail(failures, file, reason, row_id=""):
    failures.append({"file": file, "reason": reason, "row_id": row_id})


def assert_text_contains(failures, file_name, phrases):
    text = (ROOT / file_name).read_text(encoding="utf-8", errors="ignore")
    for phrase in phrases:
        if phrase not in text:
            fail(failures, file_name, "missing_contract_phrase", phrase)


def main():
    failures = []
    required = [
        "runtime_promotion_gate_design_v1_0_rc.json",
        "runtime_data_contract_v1_0_rc.json",
        "runtime_import_candidate_manifest_v1_0_rc.json",
        "runtime_contract_test_plan_v1_0_rc.md",
        "approval_workflow_v1_0_rc.md",
        "security_audit_log_design_v1_0_rc.json",
        "candidate_to_runtime_mapping_v1_0_rc.csv",
        "human_review_overlay_v0_8.csv",
        "formalization_candidate_queue_v0_8.csv",
        "runtime_readiness_matrix_v1_7.csv",
        "knowledge_base_manifest_v1_2_to_v1_7.json",
    ]
    for name in required:
        if not (ROOT / name).exists():
            fail(failures, name, "missing_required_input")

    gate = read_json(ROOT / "runtime_promotion_gate_design_v1_0_rc.json")
    contract = read_json(ROOT / "runtime_data_contract_v1_0_rc.json")
    import_manifest = read_json(ROOT / "runtime_import_candidate_manifest_v1_0_rc.json")
    audit = read_json(ROOT / "security_audit_log_design_v1_0_rc.json")
    kb_manifest = read_json(ROOT / "knowledge_base_manifest_v1_2_to_v1_7.json")
    mapping = read_csv(ROOT / "candidate_to_runtime_mapping_v1_0_rc.csv")
    review_overlay = read_csv(ROOT / "human_review_overlay_v0_8.csv")
    formalization = read_csv(ROOT / "formalization_candidate_queue_v0_8.csv")
    readiness = read_csv(ROOT / "runtime_readiness_matrix_v1_7.csv")

    for file, doc in [
        ("runtime_promotion_gate_design_v1_0_rc.json", gate),
        ("runtime_data_contract_v1_0_rc.json", contract),
        ("runtime_import_candidate_manifest_v1_0_rc.json", import_manifest),
        ("security_audit_log_design_v1_0_rc.json", audit),
        ("knowledge_base_manifest_v1_2_to_v1_7.json", kb_manifest),
    ]:
        if doc.get("final_state") != FINAL_STATE:
            fail(failures, file, "bad_final_state")
        if doc.get("runtime_integration") != RUNTIME_INTEGRATION:
            fail(failures, file, "bad_runtime_integration")

    if import_manifest.get("import_action") != "NONE_DESIGN_ONLY":
        fail(failures, "runtime_import_candidate_manifest_v1_0_rc.json", "import_action_must_stay_none")
    if gate.get("design_only") is not True:
        fail(failures, "runtime_promotion_gate_design_v1_0_rc.json", "gate_must_stay_design_only")

    for row in mapping:
        rid = row.get("runtime_candidate_id", "")
        if row.get("runtime_status") != "NOT_IMPORTED_DESIGN_ONLY":
            fail(failures, "candidate_to_runtime_mapping_v1_0_rc.csv", "runtime_mapping_imported", rid)
        if row.get("runtime_effect") != "NONE" or row.get("runtime_integration") != RUNTIME_INTEGRATION:
            fail(failures, "candidate_to_runtime_mapping_v1_0_rc.csv", "runtime_mapping_has_effect", rid)
        if row.get("second_approval_required") != "true" or row.get("second_approval_status") != "NOT_STARTED":
            fail(failures, "candidate_to_runtime_mapping_v1_0_rc.csv", "second_approval_not_blocking", rid)
        if row.get("approved_runtime_scope"):
            fail(failures, "candidate_to_runtime_mapping_v1_0_rc.csv", "approved_runtime_scope_not_empty", rid)

    for row in review_overlay:
        reviewer = (row.get("human_reviewer") or "").lower()
        reviewer_role = (row.get("human_reviewer_role") or "").lower()
        oid = row.get("overlay_id", row.get("review_overlay_id", ""))
        if reviewer.startswith("simulated") or reviewer_role.startswith("simulated"):
            if row.get("runtime_status") not in {"CANDIDATE_ONLY", "DRAFT_NOT_FOR_RUNTIME", "NOT_IMPORTED_DESIGN_ONLY"}:
                fail(failures, "human_review_overlay_v0_8.csv", "simulated_reviewer_has_runtime_status", oid)
            if row.get("runtime_integration") != RUNTIME_INTEGRATION:
                fail(failures, "human_review_overlay_v0_8.csv", "simulated_reviewer_runtime_enabled", oid)

    for row in formalization:
        fid = row.get("formalization_candidate_id", row.get("review_overlay_id", ""))
        if row.get("requires_second_approval") != "true":
            fail(failures, "formalization_candidate_queue_v0_8.csv", "formalization_without_second_approval", fid)
        if row.get("runtime_integration") != RUNTIME_INTEGRATION:
            fail(failures, "formalization_candidate_queue_v0_8.csv", "formalization_runtime_enabled", fid)

    forbidden_runtime_targets = {
        "FORMAL_PERMIT_TYPE",
        "INSPECTION_TEMPLATE",
        "AUTO_DEDUCT",
        "ECOCHECK_RUNTIME",
    }
    readiness_by_target = {row.get("target"): row for row in readiness}
    for target in forbidden_runtime_targets:
        row = readiness_by_target.get(target)
        if not row:
            fail(failures, "runtime_readiness_matrix_v1_7.csv", "missing_forbidden_target", target)
            continue
        if row.get("allowed_state") != "NOT_ALLOWED":
            fail(failures, "runtime_readiness_matrix_v1_7.csv", "forbidden_target_allowed", target)
        if "BLOCK" not in row.get("required_gate_before_change", ""):
            fail(failures, "runtime_readiness_matrix_v1_7.csv", "forbidden_target_missing_block_gate", target)

    assert_text_contains(
        failures,
        "runtime_contract_test_plan_v1_0_rc.md",
        [
            "不得导入",
            "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY",
            "二次审批",
            "不能生成正式 permit_type",
            "不能生成正式检查模板",
            "不能自动扣分",
        ],
    )
    assert_text_contains(
        failures,
        "approval_workflow_v1_0_rc.md",
        [
            "human_review",
            "second_approval",
            "Product",
            "ETO",
            "TechLead",
        ],
    )

    report = {
        "validation_status": "PASS" if not failures else "FAIL",
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
        "failure_count": len(failures),
        "checked_contracts": [
            "reject_simulated_reviewers_as_real_signatures",
            "reject_not_for_runtime_import",
            "reject_formal_permit_type_generation",
            "reject_formal_inspection_template_generation",
            "reject_auto_deduct_generation",
            "require_second_approval_before_runtime_scope",
        ],
        "failure_samples": failures[:50],
    }
    (ROOT / "runtime_preintegration_contract_validation_report_v1_0_rc.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (ROOT / "runtime_preintegration_contract_failure_list_v1_0_rc.json").write_text(
        json.dumps(failures, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
