import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FINAL_STATE = "APPROVED_STANDARD_LIMIT_PROFILE_ADAPTER"
RUNTIME_STATUS = "APPROVED_FOR_IMPORT_PENDING_TESTS"
RUNTIME_INTEGRATION = "approved_standard_limit_profile_import_contract"
HUMAN_REVIEW_STATUS = "APPROVED_BY_CANDY_FOR_STANDARD_LIMIT_PROFILE_ADAPTER"

OUT_CSV = ROOT / "data" / "review" / "pollutant_standard_limit_profile_adapter_v8_7.csv"
OUT_JSON = ROOT / "data" / "review" / "pollutant_standard_limit_profile_adapter_v8_7.json"
OUT_REPORT = ROOT / "reports" / "pollutant_standard_limit_profile_adapter_v8_7.json"
EXPECTED_STANDARDS = {"GB 13457-2025", "GB 15848-2009", "HJ 5.2-2026"}
REQUIRED_FIELDSET = {"metric", "operator", "value", "unit", "raw_fragment", "source_page", "governance_status"}


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
    for path in [OUT_CSV, OUT_JSON, OUT_REPORT]:
        if not path.exists():
            fail(failures, path.name, "missing_required_output")
    if failures:
        print(json.dumps({"validation_status": "FAIL", "failure_samples": failures}, ensure_ascii=False, indent=2))
        raise SystemExit(1)

    rows = read_csv(OUT_CSV)
    rows_json = read_json(OUT_JSON)
    report = read_json(OUT_REPORT)

    if len(rows) != len(rows_json):
        fail(failures, OUT_JSON.name, "json_csv_row_count_mismatch")
    if len(rows) < 35:
        fail(failures, OUT_CSV.name, "too_few_adapter_rows", str(len(rows)))
    if {row["replacement_standard_no"] for row in rows} != EXPECTED_STANDARDS:
        fail(failures, OUT_CSV.name, "standard_set_mismatch")

    profile_ids = [row["profile_id"] for row in rows]
    if len(set(profile_ids)) != len(profile_ids):
        fail(failures, OUT_CSV.name, "duplicate_profile_id")

    for row in rows:
        row_id = row.get("profile_id", "")
        if row.get("final_state") != FINAL_STATE or row.get("runtime_status") != RUNTIME_STATUS or row.get("runtime_integration") != RUNTIME_INTEGRATION:
            fail(failures, OUT_CSV.name, "bad_candidate_boundary", row_id)
        if row.get("candidate_only") != "TRUE":
            fail(failures, OUT_CSV.name, "candidate_only_not_true", row_id)
        if row.get("human_review_status") != HUMAN_REVIEW_STATUS:
            fail(failures, OUT_CSV.name, "missing_human_review_approval", row_id)
        if row.get("governance_status") != "STANDARD_LIMIT_PROFILE_ADAPTER_APPROVED_FOR_RUNTIME_IMPORT_CONTRACT":
            fail(failures, OUT_CSV.name, "bad_governance_status", row_id)
        if not row.get("adapter_mapping_basis"):
            fail(failures, OUT_CSV.name, "missing_adapter_mapping_basis", row_id)
        for required in REQUIRED_FIELDSET:
            if required not in row:
                fail(failures, OUT_CSV.name, f"missing_required_column:{required}", row_id)
        if not row.get("raw_fragment"):
            fail(failures, OUT_CSV.name, "missing_raw_fragment", row_id)
        if not row.get("source_page"):
            fail(failures, OUT_CSV.name, "missing_source_page", row_id)

    gb13457 = [row for row in rows if row["replacement_standard_no"] == "GB 13457-2025"]
    if not any(row["profile_family"] == "EMISSION_STANDARD_LIMIT_TABLE" and row["pollutant_item"].startswith("pH") and row["lower_value"] == "6" and row["upper_value"] == "9" for row in gb13457):
        fail(failures, OUT_CSV.name, "missing_gb13457_ph_direct_range")
    if not any(row["profile_family"] == "WATER_USE_BENCHMARK_TABLE" and row["standard_limit_metric"] == "unit_product_benchmark_drainage" for row in gb13457):
        fail(failures, OUT_CSV.name, "missing_gb13457_benchmark_drainage")

    if not any(row["replacement_standard_no"] == "GB 15848-2009" and row["profile_family"] == "RADIATION_NUMERIC_CONSTRAINT" for row in rows):
        fail(failures, OUT_CSV.name, "missing_gb15848_radiation_constraints")
    if not any(row["replacement_standard_no"] == "HJ 5.2-2026" and row["profile_family"] == "STANDARD_LIMIT_FIELD_REQUIREMENT" for row in rows):
        fail(failures, OUT_CSV.name, "missing_hj52_field_requirements")

    outputs = report.get("outputs", {})
    if outputs.get("adapter_csv", {}).get("sha256") != sha256_file(OUT_CSV):
        fail(failures, OUT_REPORT.name, "adapter_csv_sha256_mismatch")
    if outputs.get("adapter_json", {}).get("sha256") != sha256_file(OUT_JSON):
        fail(failures, OUT_REPORT.name, "adapter_json_sha256_mismatch")

    validation = {
        "validation_status": "PASS" if not failures else "FAIL",
        "failure_count": len(failures),
        "row_count": len(rows),
        "final_state": FINAL_STATE,
        "runtime_status": RUNTIME_STATUS,
        "runtime_integration": RUNTIME_INTEGRATION,
        "human_review_status": HUMAN_REVIEW_STATUS,
        "failure_samples": failures[:50],
    }
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
