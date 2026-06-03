import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
APPROVAL_ID = "CANDY-APPROVAL-STANDARD-LIMIT-RUNTIME-IMPORT-2026-06-03"
FINAL_STATE = "APPROVED_STANDARD_LIMIT_PROFILE_RUNTIME_IMPORT_CONTRACT"
RUNTIME_STATUS = "APPROVED_FOR_IMPORT_PENDING_TESTS"
RUNTIME_INTEGRATION = "approved_standard_limit_profile_import_contract"
IMPORT_ACTION = "APPROVED_FOR_RUNTIME_IMPORT_CONTRACT"
CONTRACT_VERSION = "v8.7-standard-limit-runtime-import-contract"
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

SOURCE_CSV = ROOT / "data" / "review" / "pollutant_standard_limit_profile_adapter_v8_7.csv"
OUT_CSV = ROOT / "data" / "runtime" / "pollutant_standard_limit_runtime_import_v8_7.csv"
OUT_JSON = ROOT / "data" / "runtime" / "pollutant_standard_limit_runtime_import_v8_7.json"
OUT_CONTRACT = ROOT / "data" / "runtime" / "pollutant_standard_limit_runtime_data_contract_v8_7.json"
OUT_CONTRACT_MD = ROOT / "docs" / "runtime" / "pollutant_standard_limit_runtime_data_contract_v8_7.md"
OUT_MANIFEST = ROOT / "manifests" / "pollutant_standard_limit_runtime_import_manifest_v8_7.json"
OUT_REPORT = ROOT / "reports" / "pollutant_standard_limit_runtime_import_v8_7.json"
ARTIFACT_MANIFEST = ROOT / "artifact_manifest.json"

IMPORT_FIELDS = [
    "runtime_import_id",
    "source_profile_id",
    "approval_id",
    "replacement_standard_no",
    "obsolete_source_id",
    "replacement_standard_title",
    "profile_family",
    "standard_limit_target",
    "medium",
    "table_or_clause_ref",
    "source_page",
    "source_table_index",
    "source_row_index",
    "pollutant_item",
    "standard_limit_metric",
    "metric",
    "operator",
    "value",
    "unit",
    "lower_value",
    "lower_unit",
    "lower_inclusive",
    "upper_value",
    "upper_unit",
    "upper_inclusive",
    "equivalent_value",
    "equivalent_unit",
    "limit_context",
    "monitoring_location",
    "raw_fragment",
    "source_evidence_ref",
    "adapter_mapping_basis",
    "human_review_status",
    "runtime_scope",
    "runtime_status",
    "runtime_integration",
    "runtime_effect",
    "import_action",
    "forbidden_runtime_actions",
    "rollback_manifest_id",
    "contract_version",
    "final_state",
]


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    with tmp.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    tmp.replace(path)


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    tmp.replace(path)


def sha256_file(path):
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_scope_for(row):
    family = row["profile_family"]
    if family == "EMISSION_STANDARD_LIMIT_TABLE":
        return "standard_limit_lookup.water_pollutant_concentration"
    if family == "WATER_USE_BENCHMARK_TABLE":
        return "standard_limit_lookup.water_use_benchmark"
    if family == "RADIATION_NUMERIC_CONSTRAINT":
        return "standard_limit_lookup.radiation_numeric_constraint"
    if family == "STANDARD_LIMIT_FIELD_REQUIREMENT":
        return "standard_limit_lookup.eia_report_field_requirement"
    return "standard_limit_lookup.unspecified"


def build_rows():
    rows = []
    source_rows = read_csv(SOURCE_CSV)
    for index, source in enumerate(source_rows, start=1):
        rows.append({
            "runtime_import_id": f"PSLRT-V8_7-{index:05d}",
            "source_profile_id": source["profile_id"],
            "approval_id": APPROVAL_ID,
            "replacement_standard_no": source["replacement_standard_no"],
            "obsolete_source_id": source["obsolete_source_id"],
            "replacement_standard_title": source["replacement_standard_title"],
            "profile_family": source["profile_family"],
            "standard_limit_target": source["standard_limit_target"],
            "medium": source["medium"],
            "table_or_clause_ref": source["table_or_clause_ref"],
            "source_page": source["source_page"],
            "source_table_index": source["source_table_index"],
            "source_row_index": source["source_row_index"],
            "pollutant_item": source["pollutant_item"],
            "standard_limit_metric": source["standard_limit_metric"],
            "metric": source["metric"],
            "operator": source["operator"],
            "value": source["value"],
            "unit": source["unit"],
            "lower_value": source["lower_value"],
            "lower_unit": source["lower_unit"],
            "lower_inclusive": source["lower_inclusive"],
            "upper_value": source["upper_value"],
            "upper_unit": source["upper_unit"],
            "upper_inclusive": source["upper_inclusive"],
            "equivalent_value": source["equivalent_value"],
            "equivalent_unit": source["equivalent_unit"],
            "limit_context": source["limit_context"],
            "monitoring_location": source["monitoring_location"],
            "raw_fragment": source["raw_fragment"],
            "source_evidence_ref": "pollutant_standard_replacement_source_evidence_v8_7.csv;pollutant_standard_limit_profile_adapter_v8_7.csv",
            "adapter_mapping_basis": source["adapter_mapping_basis"],
            "human_review_status": source["human_review_status"],
            "runtime_scope": runtime_scope_for(source),
            "runtime_status": RUNTIME_STATUS,
            "runtime_integration": RUNTIME_INTEGRATION,
            "runtime_effect": "STANDARD_LIMIT_LOOKUP_ONLY",
            "import_action": IMPORT_ACTION,
            "forbidden_runtime_actions": ";".join(FORBIDDEN_RUNTIME_ACTIONS),
            "rollback_manifest_id": "rollback_pollutant_standard_limit_runtime_import_v8_7",
            "contract_version": CONTRACT_VERSION,
            "final_state": FINAL_STATE,
        })
    return rows


def build_contract(rows):
    return {
        "contract_version": CONTRACT_VERSION,
        "approval_id": APPROVAL_ID,
        "final_state": FINAL_STATE,
        "runtime_status": RUNTIME_STATUS,
        "runtime_integration": RUNTIME_INTEGRATION,
        "import_action": IMPORT_ACTION,
        "runtime_effect": "STANDARD_LIMIT_LOOKUP_ONLY",
        "row_count": len(rows),
        "required_fields": IMPORT_FIELDS,
        "allowed_runtime_scopes": sorted(set(row["runtime_scope"] for row in rows)),
        "status_values": [RUNTIME_STATUS],
        "hard_rules": [
            "This contract imports standard-limit lookup profiles only.",
            "It must not create ConfirmedDataset.",
            "It must not run formal emission-right calculation.",
            "It must not auto-select or mutate coefficient selection.",
            "It must not enable all-industry radiation defaults.",
            "It must not generate formal permit_type.",
            "It must not generate formal inspection templates.",
            "It must not generate automatic deduct values.",
            "It must not make formal compliance conclusions without downstream runtime tests and enterprise evidence.",
            "Every row must preserve source_profile_id, raw_fragment, source_page, approval_id, and rollback_manifest_id.",
        ],
    }


def write_contract_md(contract):
    lines = [
        "# pollutant_standard_limit_runtime_data_contract_v8_7",
        "",
        f"contract_version: `{CONTRACT_VERSION}`",
        f"approval_id: `{APPROVAL_ID}`",
        f"final_state: `{FINAL_STATE}`",
        f"runtime_status: `{RUNTIME_STATUS}`",
        f"runtime_integration: `{RUNTIME_INTEGRATION}`",
        f"import_action: `{IMPORT_ACTION}`",
        "",
        "This contract promotes the 74 approved standard-limit profile rows into a runtime import contract for standard-limit lookup only.",
        "",
        "Required fields:",
        *[f"- `{field}`" for field in IMPORT_FIELDS],
        "",
        "Hard rules:",
        *[f"- {rule}" for rule in contract["hard_rules"]],
    ]
    OUT_CONTRACT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_CONTRACT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_artifact_manifest():
    manifest = json.loads(ARTIFACT_MANIFEST.read_text(encoding="utf-8"))
    artifacts = manifest.setdefault("artifacts", {})
    updates = {
        "pollutant_standard_limit_runtime_import_v8_7.csv": "data/runtime/pollutant_standard_limit_runtime_import_v8_7.csv",
        "pollutant_standard_limit_runtime_import_v8_7.json": "data/runtime/pollutant_standard_limit_runtime_import_v8_7.json",
        "pollutant_standard_limit_runtime_data_contract_v8_7.json": "data/runtime/pollutant_standard_limit_runtime_data_contract_v8_7.json",
        "pollutant_standard_limit_runtime_data_contract_v8_7.md": "docs/runtime/pollutant_standard_limit_runtime_data_contract_v8_7.md",
        "pollutant_standard_limit_runtime_import_manifest_v8_7.json": "manifests/pollutant_standard_limit_runtime_import_manifest_v8_7.json",
        "pollutant_standard_limit_runtime_import_v8_7_report.json": "reports/pollutant_standard_limit_runtime_import_v8_7.json",
        "build_standard_limit_runtime_import_v8_7.py": "build_standard_limit_runtime_import_v8_7.py",
        "validate_standard_limit_runtime_import_v8_7.py": "validate_standard_limit_runtime_import_v8_7.py",
    }
    artifacts.update(updates)
    write_json(ARTIFACT_MANIFEST, manifest)


def main():
    rows = build_rows()
    write_csv(OUT_CSV, rows, IMPORT_FIELDS)
    write_json(OUT_JSON, rows)
    contract = build_contract(rows)
    write_json(OUT_CONTRACT, contract)
    write_contract_md(contract)
    manifest = {
        "manifest_id": "pollutant_standard_limit_runtime_import_manifest_v8_7",
        "contract_version": CONTRACT_VERSION,
        "approval_id": APPROVAL_ID,
        "final_state": FINAL_STATE,
        "runtime_status": RUNTIME_STATUS,
        "runtime_integration": RUNTIME_INTEGRATION,
        "import_action": IMPORT_ACTION,
        "runtime_effect": "STANDARD_LIMIT_LOOKUP_ONLY",
        "import_row_count": len(rows),
        "standard_counts": dict(sorted(Counter(row["replacement_standard_no"] for row in rows).items())),
        "profile_family_counts": dict(sorted(Counter(row["profile_family"] for row in rows).items())),
        "source_files": [
            "pollutant_standard_replacement_source_evidence_v8_7.csv",
            "pollutant_standard_limit_profile_adapter_v8_7.csv",
            "pollutant_standard_limit_runtime_import_v8_7.csv",
        ],
        "forbidden_runtime_actions": FORBIDDEN_RUNTIME_ACTIONS,
    }
    write_json(OUT_MANIFEST, manifest)
    report = {
        **manifest,
        "outputs": {
            "runtime_import_csv": {"path": str(OUT_CSV.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256_file(OUT_CSV)},
            "runtime_import_json": {"path": str(OUT_JSON.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256_file(OUT_JSON)},
            "runtime_contract_json": {"path": str(OUT_CONTRACT.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256_file(OUT_CONTRACT)},
            "runtime_manifest_json": {"path": str(OUT_MANIFEST.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256_file(OUT_MANIFEST)},
        },
    }
    write_json(OUT_REPORT, report)
    update_artifact_manifest()
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
