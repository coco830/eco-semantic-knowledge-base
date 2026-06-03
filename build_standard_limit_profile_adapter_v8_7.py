import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parent
FINAL_STATE = "APPROVED_STANDARD_LIMIT_PROFILE_ADAPTER"
RUNTIME_STATUS = "APPROVED_FOR_IMPORT_PENDING_TESTS"
RUNTIME_INTEGRATION = "approved_standard_limit_profile_import_contract"
HUMAN_REVIEW_STATUS = "APPROVED_BY_CANDY_FOR_STANDARD_LIMIT_PROFILE_ADAPTER"

EVIDENCE_CSV = ROOT / "data" / "review" / "pollutant_standard_replacement_source_evidence_v8_7.csv"
OUT_CSV = ROOT / "data" / "review" / "pollutant_standard_limit_profile_adapter_v8_7.csv"
OUT_JSON = ROOT / "data" / "review" / "pollutant_standard_limit_profile_adapter_v8_7.json"
OUT_REPORT = ROOT / "reports" / "pollutant_standard_limit_profile_adapter_v8_7.json"
ARTIFACT_MANIFEST = ROOT / "artifact_manifest.json"

FIELDS = [
    "profile_id",
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
    "extraction_method",
    "extraction_confidence",
    "adapter_mapping_basis",
    "human_review_status",
    "governance_status",
    "final_state",
    "runtime_status",
    "runtime_integration",
    "candidate_only",
]


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    with tmp.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
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


def compact(text):
    return re.sub(r"\s+", "", text or "")


def one_line(text):
    return re.sub(r"\s+", " ", text or "").strip()


def normalize_number(value):
    return (value or "").replace("．", ".").replace(" ", "")


def common(row, profile_no, profile_family, target, medium, page, table_index, row_index):
    return {
        "profile_id": f"PSLPA-V8_7-{profile_no:05d}",
        "replacement_standard_no": row["replacement_standard_no"],
        "obsolete_source_id": row["obsolete_source_id"],
        "replacement_standard_title": row["replacement_standard_title"],
        "profile_family": profile_family,
        "standard_limit_target": target,
        "medium": medium,
        "table_or_clause_ref": "",
        "source_page": str(page),
        "source_table_index": str(table_index),
        "source_row_index": str(row_index),
        "pollutant_item": "",
        "standard_limit_metric": "",
        "metric": "",
        "operator": "",
        "value": "",
        "unit": "",
        "lower_value": "",
        "lower_unit": "",
        "lower_inclusive": "",
        "upper_value": "",
        "upper_unit": "",
        "upper_inclusive": "",
        "equivalent_value": "",
        "equivalent_unit": "",
        "limit_context": "",
        "monitoring_location": "",
        "raw_fragment": "",
        "extraction_method": "",
        "extraction_confidence": "",
        "adapter_mapping_basis": "reuses permit_threshold_predicate_governance fieldset: metric/operator/value/unit/lower/upper/equivalent/raw_fragment/source_page/governance_status",
        "human_review_status": HUMAN_REVIEW_STATUS,
        "governance_status": "STANDARD_LIMIT_PROFILE_ADAPTER_APPROVED_FOR_RUNTIME_IMPORT_CONTRACT",
        "final_state": FINAL_STATE,
        "runtime_status": RUNTIME_STATUS,
        "runtime_integration": RUNTIME_INTEGRATION,
        "candidate_only": "TRUE",
    }


def pollutant_limit_unit(item):
    if "pH" in item:
        return "dimensionless"
    if "色度" in item:
        return "dilution_factor"
    if "总大肠菌群" in item:
        return "MPN/L"
    return "mg/L"


def assign_limit_value(out, raw_value, unit):
    value = normalize_number(raw_value)
    out["unit"] = unit
    if "～" in value or "~" in value:
        parts = re.split(r"[～~]", value, maxsplit=1)
        out["operator"] = "range"
        out["lower_value"] = normalize_number(parts[0])
        out["lower_unit"] = unit
        out["lower_inclusive"] = "TRUE"
        out["upper_value"] = normalize_number(parts[1])
        out["upper_unit"] = unit
        out["upper_inclusive"] = "TRUE"
        return
    if "/" in value:
        out["operator"] = "mixed_limit_with_note"
        out["value"] = value
        return
    out["operator"] = "lte"
    out["value"] = value


def build_gb13457_profiles(source_row, start_no):
    pdf = ROOT / source_row["local_snapshot_path"]
    doc = fitz.open(pdf)
    rows = []
    profile_no = start_no
    limit_columns = [
        (2, "direct_discharge_max_concentration"),
        (3, "indirect_discharge_max_concentration"),
        (4, "negotiated_indirect_discharge_max_concentration"),
    ]
    for page_no in [6, 7]:
        page = doc[page_no - 1]
        for table_index, table in enumerate(page.find_tables().tables, start=1):
            extracted = table.extract()
            if table_index == 1:
                for row_index, raw_row in enumerate(extracted):
                    if len(raw_row) < 5 or not re.fullmatch(r"\d+", one_line(raw_row[0] or "")):
                        continue
                    item = one_line(raw_row[1]).replace(" \n", "").replace("\n", "")
                    unit = pollutant_limit_unit(item)
                    for col_index, target in limit_columns:
                        value = one_line(raw_row[col_index] or "")
                        if not value or value == "—":
                            continue
                        out = common(source_row, profile_no, "EMISSION_STANDARD_LIMIT_TABLE", target, "water", page_no, table_index, row_index)
                        out["table_or_clause_ref"] = "表1"
                        out["pollutant_item"] = item
                        out["standard_limit_metric"] = target
                        out["metric"] = target
                        out["limit_context"] = target
                        out["monitoring_location"] = "排污单位污水总排放口"
                        out["raw_fragment"] = f"{item} | {target} | {value}"
                        out["extraction_method"] = "pymupdf_find_tables_standard_limit_adapter"
                        out["extraction_confidence"] = "HIGH"
                        assign_limit_value(out, value, unit)
                        rows.append(out)
                        profile_no += 1
            elif table_index == 2:
                current_category = ""
                current_unit = ""
                for row_index, raw_row in enumerate(extracted):
                    cells = [one_line(c or "") for c in raw_row]
                    if not cells or "分类" in cells[0] or "注" in cells[0]:
                        continue
                    if cells[0]:
                        current_category = cells[0]
                        match = re.search(r"（([^）]+)）", current_category)
                        current_unit = match.group(1) if match else current_unit
                    product = cells[1] if len(cells) > 1 and cells[1] else current_category
                    value = cells[2] if len(cells) > 2 else ""
                    if not value or not re.search(r"\d", value):
                        continue
                    out = common(source_row, profile_no, "WATER_USE_BENCHMARK_TABLE", "unit_product_benchmark_drainage", "water", page_no, table_index, row_index)
                    out["table_or_clause_ref"] = "表2"
                    out["pollutant_item"] = product
                    out["standard_limit_metric"] = "unit_product_benchmark_drainage"
                    out["metric"] = "unit_product_benchmark_drainage"
                    out["operator"] = "benchmark"
                    out["value"] = normalize_number(value)
                    out["unit"] = current_unit
                    out["limit_context"] = current_category
                    out["monitoring_location"] = "与污染物排放监控位置一致"
                    out["raw_fragment"] = " | ".join(cell for cell in cells if cell)
                    out["extraction_method"] = "pymupdf_find_tables_standard_limit_adapter"
                    out["extraction_confidence"] = "HIGH"
                    rows.append(out)
                    profile_no += 1
    return rows, profile_no


def infer_constraint_metric(fragment):
    if "表面污染" in fragment:
        return "surface_contamination_control_level", "radiation_surface"
    if "限制距离" in fragment:
        return "restricted_distance", "radiation_workplace"
    if "通风" in fragment:
        return "ventilation_distance_or_depth_requirement", "radiation_workplace"
    if "摄入量" in fragment:
        return "annual_intake_or_internal_dose_constraint", "radiation"
    if "剂量" in fragment:
        return "effective_dose_constraint", "radiation"
    return "radiation_numeric_constraint", "radiation"


def numeric_tokens(fragment):
    normalized = fragment.replace("．", ".")
    pattern = re.compile(r"(?P<value>\d+(?:\.\d+)?)\s*(?P<unit>mSv(?:／a|/a)?|Bq／cm2|Bq/cm2|J／m3|J·h／m3|m|米|倍|cm2|MeV)")
    return [(m.group("value"), m.group("unit")) for m in pattern.finditer(normalized)]


def build_gb15848_profiles(source_row, start_no):
    pdf = ROOT / source_row["local_snapshot_path"]
    doc = fitz.open(pdf)
    rows = []
    profile_no = start_no
    pattern = re.compile(
        r"[^。；;\n]{0,45}(?:不高于|不超过|不得超过|超过|限值|控制水平|限制距离|应控制)[^。；;\n]{0,100}"
        r"(?:mSv|Bq／cm2|Bq/cm2|J／m3|J·h／m3|米|m|倍|cm2|MeV)[^。；;\n]{0,45}"
    )
    for page_index, page in enumerate(doc, start=1):
        text = re.sub(r"\s+", " ", page.get_text("text") or "")
        seen = set()
        for match_index, match in enumerate(pattern.finditer(text), start=1):
            fragment = one_line(match.group(0))
            if fragment in seen:
                continue
            seen.add(fragment)
            tokens = numeric_tokens(fragment)
            if not tokens:
                continue
            metric, medium = infer_constraint_metric(fragment)
            for token_index, (value, unit) in enumerate(tokens, start=1):
                out = common(source_row, profile_no, "RADIATION_NUMERIC_CONSTRAINT", metric, medium, page_index, 0, match_index)
                out["table_or_clause_ref"] = f"page_{page_index}_numeric_constraint"
                out["pollutant_item"] = metric
                out["standard_limit_metric"] = metric
                out["metric"] = metric
                out["operator"] = "lte_or_threshold_context"
                out["value"] = normalize_number(value)
                out["unit"] = unit.replace("／", "/")
                out["limit_context"] = metric
                out["raw_fragment"] = fragment
                out["extraction_method"] = "text_numeric_constraint_standard_limit_adapter"
                out["extraction_confidence"] = "MEDIUM"
                rows.append(out)
                profile_no += 1
    return rows, profile_no


HJ_REQUIREMENT_PATTERNS = [
    ("A.3.7.1", "pollutant_concentration_and_generation_amount_requirement", "pollutant_concentration;generation_amount"),
    ("流出物排放清单", "effluent_discharge_inventory_requirement", "nuclide_type;discharge_concentration;radioactivity_level;executed_standard"),
    ("非放射性污染物", "nonradioactive_pollutant_discharge_requirement", "waste_gas_concentration;discharge_concentration;discharge_amount;waste_liquid_characteristic_pollutant_concentration"),
    ("核素年均浓度", "nuclide_annual_concentration_and_dose_requirement", "nuclide_annual_concentration;personal_effective_dose"),
    ("公众个人有效剂量", "public_effective_dose_estimation_requirement", "public_effective_dose"),
    ("废物包表面剂量率水平", "waste_package_radioactivity_profile_requirement", "nuclide_composition;activity_concentration;total_activity;surface_dose_rate;surface_contamination_level"),
]


def build_hj52_profiles(source_row, start_no):
    pdf = ROOT / source_row["local_snapshot_path"]
    doc = fitz.open(pdf)
    rows = []
    profile_no = start_no
    for page_index, page in enumerate(doc, start=1):
        lines = [one_line(line) for line in (page.get_text("text") or "").splitlines()]
        lines = [line for line in lines if line]
        for marker, metric, fields in HJ_REQUIREMENT_PATTERNS:
            for line_index, line in enumerate(lines):
                if marker not in line:
                    continue
                fragment = " ".join(lines[line_index: min(len(lines), line_index + 5)])
                out = common(source_row, profile_no, "STANDARD_LIMIT_FIELD_REQUIREMENT", metric, "radiation", page_index, 0, line_index)
                out["table_or_clause_ref"] = marker
                out["pollutant_item"] = fields
                out["standard_limit_metric"] = metric
                out["metric"] = metric
                out["operator"] = "required_field_present"
                out["limit_context"] = "EIA_REPORT_FORMAT_AND_CONTENT_REQUIREMENT"
                out["raw_fragment"] = fragment
                out["extraction_method"] = "text_requirement_standard_limit_adapter"
                out["extraction_confidence"] = "MEDIUM"
                rows.append(out)
                profile_no += 1
                break
    return rows, profile_no


def build_rows():
    evidence_rows = read_csv(EVIDENCE_CSV)
    rows = []
    profile_no = 1
    by_standard = {row["replacement_standard_no"]: row for row in evidence_rows}
    for standard_no in ["GB 13457-2025", "GB 15848-2009", "HJ 5.2-2026"]:
        source_row = by_standard[standard_no]
        if standard_no == "GB 13457-2025":
            new_rows, profile_no = build_gb13457_profiles(source_row, profile_no)
        elif standard_no == "GB 15848-2009":
            new_rows, profile_no = build_gb15848_profiles(source_row, profile_no)
        else:
            new_rows, profile_no = build_hj52_profiles(source_row, profile_no)
        rows.extend(new_rows)
    return rows


def update_artifact_manifest():
    manifest = json.loads(ARTIFACT_MANIFEST.read_text(encoding="utf-8"))
    artifacts = manifest.setdefault("artifacts", {})
    updates = {
        "pollutant_standard_limit_profile_adapter_v8_7.csv": "data/review/pollutant_standard_limit_profile_adapter_v8_7.csv",
        "pollutant_standard_limit_profile_adapter_v8_7.json": "data/review/pollutant_standard_limit_profile_adapter_v8_7.json",
        "pollutant_standard_limit_profile_adapter_v8_7_report.json": "reports/pollutant_standard_limit_profile_adapter_v8_7.json",
        "build_standard_limit_profile_adapter_v8_7.py": "build_standard_limit_profile_adapter_v8_7.py",
        "validate_standard_limit_profile_adapter_v8_7.py": "validate_standard_limit_profile_adapter_v8_7.py",
    }
    changed = False
    for key, value in updates.items():
        if artifacts.get(key) != value:
            artifacts[key] = value
            changed = True
    if changed:
        write_json(ARTIFACT_MANIFEST, manifest)


def main():
    rows = build_rows()
    write_csv(OUT_CSV, rows)
    write_json(OUT_JSON, rows)
    report = {
        "schema_version": "pollutant-standard-limit-profile-adapter.v8_7",
        "final_state": FINAL_STATE,
        "runtime_status": RUNTIME_STATUS,
        "runtime_integration": RUNTIME_INTEGRATION,
        "human_review_status": HUMAN_REVIEW_STATUS,
        "row_count": len(rows),
        "standard_counts": dict(sorted(Counter(row["replacement_standard_no"] for row in rows).items())),
        "profile_family_counts": dict(sorted(Counter(row["profile_family"] for row in rows).items())),
        "extraction_confidence_counts": dict(sorted(Counter(row["extraction_confidence"] for row in rows).items())),
        "outputs": {
            "adapter_csv": {"path": str(OUT_CSV.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256_file(OUT_CSV)},
            "adapter_json": {"path": str(OUT_JSON.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256_file(OUT_JSON)},
        },
    }
    write_json(OUT_REPORT, report)
    update_artifact_manifest()
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
