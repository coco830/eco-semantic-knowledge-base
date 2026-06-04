import csv
import hashlib
import json

from kb_paths import artifact_path


VERSION = "v1.0-approved-specialized-inspection-items"
FINAL_STATE = "APPROVED_SPECIALIZED_INSPECTION_ITEMS_BASELINE"
RUNTIME_STATUS = "APPROVED_BASELINE"
RUNTIME_INTEGRATION = "approved_baseline_export_ready"
APPROVAL_STATUS = "HUMAN_APPROVED_BASELINE"
SOURCE_FINAL_STATE = "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"
SOURCE_RUNTIME_INTEGRATION = "disabled"
EXPECTED_COUNT = 49
EXPECTED_PROCESS_PACKAGE_COUNT = 24
EXPECTED_PROCESS_DETAIL_COUNT = 10

REQUIRED_FIELDS = {
    "item_id",
    "industry",
    "scenario",
    "chapter",
    "dimension",
    "title",
    "content",
    "threshold_text",
    "source_basis",
    "photo_points",
    "approval_status",
    "source_hash",
}

VALID_PROCESS_DIMENSIONS = {
    "vocs_emission",
    "wastewater_discharge_route",
    "wastewater_generation",
    "boiler_combustion",
    "wastewater_station",
    "medical_waste",
    "hazardous_waste",
    "rainwater_accident_risk",
    "dust_particulate",
    "noise_source",
    "radiation",
}


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path):
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def basis_hash(source_basis):
    return "sha256:" + hashlib.sha256(source_basis.encode("utf-8")).hexdigest()


def fail(failures, file, reason, row_id=""):
    failures.append({"file": file, "reason": reason, "row_id": row_id})


def require_lf_only(failures, name, path):
    if b"\r\n" in path.read_bytes():
        fail(failures, name, "crlf_detected")


def require_boundary(failures, row):
    row_id = row.get("item_id", "")
    if row.get("runtime_status") != RUNTIME_STATUS:
        fail(failures, "approved_specialized_inspection_items_v1_0.csv", "bad_runtime_status", row_id)
    if row.get("final_state") != FINAL_STATE:
        fail(failures, "approved_specialized_inspection_items_v1_0.csv", "bad_final_state", row_id)
    if row.get("runtime_integration") != RUNTIME_INTEGRATION:
        fail(failures, "approved_specialized_inspection_items_v1_0.csv", "bad_runtime_integration", row_id)
    if row.get("approval_status") != APPROVAL_STATUS:
        fail(failures, "approved_specialized_inspection_items_v1_0.csv", "bad_approval_status", row_id)
    if row.get("source_final_state") != SOURCE_FINAL_STATE:
        fail(failures, "approved_specialized_inspection_items_v1_0.csv", "bad_source_final_state", row_id)
    if row.get("source_runtime_integration") != SOURCE_RUNTIME_INTEGRATION:
        fail(failures, "approved_specialized_inspection_items_v1_0.csv", "bad_source_runtime_integration", row_id)


def main():
    failures = []
    required = [
        "approved_specialized_inspection_items_v1_0.csv",
        "approved_specialized_inspection_items_manifest_v1_0.json",
        "approved_specialized_inspection_items_gate_report_v1_0.json",
        "build_specialized_inspection_items_v1_0.py",
        "validate_specialized_inspection_items_v1_0.py",
    ]
    for name in required:
        if not artifact_path(name).exists():
            fail(failures, name, "missing_required_output")

    csv_path = artifact_path("approved_specialized_inspection_items_v1_0.csv")
    manifest_path = artifact_path("approved_specialized_inspection_items_manifest_v1_0.json")
    gate_path = artifact_path("approved_specialized_inspection_items_gate_report_v1_0.json")
    rows = read_csv(csv_path)
    manifest = read_json(manifest_path)

    require_lf_only(failures, "approved_specialized_inspection_items_v1_0.csv", csv_path)
    require_lf_only(failures, "approved_specialized_inspection_items_manifest_v1_0.json", manifest_path)

    if len(rows) != EXPECTED_COUNT:
        fail(failures, "approved_specialized_inspection_items_v1_0.csv", "approved_count_mismatch", str(len(rows)))

    fieldnames = set(rows[0].keys()) if rows else set()
    for field in REQUIRED_FIELDS:
        if field not in fieldnames:
            fail(failures, "approved_specialized_inspection_items_v1_0.csv", "missing_required_field", field)

    seen = set()
    five_code_count = 0
    process_count = 0
    process_package_count = 0
    process_detail_count = 0
    residual_chlorine_rows = []
    for row in rows:
        row_id = row.get("item_id", "")
        if row_id in seen:
            fail(failures, "approved_specialized_inspection_items_v1_0.csv", "duplicate_item_id", row_id)
        seen.add(row_id)
        if not row_id.startswith("FIRST_"):
            fail(failures, "approved_specialized_inspection_items_v1_0.csv", "bad_item_namespace", row_id)
        if "_SPEC_PROCESS_" in row_id:
            process_count += 1
            is_detail = "ETO supplied specialized detail checklist" in row.get("source_candidate_boundary", "")
            if is_detail:
                process_detail_count += 1
            else:
                process_package_count += 1
            if not row.get("source_process_id", "").strip():
                fail(failures, "approved_specialized_inspection_items_v1_0.csv", "missing_source_process_id", row_id)
            if row.get("dimension") not in VALID_PROCESS_DIMENSIONS:
                fail(failures, "approved_specialized_inspection_items_v1_0.csv", "bad_process_dimension", row_id)
            if row.get("eto_review_decision") not in {"通过", "修改后通过"}:
                fail(failures, "approved_specialized_inspection_items_v1_0.csv", "bad_process_eto_review_decision", row_id)
            if not row.get("eto_review_note", "").strip():
                fail(failures, "approved_specialized_inspection_items_v1_0.csv", "missing_process_eto_review_note", row_id)
            if not is_detail and "存在该工序/设施/风险单元即触发" not in row.get("threshold_text", ""):
                fail(failures, "approved_specialized_inspection_items_v1_0.csv", "bad_process_threshold", row_id)
            if is_detail and "排查节点：" not in row.get("content", ""):
                fail(failures, "approved_specialized_inspection_items_v1_0.csv", "detail_missing_node", row_id)
        require_boundary(failures, row)
        for field in REQUIRED_FIELDS:
            if not row.get(field, "").strip():
                fail(failures, "approved_specialized_inspection_items_v1_0.csv", f"empty_{field}", row_id)
        if row.get("source_hash") != basis_hash(row.get("source_basis", "")):
            fail(failures, "approved_specialized_inspection_items_v1_0.csv", "source_hash_mismatch", row_id)
        if "FIVE_CODE" in row_id:
            five_code_count += 1
            if row.get("chapter") != "S07":
                fail(failures, "approved_specialized_inspection_items_v1_0.csv", "five_code_not_s07", row_id)
            if "危废" not in row.get("industry", "") and "危废" not in row.get("scenario", ""):
                fail(failures, "approved_specialized_inspection_items_v1_0.csv", "five_code_not_hazwaste_scoped", row_id)
            basis = row.get("source_basis", "")
            if "GB 18597-2023" not in basis or "HJ 1276-2022" not in basis:
                fail(failures, "approved_specialized_inspection_items_v1_0.csv", "five_code_missing_gb_hj_basis", row_id)
        if row_id == "FIRST_S06_SPEC_HOSPITAL_RESIDUAL_CHLORINE_3_10":
            residual_chlorine_rows.append(row)

    if five_code_count < 5:
        fail(failures, "approved_specialized_inspection_items_v1_0.csv", "five_code_count_below_minimum", str(five_code_count))
    if process_package_count != EXPECTED_PROCESS_PACKAGE_COUNT:
        fail(failures, "approved_specialized_inspection_items_v1_0.csv", "process_package_count_mismatch", str(process_package_count))
    if process_detail_count != EXPECTED_PROCESS_DETAIL_COUNT:
        fail(failures, "approved_specialized_inspection_items_v1_0.csv", "process_detail_count_mismatch", str(process_detail_count))
    if len(residual_chlorine_rows) != 1:
        fail(failures, "approved_specialized_inspection_items_v1_0.csv", "hospital_residual_chlorine_row_missing")
    else:
        row = residual_chlorine_rows[0]
        if row.get("threshold_text") != "3–10 mg/L":
            fail(failures, "approved_specialized_inspection_items_v1_0.csv", "bad_residual_chlorine_threshold", row.get("threshold_text", ""))
        if "GB 18466-2005" not in row.get("source_basis", ""):
            fail(failures, "approved_specialized_inspection_items_v1_0.csv", "missing_gb18466_basis", row.get("item_id", ""))

    if manifest.get("knowledge_base_version") != VERSION:
        fail(failures, "approved_specialized_inspection_items_manifest_v1_0.json", "bad_knowledge_base_version")
    if manifest.get("final_state") != FINAL_STATE:
        fail(failures, "approved_specialized_inspection_items_manifest_v1_0.json", "bad_final_state")
    if manifest.get("runtime_status") != RUNTIME_STATUS:
        fail(failures, "approved_specialized_inspection_items_manifest_v1_0.json", "bad_runtime_status")
    if manifest.get("runtime_integration") != RUNTIME_INTEGRATION:
        fail(failures, "approved_specialized_inspection_items_manifest_v1_0.json", "bad_runtime_integration")
    if manifest.get("approval_status") != APPROVAL_STATUS:
        fail(failures, "approved_specialized_inspection_items_manifest_v1_0.json", "bad_approval_status")
    if manifest.get("approved_entry_count") != len(rows):
        fail(failures, "approved_specialized_inspection_items_manifest_v1_0.json", "approved_count_mismatch")
    source_boundary = manifest.get("source_candidate_boundary", {})
    if source_boundary.get("source_final_state") != SOURCE_FINAL_STATE:
        fail(failures, "approved_specialized_inspection_items_manifest_v1_0.json", "bad_source_final_state")
    if source_boundary.get("source_runtime_integration") != SOURCE_RUNTIME_INTEGRATION:
        fail(failures, "approved_specialized_inspection_items_manifest_v1_0.json", "bad_source_runtime_integration")
    if manifest.get("outputs", {}).get("baseline_csv", {}).get("sha256") != sha256_file(csv_path):
        fail(failures, "approved_specialized_inspection_items_manifest_v1_0.json", "baseline_csv_sha256_mismatch")

    report = {
        "validation_status": "PASS" if not failures else "FAIL",
        "failure_count": len(failures),
        "knowledge_base_version": VERSION,
        "final_state": FINAL_STATE,
        "runtime_status": RUNTIME_STATUS,
        "runtime_integration": RUNTIME_INTEGRATION,
        "approval_status": APPROVAL_STATUS,
        "counts": {
            "approved_entry_count": len(rows),
            "hazwaste_five_code_items": five_code_count,
            "process_items": process_count,
            "process_package_items": process_package_count,
            "process_detail_items": process_detail_count,
            "hospital_residual_chlorine_items": len(residual_chlorine_rows),
        },
        "failure_samples": failures[:50],
    }
    gate_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
