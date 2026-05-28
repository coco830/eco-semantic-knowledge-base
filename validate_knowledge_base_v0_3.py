import csv
import json
from collections import Counter
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
    if not value:
        return default
    return json.loads(value)


def main():
    errors = []
    failures = []

    classes = [r for r in read_csv(ROOT / "industry_catalog_base.csv") if r["level"] == "class"]
    class_codes = {r["class_code"] for r in classes}
    candidates = read_json(ROOT / "all_industry_scenario_candidates_v0_2.json")
    candidate_codes = [r["industry_code"] for r in candidates]
    candidate_ids = [r["candidate_rule_id"] for r in candidates]
    if len(set(candidate_codes)) != 1382 or set(candidate_codes) != class_codes:
        errors.append("全量行业候选覆盖不是 1382/1382")
    if len(set(candidate_ids)) != len(candidate_ids):
        errors.append("candidate_rule_id 存在重复")
    if any(r["permit_type"] != "NEED_CONFIRM" for r in candidates):
        errors.append("存在非 NEED_CONFIRM 的 permit_type")
    if any(r["runtime_status"] != "CANDIDATE_ONLY" for r in candidates):
        errors.append("存在非 CANDIDATE_ONLY 的主候选 runtime_status")

    raw_permit = read_csv(ROOT / "permit_management_catalog_table_cells.csv")
    entry_nos = [int(r["catalog_entry_no"]) for r in raw_permit]
    if sorted(entry_nos) != list(range(1, 113)):
        errors.append("排污许可名录条目不是 1-112 连续")
    if len(entry_nos) != len(set(entry_nos)):
        errors.append("排污许可名录条目存在重复")

    permit_conditions = read_csv(ROOT / "all_permit_condition_backfill_v0_3.csv")
    if len(permit_conditions) != 336:
        errors.append("三类管理条件未覆盖 112*3")
    for r in permit_conditions:
        if not r["source_basis"] or not r["entry_no"] or not r["raw_condition"] or not r["confidence"] or not r["blocking_flags"]:
            failures.append({"file": "all_permit_condition_backfill_v0_3.csv", "reason": "missing condition audit fields", "row": r.get("entry_no")})
        if r["permit_type"] != "NEED_CONFIRM" or r["runtime_status"] != "DRAFT_NOT_FOR_RUNTIME":
            failures.append({"file": "all_permit_condition_backfill_v0_3.csv", "reason": "bad status", "row": r.get("entry_no")})

    scenario_ids = {r["scenario_id"] for r in read_json(ROOT / "scenario_templates.json")}
    context = read_csv(ROOT / "all_context_applicability_review_v0_3.csv")
    context_industry_codes = {r["industry_code"] for r in context}
    context_entry_nos = {int(r["entry_no"]) for r in context}
    if not context_industry_codes.issubset(class_codes):
        errors.append("适用关系存在悬空 industry_code")
    if not context_entry_nos.issubset(set(entry_nos)):
        errors.append("适用关系存在悬空 entry_no")
    for r in context:
        related = parse_json(r["related_scenario_ids"])
        bad = [sid for sid in related if sid not in scenario_ids]
        if bad:
            failures.append({"file": "all_context_applicability_review_v0_3.csv", "reason": "orphan scenario_id", "industry_code": r["industry_code"], "bad": bad})
        if r["permit_type"] != "NEED_CONFIRM" or r["runtime_status"] != "DRAFT_NOT_FOR_RUNTIME":
            failures.append({"file": "all_context_applicability_review_v0_3.csv", "reason": "bad status", "industry_code": r["industry_code"]})
        if not r["source_basis"] or not r["confidence"] or not parse_json(r["confirmation_questions"]):
            failures.append({"file": "all_context_applicability_review_v0_3.csv", "reason": "missing source/confidence/questions", "industry_code": r["industry_code"]})
        if r["relation_source"] == "DIVISION_CONTEXT" and r["gate_status"] == "APPLIES" and r["evidence_field"] in {"", "none"}:
            failures.append({"file": "all_context_applicability_review_v0_3.csv", "reason": "DIVISION_CONTEXT no-evidence APPLIES", "industry_code": r["industry_code"]})

    inspections = read_csv(ROOT / "inspection_candidate_recommendations_v0_3.csv")
    for r in inspections:
        if r["runtime_status"] != "CANDIDATE_ONLY":
            failures.append({"file": "inspection_candidate_recommendations_v0_3.csv", "reason": "bad runtime_status", "scenario_id": r["scenario_id"]})
        if not r["photo_points"] or not r["evidence_chain"]:
            failures.append({"file": "inspection_candidate_recommendations_v0_3.csv", "reason": "missing photo_points/evidence_chain", "scenario_id": r["scenario_id"]})
        if r["scenario_id"] not in scenario_ids:
            failures.append({"file": "inspection_candidate_recommendations_v0_3.csv", "reason": "orphan scenario_id", "scenario_id": r["scenario_id"]})

    scenario_gov = read_json(ROOT / "scenario_template_governance_v0_3.json")
    for r in scenario_gov:
        if not r["activation_condition"] or not r["evidence_requirements"] or not r["photo_points"] or not r["risk_points"] or not r["confirmation_questions"]:
            failures.append({"file": "scenario_template_governance_v0_3.json", "reason": "missing scenario governance fields", "scenario_id": r["scenario_id"]})
        if r["runtime_status"] != "DRAFT_NOT_FOR_RUNTIME":
            failures.append({"file": "scenario_template_governance_v0_3.json", "reason": "bad runtime_status", "scenario_id": r["scenario_id"]})

    manifest = read_json(ROOT / "knowledge_base_manifest_v0_3.json")
    if manifest.get("final_state") != FINAL_STATE or manifest.get("runtime_integration") != "disabled":
        errors.append("manifest final_state/runtime_integration 错误")

    all_errors = errors + [f"{f['file']}:{f['reason']}" for f in failures]
    report = {
        "validation_status": "PASS" if not all_errors else "FAIL",
        "final_state": FINAL_STATE,
        "industry_candidate_coverage": f"{len(set(candidate_codes))}/1382",
        "permit_catalog_entry_coverage": f"{min(entry_nos)}-{max(entry_nos)}",
        "permit_condition_rows": len(permit_conditions),
        "context_relation_rows": len(context),
        "context_gate_status_counts": dict(sorted(Counter(r["gate_status"] for r in context).items())),
        "inspection_candidate_rows": len(inspections),
        "failure_count": len(all_errors),
        "errors": errors,
        "failure_samples": failures[:200],
    }
    (ROOT / "knowledge_base_v0_3_validation_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    fail_fields = ["file", "reason", "industry_code", "scenario_id", "row", "bad"]
    with (ROOT / "knowledge_base_v0_3_failure_list.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fail_fields)
        writer.writeheader()
        for row in failures:
            writer.writerow({field: json.dumps(row.get(field), ensure_ascii=False) if isinstance(row.get(field), list) else row.get(field, "") for field in fail_fields})
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["validation_status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
