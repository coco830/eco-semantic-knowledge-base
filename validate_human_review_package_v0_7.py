import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FINAL_STATE = "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"
RUNTIME_INTEGRATION = "disabled"
LABELS = {
    "CONFIRM_APPLIES",
    "CONFIRM_MAY_APPLY",
    "CONFIRM_NOT_APPLY",
    "NEED_EIA_CONFIRM",
    "NEED_PERMIT_CONFIRM",
    "NEED_SITE_CONFIRM",
    "REJECT_CANDIDATE",
    "MERGE_DUPLICATE",
    "NEED_RULE_FIX",
}
EDITABLE_FIELDS = [
    "human_review_label",
    "human_reviewer",
    "human_reviewer_role",
    "reviewed_at",
    "human_review_notes",
    "review_basis",
    "evidence_refs",
    "decision_confidence",
]


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
        "human_review_queue_v0_7.csv",
        "human_review_queue_v0_7.json",
        "human_review_decision_schema_v0_7.md",
        "human_review_decision_schema_v0_7.json",
        "human_review_worksheet_v0_7.csv",
        "human_review_worksheet_v0_7.xlsx",
        "human_review_guidance_v0_7.md",
        "human_review_backfill_plan_v0_7.md",
        "build_human_review_package_v0_7.py",
        "validate_human_review_package_v0_7.py",
        "human_review_v0_7_gate_report.md",
        "human_review_v0_7_gate_report.json",
        "FINAL_COMPLETION_REPORT_v0_7.md",
    ]
    for name in required:
        if not (ROOT / name).exists():
            fail(failures, name, "missing_required_output")

    context = read_csv(ROOT / "all_context_applicability_review_v0_4_1.csv")
    permit = read_csv(ROOT / "all_permit_condition_backfill_v0_4_1.csv")
    open_questions = read_csv(ROOT / "open_questions_v0_4_1.csv")
    risks = read_csv(ROOT / "risk_acceptance_queue_v0_4_1.csv")
    queue = read_csv(ROOT / "human_review_queue_v0_7.csv")
    queue_json = read_json(ROOT / "human_review_queue_v0_7.json")
    worksheet = read_csv(ROOT / "human_review_worksheet_v0_7.csv")
    schema = read_json(ROOT / "human_review_decision_schema_v0_7.json")
    gate = read_json(ROOT / "human_review_v0_7_gate_report.json")

    if len(context) != 22815:
        fail(failures, "all_context_applicability_review_v0_4_1.csv", "context_count_drift", str(len(context)))
    if len(permit) != 336:
        fail(failures, "all_permit_condition_backfill_v0_4_1.csv", "permit_condition_count_drift", str(len(permit)))
    if len(open_questions) != 19:
        fail(failures, "open_questions_v0_4_1.csv", "open_question_count_drift", str(len(open_questions)))
    if len(risks) != 9:
        fail(failures, "risk_acceptance_queue_v0_4_1.csv", "risk_count_drift", str(len(risks)))
    if len(queue) != 22815 or len(queue_json) != 22815 or len(worksheet) != 22815:
        fail(failures, "human_review_queue_v0_7.csv", "review_queue_count_drift")

    required_queue_fields = {
        "review_item_id", "source_table", "source_row_id", "candidate_relation_id",
        "industry_code", "industry_name", "entry_no", "target_management_condition",
        "raw_condition", "normalized_condition", "gate_status", "gate_reason", "relation_source",
        "source_basis", "confidence", "blocking_flags", "confirmation_questions",
        "related_scenario_ids", "open_question_refs", "risk_refs", "review_priority", "review_bucket",
    }
    for field in required_queue_fields:
        if field not in queue[0]:
            fail(failures, "human_review_queue_v0_7.csv", "missing_required_field", field)

    review_ids = [r["review_item_id"] for r in queue]
    if len(review_ids) != len(set(review_ids)):
        fail(failures, "human_review_queue_v0_7.csv", "duplicate_review_item_id")

    for row in queue:
        rid = row["review_item_id"]
        if row.get("final_state") != FINAL_STATE or row.get("runtime_integration") != RUNTIME_INTEGRATION:
            fail(failures, "human_review_queue_v0_7.csv", "bad_boundary", rid)
        if not row.get("open_question_refs") or not row.get("risk_refs"):
            fail(failures, "human_review_queue_v0_7.csv", "missing_refs", rid)

    for row in worksheet:
        rid = row["review_item_id"]
        label = row.get("human_review_label", "")
        if label and label not in LABELS:
            fail(failures, "human_review_worksheet_v0_7.csv", "invalid_label", rid)
        if any(row.get(field) for field in ["human_reviewer", "reviewed_at"]):
            fail(failures, "human_review_worksheet_v0_7.csv", "forged_human_review_prefill", rid)
        if label.startswith("CONFIRM"):
            for field in ["human_reviewer", "human_review_notes", "review_basis", "evidence_refs"]:
                if not row.get(field):
                    fail(failures, "human_review_worksheet_v0_7.csv", f"confirm_missing_{field}", rid)

    schema_labels = {item["label"] for item in schema.get("labels", [])}
    if schema_labels != LABELS:
        fail(failures, "human_review_decision_schema_v0_7.json", "label_enum_mismatch")
    if schema.get("final_state") != FINAL_STATE or schema.get("runtime_integration") != RUNTIME_INTEGRATION:
        fail(failures, "human_review_decision_schema_v0_7.json", "bad_boundary")
    if "runtime_integration" not in schema.get("second_approval_required_for", []):
        fail(failures, "human_review_decision_schema_v0_7.json", "missing_second_approval_runtime")

    if gate.get("final_state") != FINAL_STATE or gate.get("runtime_integration") != RUNTIME_INTEGRATION:
        fail(failures, "human_review_v0_7_gate_report.json", "bad_gate_boundary")

    guidance = (ROOT / "human_review_guidance_v0_7.md").read_text(encoding="utf-8")
    for phrase in ["DIVISION_CONTEXT", "photo_points", "evidence_chain", "人工审阅不等于运行时批准"]:
        if phrase not in guidance:
            fail(failures, "human_review_guidance_v0_7.md", "missing_guidance_phrase", phrase)

    plan = (ROOT / "human_review_backfill_plan_v0_7.md").read_text(encoding="utf-8")
    for phrase in ["不覆盖 v0.4.1 源表", "BLOCKS_RUNTIME", "二次审批", "签字留痕"]:
        if phrase not in plan:
            fail(failures, "human_review_backfill_plan_v0_7.md", "missing_plan_phrase", phrase)

    report = {
        "validation_status": "PASS" if not failures else "FAIL",
        "final_state": FINAL_STATE,
        "failure_count": len(failures),
        "input_counts": {
            "context_relations": len(context),
            "permit_conditions": len(permit),
            "open_questions": len(open_questions),
            "risk_queue": len(risks),
        },
        "review_queue_rows": len(queue),
        "worksheet_rows": len(worksheet),
        "failure_samples": failures[:50],
    }
    (ROOT / "human_review_v0_7_validation_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    gate["validation_status"] = report["validation_status"]
    gate["failure_count"] = len(failures)
    gate["validator"] = "validate_human_review_package_v0_7.py"
    (ROOT / "human_review_v0_7_gate_report.json").write_text(
        json.dumps(gate, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (ROOT / "human_review_v0_7_gate_report.md").write_text(
        "# human_review_v0_7_gate_report\n\n"
        f"- validation_status: `{report['validation_status']}`\n"
        f"- final_state: `{FINAL_STATE}`\n"
        f"- runtime_integration: `{RUNTIME_INTEGRATION}`\n"
        f"- context_relations: {len(context)}\n"
        f"- permit_conditions: {len(permit)}\n"
        f"- open_questions: {len(open_questions)}\n"
        f"- risk_queue: {len(risks)}\n"
        f"- review_queue_rows: {len(queue)}\n"
        f"- worksheet_rows: {len(worksheet)}\n"
        f"- human_review_prefill_count: 0\n"
        f"- failure_count: {len(failures)}\n",
        encoding="utf-8",
    )
    (ROOT / "human_review_v0_7_failure_list.json").write_text(
        json.dumps(failures, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
