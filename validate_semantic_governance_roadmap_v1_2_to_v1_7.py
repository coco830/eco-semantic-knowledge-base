import csv
import json
from pathlib import Path
from kb_paths import artifact_path


ROOT = Path(__file__).resolve().parent
FINAL_STATE = "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"
RUNTIME_INTEGRATION = "disabled"
RUNTIME_STATUS = "DRAFT_NOT_FOR_RUNTIME"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def fail(failures, file, reason, row_id=""):
    failures.append({"file": file, "reason": reason, "row_id": row_id})


def check_boundary(failures, file, rows, row_id_field):
    for row in rows:
        row_id = row.get(row_id_field, "")
        if row.get("runtime_status") != RUNTIME_STATUS:
            fail(failures, file, "bad_runtime_status", row_id)
        if row.get("final_state") != FINAL_STATE:
            fail(failures, file, "bad_final_state", row_id)
        if row.get("runtime_integration") != RUNTIME_INTEGRATION:
            fail(failures, file, "bad_runtime_integration", row_id)


def main():
    failures = []
    required = [
        "eia_permit_extraction_schema_v1_2.md",
        "eia_permit_extraction_schema_v1_2.json",
        "eia_permit_extraction_samples_v1_2.csv",
        "eia_permit_extraction_samples_v1_2.json",
        "eia_permit_extracted_predicates_v1_2.csv",
        "eia_permit_extracted_predicates_v1_2.json",
        "process_scenario_activation_rules_v1_3.csv",
        "process_scenario_activation_rules_v1_3.json",
        "open_question_decision_overlay_v1_4.csv",
        "open_question_decision_overlay_v1_4.json",
        "open_question_closure_status_v1_4.json",
        "human_review_slices_v1_5.csv",
        "human_review_slices_v1_5.json",
        "human_review_slice_guidance_v1_5.md",
        "retrieval_eval_set_v1_6.jsonl",
        "rag_eval_coverage_v1_6.md",
        "rag_eval_coverage_v1_6.json",
        "runtime_readiness_matrix_v1_7.csv",
        "runtime_readiness_matrix_v1_7.json",
        "runtime_readiness_gap_report_v1_7.md",
        "runtime_readiness_gap_report_v1_7.json",
        "knowledge_base_manifest_v1_2_to_v1_7.json",
        "FINAL_COMPLETION_REPORT_v1_2_to_v1_7.md",
        "build_semantic_governance_roadmap_v1_2_to_v1_7.py",
        "validate_semantic_governance_roadmap_v1_2_to_v1_7.py",
    ]
    for name in required:
        if not (artifact_path(name)).exists():
            fail(failures, name, "missing_required_output")

    samples = read_csv(artifact_path("eia_permit_extraction_samples_v1_2.csv"))
    samples_json = read_json(artifact_path("eia_permit_extraction_samples_v1_2.json"))
    predicates = read_csv(artifact_path("eia_permit_extracted_predicates_v1_2.csv"))
    rules = read_csv(artifact_path("process_scenario_activation_rules_v1_3.csv"))
    oq_overlay = read_csv(artifact_path("open_question_decision_overlay_v1_4.csv"))
    oq_source = read_csv(artifact_path("open_questions_v0_4_1.csv"))
    review_slices = read_csv(artifact_path("human_review_slices_v1_5.csv"))
    eval_rows = read_jsonl(artifact_path("retrieval_eval_set_v1_6.jsonl"))
    readiness = read_csv(artifact_path("runtime_readiness_matrix_v1_7.csv"))
    manifest = read_json(artifact_path("knowledge_base_manifest_v1_2_to_v1_7.json"))
    coverage = read_json(artifact_path("rag_eval_coverage_v1_6.json"))
    gap = read_json(artifact_path("runtime_readiness_gap_report_v1_7.json"))

    if len(samples) != len(samples_json):
        fail(failures, "eia_permit_extraction_samples_v1_2.json", "csv_json_count_mismatch")
    if len(samples) < 5:
        fail(failures, "eia_permit_extraction_samples_v1_2.csv", "too_few_samples")
    if len(predicates) < 15:
        fail(failures, "eia_permit_extracted_predicates_v1_2.csv", "too_few_predicates")
    if len(rules) < 10:
        fail(failures, "process_scenario_activation_rules_v1_3.csv", "too_few_activation_rules")
    if len(oq_overlay) != len(oq_source) or len(oq_overlay) != 19:
        fail(failures, "open_question_decision_overlay_v1_4.csv", "open_question_count_drift", str(len(oq_overlay)))
    if len(review_slices) < 7:
        fail(failures, "human_review_slices_v1_5.csv", "too_few_review_slices")
    if len(eval_rows) < 12:
        fail(failures, "retrieval_eval_set_v1_6.jsonl", "too_few_eval_items")
    if len(readiness) < 8:
        fail(failures, "runtime_readiness_matrix_v1_7.csv", "too_few_readiness_rows")

    check_boundary(failures, "eia_permit_extraction_samples_v1_2.csv", samples, "sample_id")
    check_boundary(failures, "eia_permit_extracted_predicates_v1_2.csv", predicates, "predicate_id")
    check_boundary(failures, "process_scenario_activation_rules_v1_3.csv", rules, "rule_id")
    check_boundary(failures, "open_question_decision_overlay_v1_4.csv", oq_overlay, "question_id")
    check_boundary(failures, "human_review_slices_v1_5.csv", review_slices, "review_slice_id")
    check_boundary(failures, "runtime_readiness_matrix_v1_7.csv", readiness, "target")
    for row in eval_rows:
        if row.get("runtime_status") != RUNTIME_STATUS or row.get("final_state") != FINAL_STATE or row.get("runtime_integration") != RUNTIME_INTEGRATION:
            fail(failures, "retrieval_eval_set_v1_6.jsonl", "bad_runtime_boundary", row.get("eval_id", ""))
        if not row.get("must_include_boundary_notice") or not row.get("must_not_claim_runtime_ready"):
            fail(failures, "retrieval_eval_set_v1_6.jsonl", "missing_rag_boundary_assertion", row.get("eval_id", ""))

    for row in samples:
        for field in ["source_excerpt", "linked_process_ids", "linked_scenario_ids", "confirmation_questions", "evidence_refs"]:
            if not row.get(field, "").strip():
                fail(failures, "eia_permit_extraction_samples_v1_2.csv", f"missing_{field}", row.get("sample_id", ""))
    for row in rules:
        for field in ["activation_condition", "negative_condition", "evidence_chain", "photo_points", "score13_hint"]:
            if not row.get(field, "").strip():
                fail(failures, "process_scenario_activation_rules_v1_3.csv", f"missing_{field}", row.get("rule_id", ""))
        if row.get("rule_effect") != "CANDIDATE_SCENARIO_ACTIVATION_ONLY":
            fail(failures, "process_scenario_activation_rules_v1_3.csv", "bad_rule_effect", row.get("rule_id", ""))
    for row in oq_overlay:
        if row.get("human_review_label") or row.get("human_reviewer"):
            fail(failures, "open_question_decision_overlay_v1_4.csv", "fake_human_review", row.get("question_id", ""))
        if row.get("decision_status") != "PRELIMINARY_NOT_CLOSED":
            fail(failures, "open_question_decision_overlay_v1_4.csv", "question_closed_without_review", row.get("question_id", ""))

    required_categories = {
        "process_evidence",
        "negation_scope",
        "industry_code",
        "permit_catalog",
        "score13_mapping",
        "inspection_evidence",
        "open_question_trace",
        "runtime_boundary",
        "scenario_template",
        "solid_waste",
        "emergency",
        "rag_boundary",
    }
    categories = {row.get("eval_category") for row in eval_rows}
    missing_categories = required_categories - categories
    if missing_categories:
        fail(failures, "retrieval_eval_set_v1_6.jsonl", "missing_eval_categories", ";".join(sorted(missing_categories)))
    if set(coverage.get("required_categories", [])) != categories:
        fail(failures, "rag_eval_coverage_v1_6.json", "coverage_category_mismatch")

    for doc_name, doc in [
        ("knowledge_base_manifest_v1_2_to_v1_7.json", manifest),
        ("rag_eval_coverage_v1_6.json", coverage),
        ("runtime_readiness_gap_report_v1_7.json", gap),
    ]:
        if doc.get("final_state") != FINAL_STATE:
            fail(failures, doc_name, "bad_final_state")
        if doc.get("runtime_integration") != RUNTIME_INTEGRATION:
            fail(failures, doc_name, "bad_runtime_integration")

    for row in readiness:
        if row.get("allowed_state") == "APPROVED_RUNTIME":
            fail(failures, "runtime_readiness_matrix_v1_7.csv", "runtime_approved_in_candidate_package", row.get("target", ""))

    forbidden_claims = [
        "runtime_integration: enabled",
        "正式permit_type已生成",
        "正式检查模板已生成",
        "自动扣分已启用",
        "已接 EcoCheck runtime",
    ]
    for name in required:
        path = artifact_path(name)
        if path.suffix.lower() in {".md", ".json", ".csv", ".jsonl"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
            for phrase in forbidden_claims:
                if phrase in text:
                    fail(failures, name, "forbidden_runtime_claim", phrase)

    report = {
        "validation_status": "PASS" if not failures else "FAIL",
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
        "failure_count": len(failures),
        "counts": {
            "v1_2_samples": len(samples),
            "v1_2_predicates": len(predicates),
            "v1_3_rules": len(rules),
            "v1_4_open_questions": len(oq_overlay),
            "v1_5_review_slices": len(review_slices),
            "v1_6_eval_items": len(eval_rows),
            "v1_7_readiness_rows": len(readiness),
        },
        "failure_samples": failures[:50],
    }
    (artifact_path("semantic_governance_roadmap_validation_report_v1_2_to_v1_7.json")).write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (artifact_path("semantic_governance_roadmap_failure_list_v1_2_to_v1_7.json")).write_text(
        json.dumps(failures, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
