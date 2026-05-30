import csv
import json
from pathlib import Path

from kb_paths import artifact_path


ROOT = Path(__file__).resolve().parent
FINAL_STATE = "APPROVED_BASELINE_KNOWLEDGE"
RUNTIME_STATUS = "APPROVED_BASELINE"
RUNTIME_INTEGRATION = "approved_baseline_export_ready"
APPROVAL_STATUS = "HUMAN_APPROVED_BASELINE"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def fail(failures, file, reason, row_id=""):
    failures.append({"file": file, "reason": reason, "row_id": row_id})


def split_items(value):
    return [part.strip() for part in (value or "").replace("；", ";").split(";") if part.strip()]


def require_boundary(failures, file, row, row_id):
    if row.get("runtime_status") != RUNTIME_STATUS:
        fail(failures, file, "bad_runtime_status", row_id)
    if row.get("final_state") != FINAL_STATE:
        fail(failures, file, "bad_final_state", row_id)
    if row.get("runtime_integration") != RUNTIME_INTEGRATION:
        fail(failures, file, "bad_runtime_integration", row_id)
    if row.get("approval_status") != APPROVAL_STATUS:
        fail(failures, file, "bad_approval_status", row_id)
    if not row.get("approval_source"):
        fail(failures, file, "missing_approval_source", row_id)


def main():
    failures = []
    required = [
        "approved_scenario_templates_v1_0.json",
        "approved_score13_mapping_v1_0.csv",
        "approved_inspection_items_v1_0.csv",
        "approved_inspection_items_v1_0.json",
        "approved_show_if_rules_v1_0.csv",
        "approved_show_if_rules_v1_0.json",
        "approved_issue_remediation_report_chain_v1_0.csv",
        "approved_issue_remediation_report_chain_v1_0.json",
        "approved_baseline_knowledge_manifest_v1_0.json",
        "approved_baseline_knowledge_gate_report_v1_0.json",
        "FINAL_APPROVED_BASELINE_KNOWLEDGE_v1_0.md",
        "build_approved_baseline_knowledge_v1_0.py",
        "validate_approved_baseline_knowledge_v1_0.py",
    ]
    for name in required:
        if not artifact_path(name).exists():
            fail(failures, name, "missing_required_output")

    scenarios = read_json(artifact_path("approved_scenario_templates_v1_0.json"))
    scores = read_csv(artifact_path("approved_score13_mapping_v1_0.csv"))
    inspections = read_csv(artifact_path("approved_inspection_items_v1_0.csv"))
    inspections_json = read_json(artifact_path("approved_inspection_items_v1_0.json"))
    show_if = read_csv(artifact_path("approved_show_if_rules_v1_0.csv"))
    show_if_json = read_json(artifact_path("approved_show_if_rules_v1_0.json"))
    chains = read_csv(artifact_path("approved_issue_remediation_report_chain_v1_0.csv"))
    chains_json = read_json(artifact_path("approved_issue_remediation_report_chain_v1_0.json"))
    manifest = read_json(artifact_path("approved_baseline_knowledge_manifest_v1_0.json"))

    source_scenarios = read_json(artifact_path("scenario_templates.json"))
    source_inspections = read_csv(artifact_path("inspection_candidate_recommendations_v0_3.csv"))

    if len(scenarios) != len(source_scenarios):
        fail(failures, "approved_scenario_templates_v1_0.json", "scenario_count_drift", f"{len(scenarios)}!={len(source_scenarios)}")
    if len(inspections) != len(source_inspections):
        fail(failures, "approved_inspection_items_v1_0.csv", "inspection_count_drift", f"{len(inspections)}!={len(source_inspections)}")
    if len(inspections) != len(inspections_json):
        fail(failures, "approved_inspection_items_v1_0.json", "csv_json_count_mismatch")
    if len(show_if) != len(show_if_json):
        fail(failures, "approved_show_if_rules_v1_0.json", "csv_json_count_mismatch")
    if len(chains) != len(chains_json):
        fail(failures, "approved_issue_remediation_report_chain_v1_0.json", "csv_json_count_mismatch")
    if len(show_if) != len(inspections):
        fail(failures, "approved_show_if_rules_v1_0.csv", "show_if_count_mismatch")
    if len(chains) != len(inspections):
        fail(failures, "approved_issue_remediation_report_chain_v1_0.csv", "issue_chain_count_mismatch")

    scenario_ids = {row.get("scenario_id") for row in scenarios}
    score_ids = {row.get("scenario_id") for row in scores}
    seen_show_if = set()
    seen_chain = set()

    for row in scenarios:
        sid = row.get("scenario_id", "")
        require_boundary(failures, "approved_scenario_templates_v1_0.json", row, sid)
        for field in ["triggers", "confirmation_questions", "evidence_requirements", "photo_points"]:
            if not row.get(field):
                fail(failures, "approved_scenario_templates_v1_0.json", f"missing_{field}", sid)

    for row in scores:
        sid = row.get("scenario_id", "")
        require_boundary(failures, "approved_score13_mapping_v1_0.csv", row, sid)
        if sid not in scenario_ids:
            fail(failures, "approved_score13_mapping_v1_0.csv", "dangling_scenario_id", sid)
        if not row.get("primary_score_item_id"):
            fail(failures, "approved_score13_mapping_v1_0.csv", "missing_primary_score_item_id", sid)

    for row in inspections:
        sid = row.get("scenario_id", "")
        require_boundary(failures, "approved_inspection_items_v1_0.csv", row, f"{sid}:{row.get('inspection_type')}")
        if sid not in scenario_ids:
            fail(failures, "approved_inspection_items_v1_0.csv", "dangling_scenario_id", sid)
        if sid not in score_ids:
            fail(failures, "approved_inspection_items_v1_0.csv", "missing_score13_mapping", sid)
        for field in ["candidate_section", "candidate_subsection", "evidence_chain", "photo_points", "confirmation_questions"]:
            if not row.get(field, "").strip():
                fail(failures, "approved_inspection_items_v1_0.csv", f"missing_{field}", sid)

    for row in show_if:
        sid = row.get("scenario_id", "")
        row_id = row.get("show_if_rule_id", "")
        require_boundary(failures, "approved_show_if_rules_v1_0.csv", row, row_id)
        if row_id in seen_show_if:
            fail(failures, "approved_show_if_rules_v1_0.csv", "duplicate_show_if_rule_id", row_id)
        seen_show_if.add(row_id)
        if sid not in scenario_ids:
            fail(failures, "approved_show_if_rules_v1_0.csv", "dangling_scenario_id", row_id)
        if not row.get("show_if_condition_json"):
            fail(failures, "approved_show_if_rules_v1_0.csv", "missing_show_if_condition_json", row_id)
        else:
            try:
                condition = json.loads(row["show_if_condition_json"])
            except json.JSONDecodeError:
                fail(failures, "approved_show_if_rules_v1_0.csv", "invalid_show_if_condition_json", row_id)
            else:
                fields = [item.get("field", "") for group in condition.values() for item in group]
                if not any(f"profile.scenarios.{sid}.active" == field for field in fields):
                    fail(failures, "approved_show_if_rules_v1_0.csv", "missing_scenario_active_condition", row_id)

    for row in chains:
        sid = row.get("scenario_id", "")
        row_id = row.get("chain_id", "")
        require_boundary(failures, "approved_issue_remediation_report_chain_v1_0.csv", row, row_id)
        if row_id in seen_chain:
            fail(failures, "approved_issue_remediation_report_chain_v1_0.csv", "duplicate_chain_id", row_id)
        seen_chain.add(row_id)
        if sid not in scenario_ids:
            fail(failures, "approved_issue_remediation_report_chain_v1_0.csv", "dangling_scenario_id", row_id)
        for field in ["problem_statement_template", "rectification_template", "report_section_hint", "evidence_chain", "photo_points", "default_deduct_policy"]:
            if not row.get(field, "").strip():
                fail(failures, "approved_issue_remediation_report_chain_v1_0.csv", f"missing_{field}", row_id)

    if manifest.get("final_state") != FINAL_STATE:
        fail(failures, "approved_baseline_knowledge_manifest_v1_0.json", "bad_final_state")
    if manifest.get("runtime_integration") != RUNTIME_INTEGRATION:
        fail(failures, "approved_baseline_knowledge_manifest_v1_0.json", "bad_runtime_integration")
    if manifest.get("approval_status") != APPROVAL_STATUS:
        fail(failures, "approved_baseline_knowledge_manifest_v1_0.json", "bad_approval_status")
    if not manifest.get("approval_attestation"):
        fail(failures, "approved_baseline_knowledge_manifest_v1_0.json", "missing_approval_attestation")
    contract = manifest.get("runtime_contract", {})
    if contract.get("can_drive_show_if") is not True:
        fail(failures, "approved_baseline_knowledge_manifest_v1_0.json", "show_if_not_enabled")
    if "Do not infer" not in contract.get("enterprise_permit_type_policy", ""):
        fail(failures, "approved_baseline_knowledge_manifest_v1_0.json", "missing_enterprise_permit_type_guard")

    report = {
        "validation_status": "PASS" if not failures else "FAIL",
        "failure_count": len(failures),
        "final_state": FINAL_STATE,
        "runtime_status": RUNTIME_STATUS,
        "runtime_integration": RUNTIME_INTEGRATION,
        "approval_status": APPROVAL_STATUS,
        "counts": {
            "approved_scenarios": len(scenarios),
            "approved_score13_rows": len(scores),
            "approved_inspection_items": len(inspections),
            "approved_show_if_rules": len(show_if),
            "approved_issue_chains": len(chains),
        },
        "failure_samples": failures[:50],
    }
    artifact_path("approved_baseline_knowledge_gate_report_v1_0.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
