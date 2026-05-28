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


def fail(failures, file, reason, row_id=""):
    failures.append({"file": file, "reason": reason, "row_id": row_id})


def split_semicolon(value):
    return [x for x in (value or "").split(";") if x]


def normalize_json_value(value):
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return ""
    return str(value)


def check_csv_json_parity(failures, csv_name, json_name, id_field):
    csv_rows = read_csv(artifact_path(csv_name))
    json_rows = read_json(artifact_path(json_name))
    if len(csv_rows) != len(json_rows):
        fail(failures, json_name, "csv_json_count_mismatch", f"{len(csv_rows)}!={len(json_rows)}")
        return
    csv_by_id = {row.get(id_field, ""): row for row in csv_rows}
    json_by_id = {normalize_json_value(row.get(id_field, "")): row for row in json_rows}
    if set(csv_by_id) != set(json_by_id):
        fail(failures, json_name, "csv_json_id_set_mismatch", id_field)
        return
    for row_id, csv_row in csv_by_id.items():
        json_row = json_by_id[row_id]
        csv_fields = set(csv_row)
        json_fields = set(json_row)
        if csv_fields != json_fields:
            fail(failures, json_name, "csv_json_field_set_mismatch", row_id)
            continue
        for field in csv_fields:
            if csv_row.get(field, "") != normalize_json_value(json_row.get(field, "")):
                fail(failures, json_name, f"csv_json_value_mismatch:{field}", row_id)


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
        if not (artifact_path(name)).exists():
            fail(failures, name, "missing_required_output")

    scenarios = {row["scenario_id"] for row in read_json(artifact_path("scenario_templates.json"))}
    triggers = read_csv(artifact_path("process_trigger_dictionary_v1_1.csv"))
    triggers_json = read_json(artifact_path("process_trigger_dictionary_v1_1.json"))
    activations = read_csv(artifact_path("process_to_scenario_activation_v1_1.csv"))
    evidence = read_csv(artifact_path("process_evidence_predicates_samples_v1_1.csv"))
    overlays = read_csv(artifact_path("enterprise_profile_overlay_samples_v1_1.csv"))
    manifest = read_json(artifact_path("knowledge_base_manifest_v1_1.json"))
    gate = read_json(artifact_path("process_evidence_gate_report_v1_1.json"))
    graph_design = read_json(artifact_path("process_graph_rag_design_v1_1.json"))

    check_csv_json_parity(failures, "process_trigger_dictionary_v1_1.csv", "process_trigger_dictionary_v1_1.json", "process_id")
    check_csv_json_parity(failures, "process_to_scenario_activation_v1_1.csv", "process_to_scenario_activation_v1_1.json", "activation_id")
    check_csv_json_parity(failures, "process_evidence_predicates_samples_v1_1.csv", "process_evidence_predicates_samples_v1_1.json", "evidence_id")
    check_csv_json_parity(failures, "enterprise_profile_overlay_samples_v1_1.csv", "enterprise_profile_overlay_samples_v1_1.json", "overlay_id")
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
        if row.get("final_state") != FINAL_STATE or row.get("runtime_integration") != RUNTIME_INTEGRATION:
            fail(failures, "process_trigger_dictionary_v1_1.csv", "bad_runtime_boundary", pid)

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
        if (
            row.get("runtime_status") != RUNTIME_STATUS
            or row.get("final_state") != FINAL_STATE
            or row.get("runtime_integration") != RUNTIME_INTEGRATION
        ):
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
        if row.get("final_state") != FINAL_STATE or row.get("runtime_integration") != RUNTIME_INTEGRATION:
            fail(failures, "process_evidence_predicates_samples_v1_1.csv", "bad_runtime_boundary", eid)
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
    allowed_overlay_scope = {"PROCESS_ONLY", "SCENARIO_WIDE"}
    overlay_groups = {}
    for row in overlays:
        oid = row.get("overlay_id", "")
        overlay_groups.setdefault((row.get("enterprise_id"), row.get("scenario_id")), []).append(row)
        if row.get("evidence_id") not in evidence_ids:
            fail(failures, "enterprise_profile_overlay_samples_v1_1.csv", "dangling_evidence_id", oid)
        if row.get("overlay_status") not in allowed_overlay_status:
            fail(failures, "enterprise_profile_overlay_samples_v1_1.csv", "bad_overlay_status", oid)
        if row.get("overlay_scope") not in allowed_overlay_scope:
            fail(failures, "enterprise_profile_overlay_samples_v1_1.csv", "bad_overlay_scope", oid)
        if not row.get("overlay_scope_reason", "").strip():
            fail(failures, "enterprise_profile_overlay_samples_v1_1.csv", "missing_overlay_scope_reason", oid)
        if row.get("permit_type_status") != "NEED_PERMIT_CONFIRM":
            fail(failures, "enterprise_profile_overlay_samples_v1_1.csv", "permit_type_not_blocked", oid)
        if (
            row.get("runtime_status") != RUNTIME_STATUS
            or row.get("final_state") != FINAL_STATE
            or row.get("runtime_integration") != RUNTIME_INTEGRATION
        ):
            fail(failures, "enterprise_profile_overlay_samples_v1_1.csv", "bad_runtime_boundary", oid)
        if row.get("overlay_status") == "SCENARIO_EVIDENCE_CONFIRMED" and row.get("site_verification_status") != "SITE_VERIFICATION_REQUIRED":
            fail(failures, "enterprise_profile_overlay_samples_v1_1.csv", "confirmed_without_site_verification", oid)
        if row.get("overlay_status") == "NOT_APPLY_WITH_EVIDENCE" and row.get("overlay_scope") != "PROCESS_ONLY":
            fail(failures, "enterprise_profile_overlay_samples_v1_1.csv", "not_apply_without_process_scope", oid)

    for (enterprise_id, scenario_id), rows in overlay_groups.items():
        confirmed = [row for row in rows if row.get("overlay_status") == "SCENARIO_EVIDENCE_CONFIRMED"]
        not_apply = [row for row in rows if row.get("overlay_status") == "NOT_APPLY_WITH_EVIDENCE"]
        if confirmed and not_apply:
            confirmed_processes = {row.get("process_id") for row in confirmed}
            for row in not_apply:
                row_key = f"{enterprise_id}|{scenario_id}|{row.get('overlay_id')}"
                if row.get("overlay_scope") != "PROCESS_ONLY":
                    fail(failures, "enterprise_profile_overlay_samples_v1_1.csv", "scenario_conflict_without_scope", row_key)
                if row.get("process_id") in confirmed_processes:
                    fail(failures, "enterprise_profile_overlay_samples_v1_1.csv", "same_process_confirmed_and_not_apply", row_key)

    forbidden_claims = [
        "runtime_integration: enabled",
        "正式permit_type已生成",
        "正式检查模板已生成",
        "自动扣分已启用",
        "已接 EcoCheck runtime",
    ]
    for name in required:
        path = artifact_path(name)
        if path.suffix.lower() in {".md", ".json", ".csv"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
            for phrase in forbidden_claims:
                if phrase in text:
                    fail(failures, name, "forbidden_runtime_claim", phrase)

    schema_text = (artifact_path("process_evidence_schema_v1_1.md")).read_text(encoding="utf-8")
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
    (artifact_path("process_evidence_validation_report_v1_1.json")).write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (artifact_path("process_evidence_failure_list_v1_1.json")).write_text(
        json.dumps(failures, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
