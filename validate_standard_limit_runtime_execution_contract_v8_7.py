import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
APPROVAL_ID = "CANDY-APPROVAL-STANDARD-LIMIT-RUNTIME-IMPORT-2026-06-03"
FINAL_STATE = "APPROVED_STANDARD_LIMIT_RUNTIME_EXECUTION_CONTRACT_TESTED"
RUNTIME_STATUS = "DOWNSTREAM_IMPORT_CONTRACT_TEST_EXECUTION_PASS"
RUNTIME_INTEGRATION = "approved_standard_limit_profile_import_contract"
EXECUTION_ACTION = "DOWNSTREAM_RUNTIME_IMPORT_CONTRACT_TEST_EXECUTED"
EXECUTION_MODE = "DRY_RUN_MATERIALIZATION_ONLY"
CONTRACT_VERSION = "v8.7-standard-limit-runtime-execution-contract"
RUNTIME_EFFECT = "STANDARD_LIMIT_LOOKUP_ONLY"

SOURCE_CSV = ROOT / "data" / "runtime" / "pollutant_standard_limit_runtime_import_v8_7.csv"
OUT_SNAPSHOT = ROOT / "data" / "runtime" / "pollutant_standard_limit_runtime_lookup_snapshot_v8_7.json"
OUT_CONTRACT = ROOT / "data" / "runtime" / "pollutant_standard_limit_runtime_execution_contract_v8_7.json"
OUT_TEST_CASES = ROOT / "data" / "runtime" / "pollutant_standard_limit_runtime_execution_test_cases_v8_7.json"
OUT_MANIFEST = ROOT / "manifests" / "pollutant_standard_limit_runtime_execution_manifest_v8_7.json"
OUT_REPORT = ROOT / "reports" / "pollutant_standard_limit_runtime_execution_contract_v8_7.json"
OUT_DOC = ROOT / "docs" / "runtime" / "pollutant_standard_limit_runtime_execution_contract_v8_7.md"

EXPECTED_STANDARDS = {"GB 13457-2025", "GB 15848-2009", "HJ 5.2-2026"}
EXPECTED_SCOPES = {
    "standard_limit_lookup.eia_report_field_requirement",
    "standard_limit_lookup.radiation_numeric_constraint",
    "standard_limit_lookup.water_pollutant_concentration",
    "standard_limit_lookup.water_use_benchmark",
}


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path):
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def fail(failures, file, reason, row_id=""):
    failures.append({"file": file, "reason": reason, "row_id": row_id})


def check_doc_fields(failures):
    text = OUT_DOC.read_text(encoding="utf-8")
    for phrase in [APPROVAL_ID, FINAL_STATE, RUNTIME_STATUS, EXECUTION_ACTION, EXECUTION_MODE, "lookup-only dry-run snapshot"]:
        if phrase not in text:
            fail(failures, OUT_DOC.name, "missing_execution_doc_phrase", phrase)


def main():
    failures = []
    required_paths = [SOURCE_CSV, OUT_SNAPSHOT, OUT_CONTRACT, OUT_TEST_CASES, OUT_MANIFEST, OUT_REPORT, OUT_DOC]
    for path in required_paths:
        if not path.exists():
            fail(failures, path.name, "missing_required_output")
    if failures:
        print(json.dumps({"validation_status": "FAIL", "failure_samples": failures}, ensure_ascii=False, indent=2))
        raise SystemExit(1)

    source_rows = read_csv(SOURCE_CSV)
    snapshot = read_json(OUT_SNAPSHOT)
    contract = read_json(OUT_CONTRACT)
    test_cases = read_json(OUT_TEST_CASES)
    manifest = read_json(OUT_MANIFEST)
    report = read_json(OUT_REPORT)
    entries = snapshot.get("entries", [])

    if len(source_rows) != 74:
        fail(failures, SOURCE_CSV.name, "source_runtime_import_row_count_not_74", str(len(source_rows)))
    if len(entries) != len(source_rows):
        fail(failures, OUT_SNAPSHOT.name, "lookup_snapshot_row_count_mismatch", str(len(entries)))
    if len({entry.get("lookup_id") for entry in entries}) != len(entries):
        fail(failures, OUT_SNAPSHOT.name, "duplicate_lookup_id")
    if {entry.get("standard_no") for entry in entries} != EXPECTED_STANDARDS:
        fail(failures, OUT_SNAPSHOT.name, "standard_set_mismatch")
    if {entry.get("runtime_scope") for entry in entries} != EXPECTED_SCOPES:
        fail(failures, OUT_SNAPSHOT.name, "runtime_scope_set_mismatch")

    for entry in entries:
        row_id = entry.get("lookup_id", "")
        if entry.get("runtime_effect") != RUNTIME_EFFECT:
            fail(failures, OUT_SNAPSHOT.name, "bad_runtime_effect", row_id)
        if entry.get("execution_mode") != EXECUTION_MODE:
            fail(failures, OUT_SNAPSHOT.name, "bad_execution_mode", row_id)
        for field in ["source_profile_id", "approval_id", "raw_fragment", "source_page", "rollback_manifest_id"]:
            if not entry.get(field):
                fail(failures, OUT_SNAPSHOT.name, f"missing_{field}", row_id)
        for flag in [
            "confirmed_dataset_creation_enabled",
            "formal_calculation_enabled",
            "coefficient_auto_selection_enabled",
            "coefficient_selector_mutation_enabled",
            "radiation_all_industry_default_enabled",
            "permit_type_generation_enabled",
            "inspection_template_generation_enabled",
            "auto_deduct_enabled",
            "formal_compliance_conclusion_enabled",
        ]:
            if entry.get(flag) is not False:
                fail(failures, OUT_SNAPSHOT.name, f"forbidden_flag_enabled_{flag}", row_id)
        forbidden = set((entry.get("forbidden_runtime_actions") or "").split(";"))
        for action in [
            "create_confirmed_dataset",
            "run_formal_calculation",
            "auto_select_coefficient",
            "radiation_all_industry_default",
        ]:
            if action not in forbidden:
                fail(failures, OUT_SNAPSHOT.name, "missing_guardrail_forbidden_action", f"{row_id}:{action}")

    for file, doc in [(OUT_SNAPSHOT.name, snapshot), (OUT_CONTRACT.name, contract), (OUT_MANIFEST.name, manifest), (OUT_REPORT.name, report)]:
        if doc.get("approval_id") != APPROVAL_ID:
            fail(failures, file, "bad_approval_id")
        if doc.get("final_state") != FINAL_STATE:
            fail(failures, file, "bad_final_state")
        if doc.get("runtime_status") != RUNTIME_STATUS:
            fail(failures, file, "bad_runtime_status")
        if doc.get("runtime_integration") != RUNTIME_INTEGRATION:
            fail(failures, file, "bad_runtime_integration")
        if doc.get("runtime_effect") != RUNTIME_EFFECT:
            fail(failures, file, "bad_runtime_effect")

    if contract.get("contract_version") != CONTRACT_VERSION:
        fail(failures, OUT_CONTRACT.name, "bad_contract_version")
    contract_forbidden = set(contract.get("forbidden_runtime_actions", []))
    for action in ["create_confirmed_dataset", "run_formal_calculation", "auto_select_coefficient", "radiation_all_industry_default"]:
        if action not in contract_forbidden:
            fail(failures, OUT_CONTRACT.name, "missing_guardrail_forbidden_action", action)
    if manifest.get("execution_action") != EXECUTION_ACTION or report.get("execution_action") != EXECUTION_ACTION:
        fail(failures, OUT_MANIFEST.name, "bad_execution_action")
    if contract.get("test_status") != "PASS" or manifest.get("test_status") != "PASS" or report.get("test_status") != "PASS":
        fail(failures, OUT_REPORT.name, "test_status_not_pass")
    if len(test_cases) != 10:
        fail(failures, OUT_TEST_CASES.name, "test_case_count_not_10", str(len(test_cases)))
    for case in test_cases:
        if case.get("status") != "PASS":
            fail(failures, OUT_TEST_CASES.name, "test_case_not_pass", case.get("test_case_id", ""))

    outputs = report.get("outputs", {})
    expected_hashes = {
        "lookup_snapshot_json": sha256_file(OUT_SNAPSHOT),
        "execution_contract_json": sha256_file(OUT_CONTRACT),
        "execution_test_cases_json": sha256_file(OUT_TEST_CASES),
        "execution_manifest_json": sha256_file(OUT_MANIFEST),
    }
    for key, digest in expected_hashes.items():
        if outputs.get(key, {}).get("sha256") != digest:
            fail(failures, OUT_REPORT.name, f"{key}_sha256_mismatch")

    check_doc_fields(failures)

    validation = {
        "validation_status": "PASS" if not failures else "FAIL",
        "failure_count": len(failures),
        "source_row_count": len(source_rows),
        "lookup_entry_count": len(entries),
        "test_case_count": len(test_cases),
        "approval_id": APPROVAL_ID,
        "final_state": FINAL_STATE,
        "runtime_status": RUNTIME_STATUS,
        "runtime_integration": RUNTIME_INTEGRATION,
        "execution_action": EXECUTION_ACTION,
        "execution_mode": EXECUTION_MODE,
        "failure_samples": failures[:50],
    }
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
