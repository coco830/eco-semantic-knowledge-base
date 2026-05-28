import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FINAL_STATE = "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def parse_json(value):
    return json.loads(value) if value else []


def fail(failures, file, reason, row_id=""):
    failures.append({"file": file, "reason": reason, "row_id": row_id})


def main():
    failures = []
    for name in [
        "all_context_applicability_review_v0_4_1.csv",
        "all_permit_condition_backfill_v0_4_1.csv",
        "risk_acceptance_queue_v0_4_1.csv",
        "knowledge_base_manifest_v0_4_1.json",
        "knowledge_base_v0_4_1_gate_report.json",
        "FINAL_COMPLETION_REPORT_v0_4_1.md",
    ]:
        if not (ROOT / name).exists():
            fail(failures, name, "missing")

    context = read_csv(ROOT / "all_context_applicability_review_v0_4_1.csv")
    target = [r for r in context if r["candidate_relation_id"] == "CTXV04_3012_63_REGISTRATION"]
    if len(target) != 1:
        fail(failures, "all_context_applicability_review_v0_4_1.csv", "target_relation_missing_or_duplicate", "CTXV04_3012_63_REGISTRATION")
    elif target[0]["gate_status"] != "NOT_APPLY" or not parse_json(target[0]["blocking_flags"]):
        fail(failures, "all_context_applicability_review_v0_4_1.csv", "target_relation_not_denoised", "CTXV04_3012_63_REGISTRATION")

    for r in context:
        if r["permit_type"] != "NEED_CONFIRM" or r["runtime_status"] != "DRAFT_NOT_FOR_RUNTIME":
            fail(failures, "all_context_applicability_review_v0_4_1.csv", "bad_status", r["candidate_relation_id"])
        if r["relation_source"] == "DIVISION_CONTEXT" and r["gate_status"] == "APPLIES":
            fail(failures, "all_context_applicability_review_v0_4_1.csv", "pure_division_context_applies", r["candidate_relation_id"])
        if r["gate_status"] == "NOT_APPLY" and not parse_json(r["blocking_flags"]):
            fail(failures, "all_context_applicability_review_v0_4_1.csv", "not_apply_missing_blocking_flags", r["candidate_relation_id"])

    risks = read_csv(ROOT / "risk_acceptance_queue_v0_4_1.csv")
    required_topics = {"runtime_approval_gate", "permit_type_not_formal", "inspection_candidate_not_template", "entry108_strategy"}
    topics = {r["risk_topic"] for r in risks}
    for topic in required_topics - topics:
        fail(failures, "risk_acceptance_queue_v0_4_1.csv", "missing_required_risk_topic", topic)
    for r in risks:
        if not r.get("open_question_refs") or r.get("runtime_status") != "DRAFT_NOT_FOR_RUNTIME" or r.get("final_state") != FINAL_STATE:
            fail(failures, "risk_acceptance_queue_v0_4_1.csv", "bad_risk_fields", r.get("risk_id", ""))

    manifest = read_json(ROOT / "knowledge_base_manifest_v0_4_1.json")
    gate = read_json(ROOT / "knowledge_base_v0_4_1_gate_report.json")
    if manifest.get("final_state") != FINAL_STATE or manifest.get("runtime_integration") != "disabled":
        fail(failures, "knowledge_base_manifest_v0_4_1.json", "bad_boundary")
    if gate.get("catalog_entry_coverage") != "1-112 continuous in permit_management_catalog_table_cells.csv":
        fail(failures, "knowledge_base_v0_4_1_gate_report.json", "catalog_coverage_text_missing")
    if "第108条" not in gate.get("context_relation_entry_count_note", ""):
        fail(failures, "knowledge_base_v0_4_1_gate_report.json", "entry108_note_missing")

    with (ROOT / "knowledge_base_v0_4_1_failure_list.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["file", "reason", "row_id"])
        writer.writeheader()
        writer.writerows(failures)
    report = {
        "validation_status": "PASS" if not failures else "FAIL",
        "final_state": FINAL_STATE,
        "failure_count": len(failures),
        "context_relation_rows": len(context),
        "risk_acceptance_rows": len(risks),
        "failure_samples": failures[:50],
    }
    (ROOT / "knowledge_base_v0_4_1_validation_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
