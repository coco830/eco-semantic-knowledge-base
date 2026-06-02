import csv
import hashlib
import json
from pathlib import Path

from kb_paths import artifact_path


ROOT = Path(__file__).resolve().parent
VERSION = "v8.5-pollutant-domain-approved-baseline"
FINAL_STATE = "APPROVED_POLLUTANT_DOMAIN_BASELINE_KNOWLEDGE"
RUNTIME_STATUS = "APPROVED_BASELINE"
RUNTIME_INTEGRATION = "approved_baseline_export_ready"
APPROVAL_STATUS = "HUMAN_APPROVED_BASELINE"
EXPECTED_APPROVED_COUNT = 209
EXPECTED_EXCLUDED_COUNT = 6
EXPECTED_P1_EXCLUDED_SOURCE_IDS = {
    "PDS-V8_0-0079",
    "PDS-V8_0-0081",
    "PDS-V8_0-0150",
    "PDS-V8_0-0165",
    "PDS-V8_0-0169",
    "PDS-V8_0-0194",
}
REQUIRED_BLOCKED_ACTIONS = {
    "write_review_field",
    "create_confirmed_dataset",
    "run_formal_calculation",
    "auto_select_coefficient",
    "mutate_coefficient_selector",
    "radiation_all_industry_default",
}
FORBIDDEN_COLUMNS = {"write_allowed", "approved_baseline_write_allowed"}


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path):
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def split_actions(value):
    if isinstance(value, list):
        return {str(item).strip() for item in value if str(item).strip()}
    return {part.strip() for part in (value or "").replace("；", ";").split(";") if part.strip()}


def fail(failures, file, reason, row_id=""):
    failures.append({"file": file, "reason": reason, "row_id": row_id})


def require_lf_only(failures, name, path):
    data = path.read_bytes()
    if b"\r\n" in data:
        fail(failures, name, "crlf_detected")


def require_row_boundary(failures, row):
    row_id = row.get("baseline_entry_id", "")
    if row.get("runtime_status") != RUNTIME_STATUS:
        fail(failures, "pollutant_domain_approved_baseline_v8_5.csv", "bad_runtime_status", row_id)
    if row.get("final_state") != FINAL_STATE:
        fail(failures, "pollutant_domain_approved_baseline_v8_5.csv", "bad_final_state", row_id)
    if row.get("runtime_integration") != RUNTIME_INTEGRATION:
        fail(failures, "pollutant_domain_approved_baseline_v8_5.csv", "bad_runtime_integration", row_id)
    if row.get("approval_status") != APPROVAL_STATUS:
        fail(failures, "pollutant_domain_approved_baseline_v8_5.csv", "bad_approval_status", row_id)
    if row.get("source_runtime_status") != "DRAFT_NOT_FOR_RUNTIME":
        fail(failures, "pollutant_domain_approved_baseline_v8_5.csv", "bad_source_runtime_status", row_id)
    if row.get("source_final_state") != "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY":
        fail(failures, "pollutant_domain_approved_baseline_v8_5.csv", "bad_source_final_state", row_id)
    if row.get("source_runtime_integration") != "disabled":
        fail(failures, "pollutant_domain_approved_baseline_v8_5.csv", "bad_source_runtime_integration", row_id)
    if row.get("confirmed_dataset_status") != "NOT_CREATED":
        fail(failures, "pollutant_domain_approved_baseline_v8_5.csv", "bad_confirmed_dataset_status", row_id)
    if row.get("formal_calculation_status") != "NOT_AUTHORIZED":
        fail(failures, "pollutant_domain_approved_baseline_v8_5.csv", "bad_formal_calculation_status", row_id)
    if row.get("baseline_package_scope") != "DOWNSTREAM_KNOWLEDGE_BASE_STAGING_ONLY":
        fail(failures, "pollutant_domain_approved_baseline_v8_5.csv", "bad_baseline_package_scope", row_id)
    if row.get("downstream_target_repository") != "coco830/eco-semantic-knowledge-base":
        fail(failures, "pollutant_domain_approved_baseline_v8_5.csv", "bad_downstream_target_repository", row_id)
    if not REQUIRED_BLOCKED_ACTIONS.issubset(split_actions(row.get("blocked_actions", ""))):
        fail(failures, "pollutant_domain_approved_baseline_v8_5.csv", "missing_blocked_action", row_id)


def main():
    failures = []
    required = [
        "pollutant_domain_approved_baseline_v8_5.csv",
        "pollutant_domain_approved_baseline_package_v8_5.json",
        "pollutant_domain_approved_baseline_manifest_v8_5.json",
        "FINAL_POLLUTANT_DOMAIN_APPROVED_BASELINE_v8_5.md",
        "build_pollutant_domain_approved_baseline_v8_5.py",
        "validate_pollutant_domain_approved_baseline_v8_5.py",
    ]
    for name in required:
        if not artifact_path(name).exists():
            fail(failures, name, "missing_required_output")

    baseline_path = artifact_path("pollutant_domain_approved_baseline_v8_5.csv")
    package_path = artifact_path("pollutant_domain_approved_baseline_package_v8_5.json")
    manifest_path = artifact_path("pollutant_domain_approved_baseline_manifest_v8_5.json")
    report_path = artifact_path("FINAL_POLLUTANT_DOMAIN_APPROVED_BASELINE_v8_5.md")

    rows = read_csv(baseline_path)
    package = read_json(package_path)
    manifest = read_json(manifest_path)

    for name, path in [
        ("pollutant_domain_approved_baseline_v8_5.csv", baseline_path),
        ("pollutant_domain_approved_baseline_package_v8_5.json", package_path),
        ("pollutant_domain_approved_baseline_manifest_v8_5.json", manifest_path),
        ("FINAL_POLLUTANT_DOMAIN_APPROVED_BASELINE_v8_5.md", report_path),
    ]:
        require_lf_only(failures, name, path)

    if len(rows) != EXPECTED_APPROVED_COUNT:
        fail(failures, "pollutant_domain_approved_baseline_v8_5.csv", "approved_count_mismatch", str(len(rows)))

    fieldnames = set(rows[0].keys()) if rows else set()
    for column in FORBIDDEN_COLUMNS:
        if column in fieldnames:
            fail(failures, "pollutant_domain_approved_baseline_v8_5.csv", "forbidden_column_present", column)

    seen_entries = set()
    seen_sources = set()
    domains = {}
    for row in rows:
        entry_id = row.get("baseline_entry_id", "")
        source_id = row.get("source_id", "")
        if entry_id in seen_entries:
            fail(failures, "pollutant_domain_approved_baseline_v8_5.csv", "duplicate_baseline_entry_id", entry_id)
        seen_entries.add(entry_id)
        if source_id in seen_sources:
            fail(failures, "pollutant_domain_approved_baseline_v8_5.csv", "duplicate_source_id", source_id)
        seen_sources.add(source_id)
        if source_id in EXPECTED_P1_EXCLUDED_SOURCE_IDS:
            fail(failures, "pollutant_domain_approved_baseline_v8_5.csv", "p1_excluded_source_present", source_id)
        domains[row.get("domain", "")] = domains.get(row.get("domain", ""), 0) + 1
        require_row_boundary(failures, row)

    if package.get("knowledge_base_version") != VERSION:
        fail(failures, "pollutant_domain_approved_baseline_package_v8_5.json", "bad_knowledge_base_version")
    if package.get("final_state") != FINAL_STATE:
        fail(failures, "pollutant_domain_approved_baseline_package_v8_5.json", "bad_final_state")
    if package.get("runtime_status") != RUNTIME_STATUS:
        fail(failures, "pollutant_domain_approved_baseline_package_v8_5.json", "bad_runtime_status")
    if package.get("runtime_integration") != RUNTIME_INTEGRATION:
        fail(failures, "pollutant_domain_approved_baseline_package_v8_5.json", "bad_runtime_integration")
    if package.get("approval_status") != APPROVAL_STATUS:
        fail(failures, "pollutant_domain_approved_baseline_package_v8_5.json", "bad_approval_status")

    counts = package.get("counts", {})
    if counts.get("approved_entry_count") != EXPECTED_APPROVED_COUNT:
        fail(failures, "pollutant_domain_approved_baseline_package_v8_5.json", "approved_count_mismatch")
    if counts.get("excluded_entry_count") != EXPECTED_EXCLUDED_COUNT:
        fail(failures, "pollutant_domain_approved_baseline_package_v8_5.json", "excluded_count_mismatch")
    if counts.get("domain_distribution") != domains:
        fail(failures, "pollutant_domain_approved_baseline_package_v8_5.json", "domain_distribution_mismatch")

    boundary = package.get("boundary", {})
    if boundary.get("baseline_package_scope") != "DOWNSTREAM_KNOWLEDGE_BASE_STAGING_ONLY":
        fail(failures, "pollutant_domain_approved_baseline_package_v8_5.json", "bad_baseline_package_scope")
    if boundary.get("downstream_target_repository") != "coco830/eco-semantic-knowledge-base":
        fail(failures, "pollutant_domain_approved_baseline_package_v8_5.json", "bad_downstream_target_repository")
    if boundary.get("confirmed_dataset_status") != "NOT_CREATED":
        fail(failures, "pollutant_domain_approved_baseline_package_v8_5.json", "bad_confirmed_dataset_status")
    if boundary.get("formal_calculation_status") != "NOT_AUTHORIZED":
        fail(failures, "pollutant_domain_approved_baseline_package_v8_5.json", "bad_formal_calculation_status")
    if not REQUIRED_BLOCKED_ACTIONS.issubset(split_actions(boundary.get("blocked_actions", []))):
        fail(failures, "pollutant_domain_approved_baseline_package_v8_5.json", "missing_blocked_action")

    excluded = {
        item.get("source_id")
        for item in package.get("source_package_summary", {}).get("excluded_p1_decisions", [])
    }
    if excluded != EXPECTED_P1_EXCLUDED_SOURCE_IDS:
        fail(failures, "pollutant_domain_approved_baseline_package_v8_5.json", "p1_excluded_ids_mismatch")

    if manifest.get("approved_entry_count") != EXPECTED_APPROVED_COUNT:
        fail(failures, "pollutant_domain_approved_baseline_manifest_v8_5.json", "approved_count_mismatch")
    if manifest.get("excluded_entry_count") != EXPECTED_EXCLUDED_COUNT:
        fail(failures, "pollutant_domain_approved_baseline_manifest_v8_5.json", "excluded_count_mismatch")
    if set(manifest.get("p1_excluded_source_ids", [])) != EXPECTED_P1_EXCLUDED_SOURCE_IDS:
        fail(failures, "pollutant_domain_approved_baseline_manifest_v8_5.json", "p1_excluded_ids_mismatch")
    if manifest.get("baseline_package_scope") != "DOWNSTREAM_KNOWLEDGE_BASE_STAGING_ONLY":
        fail(failures, "pollutant_domain_approved_baseline_manifest_v8_5.json", "bad_baseline_package_scope")
    if manifest.get("downstream_target_repository") != "coco830/eco-semantic-knowledge-base":
        fail(failures, "pollutant_domain_approved_baseline_manifest_v8_5.json", "bad_downstream_target_repository")
    if manifest.get("confirmed_dataset_status") != "NOT_CREATED":
        fail(failures, "pollutant_domain_approved_baseline_manifest_v8_5.json", "bad_confirmed_dataset_status")
    if manifest.get("formal_calculation_status") != "NOT_AUTHORIZED":
        fail(failures, "pollutant_domain_approved_baseline_manifest_v8_5.json", "bad_formal_calculation_status")
    if not REQUIRED_BLOCKED_ACTIONS.issubset(split_actions(manifest.get("blocked_actions", []))):
        fail(failures, "pollutant_domain_approved_baseline_manifest_v8_5.json", "missing_blocked_action")

    outputs = manifest.get("outputs", {})
    expected_hashes = {
        "baseline_csv": sha256_file(baseline_path),
        "package_json": sha256_file(package_path),
        "report_md": sha256_file(report_path),
    }
    for key, expected_hash in expected_hashes.items():
        if outputs.get(key, {}).get("sha256") != expected_hash:
            fail(failures, "pollutant_domain_approved_baseline_manifest_v8_5.json", f"{key}_sha256_mismatch")

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
            "excluded_entry_count": EXPECTED_EXCLUDED_COUNT,
            "domain_distribution": domains,
        },
        "failure_samples": failures[:50],
    }
    artifact_path("pollutant_domain_approved_baseline_gate_report_v8_5.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
