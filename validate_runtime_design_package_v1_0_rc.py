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


def main():
    failures = []
    required = [
        "PROJECT_INDEX_v1_0_rc.md",
        "HANDOFF_v1_0_rc.md",
        "DEPRECATED_AND_REMOVED_FILES_v1_0_rc.md",
        "open_questions_review_guide_v1_0_rc.md",
        "open_questions_review_matrix_v1_0_rc.csv",
        "eto_eso_open_question_decisions_v1_0_rc.md",
        "eto_eso_open_question_decisions_v1_0_rc.csv",
        "runtime_promotion_gate_design_v1_0_rc.md",
        "runtime_promotion_gate_design_v1_0_rc.json",
        "runtime_data_contract_v1_0_rc.md",
        "runtime_data_contract_v1_0_rc.json",
        "runtime_import_candidate_manifest_v1_0_rc.json",
        "runtime_rollback_plan_v1_0_rc.md",
        "runtime_contract_test_plan_v1_0_rc.md",
        "approval_workflow_v1_0_rc.md",
        "security_audit_log_design_v1_0_rc.md",
        "security_audit_log_design_v1_0_rc.json",
        "candidate_to_runtime_mapping_v1_0_rc.csv",
        "build_runtime_design_package_v1_0_rc.py",
        "validate_runtime_design_package_v1_0_rc.py",
        "FINAL_COMPLETION_REPORT_v1_0_rc.md",
        "knowledge_base_manifest_v1_0_rc.json",
    ]
    for name in required:
        if not (ROOT / name).exists():
            fail(failures, name, "missing_required_output")

    gate = read_json(ROOT / "runtime_promotion_gate_design_v1_0_rc.json")
    contract = read_json(ROOT / "runtime_data_contract_v1_0_rc.json")
    import_manifest = read_json(ROOT / "runtime_import_candidate_manifest_v1_0_rc.json")
    audit = read_json(ROOT / "security_audit_log_design_v1_0_rc.json")
    manifest = read_json(ROOT / "knowledge_base_manifest_v1_0_rc.json")
    mapping = read_csv(ROOT / "candidate_to_runtime_mapping_v1_0_rc.csv")
    formalization = read_csv(ROOT / "formalization_candidate_queue_v0_8.csv")

    for file, doc in [
        ("runtime_promotion_gate_design_v1_0_rc.json", gate),
        ("runtime_data_contract_v1_0_rc.json", contract),
        ("runtime_import_candidate_manifest_v1_0_rc.json", import_manifest),
        ("security_audit_log_design_v1_0_rc.json", audit),
        ("knowledge_base_manifest_v1_0_rc.json", manifest),
    ]:
        if doc.get("final_state") != FINAL_STATE or doc.get("runtime_integration") != RUNTIME_INTEGRATION:
            fail(failures, file, "bad_boundary")

    if gate.get("design_only") is not True or len(gate.get("gates", [])) < 6:
        fail(failures, "runtime_promotion_gate_design_v1_0_rc.json", "gate_design_incomplete")
    if import_manifest.get("import_action") != "NONE_DESIGN_ONLY":
        fail(failures, "runtime_import_candidate_manifest_v1_0_rc.json", "import_action_not_none")
    if len(mapping) != len(formalization):
        fail(failures, "candidate_to_runtime_mapping_v1_0_rc.csv", "mapping_count_mismatch")

    for row in mapping:
        rid = row.get("runtime_candidate_id", "")
        if row.get("runtime_status") != "NOT_IMPORTED_DESIGN_ONLY":
            fail(failures, "candidate_to_runtime_mapping_v1_0_rc.csv", "bad_runtime_status", rid)
        if row.get("second_approval_required") != "true" or row.get("second_approval_status") != "NOT_STARTED":
            fail(failures, "candidate_to_runtime_mapping_v1_0_rc.csv", "missing_second_approval_gate", rid)
        if row.get("runtime_integration") != RUNTIME_INTEGRATION or row.get("runtime_effect") != "NONE":
            fail(failures, "candidate_to_runtime_mapping_v1_0_rc.csv", "bad_runtime_boundary", rid)
        if row.get("approved_runtime_scope"):
            fail(failures, "candidate_to_runtime_mapping_v1_0_rc.csv", "approved_runtime_scope_should_be_empty", rid)

    text_files = [
        "PROJECT_INDEX_v1_0_rc.md",
        "HANDOFF_v1_0_rc.md",
        "DEPRECATED_AND_REMOVED_FILES_v1_0_rc.md",
        "open_questions_review_guide_v1_0_rc.md",
        "eto_eso_open_question_decisions_v1_0_rc.md",
        "runtime_rollback_plan_v1_0_rc.md",
        "runtime_contract_test_plan_v1_0_rc.md",
        "approval_workflow_v1_0_rc.md",
        "FINAL_COMPLETION_REPORT_v1_0_rc.md",
    ]
    for name in text_files:
        text = (ROOT / name).read_text(encoding="utf-8")
        for phrase in [FINAL_STATE, "不", "runtime"]:
            if phrase not in text:
                fail(failures, name, "missing_boundary_phrase", phrase)

    project_index = (ROOT / "PROJECT_INDEX_v1_0_rc.md").read_text(encoding="utf-8")
    for phrase in [
        "v1.0-rc design-only baseline",
        "human_review_worksheet_v0_7.xlsx",
        "runtime_promotion_gate_design_v1_0_rc.md/json",
        "不接 EcoCheck runtime",
        "不生成正式 `permit_type`",
        "不把旧 `12个优先行业规则库_v1.1接入版` 当作当前入口",
    ]:
        if phrase not in project_index:
            fail(failures, "PROJECT_INDEX_v1_0_rc.md", "missing_index_phrase", phrase)

    handoff = (ROOT / "HANDOFF_v1_0_rc.md").read_text(encoding="utf-8")
    for phrase in [
        "人工审阅",
        "RAG demo",
        "图谱 demo",
        "真正接入前置条件",
        "旧 `12个优先行业规则库_v1.1接入版`",
    ]:
        if phrase not in handoff:
            fail(failures, "HANDOFF_v1_0_rc.md", "missing_handoff_phrase", phrase)

    deprecation = (ROOT / "DEPRECATED_AND_REMOVED_FILES_v1_0_rc.md").read_text(encoding="utf-8")
    for phrase in [
        "已移除",
        "12个优先行业规则库_v1.1接入版.json",
        "generate_rules_v1_1_complete.py",
        "build_knowledge_base.py",
        "不得恢复旧接入版直接导入路径",
    ]:
        if phrase not in deprecation:
            fail(failures, "DEPRECATED_AND_REMOVED_FILES_v1_0_rc.md", "missing_deprecation_phrase", phrase)

    removed_legacy_files = [
        "12个优先行业规则库_v1.1接入版.json",
        "v1.1更新说明.md",
        "generate_rules_v1_1_complete.py",
        "build_knowledge_base.py",
    ]
    for name in removed_legacy_files:
        if (ROOT / name).exists():
            fail(failures, name, "legacy_runtime_entry_should_be_removed")

    review_matrix = read_csv(ROOT / "open_questions_review_matrix_v1_0_rc.csv")
    open_questions = read_csv(ROOT / "open_questions_v0_4_1.csv")
    if len(review_matrix) != len(open_questions):
        fail(failures, "open_questions_review_matrix_v1_0_rc.csv", "row_count_mismatch")
    matrix_ids = {r.get("question_id", "") for r in review_matrix}
    open_ids = {r.get("question_id", "") for r in open_questions}
    if matrix_ids != open_ids:
        fail(failures, "open_questions_review_matrix_v1_0_rc.csv", "question_id_set_mismatch")
    for row in review_matrix:
        qid = row.get("question_id", "")
        for field in [
            "ask_who",
            "concrete_question",
            "check_materials",
            "decision_options",
            "evidence_to_record",
            "close_condition",
            "runtime_effect",
        ]:
            if not row.get(field, "").strip():
                fail(failures, "open_questions_review_matrix_v1_0_rc.csv", f"missing_{field}", qid)
    guide = (ROOT / "open_questions_review_guide_v1_0_rc.md").read_text(encoding="utf-8")
    for phrase in [
        "找谁问",
        "具体要问",
        "怎么查",
        "要留什么证据",
        "关闭条件",
        "BLOCKS_RUNTIME",
    ]:
        if phrase not in guide:
            fail(failures, "open_questions_review_guide_v1_0_rc.md", "missing_guide_phrase", phrase)

    decision_rows = read_csv(ROOT / "eto_eso_open_question_decisions_v1_0_rc.csv")
    if len(decision_rows) != len(open_questions):
        fail(failures, "eto_eso_open_question_decisions_v1_0_rc.csv", "row_count_mismatch")
    decision_ids = {r.get("question_id", "") for r in decision_rows}
    if decision_ids != open_ids:
        fail(failures, "eto_eso_open_question_decisions_v1_0_rc.csv", "question_id_set_mismatch")
    for row in decision_rows:
        qid = row.get("question_id", "")
        if row.get("runtime_boundary") != "BLOCKS_RUNTIME":
            fail(failures, "eto_eso_open_question_decisions_v1_0_rc.csv", "runtime_boundary_not_blocked", qid)
        if row.get("implementation_required") != "true":
            fail(failures, "eto_eso_open_question_decisions_v1_0_rc.csv", "implementation_required_not_true", qid)
        for field in ["owner_decision", "decision_status", "evidence_required"]:
            if not row.get(field, "").strip():
                fail(failures, "eto_eso_open_question_decisions_v1_0_rc.csv", f"missing_{field}", qid)
    decision_text = (ROOT / "eto_eso_open_question_decisions_v1_0_rc.md").read_text(encoding="utf-8")
    for phrase in [
        "PRELIMINARY_ETO_ESO_REVIEW_RECORDED",
        "BLOCKS_RUNTIME",
        "不解除任何运行时阻断",
        "不填写或伪造",
        "1512=白酒制造",
        "1513=啤酒制造",
        "另开 v1.1 治理修复任务",
    ]:
        if phrase not in decision_text:
            fail(failures, "eto_eso_open_question_decisions_v1_0_rc.md", "missing_decision_phrase", phrase)

    forbidden_claims = ["runtime_integration: enabled", "自动扣分已启用", "正式模板已生成", "已接 EcoCheck runtime"]
    for name in required:
        path = ROOT / name
        if path.suffix.lower() in {".md", ".json", ".csv"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
            for phrase in forbidden_claims:
                if phrase in text:
                    fail(failures, name, "forbidden_runtime_claim", phrase)

    report = {
        "validation_status": "PASS" if not failures else "FAIL",
        "final_state": FINAL_STATE,
        "failure_count": len(failures),
        "candidate_mapping_rows": len(mapping),
        "gate_count": len(gate.get("gates", [])),
        "audit_event_count": len(audit.get("events", [])),
        "failure_samples": failures[:50],
    }
    (ROOT / "runtime_design_package_v1_0_rc_validation_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (ROOT / "runtime_design_package_v1_0_rc_failure_list.json").write_text(
        json.dumps(failures, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
