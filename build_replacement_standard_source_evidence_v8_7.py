import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parent
FINAL_STATE = "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"
RUNTIME_STATUS = "DRAFT_NOT_FOR_RUNTIME"
RUNTIME_INTEGRATION = "disabled"
HUMAN_REVIEW_STATUS = "APPROVED_BY_CANDY_FOR_STANDARD_LIMIT_PROFILE_ADAPTER"

SOURCE_RECOVERY = ROOT / "data" / "review" / "pollutant_standard_source_recovery_v8_7.csv"
SNAPSHOT_DIR = ROOT / "reference_sources" / "replacement_standard_governance_v8_7"
OUT_CSV = ROOT / "data" / "review" / "pollutant_standard_replacement_source_evidence_v8_7.csv"
OUT_JSON = ROOT / "data" / "review" / "pollutant_standard_replacement_source_evidence_v8_7.json"
OUT_REPORT = ROOT / "reports" / "pollutant_standard_replacement_source_evidence_v8_7.json"

PDF_BY_STANDARD = {
    "GB 13457-2025": {
        "file": "GB_13457-2025_slaughter_meat_water_pollutants.pdf",
        "official_pdf_url": "https://www.mee.gov.cn/ywgz/fgbz/bz/bzwb/shjbh/swrwpfbz/202512/W020251205581800287905.pdf",
        "expected_terms": ["GB 13457", "屠宰及肉类加工工业", "代替GB 13457", "表1", "表2"],
    },
    "HJ 5.2-2026": {
        "file": "HJ_5_2-2026_near_surface_radioactive_solid_waste_eia.pdf",
        "official_pdf_url": "https://www.mee.gov.cn/ywgz/fgbz/bz/bzwb/hxxhj/xgbz/202602/W020260209504622239576.pdf",
        "expected_terms": ["HJ 5.2", "放射性固体废物近地表处置", "代替 HJ/T 5.2", "附录A", "表"],
    },
    "GB 15848-2009": {
        "file": "GB_15848-2009_uranium_exploration_radiation_environment.pdf",
        "official_pdf_url": "https://nnsa.mee.gov.cn/ztzl/fgbzwjk/bz/fshjxl/202303/P020230331581060889322.pdf?keywords=",
        "expected_terms": ["GB 15848", "铀矿地质勘查", "代替GB 15848", "表1", "附录A"],
    },
}

FIELDS = [
    "replacement_standard_no",
    "obsolete_source_id",
    "obsolete_standard_no",
    "replacement_standard_title",
    "replacement_lifecycle_status",
    "replacement_effective_date",
    "official_pdf_url",
    "local_snapshot_path",
    "local_snapshot_sha256",
    "local_snapshot_size_bytes",
    "page_count",
    "text_extraction_method",
    "extracted_text_chars",
    "expected_term_hits",
    "replacement_clause_evidence",
    "scope_evidence",
    "table_evidence_status",
    "table_candidate_pages",
    "extraction_rule_reuse_status",
    "reusable_limit_fieldset",
    "ocr_status",
    "human_review_status",
    "standard_limit_profile_adapter_status",
    "runtime_promotion_readiness",
    "runtime_promotion_blockers",
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


def normalized_text(value):
    return re.sub(r"\s+", "", value or "")


def extract_pdf(path):
    doc = fitz.open(path)
    page_texts = []
    for page in doc:
        page_texts.append(page.get_text("text"))
    text = "\n".join(page_texts)
    return doc.page_count, page_texts, text


def first_match(text, patterns):
    squashed = normalized_text(text)
    for pattern in patterns:
        match = re.search(pattern, squashed)
        if match:
            start = max(match.start() - 45, 0)
            end = min(match.end() + 90, len(squashed))
            return squashed[start:end]
    return ""


def table_candidate_pages(page_texts):
    pages = []
    for index, text in enumerate(page_texts, start=1):
        squashed = normalized_text(text)
        if re.search(r"表[0-9A-Za-z.．]*", squashed) and re.search(r"mg/L|mSv|Bq|限值|要求|项目|内容|格式", squashed):
            pages.append(str(index))
    return pages


def build_rows():
    source_rows = [
        row for row in read_csv(SOURCE_RECOVERY)
        if row.get("recovery_action") == "OBSOLETE_EXCLUDE_REPLACEMENT_GOVERNANCE"
    ]
    rows = []
    for source in sorted(source_rows, key=lambda item: item["replacement_standard_no"]):
        standard_no = source["replacement_standard_no"]
        pdf_meta = PDF_BY_STANDARD[standard_no]
        snapshot = SNAPSHOT_DIR / pdf_meta["file"]
        if not snapshot.exists():
            raise FileNotFoundError(snapshot)
        page_count, page_texts, text = extract_pdf(snapshot)
        expected_hits = [term for term in pdf_meta["expected_terms"] if normalized_text(term) in normalized_text(text)]
        replacement_evidence = first_match(text, [r"代替[^。；;]{0,35}", r"同时废止[^。；;]{0,45}"])
        scope_evidence = first_match(text, [r"本标准规定[^。；;]{0,85}", r"本标准适用于[^。；;]{0,100}"])
        table_pages = table_candidate_pages(page_texts)
        table_status = "TEXT_TABLE_CANDIDATES_IDENTIFIED_NOT_NUMERIC_ADOPTED" if table_pages else "NO_TABLE_CANDIDATE_FOUND"
        text_chars = len(normalized_text(text))
        rows.append({
            "replacement_standard_no": standard_no,
            "obsolete_source_id": source["source_id"],
            "obsolete_standard_no": source["canonical_standard_no"],
            "replacement_standard_title": source["replacement_standard_title"],
            "replacement_lifecycle_status": source["replacement_lifecycle_status"],
            "replacement_effective_date": source["replacement_effective_date"],
            "official_pdf_url": pdf_meta["official_pdf_url"],
            "local_snapshot_path": str(snapshot.relative_to(ROOT)).replace("\\", "/"),
            "local_snapshot_sha256": sha256_file(snapshot),
            "local_snapshot_size_bytes": str(snapshot.stat().st_size),
            "page_count": str(page_count),
            "text_extraction_method": "PyMuPDF.get_text",
            "extracted_text_chars": str(text_chars),
            "expected_term_hits": ";".join(expected_hits),
            "replacement_clause_evidence": replacement_evidence,
            "scope_evidence": scope_evidence,
            "table_evidence_status": table_status,
            "table_candidate_pages": ";".join(table_pages),
            "extraction_rule_reuse_status": "REUSE_EXISTING_THRESHOLD_FIELD_GOVERNANCE_NEEDS_STANDARD_LIMIT_PROFILE_ADAPTER",
            "reusable_limit_fieldset": "metric;operator;value;unit;lower_value;lower_unit;lower_inclusive;upper_value;upper_unit;upper_inclusive;equivalent_value;equivalent_unit;raw_fragment;source_page;governance_status",
            "ocr_status": "NATIVE_TEXT_EXTRACTED_NO_OCR_REQUIRED" if text_chars >= 1000 else "OCR_REQUIRED",
            "human_review_status": HUMAN_REVIEW_STATUS,
            "standard_limit_profile_adapter_status": "APPLIED_AND_RUNTIME_IMPORT_CONTRACT_APPROVED_IN_pollutant_standard_limit_runtime_import_v8_7",
            "runtime_promotion_readiness": "APPROVED_FOR_IMPORT_PENDING_TESTS" if text_chars >= 1000 and table_pages else "NOT_READY",
            "runtime_promotion_blockers": "downstream_ecocheck_import_execution_not_in_this_package;runtime_tests_required",
            "final_state": FINAL_STATE,
            "runtime_status": RUNTIME_STATUS,
            "runtime_integration": RUNTIME_INTEGRATION,
            "candidate_only": "TRUE",
        })
    return rows


def main():
    rows = build_rows()
    write_csv(OUT_CSV, rows)
    write_json(OUT_JSON, rows)
    report = {
        "schema_version": "pollutant-standard-replacement-source-evidence.v8_7",
        "final_state": FINAL_STATE,
        "runtime_status": RUNTIME_STATUS,
        "runtime_integration": RUNTIME_INTEGRATION,
        "row_count": len(rows),
        "replacement_standards": [row["replacement_standard_no"] for row in rows],
        "ocr_status_counts": dict(sorted(Counter(row["ocr_status"] for row in rows).items())),
        "table_evidence_status_counts": dict(sorted(Counter(row["table_evidence_status"] for row in rows).items())),
        "extraction_rule_reuse_status_counts": dict(sorted(Counter(row["extraction_rule_reuse_status"] for row in rows).items())),
        "standard_limit_profile_adapter_status_counts": dict(sorted(Counter(row["standard_limit_profile_adapter_status"] for row in rows).items())),
        "runtime_promotion_readiness_counts": dict(sorted(Counter(row["runtime_promotion_readiness"] for row in rows).items())),
        "outputs": {
            "evidence_csv": {"path": str(OUT_CSV.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256_file(OUT_CSV)},
            "evidence_json": {"path": str(OUT_JSON.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256_file(OUT_JSON)},
        },
    }
    write_json(OUT_REPORT, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
