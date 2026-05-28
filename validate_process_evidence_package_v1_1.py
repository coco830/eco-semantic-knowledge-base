import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FINAL_STATE = "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"
RUNTIME_INTEGRATION = "disabled"
RUNTIME_STATUS = "DRAFT_NOT_FOR_RUNTIME"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def fail(failures, file, reason, row_id=""):
    failures.append({"file": file, "reason": reason, "row_id": row_id})


def split_semicolon(value):
    return [x for x in (value or "").split(";") if x]


def main():
    failures = []
    required = [
        "process_evidence_schema_v1_1.md",
        "process_trigger_dictionary_v1_1.csv",
        "process_trigger_dictionary_v1_1.json",
        "process_to_scenario_activation_v1_1.csv",
        "process_to_scenario_activation_v1_1.json",
        "process_evidence_predicates_samples_v1_1.csv",
        "process_evidence_predicates_samples_v1_1.json",
        "enterprise_profile_overlay_samples_v1_1.csv",
        "enterprise_profile_overlay_samples_v1_1.json",
        "process_graph_rag_design_v1_1.md",
        "process_graph_rag_design_v1_1.json",
        "process_evidence_gate_report_v1_1.md",
        "process_evidence_gate_report_v1_1.json",
        "knowledge_base_manifest_v1_1.json",
        "FINAL_COMPLETION_REPORT_v1_1.md",
        "build_process_evidence_package_v1_1.py",
        "validate_process_evidence_package_v1_1.py",
    ]
    for name in required:
        if not (ROOT / name).exists():
            fail(failures, name, "missing_required_output")

    scenarios = {row["scenario_id"] for row in read_json(ROOT / "scenario_templates.json")}
    triggers = read_csv(ROOT / "process_trigger_dictionary_v1_1.csv")
    triggers_json = read_json(ROOT / "process_trigger_dictionary_v1_1.json")
    activations = read_csv(ROOT / "process_to_scenario_activation_v1_1.csv")
    evidence = read_csv(ROOT / "process_evidence_predicates_samples_v1_1.csv")
    overlays = read_csv(ROOT / "enterprise_profile_overlay_samples_v1_1.csv")
    manifest = read_json(ROOT / "knowledge_base_manifest_v1_1.json")
    gate = read_json(ROOT / "process_evidence_gate_report_v1_1.json")
    graph_design = read_json(ROOT / "process_graph_rag_design_v1_1.json")

    if len(triggers) != len(triggers_json):
        fail(failures, "process_trigger_dictionary_v1_1.json", "csv_json_count_mismatch")
    if len(triggers) < 10:
        fail(failures, "process_trigger_dictionary_v1_1.csv", "too_few_process_triggers")
    if len(evidence) < 5:
        fail(failures, "process_evidence_predicates_samples_v1_1.csv", "too_few_sample_evidence_rows")
    if len(overlays) < len(evidence):
        fail(failures, "enterprise_profile_overlay_samples_v1_1.csv", "overlay_count_too_low")

    for file, doc in [
        ("knowledge_base_manifest_v1_1.json", manifest),
        ("process_evidence_gate_report_v1_1.json", gate),
        ("process_graph_rag_design_v1_1.json", graph_design),
    ]:
        if doc.get("final_state") != FINAL_STATE:
            fail(failures, file, "bad_final_state")
        if doc.get("runtime_integration") != RUNTIME_INTEGRATION:
            fail(failures, file, "bad_runtime_integration")

    process_ids = {row["process_id"] for row in triggers}
    for row in triggers:
        pid = row.get("process_id", "")
        for field in [
            "aliases",
            "positive_keywords",
            "negative_keywords",
            "linked_scenario_ids",
            "evidence_requirements",
            "photo_points",
        ]:
            if not row.get(field, "").strip():
                fail(failures, "process_trigger_dictionary_v1_1.csv", f"missing_{field}", pid)
        if row.get("runtime_status") != RUNTIME_STATUS:
            fail(failures, "process_trigger_dictionary_v1_1.csv", "bad_runtime_status", pid)

    allowed_new_scenarios = {
        "NEW_SCN_LAB_WASTE_CANDIDATE",
        "NEW_SCN_TAILINGS_CANDIDATE",
        "NEW_SCN_WASTE_DISPOSAL_CANDIDATE",
    }
    for row in activations:
        aid = row.get("activation_id", "")
        if row.get("process_id") not in process_ids:
            fail(failures, "process_to_scenario_activation_v1_1.csv", "dangling_process_id", aid)
        sid = row.get("scenario_id")
        if sid not in scenarios and sid not in allowed_new_scenarios:
            fail(failures, "process_to_scenario_activation_v1_1.csv", "dangling_scenario_id", aid)
        if row.get("runtime_status") != RUNTIME_STATUS or row.get("final_state") != FINAL_STATE:
            fail(failures, "process_to_scenario_activation_v1_1.csv", "bad_boundary", aid)
        for field in ["activation_condition", "confirmation_questions", "photo_points"]:
            if not row.get(field, "").strip():
                fail(failures, "process_to_scenario_activation_v1_1.csv", f"missing_{field}", aid)

    evidence_ids = {row["evidence_id"] for row in evidence}
    allowed_strength = {"DIRECT", "IMPLIED", "NEGATED", "UNKNOWN"}
    for row in evidence:
        eid = row.get("evidence_id", "")
        if row.get("process_id") not in process_ids:
            fail(failures, "process_evidence_predicates_samples_v1_1.csv", "dangling_process_id", eid)
        if row.get("evidence_strength") not in allowed_strength:
            fail(failures, "process_evidence_predicates_samples_v1_1.csv", "bad_evidence_strength", eid)
        if not row.get("source_excerpt", "").strip():
            fail(failures, "process_evidence_predicates_samples_v1_1.csv", "missing_source_excerpt", eid)
        if not row.get("confirmation_questions", "").strip():
            fail(failures, "process_evidence_predicates_samples_v1_1.csv", "missing_confirmation_questions", eid)
        if row.get("runtime_status") != RUNTIME_STATUS:
            fail(failures, "process_evidence_predicates_samples_v1_1.csv", "bad_runtime_status", eid)
        if row.get("evidence_strength") == "NEGATED":
            text = row.get("source_excerpt", "")
            if not any(token in text for token in ["不设置", "无", "外协", "不产生"]):
                fail(failures, "process_evidence_predicates_samples_v1_1.csv", "negated_without_negative_text", eid)

    allowed_overlay_status = {
        "SCENARIO_EVIDENCE_CONFIRMED",
        "NOT_APPLY_WITH_EVIDENCE",
        "NEW_SCENARIO_CANDIDATE",
        "SITE_CONFLICT_NEEDS_REVIEW",
    }
    for row in overlays:
        oid = row.get("overlay_id", "")
        if row.get("evidence_id") not in evidence_ids:
            fail(failures, "enterprise_profile_overlay_samples_v1_1.csv", "dangling_evidence_id", oid)
        if row.get("overlay_status") not in allowed_overlay_status:
            fail(failures, "enterprise_profile_overlay_samples_v1_1.csv", "bad_overlay_status", oid)
        if row.get("permit_type_status") != "NEED_PERMIT_CONFIRM":
            fail(failures, "enterprise_profile_overlay_samples_v1_1.csv", "permit_type_not_blocked", oid)
        if row.get("runtime_status") != RUNTIME_STATUS or row.get("runtime_integration") != RUNTIME_INTEGRATION:
            fail(failures, "enterprise_profile_overlay_samples_v1_1.csv", "bad_runtime_boundary", oid)
        if row.get("overlay_status") == "SCENARIO_EVIDENCE_CONFIRMED" and row.get("site_verification_status") != "SITE_VERIFICATION_REQUIRED":
            fail(failures, "enterprise_profile_overlay_samples_v1_1.csv", "confirmed_without_site_verification", oid)

    forbidden_claims = [
        "runtime_integration: enabled",
        "正式permit_type已生成",
        "正式检查模板已生成",
        "自动扣分已启用",
        "已接 EcoCheck runtime",
    ]
    for name in required:
        path = ROOT / name
        if path.suffix.lower() in {".md", ".json", ".csv"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
            for phrase in forbidden_claims:
                if phrase in text:
                    fail(failures, name, "forbidden_runtime_claim", phrase)

    schema_text = (ROOT / "process_evidence_schema_v1_1.md").read_text(encoding="utf-8")
    for phrase in ["PROCESS_EVIDENCE_CONFIRMED", "SCENARIO_EVIDENCE_CONFIRMED", "NOT_APPLY_WITH_EVIDENCE", "SITE_VERIFICATION_REQUIRED", FINAL_STATE]:
        if phrase not in schema_text:
            fail(failures, "process_evidence_schema_v1_1.md", "missing_schema_phrase", phrase)

    report = {
        "validation_status": "PASS" if not failures else "FAIL",
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
        "failure_count": len(failures),
        "process_trigger_rows": len(triggers),
        "activation_rows": len(activations),
        "sample_evidence_rows": len(evidence),
        "overlay_rows": len(overlays),
        "failure_samples": failures[:50],
    }
    (ROOT / "process_evidence_validation_report_v1_1.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (ROOT / "process_evidence_failure_list_v1_1.json").write_text(
        json.dumps(failures, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
