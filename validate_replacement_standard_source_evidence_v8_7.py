import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FINAL_STATE = "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"
RUNTIME_STATUS = "DRAFT_NOT_FOR_RUNTIME"
RUNTIME_INTEGRATION = "disabled"
HUMAN_REVIEW_STATUS = "APPROVED_BY_CANDY_FOR_STANDARD_LIMIT_PROFILE_ADAPTER"
EXPECTED_STANDARDS = {"GB 13457-2025", "HJ 5.2-2026", "GB 15848-2009"}

EVIDENCE_CSV = ROOT / "data" / "review" / "pollutant_standard_replacement_source_evidence_v8_7.csv"
EVIDENCE_JSON = ROOT / "data" / "review" / "pollutant_standard_replacement_source_evidence_v8_7.json"
REPORT_JSON = ROOT / "reports" / "pollutant_standard_replacement_source_evidence_v8_7.json"


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
    for path in [EVIDENCE_CSV, EVIDENCE_JSON, REPORT_JSON]:
        if not path.exists():
            fail(failures, path.name, "missing_required_output")

    rows = read_csv(EVIDENCE_CSV)
    rows_json = read_json(EVIDENCE_JSON)
    report = read_json(REPORT_JSON)

    if len(rows) != 3:
        fail(failures, EVIDENCE_CSV.name, "row_count_mismatch", str(len(rows)))
    if len(rows_json) != len(rows):
        fail(failures, EVIDENCE_JSON.name, "json_csv_row_count_mismatch")
    if {row["replacement_standard_no"] for row in rows} != EXPECTED_STANDARDS:
        fail(failures, EVIDENCE_CSV.name, "replacement_standard_set_mismatch")

    for row in rows:
        row_id = row["replacement_standard_no"]
        if row.get("final_state") != FINAL_STATE or row.get("runtime_status") != RUNTIME_STATUS or row.get("runtime_integration") != RUNTIME_INTEGRATION:
            fail(failures, EVIDENCE_CSV.name, "bad_candidate_boundary", row_id)
        if row.get("candidate_only") != "TRUE":
            fail(failures, EVIDENCE_CSV.name, "candidate_only_not_true", row_id)
        snapshot = ROOT / row["local_snapshot_path"]
        if not snapshot.exists():
            fail(failures, EVIDENCE_CSV.name, "missing_local_snapshot", row_id)
            continue
        if row["local_snapshot_sha256"] != sha256_file(snapshot):
            fail(failures, EVIDENCE_CSV.name, "snapshot_sha256_mismatch", row_id)
        if int(row.get("page_count") or 0) <= 0:
            fail(failures, EVIDENCE_CSV.name, "bad_page_count", row_id)
        if int(row.get("extracted_text_chars") or 0) < 1000:
            fail(failures, EVIDENCE_CSV.name, "text_extraction_too_small", row_id)
        if row.get("ocr_status") != "NATIVE_TEXT_EXTRACTED_NO_OCR_REQUIRED":
            fail(failures, EVIDENCE_CSV.name, "unexpected_ocr_status", row_id)
        if row.get("table_evidence_status") != "TEXT_TABLE_CANDIDATES_IDENTIFIED_NOT_NUMERIC_ADOPTED":
            fail(failures, EVIDENCE_CSV.name, "table_evidence_not_identified", row_id)
        if not row.get("table_candidate_pages"):
            fail(failures, EVIDENCE_CSV.name, "missing_table_candidate_pages", row_id)
        if row.get("extraction_rule_reuse_status") != "REUSE_EXISTING_THRESHOLD_FIELD_GOVERNANCE_NEEDS_STANDARD_LIMIT_PROFILE_ADAPTER":
            fail(failures, EVIDENCE_CSV.name, "bad_extraction_rule_reuse_status", row_id)
        reusable_fieldset = row.get("reusable_limit_fieldset", "")
        for required_field in ["metric", "operator", "value", "unit", "raw_fragment", "source_page", "governance_status"]:
            if required_field not in reusable_fieldset.split(";"):
                fail(failures, EVIDENCE_CSV.name, f"missing_reusable_field:{required_field}", row_id)
        if row.get("human_review_status") != HUMAN_REVIEW_STATUS:
            fail(failures, EVIDENCE_CSV.name, "missing_human_review_adapter_approval", row_id)
        if row.get("standard_limit_profile_adapter_status") != "APPLIED_AND_RUNTIME_IMPORT_CONTRACT_APPROVED_IN_pollutant_standard_limit_runtime_import_v8_7":
            fail(failures, EVIDENCE_CSV.name, "standard_limit_profile_adapter_not_applied", row_id)
        if row.get("runtime_promotion_readiness") != "APPROVED_FOR_IMPORT_PENDING_TESTS":
            fail(failures, EVIDENCE_CSV.name, "not_ready_for_runtime_import_task", row_id)

    outputs = report.get("outputs", {})
    if outputs.get("evidence_csv", {}).get("sha256") != sha256_file(EVIDENCE_CSV):
        fail(failures, REPORT_JSON.name, "evidence_csv_sha256_mismatch")
    if outputs.get("evidence_json", {}).get("sha256") != sha256_file(EVIDENCE_JSON):
        fail(failures, REPORT_JSON.name, "evidence_json_sha256_mismatch")

    validation = {
        "validation_status": "PASS" if not failures else "FAIL",
        "failure_count": len(failures),
        "final_state": FINAL_STATE,
        "runtime_status": RUNTIME_STATUS,
        "runtime_integration": RUNTIME_INTEGRATION,
        "counts": {
            "replacement_standard_count": len(rows),
            "approved_for_import_pending_tests_count": sum(1 for row in rows if row.get("runtime_promotion_readiness") == "APPROVED_FOR_IMPORT_PENDING_TESTS"),
        },
        "failure_samples": failures[:50],
    }
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
