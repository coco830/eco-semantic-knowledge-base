import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
APPROVAL_ID = "CANDY-APPROVAL-STANDARD-LIMIT-RUNTIME-IMPORT-2026-06-03"
FINAL_STATE = "APPROVED_STANDARD_LIMIT_PROFILE_RUNTIME_IMPORT_CONTRACT"
RUNTIME_STATUS = "APPROVED_FOR_IMPORT_PENDING_TESTS"
RUNTIME_INTEGRATION = "approved_standard_limit_profile_import_contract"
IMPORT_ACTION = "APPROVED_FOR_RUNTIME_IMPORT_CONTRACT"
CONTRACT_VERSION = "v8.7-standard-limit-runtime-import-contract"

ADAPTER_CSV = ROOT / "data" / "review" / "pollutant_standard_limit_profile_adapter_v8_7.csv"
OUT_CSV = ROOT / "data" / "runtime" / "pollutant_standard_limit_runtime_import_v8_7.csv"
OUT_JSON = ROOT / "data" / "runtime" / "pollutant_standard_limit_runtime_import_v8_7.json"
OUT_CONTRACT = ROOT / "data" / "runtime" / "pollutant_standard_limit_runtime_data_contract_v8_7.json"
OUT_CONTRACT_MD = ROOT / "docs" / "runtime" / "pollutant_standard_limit_runtime_data_contract_v8_7.md"
OUT_MANIFEST = ROOT / "manifests" / "pollutant_standard_limit_runtime_import_manifest_v8_7.json"
OUT_REPORT = ROOT / "reports" / "pollutant_standard_limit_runtime_import_v8_7.json"

EXPECTED_STANDARDS = {"GB 13457-2025", "GB 15848-2009", "HJ 5.2-2026"}
FORBIDDEN = {
    "create_confirmed_dataset",
    "run_formal_calculation",
    "formal_permit_right_quantity",
    "auto_select_coefficient",
    "mutate_coefficient_selector",
    "radiation_all_industry_default",
    "formal_permit_type",
    "formal_inspection_template",
    "auto_deduct",
    "auto_deduct_score",
    "formal_compliance_conclusion",
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


def main():
    failures = []
    for path in [ADAPTER_CSV, OUT_CSV, OUT_JSON, OUT_CONTRACT, OUT_CONTRACT_MD, OUT_MANIFEST, OUT_REPORT]:
        if not path.exists():
            fail(failures, path.name, "missing_required_output")
    if failures:
        print(json.dumps({"validation_status": "FAIL", "failure_samples": failures}, ensure_ascii=False, indent=2))
        raise SystemExit(1)

    adapter_rows = read_csv(ADAPTER_CSV)
    rows = read_csv(OUT_CSV)
    rows_json = read_json(OUT_JSON)
    contract = read_json(OUT_CONTRACT)
    manifest = read_json(OUT_MANIFEST)
    report = read_json(OUT_REPORT)

    if len(rows) != 74:
        fail(failures, OUT_CSV.name, "runtime_import_row_count_not_74", str(len(rows)))
    if len(rows) != len(adapter_rows):
        fail(failures, OUT_CSV.name, "adapter_runtime_row_count_mismatch")
    if len(rows_json) != len(rows):
        fail(failures, OUT_JSON.name, "json_csv_row_count_mismatch")
    if {row["replacement_standard_no"] for row in rows} != EXPECTED_STANDARDS:
        fail(failures, OUT_CSV.name, "standard_set_mismatch")

    source_ids = {row["profile_id"] for row in adapter_rows}
    runtime_ids = [row["runtime_import_id"] for row in rows]
    if len(set(runtime_ids)) != len(runtime_ids):
        fail(failures, OUT_CSV.name, "duplicate_runtime_import_id")

    for row in rows:
        row_id = row.get("runtime_import_id", "")
        if row.get("source_profile_id") not in source_ids:
            fail(failures, OUT_CSV.name, "source_profile_id_not_found", row_id)
        if row.get("approval_id") != APPROVAL_ID:
            fail(failures, OUT_CSV.name, "bad_approval_id", row_id)
        if row.get("final_state") != FINAL_STATE:
            fail(failures, OUT_CSV.name, "bad_final_state", row_id)
        if row.get("runtime_status") != RUNTIME_STATUS:
            fail(failures, OUT_CSV.name, "bad_runtime_status", row_id)
        if row.get("runtime_integration") != RUNTIME_INTEGRATION:
            fail(failures, OUT_CSV.name, "bad_runtime_integration", row_id)
        if row.get("import_action") != IMPORT_ACTION:
            fail(failures, OUT_CSV.name, "bad_import_action", row_id)
        if row.get("runtime_effect") != "STANDARD_LIMIT_LOOKUP_ONLY":
            fail(failures, OUT_CSV.name, "bad_runtime_effect", row_id)
        if row.get("contract_version") != CONTRACT_VERSION:
            fail(failures, OUT_CSV.name, "bad_contract_version", row_id)
        if not row.get("rollback_manifest_id"):
            fail(failures, OUT_CSV.name, "missing_rollback_manifest_id", row_id)
        if not row.get("raw_fragment") or not row.get("source_page"):
            fail(failures, OUT_CSV.name, "missing_source_evidence_fields", row_id)
        row_forbidden = set((row.get("forbidden_runtime_actions") or "").split(";"))
        if not FORBIDDEN.issubset(row_forbidden):
            fail(failures, OUT_CSV.name, "missing_forbidden_runtime_actions", row_id)

    for file, doc in [(OUT_CONTRACT.name, contract), (OUT_MANIFEST.name, manifest), (OUT_REPORT.name, report)]:
        if doc.get("approval_id") != APPROVAL_ID:
            fail(failures, file, "bad_approval_id")
        if doc.get("final_state") != FINAL_STATE:
            fail(failures, file, "bad_final_state")
        if doc.get("runtime_status") != RUNTIME_STATUS:
            fail(failures, file, "bad_runtime_status")
        if doc.get("runtime_integration") != RUNTIME_INTEGRATION:
            fail(failures, file, "bad_runtime_integration")
        if doc.get("import_action") != IMPORT_ACTION:
            fail(failures, file, "bad_import_action")

    if contract.get("row_count") != 74 or manifest.get("import_row_count") != 74:
        fail(failures, OUT_CONTRACT.name, "contract_or_manifest_row_count_not_74")
    hard_rules = "\n".join(contract.get("hard_rules", []))
    for phrase in [
        "must not create ConfirmedDataset",
        "must not run formal emission-right calculation",
        "must not auto-select or mutate coefficient selection",
        "must not enable all-industry radiation defaults",
        "must not generate formal permit_type",
        "must not generate formal inspection templates",
        "must not generate automatic deduct values",
    ]:
        if phrase not in hard_rules:
            fail(failures, OUT_CONTRACT.name, "missing_hard_rule", phrase)

    md = OUT_CONTRACT_MD.read_text(encoding="utf-8")
    for phrase in [APPROVAL_ID, FINAL_STATE, RUNTIME_STATUS, IMPORT_ACTION, "standard-limit lookup only", "Hard rules"]:
        if phrase not in md:
            fail(failures, OUT_CONTRACT_MD.name, "missing_contract_md_phrase", phrase)

    outputs = report.get("outputs", {})
    expected_hashes = {
        "runtime_import_csv": sha256_file(OUT_CSV),
        "runtime_import_json": sha256_file(OUT_JSON),
        "runtime_contract_json": sha256_file(OUT_CONTRACT),
        "runtime_manifest_json": sha256_file(OUT_MANIFEST),
    }
    for key, digest in expected_hashes.items():
        if outputs.get(key, {}).get("sha256") != digest:
            fail(failures, OUT_REPORT.name, f"{key}_sha256_mismatch")

    validation = {
        "validation_status": "PASS" if not failures else "FAIL",
        "failure_count": len(failures),
        "row_count": len(rows),
        "approval_id": APPROVAL_ID,
        "final_state": FINAL_STATE,
        "runtime_status": RUNTIME_STATUS,
        "runtime_integration": RUNTIME_INTEGRATION,
        "import_action": IMPORT_ACTION,
        "failure_samples": failures[:50],
    }
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
