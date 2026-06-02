import csv
import hashlib
import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = Path(os.environ.get("SEMANTIC_PROFILE_LAB_ROOT", r"E:\semantic-profile-lab"))
VERSION = "v8.5-pollutant-domain-approved-baseline"
FINAL_STATE = "APPROVED_POLLUTANT_DOMAIN_BASELINE_KNOWLEDGE"
RUNTIME_STATUS = "APPROVED_BASELINE"
RUNTIME_INTEGRATION = "approved_baseline_export_ready"
APPROVAL_STATUS = "HUMAN_APPROVED_BASELINE"
APPROVAL_SOURCE = "CANDY_OWNER_L5_APPROVAL_2026-06-02_SEMANTIC_PROFILE_LAB_V8_5"
APPROVAL_DATE = "2026-06-02"
TARGET_REPOSITORY = "coco830/eco-semantic-knowledge-base"
SOURCE_BOUNDARY_STATUS = {
    "source_runtime_status": "DRAFT_NOT_FOR_RUNTIME",
    "source_final_state": "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY",
    "source_runtime_integration": "disabled",
}

SOURCE_BASELINE = SOURCE_ROOT / "mappings" / "pollutant-domain-approved-baseline.v8_5.csv"
SOURCE_PACKAGE = SOURCE_ROOT / "packages" / "approved-baseline" / "v8_5" / "pollutant-domain-approved-baseline-package.v8_5.json"
SOURCE_MANIFEST = SOURCE_ROOT / "manifests" / "pollutant-domain-approved-baseline.v8_5.json"
SOURCE_REPORT = SOURCE_ROOT / "reports" / "pollutant-domain-approved-baseline-package-v8_5.md"

OUT_DIR = ROOT / "data" / "approved_baseline" / "pollutant_domain_v8_5"
OUT_BASELINE = OUT_DIR / "pollutant_domain_approved_baseline_v8_5.csv"
OUT_PACKAGE = OUT_DIR / "pollutant_domain_approved_baseline_package_v8_5.json"
OUT_MANIFEST = ROOT / "manifests" / "pollutant_domain_approved_baseline_manifest_v8_5.json"
OUT_REPORT = ROOT / "reports" / "FINAL_POLLUTANT_DOMAIN_APPROVED_BASELINE_v8_5.md"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path):
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def write_json_lf(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    tmp.replace(path)


def write_text_lf(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")
    tmp.replace(path)


def write_csv_lf(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    with tmp.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    tmp.replace(path)


def source_git_commit():
    try:
        result = subprocess.run(
            ["git", "-C", str(SOURCE_ROOT), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN_SOURCE_COMMIT"
    return result.stdout.strip()


def transform_row(row):
    copied = dict(row)
    copied["source_runtime_status"] = copied.pop("runtime_status", "")
    copied["source_final_state"] = copied.pop("final_state", "")
    copied["source_runtime_integration"] = copied.pop("runtime_integration", "")
    copied["runtime_status"] = RUNTIME_STATUS
    copied["final_state"] = FINAL_STATE
    copied["runtime_integration"] = RUNTIME_INTEGRATION
    copied["approval_status"] = APPROVAL_STATUS
    copied["approval_source"] = APPROVAL_SOURCE
    copied["approved_baseline_version"] = VERSION
    copied["knowledge_base_target_repository"] = TARGET_REPOSITORY
    return copied


def update_artifact_manifest():
    path = ROOT / "artifact_manifest.json"
    data = read_json(path)
    artifacts = data.setdefault("artifacts", {})
    artifacts.update({
        "pollutant_domain_approved_baseline_v8_5.csv": "data/approved_baseline/pollutant_domain_v8_5/pollutant_domain_approved_baseline_v8_5.csv",
        "pollutant_domain_approved_baseline_package_v8_5.json": "data/approved_baseline/pollutant_domain_v8_5/pollutant_domain_approved_baseline_package_v8_5.json",
        "pollutant_domain_approved_baseline_manifest_v8_5.json": "manifests/pollutant_domain_approved_baseline_manifest_v8_5.json",
        "pollutant_domain_approved_baseline_gate_report_v8_5.json": "reports/pollutant_domain_approved_baseline_gate_report_v8_5.json",
        "FINAL_POLLUTANT_DOMAIN_APPROVED_BASELINE_v8_5.md": "reports/FINAL_POLLUTANT_DOMAIN_APPROVED_BASELINE_v8_5.md",
        "build_pollutant_domain_approved_baseline_v8_5.py": "build_pollutant_domain_approved_baseline_v8_5.py",
        "validate_pollutant_domain_approved_baseline_v8_5.py": "validate_pollutant_domain_approved_baseline_v8_5.py",
    })
    write_json_lf(path, data)


def build_report(source_manifest, source_package, source_commit):
    excluded = source_package.get("excluded_p1_decisions", [])
    excluded_lines = "\n".join(
        f"- `{item['source_id']}`: {item['decision']} ({item['reason']})" for item in excluded
    )
    domains = "\n".join(
        f"- `{domain}`: {count}" for domain, count in source_manifest.get("domain_distribution", {}).items()
    )
    return f"""# V8.5 Pollutant Domain Approved Baseline

This package backfills the manually approved Semantic Profile Lab V8.5 pollutant-domain source baseline into `coco830/eco-semantic-knowledge-base`.

## Scope

- Approved entries: {source_manifest["approved_entry_count"]}
- P1 excluded entries: {source_manifest["excluded_entry_count"]}
- Approval authority: `{source_manifest["approval_authority"]}`
- Approval date: `{APPROVAL_DATE}`
- Source Semantic Profile Lab commit: `{source_commit}`
- Source package scope: `{source_manifest["baseline_package_scope"]}`
- Knowledge-base final state: `{FINAL_STATE}`
- Runtime integration marker: `{RUNTIME_INTEGRATION}`

The source candidate boundary is preserved on every row as `source_runtime_status`, `source_final_state`, and `source_runtime_integration`.

## Domain Distribution

{domains}

## P1 Exclusions

{excluded_lines}

## Guards

- `ConfirmedDataset` is still `NOT_CREATED`.
- Formal emission-right calculation is still `NOT_AUTHORIZED`.
- `radiation_all_industry_default` remains blocked.
- This backfill does not mutate EcoCheck runtime code, `ReviewField`, or `CoefficientSelector`.
"""


def main():
    update_artifact_manifest()

    source_rows = read_csv(SOURCE_BASELINE)
    source_manifest = read_json(SOURCE_MANIFEST)
    source_package = read_json(SOURCE_PACKAGE)
    source_commit = source_git_commit()

    rows = [transform_row(row) for row in source_rows]
    fields = list(rows[0].keys()) if rows else []
    write_csv_lf(OUT_BASELINE, rows, fields)

    package = {
        "schema_version": "pollutant-domain-approved-baseline-package.v8_5.knowledge-base-backfill",
        "knowledge_base_version": VERSION,
        "final_state": FINAL_STATE,
        "runtime_status": RUNTIME_STATUS,
        "runtime_integration": RUNTIME_INTEGRATION,
        "approval_status": APPROVAL_STATUS,
        "approval_source": APPROVAL_SOURCE,
        "approval_date": APPROVAL_DATE,
        "source_repository": "coco830/semantic-profile-lab",
        "source_commit": source_commit,
        "source_baseline_manifest": source_manifest,
        "source_package_summary": {
            "schema_version": source_package.get("schema_version"),
            "approved_entry_count": source_package.get("approved_entry_count"),
            "excluded_entry_count": source_package.get("excluded_entry_count"),
            "source_register_row_count": source_package.get("source_register_row_count"),
            "excluded_p1_decisions": source_package.get("excluded_p1_decisions", []),
        },
        "knowledge_base_outputs": {
            "baseline_csv": "data/approved_baseline/pollutant_domain_v8_5/pollutant_domain_approved_baseline_v8_5.csv",
            "manifest": "manifests/pollutant_domain_approved_baseline_manifest_v8_5.json",
            "report": "reports/FINAL_POLLUTANT_DOMAIN_APPROVED_BASELINE_v8_5.md",
        },
        "boundary": {
            **SOURCE_BOUNDARY_STATUS,
            "baseline_package_scope": source_manifest.get("baseline_package_scope"),
            "downstream_target_repository": TARGET_REPOSITORY,
            "confirmed_dataset_status": source_manifest.get("confirmed_dataset_status"),
            "formal_calculation_status": source_manifest.get("formal_calculation_status"),
            "blocked_actions": source_manifest.get("blocked_actions", []),
            "no_runtime_code_mutation": True,
        },
        "counts": {
            "approved_entry_count": len(rows),
            "excluded_entry_count": source_package.get("excluded_entry_count"),
            "source_register_row_count": source_package.get("source_register_row_count"),
            "domain_distribution": source_manifest.get("domain_distribution", {}),
            "content_usability_flag_distribution": source_manifest.get("content_usability_flag_distribution", {}),
        },
    }
    write_json_lf(OUT_PACKAGE, package)

    report = build_report(source_manifest, source_package, source_commit)
    write_text_lf(OUT_REPORT, report)

    manifest = {
        "schema_version": "pollutant-domain-approved-baseline-manifest.v8_5.knowledge-base-backfill",
        "knowledge_base_version": VERSION,
        "generated_on": APPROVAL_DATE,
        "final_state": FINAL_STATE,
        "runtime_status": RUNTIME_STATUS,
        "runtime_integration": RUNTIME_INTEGRATION,
        "approval_status": APPROVAL_STATUS,
        "approval_source": APPROVAL_SOURCE,
        "source_repository": "coco830/semantic-profile-lab",
        "source_commit": source_commit,
        "approved_entry_count": len(rows),
        "excluded_entry_count": source_package.get("excluded_entry_count"),
        "p1_excluded_source_ids": [item["source_id"] for item in source_package.get("excluded_p1_decisions", [])],
        "baseline_package_scope": source_manifest.get("baseline_package_scope"),
        "downstream_target_repository": TARGET_REPOSITORY,
        "confirmed_dataset_status": source_manifest.get("confirmed_dataset_status"),
        "formal_calculation_status": source_manifest.get("formal_calculation_status"),
        "blocked_actions": source_manifest.get("blocked_actions", []),
        "outputs": {
            "baseline_csv": {
                "path": "data/approved_baseline/pollutant_domain_v8_5/pollutant_domain_approved_baseline_v8_5.csv",
                "sha256": sha256_file(OUT_BASELINE),
            },
            "package_json": {
                "path": "data/approved_baseline/pollutant_domain_v8_5/pollutant_domain_approved_baseline_package_v8_5.json",
                "sha256": sha256_file(OUT_PACKAGE),
            },
            "report_md": {
                "path": "reports/FINAL_POLLUTANT_DOMAIN_APPROVED_BASELINE_v8_5.md",
                "sha256": sha256_file(OUT_REPORT),
            },
        },
    }
    write_json_lf(OUT_MANIFEST, manifest)

    print(json.dumps({
        "status": "BUILT",
        "approved_entry_count": len(rows),
        "excluded_entry_count": source_package.get("excluded_entry_count"),
        "baseline_sha256": sha256_file(OUT_BASELINE),
        "package_sha256": sha256_file(OUT_PACKAGE),
        "report_sha256": sha256_file(OUT_REPORT),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
