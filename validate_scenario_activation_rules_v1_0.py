import csv
import json
from pathlib import Path

from kb_paths import artifact_path


ROOT = Path(__file__).resolve().parent
FINAL_STATE = "APPROVED_BASELINE_KNOWLEDGE"
RUNTIME_STATUS = "APPROVED_BASELINE"
RUNTIME_INTEGRATION = "approved_baseline_export_ready"
APPROVAL_STATUS = "HUMAN_APPROVED_BASELINE"
CONFIDENCE = "HIGH"
REQUIRED_SCENARIOS = {
    "SCN_BASE_PRODUCTION_SOLID_NOISE_LEDGER",
    "SCN_HAZWASTE_STORAGE_TRANSFER",
    "SCN_WW_PROCESS_AND_TREATMENT",
    "SCN_VOCS_SOLVENT_AND_TREATMENT",
    "SCN_DUST_PARTICULATE_CONTROL",
    "SCN_MEDICAL_WASTE_RADIATION",
    "SCN_RAINWATER_ACCIDENT_EMERGENCY",
    "SCN_ONLINE_MONITORING_KEY_UNIT",
    "SCN_CHEMICAL_TANK_LDAR_SEEPAGE",
    "SCN_GAS_STATION_VAPOR_UST",
    "SCN_TRAINING_SIGNAGE_REVIEW_GAP",
}
REQUIRED_PERMIT_ITEMS = {
    "hazardous_waste",
    "wastewater",
    "vocs",
    "dust",
    "online_monitoring",
    "permit_execution_reporting",
    "self_monitoring_plan",
    "ledger_records",
    "rainwater_accident",
    "radiation",
    "soil_groundwater",
}
REQUIRED_MEDICAL_OVERRIDES = {
    "MEDICAL_84XX_SIM_REG_SELF_MONITORING_YES",
    "MEDICAL_84XX_SIM_REG_LEDGER_RECORDS_YES",
    "HOSPITAL_84XX_SIM_ONLINE_MONITORING_YES",
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def fail(failures, file, reason, row_id=""):
    failures.append({"file": file, "reason": reason, "row_id": row_id})


def require_boundary(failures, file, row, row_id):
    if row.get("final_state") != FINAL_STATE:
        fail(failures, file, "bad_final_state", row_id)
    if row.get("runtime_status") != RUNTIME_STATUS:
        fail(failures, file, "bad_runtime_status", row_id)
    if row.get("runtime_integration") != RUNTIME_INTEGRATION:
        fail(failures, file, "bad_runtime_integration", row_id)
    if row.get("approval_status") != APPROVAL_STATUS:
        fail(failures, file, "bad_approval_status", row_id)
    if not row.get("approval_source"):
        fail(failures, file, "missing_approval_source", row_id)


def walk_values(value):
    if isinstance(value, dict):
        for item in value.values():
            yield from walk_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk_values(item)
    else:
        yield value


def check_dimensions(failures, file, row_id, row, whitelist):
    for field in ["target_dimensions", "maps_to_dimensions"]:
        for dimension in row.get(field, []) or []:
            if dimension not in whitelist:
                fail(failures, file, f"invalid_{field}", f"{row_id}:{dimension}")


def main():
    failures = []
    rules_path = artifact_path("scenario_activation_rules_v1_0.json")
    manifest_path = artifact_path("scenario_activation_rules_manifest_v1_0.json")
    rules = read_json(rules_path)
    manifest = read_json(manifest_path)

    require_boundary(failures, "scenario_activation_rules_v1_0.json", rules, rules.get("rule_set_id", ""))
    require_boundary(failures, "scenario_activation_rules_manifest_v1_0.json", manifest, manifest.get("manifest_id", ""))

    if rules.get("confidence") != CONFIDENCE:
        fail(failures, "scenario_activation_rules_v1_0.json", "bad_rule_set_confidence")
    if any(value == "NEEDS_REVIEW" for value in walk_values(rules)):
        fail(failures, "scenario_activation_rules_v1_0.json", "contains_needs_review")
    if rules.get("decision_status") != "CLOSED_HIGH_CONFIDENCE":
        fail(failures, "scenario_activation_rules_v1_0.json", "bad_decision_status")

    whitelist = set(rules.get("applicability_dimension_whitelist") or [])
    if len(whitelist) < 24:
        fail(failures, "scenario_activation_rules_v1_0.json", "dimension_whitelist_too_small")

    source_scenarios = {row.get("scenario_id") for row in read_csv(artifact_path("scenario_to_score13_mapping.csv"))}
    rule_rows = rules.get("scenario_activation_rules") or []
    rule_scenarios = {row.get("scenario_id") for row in rule_rows}
    if rule_scenarios != REQUIRED_SCENARIOS:
        fail(
            failures,
            "scenario_activation_rules_v1_0.json",
            "scenario_set_mismatch",
            f"missing={sorted(REQUIRED_SCENARIOS - rule_scenarios)} extra={sorted(rule_scenarios - REQUIRED_SCENARIOS)}",
        )
    dangling = sorted(rule_scenarios - source_scenarios)
    if dangling:
        fail(failures, "scenario_activation_rules_v1_0.json", "scenario_not_in_score13_mapping", ";".join(dangling))

    seen_rule_ids = set()
    for row in rule_rows:
        row_id = row.get("rule_id", "")
        if not row_id:
            fail(failures, "scenario_activation_rules_v1_0.json", "missing_rule_id")
        if row_id in seen_rule_ids:
            fail(failures, "scenario_activation_rules_v1_0.json", "duplicate_rule_id", row_id)
        seen_rule_ids.add(row_id)
        if row.get("confidence") != CONFIDENCE:
            fail(failures, "scenario_activation_rules_v1_0.json", "bad_rule_confidence", row_id)
        if not row.get("reason_template"):
            fail(failures, "scenario_activation_rules_v1_0.json", "missing_reason_template", row_id)
        layer = row.get("industry_scene_layer") or {}
        for key in ["yes", "unknown", "no"]:
            if key not in layer:
                fail(failures, "scenario_activation_rules_v1_0.json", f"missing_industry_scene_layer_{key}", row_id)
        check_dimensions(failures, "scenario_activation_rules_v1_0.json", row_id, row, whitelist)

    matrix_rows = rules.get("permit_control_matrix") or []
    matrix_items = {row.get("item_id") for row in matrix_rows}
    if matrix_items != REQUIRED_PERMIT_ITEMS:
        fail(
            failures,
            "scenario_activation_rules_v1_0.json",
            "permit_matrix_set_mismatch",
            f"missing={sorted(REQUIRED_PERMIT_ITEMS - matrix_items)} extra={sorted(matrix_items - REQUIRED_PERMIT_ITEMS)}",
        )
    for row in matrix_rows:
        row_id = row.get("item_id", "")
        if row.get("confidence") != CONFIDENCE:
            fail(failures, "scenario_activation_rules_v1_0.json", "bad_permit_matrix_confidence", row_id)
        permit_values = row.get("permit_values") or {}
        if set(permit_values) != {"KEY", "SIMPLIFIED", "REGISTRATION"}:
            fail(failures, "scenario_activation_rules_v1_0.json", "permit_values_missing_three_types", row_id)
        for permit_type, value in permit_values.items():
            if value not in {"YES", "UNKNOWN", "NO"}:
                fail(failures, "scenario_activation_rules_v1_0.json", "invalid_permit_value", f"{row_id}:{permit_type}:{value}")
        check_dimensions(failures, "scenario_activation_rules_v1_0.json", row_id, row, whitelist)

    overrides = rules.get("medical_overrides") or []
    override_ids = {row.get("override_id") for row in overrides}
    if override_ids != REQUIRED_MEDICAL_OVERRIDES:
        fail(
            failures,
            "scenario_activation_rules_v1_0.json",
            "medical_override_set_mismatch",
            f"missing={sorted(REQUIRED_MEDICAL_OVERRIDES - override_ids)} extra={sorted(override_ids - REQUIRED_MEDICAL_OVERRIDES)}",
        )
    for row in overrides:
        row_id = row.get("override_id", "")
        if row.get("confidence") != CONFIDENCE:
            fail(failures, "scenario_activation_rules_v1_0.json", "bad_medical_override_confidence", row_id)
        condition = row.get("condition") or {}
        if "84" not in (condition.get("gb_code_prefixes") or []):
            fail(failures, "scenario_activation_rules_v1_0.json", "medical_override_missing_84xx", row_id)
        for value in (row.get("set_values") or {}).values():
            if value != "YES":
                fail(failures, "scenario_activation_rules_v1_0.json", "medical_override_must_set_yes", row_id)
        check_dimensions(failures, "scenario_activation_rules_v1_0.json", row_id, row, whitelist)

    composition = rules.get("composition_logic") or {}
    order = ((composition.get("l2_selection") or {}).get("checking_strength_order") or [])
    if order != ["YES", "UNKNOWN", "NO"]:
        fail(failures, "scenario_activation_rules_v1_0.json", "bad_composition_order", ";".join(order))

    outputs = manifest.get("outputs") or {}
    if outputs.get("scenario_activation_rules") != len(rule_rows):
        fail(failures, "scenario_activation_rules_manifest_v1_0.json", "bad_rule_count")
    if outputs.get("permit_control_matrix_items") != len(matrix_rows):
        fail(failures, "scenario_activation_rules_manifest_v1_0.json", "bad_matrix_count")
    if outputs.get("medical_overrides") != len(overrides):
        fail(failures, "scenario_activation_rules_manifest_v1_0.json", "bad_override_count")

    report = {
        "validation_status": "PASS" if not failures else "FAIL",
        "failure_count": len(failures),
        "final_state": FINAL_STATE,
        "runtime_status": RUNTIME_STATUS,
        "runtime_integration": RUNTIME_INTEGRATION,
        "approval_status": APPROVAL_STATUS,
        "confidence": CONFIDENCE,
        "counts": {
            "scenario_activation_rules": len(rule_rows),
            "permit_control_matrix_items": len(matrix_rows),
            "medical_overrides": len(overrides),
            "applicability_dimension_whitelist": len(whitelist),
        },
        "failure_samples": failures[:50],
    }
    artifact_path("scenario_activation_rules_v1_0_gate_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
