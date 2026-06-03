import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
APPROVAL_ID = "CANDY-APPROVAL-STANDARD-LIMIT-RUNTIME-IMPORT-2026-06-03"
IMPORT_FINAL_STATE = "APPROVED_STANDARD_LIMIT_PROFILE_RUNTIME_IMPORT_CONTRACT"
FINAL_STATE = "APPROVED_STANDARD_LIMIT_RUNTIME_EXECUTION_CONTRACT_TESTED"
RUNTIME_STATUS = "DOWNSTREAM_IMPORT_CONTRACT_TEST_EXECUTION_PASS"
RUNTIME_INTEGRATION = "approved_standard_limit_profile_import_contract"
IMPORT_ACTION = "APPROVED_FOR_RUNTIME_IMPORT_CONTRACT"
EXECUTION_ACTION = "DOWNSTREAM_RUNTIME_IMPORT_CONTRACT_TEST_EXECUTED"
EXECUTION_MODE = "DRY_RUN_MATERIALIZATION_ONLY"
CONTRACT_VERSION = "v8.7-standard-limit-runtime-execution-contract"
SOURCE_CONTRACT_VERSION = "v8.7-standard-limit-runtime-import-contract"
RUNTIME_EFFECT = "STANDARD_LIMIT_LOOKUP_ONLY"

SOURCE_CSV = ROOT / "data" / "runtime" / "pollutant_standard_limit_runtime_import_v8_7.csv"
SOURCE_JSON = ROOT / "data" / "runtime" / "pollutant_standard_limit_runtime_import_v8_7.json"
SOURCE_CONTRACT = ROOT / "data" / "runtime" / "pollutant_standard_limit_runtime_data_contract_v8_7.json"
SOURCE_MANIFEST = ROOT / "manifests" / "pollutant_standard_limit_runtime_import_manifest_v8_7.json"
OUT_SNAPSHOT = ROOT / "data" / "runtime" / "pollutant_standard_limit_runtime_lookup_snapshot_v8_7.json"
OUT_CONTRACT = ROOT / "data" / "runtime" / "pollutant_standard_limit_runtime_execution_contract_v8_7.json"
OUT_TEST_CASES = ROOT / "data" / "runtime" / "pollutant_standard_limit_runtime_execution_test_cases_v8_7.json"
OUT_MANIFEST = ROOT / "manifests" / "pollutant_standard_limit_runtime_execution_manifest_v8_7.json"
OUT_REPORT = ROOT / "reports" / "pollutant_standard_limit_runtime_execution_contract_v8_7.json"
OUT_DOC = ROOT / "docs" / "runtime" / "pollutant_standard_limit_runtime_execution_contract_v8_7.md"
ARTIFACT_MANIFEST = ROOT / "artifact_manifest.json"

FORBIDDEN_RUNTIME_ACTIONS = [
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
]

REQUIRED_SOURCE_FIELDS = [
    "runtime_import_id",
    "source_profile_id",
    "approval_id",
    "replacement_standard_no",
    "replacement_standard_title",
    "profile_family",
    "runtime_scope",
    "runtime_status",
    "runtime_integration",
    "runtime_effect",
    "import_action",
    "rollback_manifest_id",
    "contract_version",
    "final_state",
]


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    tmp.replace(path)


def sha256_file(path):
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def lookup_key(row):
    parts = [
        row["runtime_scope"],
        row["replacement_standard_no"],
        row["medium"],
        row["pollutant_item"],
        row["standard_limit_metric"],
        row["standard_limit_target"],
        row["monitoring_location"],
        row["table_or_clause_ref"],
    ]
    return "|".join((part or "-").strip() for part in parts)


def materialize_lookup_rows(rows):
    entries = []
    for row in rows:
        entries.append({
            "lookup_id": row["runtime_import_id"],
            "lookup_key": lookup_key(row),
            "source_profile_id": row["source_profile_id"],
            "approval_id": row["approval_id"],
            "standard_no": row["replacement_standard_no"],
            "standard_title": row["replacement_standard_title"],
            "profile_family": row["profile_family"],
            "runtime_scope": row["runtime_scope"],
            "medium": row["medium"],
            "pollutant_item": row["pollutant_item"],
            "metric": row["metric"],
            "standard_limit_metric": row["standard_limit_metric"],
            "operator": row["operator"],
            "value": row["value"],
            "unit": row["unit"],
            "lower_value": row["lower_value"],
            "lower_unit": row["lower_unit"],
            "lower_inclusive": row["lower_inclusive"],
            "upper_value": row["upper_value"],
            "upper_unit": row["upper_unit"],
            "upper_inclusive": row["upper_inclusive"],
            "equivalent_value": row["equivalent_value"],
            "equivalent_unit": row["equivalent_unit"],
            "limit_context": row["limit_context"],
            "monitoring_location": row["monitoring_location"],
            "source_page": row["source_page"],
            "source_table_index": row["source_table_index"],
            "source_row_index": row["source_row_index"],
            "raw_fragment": row["raw_fragment"],
            "source_evidence_ref": row["source_evidence_ref"],
            "rollback_manifest_id": row["rollback_manifest_id"],
            "runtime_effect": RUNTIME_EFFECT,
            "execution_mode": EXECUTION_MODE,
            "forbidden_runtime_actions": row["forbidden_runtime_actions"],
            "confirmed_dataset_creation_enabled": False,
            "formal_calculation_enabled": False,
            "coefficient_auto_selection_enabled": False,
            "coefficient_selector_mutation_enabled": False,
            "radiation_all_industry_default_enabled": False,
            "permit_type_generation_enabled": False,
            "inspection_template_generation_enabled": False,
            "auto_deduct_enabled": False,
            "formal_compliance_conclusion_enabled": False,
        })
    return entries


def test_case(case_id, name, status, expected, observed, evidence):
    return {
        "test_case_id": case_id,
        "name": name,
        "status": "PASS" if status else "FAIL",
        "expected": expected,
        "observed": observed,
        "evidence": evidence,
    }


def build_test_cases(rows, entries, source_contract, source_manifest):
    required_fields_ok = all(all(row.get(field) for field in REQUIRED_SOURCE_FIELDS) for row in rows)
    unique_import_ids = len({row["runtime_import_id"] for row in rows}) == len(rows)
    unique_lookup_ids = len({entry["lookup_id"] for entry in entries}) == len(entries)
    source_status_ok = all(row["final_state"] == IMPORT_FINAL_STATE for row in rows)
    source_contract_ok = source_contract.get("contract_version") == SOURCE_CONTRACT_VERSION
    manifest_count_ok = source_manifest.get("import_row_count") == len(rows)
    lookup_only_ok = all(entry["runtime_effect"] == RUNTIME_EFFECT for entry in entries)
    forbidden_blocked_ok = all(
        entry["confirmed_dataset_creation_enabled"] is False
        and entry["formal_calculation_enabled"] is False
        and entry["coefficient_auto_selection_enabled"] is False
        and entry["coefficient_selector_mutation_enabled"] is False
        and entry["radiation_all_industry_default_enabled"] is False
        and entry["permit_type_generation_enabled"] is False
        and entry["inspection_template_generation_enabled"] is False
        and entry["auto_deduct_enabled"] is False
        and entry["formal_compliance_conclusion_enabled"] is False
        for entry in entries
    )
    source_trace_ok = all(entry["source_profile_id"] and entry["raw_fragment"] and entry["source_page"] for entry in entries)
    scope_counts = Counter(entry["runtime_scope"] for entry in entries)
    standard_counts = Counter(entry["standard_no"] for entry in entries)

    return [
        test_case("PSLRT-EXEC-TC-001", "runtime_import_row_count", len(rows) == 74, "74 rows", f"{len(rows)} rows", SOURCE_CSV.name),
        test_case("PSLRT-EXEC-TC-002", "runtime_import_required_fields", required_fields_ok, REQUIRED_SOURCE_FIELDS, "all present" if required_fields_ok else "missing field", SOURCE_CSV.name),
        test_case("PSLRT-EXEC-TC-003", "unique_runtime_and_lookup_ids", unique_import_ids and unique_lookup_ids, "unique ids", f"runtime={unique_import_ids};lookup={unique_lookup_ids}", OUT_SNAPSHOT.name),
        test_case("PSLRT-EXEC-TC-004", "source_import_contract_state", source_status_ok and source_contract_ok and manifest_count_ok, IMPORT_FINAL_STATE, f"rows={source_status_ok};contract={source_contract_ok};manifest={manifest_count_ok}", SOURCE_CONTRACT.name),
        test_case("PSLRT-EXEC-TC-005", "lookup_snapshot_materialization", len(entries) == len(rows), "snapshot row count equals import row count", f"{len(entries)} entries", OUT_SNAPSHOT.name),
        test_case("PSLRT-EXEC-TC-006", "runtime_effect_lookup_only", lookup_only_ok, RUNTIME_EFFECT, sorted(set(entry["runtime_effect"] for entry in entries)), OUT_SNAPSHOT.name),
        test_case("PSLRT-EXEC-TC-007", "forbidden_runtime_actions_remain_blocked", forbidden_blocked_ok, FORBIDDEN_RUNTIME_ACTIONS, "blocked" if forbidden_blocked_ok else "enabled flag found", OUT_SNAPSHOT.name),
        test_case("PSLRT-EXEC-TC-008", "source_traceability_preserved", source_trace_ok, "source_profile_id/raw_fragment/source_page present", "present" if source_trace_ok else "missing trace", OUT_SNAPSHOT.name),
        test_case("PSLRT-EXEC-TC-009", "runtime_scope_coverage", len(scope_counts) == 4, "4 runtime scopes", dict(sorted(scope_counts.items())), OUT_SNAPSHOT.name),
        test_case("PSLRT-EXEC-TC-010", "standard_coverage", set(standard_counts) == {"GB 13457-2025", "GB 15848-2009", "HJ 5.2-2026"}, "3 approved standards", dict(sorted(standard_counts.items())), OUT_SNAPSHOT.name),
    ]


def build_contract(rows, entries, test_cases):
    return {
        "contract_version": CONTRACT_VERSION,
        "source_contract_version": SOURCE_CONTRACT_VERSION,
        "approval_id": APPROVAL_ID,
        "final_state": FINAL_STATE,
        "runtime_status": RUNTIME_STATUS,
        "runtime_integration": RUNTIME_INTEGRATION,
        "import_action": IMPORT_ACTION,
        "execution_action": EXECUTION_ACTION,
        "execution_mode": EXECUTION_MODE,
        "runtime_effect": RUNTIME_EFFECT,
        "source_row_count": len(rows),
        "lookup_entry_count": len(entries),
        "test_status": "PASS" if all(case["status"] == "PASS" for case in test_cases) else "FAIL",
        "allowed_runtime_scopes": sorted({entry["runtime_scope"] for entry in entries}),
        "forbidden_runtime_actions": FORBIDDEN_RUNTIME_ACTIONS,
        "hard_rules": [
            "This execution contract materializes standard-limit lookup entries only.",
            "Execution mode is dry-run materialization in this knowledge-base package.",
            "Downstream EcoCheck import can consume the snapshot only after its own runtime tests pass.",
            "This package must not create ConfirmedDataset, run formal emission-right calculation, auto-select coefficients, mutate coefficient selectors, or enable all-industry radiation defaults.",
            "This package must not generate formal permit_type, formal inspection templates, automatic deduct values, or formal compliance conclusions.",
            "Every lookup entry must preserve source_profile_id, raw_fragment, source_page, rollback_manifest_id, and approval_id.",
        ],
    }


def write_doc(contract, test_cases):
    lines = [
        "# pollutant_standard_limit_runtime_execution_contract_v8_7",
        "",
        f"contract_version: `{CONTRACT_VERSION}`",
        f"source_contract_version: `{SOURCE_CONTRACT_VERSION}`",
        f"approval_id: `{APPROVAL_ID}`",
        f"final_state: `{FINAL_STATE}`",
        f"runtime_status: `{RUNTIME_STATUS}`",
        f"runtime_integration: `{RUNTIME_INTEGRATION}`",
        f"execution_action: `{EXECUTION_ACTION}`",
        f"execution_mode: `{EXECUTION_MODE}`",
        "",
        "This contract connects the 74 approved standard-limit runtime import rows to downstream test execution by producing a lookup-only dry-run snapshot.",
        "",
        "Hard rules:",
        *[f"- {rule}" for rule in contract["hard_rules"]],
        "",
        "Test cases:",
        *[f"- `{case['test_case_id']}` {case['name']}: {case['status']}" for case in test_cases],
    ]
    OUT_DOC.parent.mkdir(parents=True, exist_ok=True)
    OUT_DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_artifact_manifest():
    manifest = read_json(ARTIFACT_MANIFEST)
    artifacts = manifest.setdefault("artifacts", {})
    artifacts.update({
        "pollutant_standard_limit_runtime_lookup_snapshot_v8_7.json": "data/runtime/pollutant_standard_limit_runtime_lookup_snapshot_v8_7.json",
        "pollutant_standard_limit_runtime_execution_contract_v8_7.json": "data/runtime/pollutant_standard_limit_runtime_execution_contract_v8_7.json",
        "pollutant_standard_limit_runtime_execution_test_cases_v8_7.json": "data/runtime/pollutant_standard_limit_runtime_execution_test_cases_v8_7.json",
        "pollutant_standard_limit_runtime_execution_contract_v8_7.md": "docs/runtime/pollutant_standard_limit_runtime_execution_contract_v8_7.md",
        "pollutant_standard_limit_runtime_execution_manifest_v8_7.json": "manifests/pollutant_standard_limit_runtime_execution_manifest_v8_7.json",
        "pollutant_standard_limit_runtime_execution_contract_v8_7_report.json": "reports/pollutant_standard_limit_runtime_execution_contract_v8_7.json",
        "build_standard_limit_runtime_execution_contract_v8_7.py": "build_standard_limit_runtime_execution_contract_v8_7.py",
        "validate_standard_limit_runtime_execution_contract_v8_7.py": "validate_standard_limit_runtime_execution_contract_v8_7.py",
    })
    write_json(ARTIFACT_MANIFEST, manifest)


def main():
    rows = read_csv(SOURCE_CSV)
    source_json_rows = read_json(SOURCE_JSON)
    source_contract = read_json(SOURCE_CONTRACT)
    source_manifest = read_json(SOURCE_MANIFEST)
    if len(source_json_rows) != len(rows):
        raise SystemExit("source json/csv row count mismatch")

    entries = materialize_lookup_rows(rows)
    test_cases = build_test_cases(rows, entries, source_contract, source_manifest)
    contract = build_contract(rows, entries, test_cases)
    snapshot = {
        "snapshot_id": "pollutant_standard_limit_runtime_lookup_snapshot_v8_7",
        "contract_version": CONTRACT_VERSION,
        "approval_id": APPROVAL_ID,
        "final_state": FINAL_STATE,
        "runtime_status": RUNTIME_STATUS,
        "runtime_integration": RUNTIME_INTEGRATION,
        "execution_mode": EXECUTION_MODE,
        "runtime_effect": RUNTIME_EFFECT,
        "lookup_entry_count": len(entries),
        "entries": entries,
    }
    manifest = {
        "manifest_id": "pollutant_standard_limit_runtime_execution_manifest_v8_7",
        "contract_version": CONTRACT_VERSION,
        "source_contract_version": SOURCE_CONTRACT_VERSION,
        "approval_id": APPROVAL_ID,
        "final_state": FINAL_STATE,
        "runtime_status": RUNTIME_STATUS,
        "runtime_integration": RUNTIME_INTEGRATION,
        "import_action": IMPORT_ACTION,
        "execution_action": EXECUTION_ACTION,
        "execution_mode": EXECUTION_MODE,
        "runtime_effect": RUNTIME_EFFECT,
        "lookup_entry_count": len(entries),
        "test_status": contract["test_status"],
        "standard_counts": dict(sorted(Counter(entry["standard_no"] for entry in entries).items())),
        "runtime_scope_counts": dict(sorted(Counter(entry["runtime_scope"] for entry in entries).items())),
        "forbidden_runtime_actions": FORBIDDEN_RUNTIME_ACTIONS,
    }

    write_json(OUT_SNAPSHOT, snapshot)
    write_json(OUT_CONTRACT, contract)
    write_json(OUT_TEST_CASES, test_cases)
    write_json(OUT_MANIFEST, manifest)
    write_doc(contract, test_cases)

    report = {
        **manifest,
        "source_hashes": {
            "runtime_import_csv": sha256_file(SOURCE_CSV),
            "runtime_import_json": sha256_file(SOURCE_JSON),
            "runtime_import_contract_json": sha256_file(SOURCE_CONTRACT),
            "runtime_import_manifest_json": sha256_file(SOURCE_MANIFEST),
        },
        "outputs": {
            "lookup_snapshot_json": {"path": str(OUT_SNAPSHOT.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256_file(OUT_SNAPSHOT)},
            "execution_contract_json": {"path": str(OUT_CONTRACT.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256_file(OUT_CONTRACT)},
            "execution_test_cases_json": {"path": str(OUT_TEST_CASES.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256_file(OUT_TEST_CASES)},
            "execution_manifest_json": {"path": str(OUT_MANIFEST.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256_file(OUT_MANIFEST)},
        },
        "test_cases": test_cases,
    }
    write_json(OUT_REPORT, report)
    update_artifact_manifest()
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
