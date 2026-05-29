import csv
import json
from pathlib import Path

from kb_paths import artifact_path


ROOT = Path(__file__).resolve().parent
FINAL_STATE = "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"
RUNTIME_INTEGRATION = "disabled"
RUNTIME_STATUS = "DRAFT_NOT_FOR_RUNTIME"
RUNTIME_CANDIDATE = "CANDIDATE_ONLY"

NOISE_SCENARIOS = {
    "SCN_NOISE_SOURCE_BOUNDARY_CONTROL",
    "SCN_NOISE_BOUNDARY_MONITORING_LEDGER",
    "SCN_NOISE_SENSITIVE_RECEPTOR_NIGHT_OPERATION",
    "SCN_SOCIAL_LIFE_NOISE_SOURCE",
}

RADIATION_SCENARIOS = {
    "SCN_RADIATION_DEVICE_SOURCE_SAFETY",
    "SCN_RADIOACTIVE_SOURCE_SECURITY",
    "SCN_RADIOACTIVE_WASTE_STORAGE_TRANSFER_DISPOSAL",
    "SCN_RAD_WASTE_PACKAGE_SOLIDIFICATION_CONTAINER",
    "SCN_RAD_WASTE_DISPOSAL_FACILITY",
    "SCN_RADIOACTIVE_MATERIAL_TRANSPORT",
    "SCN_NORM_RADIOACTIVITY_IN_INDUSTRIAL_RESIDUE",
    "SCN_URANIUM_THORIUM_MINING_RAD_WASTE",
    "SCN_NUCLEAR_FUEL_EFFLUENT_DECOMMISSIONING",
    "SCN_BUILDING_MATERIAL_SLAG_RADIONUCLIDE",
}

NOISE_PROCESS_IDS = {
    "industrial_noise_source",
    "boundary_noise_monitoring",
    "night_operation_sensitive_receptor",
    "social_life_noise_source",
}

RADIATION_PROCESS_IDS = {
    "radiation_device_source",
    "sealed_radioactive_source",
    "radioactive_waste_storage",
    "radioactive_waste_package_container",
    "radioactive_waste_disposal_facility",
    "radioactive_material_transport",
    "norm_industrial_residue_radioactivity",
    "uranium_thorium_mining_rad_waste",
    "nuclear_fuel_effluent_decommissioning",
    "building_material_slag_radionuclide",
}


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def fail(failures, file, reason, row_id=""):
    failures.append({"file": file, "reason": reason, "row_id": row_id})


def split_items(value):
    return [part.strip() for part in (value or "").replace("；", ";").split(";") if part.strip()]


def check_doc_boundary(failures, file, doc):
    if doc.get("final_state") != FINAL_STATE:
        fail(failures, file, "bad_final_state")
    if doc.get("runtime_integration") != RUNTIME_INTEGRATION:
        fail(failures, file, "bad_runtime_integration")


def check_csv_json_parity(failures, csv_name, json_name, id_field):
    csv_rows = read_csv(artifact_path(csv_name))
    json_rows = read_json(artifact_path(json_name))
    if len(csv_rows) != len(json_rows):
        fail(failures, json_name, "csv_json_count_mismatch", f"{len(csv_rows)}!={len(json_rows)}")
        return
    json_by_id = {str(row.get(id_field, "")): row for row in json_rows}
    for row in csv_rows:
        row_id = row.get(id_field, "")
        if row_id not in json_by_id:
            fail(failures, json_name, "csv_json_missing_id", row_id)


def main():
    failures = []
    required = [
        "scenario_templates.json",
        "scenario_to_score13_mapping_v0_3.csv",
        "inspection_candidate_recommendations_v0_3.csv",
        "process_trigger_dictionary_v1_1.csv",
        "process_trigger_dictionary_v1_1.json",
        "process_scenario_activation_rules_v1_3.csv",
        "process_scenario_activation_rules_v1_3.json",
        "noise_radiation_reference_sources_v1_8.csv",
        "noise_radiation_reference_sources_v1_8.json",
        "knowledge_base_manifest_v1_8_noise_radiation_extension.json",
        "noise_radiation_domain_extension_gate_report_v1_8.md",
        "FINAL_COMPLETION_REPORT_v1_8_noise_radiation_extension.md",
        "build_noise_radiation_domain_extension_v1_8.py",
        "validate_noise_radiation_domain_extension_v1_8.py",
    ]
    for name in required:
        if not artifact_path(name).exists():
            fail(failures, name, "missing_required_output")

    scenario_rows = read_json(artifact_path("scenario_templates.json"))
    scenario_by_id = {row.get("scenario_id"): row for row in scenario_rows}
    score_rows = read_csv(artifact_path("scenario_to_score13_mapping_v0_3.csv"))
    inspection_rows = read_csv(artifact_path("inspection_candidate_recommendations_v0_3.csv"))
    trigger_rows = read_csv(artifact_path("process_trigger_dictionary_v1_1.csv"))
    activation_rows = read_csv(artifact_path("process_scenario_activation_rules_v1_3.csv"))
    source_rows = read_csv(artifact_path("noise_radiation_reference_sources_v1_8.csv"))
    manifest = read_json(artifact_path("knowledge_base_manifest_v1_8_noise_radiation_extension.json"))

    check_doc_boundary(failures, "knowledge_base_manifest_v1_8_noise_radiation_extension.json", manifest)
    check_csv_json_parity(failures, "process_trigger_dictionary_v1_1.csv", "process_trigger_dictionary_v1_1.json", "process_id")
    check_csv_json_parity(failures, "process_scenario_activation_rules_v1_3.csv", "process_scenario_activation_rules_v1_3.json", "rule_id")
    check_csv_json_parity(failures, "noise_radiation_reference_sources_v1_8.csv", "noise_radiation_reference_sources_v1_8.json", "source_id")

    for sid in sorted(NOISE_SCENARIOS | RADIATION_SCENARIOS):
        row = scenario_by_id.get(sid)
        if not row:
            fail(failures, "scenario_templates.json", "missing_extension_scenario", sid)
            continue
        for field in ["triggers", "not_applicable_conditions", "confirmation_questions", "evidence_requirements", "photo_points", "related_regulations"]:
            if not row.get(field):
                fail(failures, "scenario_templates.json", f"missing_{field}", sid)
        if row.get("runtime_status") != RUNTIME_STATUS or row.get("final_state") != FINAL_STATE or row.get("runtime_integration") != RUNTIME_INTEGRATION:
            fail(failures, "scenario_templates.json", "bad_runtime_boundary", sid)

    score_ids = {row.get("scenario_id") for row in score_rows}
    for sid in NOISE_SCENARIOS | RADIATION_SCENARIOS:
        if sid not in score_ids:
            fail(failures, "scenario_to_score13_mapping_v0_3.csv", "missing_score_mapping", sid)

    inspections = {(row.get("scenario_id"), row.get("inspection_type")) for row in inspection_rows}
    for sid in NOISE_SCENARIOS | RADIATION_SCENARIOS:
        for typ in ["FIRST", "MONTHLY"]:
            if (sid, typ) not in inspections:
                fail(failures, "inspection_candidate_recommendations_v0_3.csv", "missing_inspection_candidate", f"{sid}:{typ}")
    for row in inspection_rows:
        sid = row.get("scenario_id")
        if sid in NOISE_SCENARIOS | RADIATION_SCENARIOS:
            for field in ["evidence_chain", "photo_points", "confirmation_questions"]:
                if not row.get(field, "").strip():
                    fail(failures, "inspection_candidate_recommendations_v0_3.csv", f"missing_{field}", sid)
            if row.get("runtime_status") != RUNTIME_CANDIDATE:
                fail(failures, "inspection_candidate_recommendations_v0_3.csv", "bad_runtime_status", sid)

    trigger_by_id = {row.get("process_id"): row for row in trigger_rows}
    for pid in NOISE_PROCESS_IDS | RADIATION_PROCESS_IDS:
        row = trigger_by_id.get(pid)
        if not row:
            fail(failures, "process_trigger_dictionary_v1_1.csv", "missing_process_trigger", pid)
            continue
        if row.get("runtime_status") != RUNTIME_STATUS or row.get("final_state") != FINAL_STATE or row.get("runtime_integration") != RUNTIME_INTEGRATION:
            fail(failures, "process_trigger_dictionary_v1_1.csv", "bad_boundary", pid)
        for field in ["positive_keywords", "negative_keywords", "evidence_requirements", "photo_points"]:
            if not row.get(field, "").strip():
                fail(failures, "process_trigger_dictionary_v1_1.csv", f"missing_{field}", pid)
        if pid in RADIATION_PROCESS_IDS and "核;" in row.get("positive_keywords", ""):
            fail(failures, "process_trigger_dictionary_v1_1.csv", "bare_nuclear_keyword_forbidden", pid)

    activation_sids = {row.get("scenario_id") for row in activation_rows}
    for sid in NOISE_SCENARIOS | RADIATION_SCENARIOS:
        if sid not in activation_sids:
            fail(failures, "process_scenario_activation_rules_v1_3.csv", "missing_activation_rule", sid)
    for row in activation_rows:
        sid = row.get("scenario_id")
        if sid in NOISE_SCENARIOS | RADIATION_SCENARIOS:
            if row.get("runtime_status") != RUNTIME_STATUS or row.get("final_state") != FINAL_STATE or row.get("runtime_integration") != RUNTIME_INTEGRATION:
                fail(failures, "process_scenario_activation_rules_v1_3.csv", "bad_boundary", row.get("rule_id", ""))
            if row.get("rule_effect") != "CANDIDATE_SCENARIO_ACTIVATION_ONLY":
                fail(failures, "process_scenario_activation_rules_v1_3.csv", "bad_rule_effect", row.get("rule_id", ""))
            for field in ["activation_condition", "negative_condition", "evidence_chain", "photo_points"]:
                if not row.get(field, "").strip():
                    fail(failures, "process_scenario_activation_rules_v1_3.csv", f"missing_{field}", row.get("rule_id", ""))

    noise_sources = [row for row in source_rows if row.get("domain") == "noise"]
    radiation_sources = [row for row in source_rows if row.get("domain") != "noise"]
    if len(noise_sources) < 4:
        fail(failures, "noise_radiation_reference_sources_v1_8.csv", "too_few_noise_sources", str(len(noise_sources)))
    if len(radiation_sources) < 20:
        fail(failures, "noise_radiation_reference_sources_v1_8.csv", "too_few_radiation_sources", str(len(radiation_sources)))
    for row in source_rows:
        source_id = row.get("source_id", "")
        if row.get("runtime_status") != RUNTIME_STATUS or row.get("final_state") != FINAL_STATE or row.get("runtime_integration") != RUNTIME_INTEGRATION:
            fail(failures, "noise_radiation_reference_sources_v1_8.csv", "bad_boundary", source_id)
        if not Path(ROOT / row.get("file_path", "")).exists():
            fail(failures, "noise_radiation_reference_sources_v1_8.csv", "missing_source_file", source_id)
        if not row.get("applicable_scenario_ids", "").strip():
            fail(failures, "noise_radiation_reference_sources_v1_8.csv", "missing_applicable_scenarios", source_id)

    # Radiation must remain evidence-triggered. It must not be injected into the all-industry default candidate base.
    for candidate_name in ["all_industry_scenario_candidates_v0_2.csv", "industry_scenario_rules.json"]:
        path = artifact_path(candidate_name)
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for sid in RADIATION_SCENARIOS:
            if sid in text:
                fail(failures, candidate_name, "radiation_default_candidate_forbidden", sid)

    report = {
        "validation_status": "PASS" if not failures else "FAIL",
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
        "failure_count": len(failures),
        "counts": {
            "noise_scenarios": len(NOISE_SCENARIOS),
            "radiation_scenarios": len(RADIATION_SCENARIOS),
            "noise_sources": len(noise_sources),
            "radiation_sources": len(radiation_sources),
            "new_process_triggers": len(NOISE_PROCESS_IDS | RADIATION_PROCESS_IDS),
        },
        "failure_samples": failures[:50],
    }
    artifact_path("noise_radiation_domain_extension_gate_report_v1_8.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
