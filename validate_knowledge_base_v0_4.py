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


def parse_json(value, default=None):
    if default is None:
        default = []
    if isinstance(value, (list, dict)):
        return value
    if not value:
        return default
    return json.loads(value)


def compact(value):
    return (value or "").replace(" ", "").replace("\n", "")


def add_failure(failures, file, reason, row_id="", extra=""):
    failures.append({"file": file, "reason": reason, "row_id": row_id, "extra": extra})


def main():
    failures = []
    required = [
        "build_knowledge_base_v0_4.py",
        "validate_knowledge_base_v0_4.py",
        "all_context_applicability_review_v0_4.csv",
        "all_context_applicability_review_v0_4.json",
        "all_permit_condition_backfill_v0_4.csv",
        "all_permit_condition_backfill_v0_4.json",
        "open_questions_v0_4.csv",
        "open_questions_v0_4.md",
        "knowledge_base_manifest_v0_4.json",
        "knowledge_base_v0_4_gate_report.md",
        "knowledge_base_v0_4_gate_report.json",
        "automated_denoise_diff_report_v0_4.md",
        "risk_acceptance_queue_v0_4.csv",
        "FINAL_COMPLETION_REPORT_v0_4.md",
    ]
    for name in required:
        if not (ROOT / name).exists():
            add_failure(failures, name, "missing_required_output")

    classes = [r for r in read_csv(ROOT / "industry_catalog_base.csv") if r["level"] == "class"]
    class_codes = {r["class_code"] for r in classes}
    candidates = read_json(ROOT / "all_industry_scenario_candidates_v0_2.json")
    if {r["industry_code"] for r in candidates} != class_codes or len({r["industry_code"] for r in candidates}) != 1382:
        add_failure(failures, "all_industry_scenario_candidates_v0_2.json", "industry_candidate_coverage_not_1382")
    if len({r["candidate_rule_id"] for r in candidates}) != len(candidates):
        add_failure(failures, "all_industry_scenario_candidates_v0_2.json", "duplicate_candidate_rule_id")
    for r in candidates:
        if r["permit_type"] != "NEED_CONFIRM" or r["runtime_status"] != "CANDIDATE_ONLY":
            add_failure(failures, "all_industry_scenario_candidates_v0_2.json", "bad_candidate_status", r["industry_code"])

    raw_entries = read_csv(ROOT / "permit_management_catalog_table_cells.csv")
    entry_nos = [int(r["catalog_entry_no"]) for r in raw_entries]
    if sorted(entry_nos) != list(range(1, 113)) or len(entry_nos) != len(set(entry_nos)):
        add_failure(failures, "permit_management_catalog_table_cells.csv", "permit_catalog_entries_not_1_112_continuous")

    permit_rows = read_csv(ROOT / "all_permit_condition_backfill_v0_4.csv")
    if len(permit_rows) != 336:
        add_failure(failures, "all_permit_condition_backfill_v0_4.csv", "permit_condition_rows_not_112_times_3", str(len(permit_rows)))
    for r in permit_rows:
        row_id = f"{r.get('entry_no')}-{r.get('target_management_condition')}"
        if r.get("permit_type") != "NEED_CONFIRM" or r.get("runtime_status") != "DRAFT_NOT_FOR_RUNTIME":
            add_failure(failures, "all_permit_condition_backfill_v0_4.csv", "bad_status", row_id)
        if not r.get("source_basis") or not r.get("confidence") or not parse_json(r.get("confirmation_questions")):
            add_failure(failures, "all_permit_condition_backfill_v0_4.csv", "missing_source_confidence_or_questions", row_id)
        if "除纳入重点排污单位名录" in compact(r.get("raw_condition")):
            predicates = parse_json(r.get("normalized_condition"))
            questions = "".join(parse_json(r.get("confirmation_questions")))
            if not any(p.get("flag") == "dynamic_key_pollutant_unit_list" and p.get("operator") == "not_present" and p.get("polarity") == "excluded" for p in predicates):
                add_failure(failures, "all_permit_condition_backfill_v0_4.csv", "negative_semantics_positivized", row_id)
            if "未被纳入" not in questions and "若已纳入" not in questions:
                add_failure(failures, "all_permit_condition_backfill_v0_4.csv", "negative_confirmation_question_missing", row_id)

    scenario_ids = {r["scenario_id"] for r in read_json(ROOT / "scenario_templates.json")}
    context_rows = read_csv(ROOT / "all_context_applicability_review_v0_4.csv")
    for r in context_rows:
        row_id = r.get("candidate_relation_id", "")
        if r.get("industry_code") not in class_codes:
            add_failure(failures, "all_context_applicability_review_v0_4.csv", "orphan_industry_code", row_id)
        if int(r.get("entry_no", "0")) not in set(entry_nos):
            add_failure(failures, "all_context_applicability_review_v0_4.csv", "orphan_entry_no", row_id)
        if r.get("permit_type") != "NEED_CONFIRM" or r.get("runtime_status") != "DRAFT_NOT_FOR_RUNTIME":
            add_failure(failures, "all_context_applicability_review_v0_4.csv", "bad_status", row_id)
        if not r.get("source_basis") or not r.get("confidence") or not parse_json(r.get("confirmation_questions")):
            add_failure(failures, "all_context_applicability_review_v0_4.csv", "missing_source_confidence_or_questions", row_id)
        if r.get("relation_source") == "DIVISION_CONTEXT" and r.get("gate_status") == "APPLIES":
            add_failure(failures, "all_context_applicability_review_v0_4.csv", "pure_division_context_applies", row_id)
        if r.get("gate_status") == "NOT_APPLY" and not parse_json(r.get("blocking_flags")):
            add_failure(failures, "all_context_applicability_review_v0_4.csv", "not_apply_missing_blocking_flags", row_id)
        for sid in parse_json(r.get("related_scenario_ids")):
            if sid not in scenario_ids:
                add_failure(failures, "all_context_applicability_review_v0_4.csv", "orphan_scenario_id", row_id, sid)

    open_questions = read_csv(ROOT / "open_questions_v0_4.csv")
    for r in open_questions:
        row_id = r.get("question_id", "")
        for field in ["question", "owner_role", "priority", "affected_artifacts", "close_criteria"]:
            if not r.get(field):
                add_failure(failures, "open_questions_v0_4.csv", f"missing_{field}", row_id)
        if r.get("human_review_label"):
            add_failure(failures, "open_questions_v0_4.csv", "human_review_label_should_remain_empty", row_id)
    if not any(r.get("question_id") == "V04_ENTRY_108_CONTEXT_001" for r in open_questions):
        add_failure(failures, "open_questions_v0_4.csv", "entry108_open_question_missing")

    manifest = read_json(ROOT / "knowledge_base_manifest_v0_4.json")
    gate = read_json(ROOT / "knowledge_base_v0_4_gate_report.json")
    for name, doc in [("knowledge_base_manifest_v0_4.json", manifest), ("knowledge_base_v0_4_gate_report.json", gate)]:
        if doc.get("final_state") != FINAL_STATE:
            add_failure(failures, name, "bad_final_state")
        if "第108条" not in doc.get("entry_108_strategy", ""):
            add_failure(failures, name, "entry108_strategy_missing")
    if manifest.get("runtime_integration") != "disabled":
        add_failure(failures, "knowledge_base_manifest_v0_4.json", "runtime_integration_not_disabled")

    inspection_path = ROOT / "inspection_candidate_recommendations_v0_3.csv"
    if inspection_path.exists():
        for r in read_csv(inspection_path):
            if r.get("runtime_status") != "CANDIDATE_ONLY":
                add_failure(failures, "inspection_candidate_recommendations_v0_3.csv", "inspection_candidate_not_candidate_only", r.get("scenario_id"))
            if not r.get("photo_points") or not r.get("evidence_chain"):
                add_failure(failures, "inspection_candidate_recommendations_v0_3.csv", "missing_photo_points_or_evidence_chain", r.get("scenario_id"))

    fail_fields = ["file", "reason", "row_id", "extra"]
    with (ROOT / "knowledge_base_v0_4_failure_list.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fail_fields)
        writer.writeheader()
        writer.writerows(failures)

    report = {
        "validation_status": "PASS" if not failures else "FAIL",
        "final_state": FINAL_STATE,
        "failure_count": len(failures),
        "industry_candidate_coverage": f"{len({r['industry_code'] for r in candidates})}/1382",
        "permit_condition_rows": len(permit_rows),
        "context_relation_rows": len(context_rows),
        "pure_division_context_applies": sum(1 for r in context_rows if r.get("relation_source") == "DIVISION_CONTEXT" and r.get("gate_status") == "APPLIES"),
        "not_apply_missing_blocking_flags": sum(1 for r in context_rows if r.get("gate_status") == "NOT_APPLY" and not parse_json(r.get("blocking_flags"))),
        "open_questions": len(open_questions),
        "failure_samples": failures[:50],
    }
    (ROOT / "knowledge_base_v0_4_validation_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
