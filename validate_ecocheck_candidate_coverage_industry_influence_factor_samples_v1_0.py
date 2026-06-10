import csv
import hashlib
import json
from collections import Counter

from kb_paths import artifact_path


VERSION = "v1.0-ecocheck-candidate-coverage-industry-influence-factor-samples"
MANIFEST_ID = "ecocheck_candidate_coverage_industry_influence_factor_samples_manifest_v1_0"
FINAL_STATE = "APPROVED_INDUSTRY_RULE_INPUT"
RUNTIME_STATUS = "APPROVED_RULE_INPUT"
RUNTIME_INTEGRATION = "industry_feature_generator"
RUNTIME_EFFECT = "PROFILE_GAP_AND_TEMPLATE_MATCHER_HINTS"
EXPECTED_ROWS = 48
EXPECTED_POSITIVE_ROWS = 40
EXPECTED_NEGATIVE_ROWS = 8

CSV_NAME = "ecocheck_candidate_coverage_industry_influence_factor_samples_v1_0.csv"
DOC_NAME = "ecocheck_candidate_coverage_industry_influence_factor_samples_v1_0.md"
MANIFEST_NAME = "ecocheck_candidate_coverage_industry_influence_factor_samples_manifest_v1_0.json"
GATE_REPORT_NAME = "ecocheck_candidate_coverage_industry_influence_factor_samples_gate_report_v1_0.json"

REQUIRED_FIELDS = {
    "sample_id",
    "sample_set",
    "sample_bucket",
    "industry_code",
    "industry_name",
    "sample_polarity",
    "factor_ids",
    "factor_names",
    "evidence_requirements",
    "photo_points",
    "confirmation_questions",
    "source_basis",
    "candidate_status",
    "gate_status",
    "confidence",
    "blocked_actions",
    "runtime_effect",
    "runtime_status",
    "final_state",
    "runtime_integration",
    "notes",
    "version_manifest_id",
}

VALID_SAMPLE_SETS = {
    "HIGH_FREQUENCY_INDUSTRY",
    "BATCH4_NEW_FACTOR_INDUSTRY",
    "BATCH5_A",
    "BATCH5_B",
    "BATCH5_C",
    "NEGATIVE_SAMPLE",
}
VALID_POLARITIES = {"POSITIVE", "NEGATIVE", "CONDITIONAL", "UNKNOWN"}
VALID_CANDIDATE_STATUS = {
    "CANDIDATE_RECALLED",
    "SITE_VERIFICATION_REQUIRED",
    "NOT_APPLY_WITH_EVIDENCE",
    "RUNTIME_BLOCKED",
}
VALID_GATE_STATUS = {
    "SITE_VERIFICATION_REQUIRED",
    "BLOCKED_BY_NEGATIVE_SAMPLE",
    "MAY_APPLY",
    "NEED_EIA_OR_PERMIT_CONFIRM",
}
REQUIRED_BLOCKED_ACTIONS = {
    "create_confirmed_dataset",
    "formal_permit_type",
    "formal_inspection_template",
    "auto_deduct",
    "auto_deduct_score",
    "formal_compliance_conclusion",
    "direct_ecoCheck_runtime_mutation",
    "mutate_coefficient_selector",
}
NEGATIVE_BLOCKED_ACTIONS = {
    "activate_positive_factor_without_evidence",
    "override_site_fact",
}
FORBIDDEN_RUNTIME_VALUES = {
    "APPROVED_BASELINE",
    "approved_baseline_export_ready",
    "CoefficientSelector",
    "formal_calculation",
    "ConfirmedDataset",
    "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY",
    "CANDIDATE_ONLY",
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


def require_lf_only(failures, name, path):
    if b"\r\n" in path.read_bytes():
        fail(failures, name, "crlf_detected")


def split_semicolon(value):
    return [item.strip() for item in value.split(";") if item.strip()]


def validate_row(failures, row):
    row_id = row.get("sample_id", "")
    for field in REQUIRED_FIELDS:
        if not row.get(field, "").strip():
            fail(failures, CSV_NAME, f"empty_{field}", row_id)

    if row.get("sample_set") not in VALID_SAMPLE_SETS:
        fail(failures, CSV_NAME, "bad_sample_set", row_id)
    if row.get("sample_polarity") not in VALID_POLARITIES:
        fail(failures, CSV_NAME, "bad_sample_polarity", row_id)
    if row.get("candidate_status") not in VALID_CANDIDATE_STATUS:
        fail(failures, CSV_NAME, "bad_candidate_status", row_id)
    if row.get("gate_status") not in VALID_GATE_STATUS:
        fail(failures, CSV_NAME, "bad_gate_status", row_id)
    if row.get("runtime_effect") != RUNTIME_EFFECT:
        fail(failures, CSV_NAME, "bad_runtime_effect", row_id)
    if row.get("runtime_status") != RUNTIME_STATUS:
        fail(failures, CSV_NAME, "bad_runtime_status", row_id)
    if row.get("final_state") != FINAL_STATE:
        fail(failures, CSV_NAME, "bad_final_state", row_id)
    if row.get("runtime_integration") != RUNTIME_INTEGRATION:
        fail(failures, CSV_NAME, "bad_runtime_integration", row_id)
    if row.get("version_manifest_id") != "ECC_CANDIDATE_COVERAGE_IFS_MANIFEST_V1_0":
        fail(failures, CSV_NAME, "bad_version_manifest_id", row_id)

    blocked_actions = set(split_semicolon(row.get("blocked_actions", "")))
    if not REQUIRED_BLOCKED_ACTIONS.issubset(blocked_actions):
        fail(failures, CSV_NAME, "missing_required_blocked_action", row_id)

    factor_ids = split_semicolon(row.get("factor_ids", ""))
    if not factor_ids:
        fail(failures, CSV_NAME, "empty_factor_ids", row_id)
    if any("coefficient" in value.lower() or "系数" in value for value in factor_ids):
        fail(failures, CSV_NAME, "coefficient_factor_id_leak", row_id)

    boundary_text = " ".join([
        row.get("runtime_effect", ""),
        row.get("runtime_status", ""),
        row.get("final_state", ""),
        row.get("runtime_integration", ""),
        row.get("candidate_status", ""),
        row.get("gate_status", ""),
    ])
    for forbidden in FORBIDDEN_RUNTIME_VALUES:
        if forbidden in boundary_text:
            fail(failures, CSV_NAME, "forbidden_runtime_value", row_id)

    if row.get("sample_set") == "NEGATIVE_SAMPLE":
        if row.get("sample_polarity") != "NEGATIVE":
            fail(failures, CSV_NAME, "negative_sample_bad_polarity", row_id)
        if row.get("candidate_status") != "NOT_APPLY_WITH_EVIDENCE":
            fail(failures, CSV_NAME, "negative_sample_bad_candidate_status", row_id)
        if row.get("gate_status") != "BLOCKED_BY_NEGATIVE_SAMPLE":
            fail(failures, CSV_NAME, "negative_sample_bad_gate_status", row_id)
        if not NEGATIVE_BLOCKED_ACTIONS.issubset(blocked_actions):
            fail(failures, CSV_NAME, "negative_sample_missing_blocked_action", row_id)
    else:
        if row.get("sample_polarity") != "POSITIVE":
            fail(failures, CSV_NAME, "positive_sample_bad_polarity", row_id)
        if row.get("gate_status") != "SITE_VERIFICATION_REQUIRED":
            fail(failures, CSV_NAME, "positive_sample_bad_gate_status", row_id)
        if row.get("candidate_status") != "CANDIDATE_RECALLED":
            fail(failures, CSV_NAME, "positive_sample_bad_candidate_status", row_id)


def main():
    failures = []
    required = [
        CSV_NAME,
        DOC_NAME,
        MANIFEST_NAME,
        "validate_ecocheck_candidate_coverage_industry_influence_factor_samples_v1_0.py",
    ]
    for name in required:
        if not artifact_path(name).exists():
            fail(failures, name, "missing_required_output")

    csv_path = artifact_path(CSV_NAME)
    doc_path = artifact_path(DOC_NAME)
    manifest_path = artifact_path(MANIFEST_NAME)
    gate_path = artifact_path(GATE_REPORT_NAME)

    rows = read_csv(csv_path) if csv_path.exists() else []
    manifest = read_json(manifest_path) if manifest_path.exists() else {}

    if csv_path.exists():
        require_lf_only(failures, CSV_NAME, csv_path)
    if doc_path.exists():
        require_lf_only(failures, DOC_NAME, doc_path)
    if manifest_path.exists():
        require_lf_only(failures, MANIFEST_NAME, manifest_path)

    if len(rows) != EXPECTED_ROWS:
        fail(failures, CSV_NAME, "row_count_mismatch", str(len(rows)))

    fieldnames = set(rows[0].keys()) if rows else set()
    for field in REQUIRED_FIELDS:
        if field not in fieldnames:
            fail(failures, CSV_NAME, "missing_required_field", field)

    seen = set()
    counts = Counter()
    for row in rows:
        row_id = row.get("sample_id", "")
        if row_id in seen:
            fail(failures, CSV_NAME, "duplicate_sample_id", row_id)
        seen.add(row_id)
        if not (row_id.startswith("ECC_IFS_") or row_id.startswith("ECC_IFS_NEG_")):
            fail(failures, CSV_NAME, "bad_sample_id_namespace", row_id)
        counts[row.get("sample_set", "")] += 1
        validate_row(failures, row)

    positive_rows = sum(1 for row in rows if row.get("sample_set") != "NEGATIVE_SAMPLE")
    negative_rows = counts.get("NEGATIVE_SAMPLE", 0)
    if positive_rows != EXPECTED_POSITIVE_ROWS:
        fail(failures, CSV_NAME, "positive_row_count_mismatch", str(positive_rows))
    if negative_rows != EXPECTED_NEGATIVE_ROWS:
        fail(failures, CSV_NAME, "negative_row_count_mismatch", str(negative_rows))
    for sample_set in VALID_SAMPLE_SETS:
        if counts.get(sample_set, 0) == 0:
            fail(failures, CSV_NAME, "missing_sample_set", sample_set)

    if manifest:
        if manifest.get("manifest_id") != MANIFEST_ID:
            fail(failures, MANIFEST_NAME, "bad_manifest_id")
        if manifest.get("knowledge_base_version") != VERSION:
            fail(failures, MANIFEST_NAME, "bad_knowledge_base_version")
        if manifest.get("final_state") != FINAL_STATE:
            fail(failures, MANIFEST_NAME, "bad_final_state")
        if manifest.get("runtime_status") != RUNTIME_STATUS:
            fail(failures, MANIFEST_NAME, "bad_runtime_status")
        if manifest.get("runtime_integration") != RUNTIME_INTEGRATION:
            fail(failures, MANIFEST_NAME, "bad_runtime_integration")
        if manifest.get("runtime_effect") != RUNTIME_EFFECT:
            fail(failures, MANIFEST_NAME, "bad_runtime_effect")
        if manifest.get("sample_count") != len(rows):
            fail(failures, MANIFEST_NAME, "sample_count_mismatch")
        outputs = manifest.get("outputs", {})
        if outputs.get("samples_csv", {}).get("sha256") != sha256_file(csv_path):
            fail(failures, MANIFEST_NAME, "samples_csv_sha256_mismatch")
        if outputs.get("design_doc", {}).get("sha256") != sha256_file(doc_path):
            fail(failures, MANIFEST_NAME, "design_doc_sha256_mismatch")
        manifest_blocked = set(manifest.get("blocked_actions", []))
        if not REQUIRED_BLOCKED_ACTIONS.issubset(manifest_blocked):
            fail(failures, MANIFEST_NAME, "manifest_missing_blocked_action")
        runtime_contract = manifest.get("runtime_contract", {})
        for key in [
            "does_not_generate_formal_permit_type",
            "does_not_generate_formal_inspection_template",
            "does_not_auto_deduct_score",
            "does_not_feed_coefficient_selector",
            "can_drive_industry_feature_generator",
            "can_drive_middle_layer_rules_engine",
            "can_drive_profile_gap_generation",
            "can_drive_template_matcher_evidence_overlays",
        ]:
            if runtime_contract.get(key) is not True:
                fail(failures, MANIFEST_NAME, f"runtime_contract_{key}_not_true")
        if runtime_contract.get("does_not_directly_mutate_ecocheck_runtime") is not True:
            fail(failures, MANIFEST_NAME, "runtime_contract_does_not_directly_mutate_ecocheck_runtime_not_true")

    report = {
        "validation_status": "PASS" if not failures else "FAIL",
        "failure_count": len(failures),
        "knowledge_base_version": VERSION,
        "manifest_id": MANIFEST_ID,
        "final_state": FINAL_STATE,
        "runtime_status": RUNTIME_STATUS,
        "runtime_integration": RUNTIME_INTEGRATION,
        "runtime_effect": RUNTIME_EFFECT,
        "counts": {
            "sample_count": len(rows),
            "positive_sample_count": positive_rows if rows else 0,
            "negative_sample_count": negative_rows if rows else 0,
            "sample_sets": dict(sorted(counts.items())),
        },
        "failures": failures,
    }
    gate_path.parent.mkdir(parents=True, exist_ok=True)
    gate_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
