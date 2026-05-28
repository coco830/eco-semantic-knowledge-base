import csv
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PDF_PATH = ROOT / "固定污染源排污许可分类管理名录(2019年版).pdf"


def require_fitz():
    try:
        import fitz  # type: ignore
    except Exception as exc:  # pragma: no cover - environment guard
        raise SystemExit(
            "PyMuPDF/fitz is required for table-cell extraction. "
            "Run with the Python environment that has PyMuPDF installed. "
            f"Original error: {exc}"
        )
    return fitz


def normalize(text):
    if text is None:
        return ""
    text = str(text).replace("\r", "\n")
    text = re.sub(r"[ \t]*\n[ \t]*", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def one_line(text):
    return re.sub(r"\s+", " ", text or "").strip()


def bbox_to_json(value):
    try:
        return json.dumps([round(float(x), 2) for x in value], ensure_ascii=False)
    except Exception:
        return json.dumps([], ensure_ascii=False)


def extract_rows():
    fitz = require_fitz()
    doc = fitz.open(PDF_PATH)
    entries = []
    current_major = ""
    page_table_counts = {}

    for page_index in range(3, 20):  # PDF pages 4-20 are the table body.
        page = doc[page_index]
        tables = page.find_tables()
        page_table_counts[page_index + 1] = len(tables.tables)
        if len(tables.tables) != 1:
            raise RuntimeError(f"Expected 1 table on page {page_index + 1}, got {len(tables.tables)}")
        table = tables.tables[0]
        extracted = table.extract()
        row_cells = getattr(table, "cells", None)

        for row_index, raw_row in enumerate(extracted):
            cells = [normalize(c) for c in raw_row]
            if len(cells) != 5:
                raise RuntimeError(f"Expected 5 cells on page {page_index + 1} row {row_index}, got {len(cells)}")
            if cells == ["序号", "行业类别", "重点管理", "简化管理", "登记管理"]:
                continue

            seq = one_line(cells[0])
            industry = cells[1]
            if not re.fullmatch(r"\d{1,3}", seq):
                title_text = one_line(" ".join(c for c in cells if c))
                if re.match(r"^[一二三四五六七八九十]+、", title_text):
                    current_major = title_text
                continue

            industry_codes = sorted(set(re.findall(r"(?<!\d)(\d{2,4})(?!\d)", cells[1])))
            code_text = " ".join(cells[1:])
            condition_code_like_tokens = sorted(set(re.findall(r"(?<!\d)(\d{2,4})(?!\d)", " ".join(cells[2:]))))
            notes = []
            if "﹡" in code_text:
                notes.append("has_asterisk_footnote_industrial_building_condition")
            if "涉及通用工序" in code_text:
                notes.append("references_general_process_109_112")
            if "纳入重点排污单位名录" in code_text:
                notes.append("references_dynamic_key_pollutant_unit_list")
            if "其他" in cells[4]:
                notes.append("registration_else_condition")

            cell_bboxes = []
            if row_cells:
                start = row_index * 5
                maybe = row_cells[start:start + 5]
                if len(maybe) == 5:
                    cell_bboxes = [list(c) if c else [] for c in maybe]

            entries.append({
                "catalog_version": "2019",
                "catalog_entry_no": int(seq),
                "major_category_text": current_major,
                "industry_category_text": industry,
                "gb_code_fragments": ";".join(industry_codes),
                "condition_code_fragments": ";".join(condition_code_like_tokens),
                "key_management_condition": cells[2],
                "simplified_management_condition": cells[3],
                "registration_management_condition": cells[4],
                "source_pdf": PDF_PATH.name,
                "source_page": page_index + 1,
                "source_row_index": row_index,
                "table_bbox": bbox_to_json(table.bbox),
                "row_cells_bbox": json.dumps(cell_bboxes, ensure_ascii=False),
                "extraction_method": "pymupdf_find_tables",
                "extraction_confidence": "HIGH",
                "audit_status": "RAW_CONDITION_EXTRACTED_NOT_RUNTIME",
                "notes": ";".join(notes),
            })

    return entries, page_table_counts


def validate(entries, page_table_counts):
    seqs = [e["catalog_entry_no"] for e in entries]
    expected = set(range(1, 113))
    actual = set(seqs)
    missing = sorted(expected - actual)
    duplicate = sorted(k for k in actual if seqs.count(k) > 1)
    errors = []
    if len(entries) != 112:
        errors.append(f"expected 112 entries, got {len(entries)}")
    if missing:
        errors.append(f"missing entries: {missing}")
    if duplicate:
        errors.append(f"duplicate entries: {duplicate}")
    if min(seqs or [0]) != 1 or max(seqs or [0]) != 112:
        errors.append("entry range is not 1-112")
    bad_pages = {p: c for p, c in page_table_counts.items() if c != 1}
    if bad_pages:
        errors.append(f"pages without exactly one table: {bad_pages}")
    for e in entries:
        for key in ["industry_category_text", "key_management_condition", "simplified_management_condition", "registration_management_condition"]:
            if e[key] == "":
                # Empty condition cells are represented by "/" in this PDF; true empties are suspicious.
                errors.append(f"entry {e['catalog_entry_no']} has empty {key}")
                break
    return {
        "entry_count": len(entries),
        "unique_entry_count": len(actual),
        "min_entry_no": min(seqs or [None]),
        "max_entry_no": max(seqs or [None]),
        "missing_entry_nos": missing,
        "duplicate_entry_nos": duplicate,
        "page_table_counts": page_table_counts,
        "runtime_status": "NOT_FOR_RUNTIME_RAW_AUDIT_ONLY",
        "validation_status": "PASS" if not errors else "FAIL",
        "errors": errors,
    }


def write_csv(path, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main():
    entries, page_table_counts = extract_rows()
    validation = validate(entries, page_table_counts)
    if validation["validation_status"] != "PASS":
        print(json.dumps(validation, ensure_ascii=False, indent=2))
        raise SystemExit(1)

    (ROOT / "permit_management_catalog_table_cells.json").write_text(
        json.dumps(entries, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_csv(ROOT / "permit_management_catalog_table_cells.csv", entries)
    (ROOT / "permit_management_catalog_table_cells_validation.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (ROOT / "permit_management_catalog_table_cells_README.md").write_text(
        "# 排污许可名录表格级抽取中间表\n\n"
        "本产物由 PyMuPDF `page.find_tables()` 从 `固定污染源排污许可分类管理名录(2019年版).pdf` 第 4-20 页抽取。"
        "它是审计型中间层，不是运行时规则库。\n\n"
        "## 验证门\n\n"
        "- `catalog_entry_no` 覆盖 1-112，连续无缺号。\n"
        "- 第 4-20 页每页识别 1 张 5 列表格。\n"
        "- 三类管理条件保留 PDF 原文，不做激进语义拆分。\n\n"
        "## 禁止用途\n\n"
        "- 不得直接从本表生成 `permit_type`。\n"
        "- 不得直接接入 EcoCheck 小程序或正式检查模板。\n"
        "- 阈值、星号、通用工序、重点排污单位名录等条件必须二次规则化和人工抽检后才能进入正式规则。\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
