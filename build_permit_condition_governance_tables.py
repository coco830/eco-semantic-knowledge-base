import csv
import json
from pathlib import Path
from kb_paths import artifact_path


ROOT = Path(__file__).resolve().parent
NORMALIZED = artifact_path("permit_condition_normalization_draft.csv")
INDUSTRY_CATALOG = artifact_path("industry_catalog_base.csv")


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fieldnames):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_industry_code_index():
    rows = read_csv(INDUSTRY_CATALOG)
    index = {}
    for row in rows:
        if row["level"] == "division":
            index[row["division_code"]] = {
                "code_level": "division",
                "industry_name": row["division_name"],
            }
        elif row["level"] == "group":
            index[row["group_code"]] = {
                "code_level": "group",
                "industry_name": row["group_name"],
            }
        elif row["level"] == "class":
            index[row["class_code"]] = {
                "code_level": "class",
                "industry_name": row["class_name"],
            }
    return index


def review_status_for_code(token, match):
    if not match:
        return "NEED_CONFIRM_NOT_IN_GB4754_BASE"
    if match["code_level"] == "class":
        return "LIKELY_CLASS_CODE_NEED_SCOPE_CONFIRM"
    if match["code_level"] == "group":
        return "LIKELY_GROUP_CODE_NEED_SCOPE_CONFIRM"
    return "LIKELY_DIVISION_CODE_NEED_SCOPE_CONFIRM"


def threshold_review_status(predicate):
    if predicate.get("metric_inference") == "INHERITED_FROM_LEFT_CONTEXT":
        return "DRAFT_INHERITED_METRIC_NEED_CONFIRM"
    metric = predicate.get("metric", "")
    units = {
        predicate.get("unit", ""),
        predicate.get("lower_unit", ""),
        predicate.get("upper_unit", ""),
        predicate.get("equivalent_unit", ""),
    }
    if metric in {"threshold_metric", "capacity"} or "UNKNOWN" in units:
        return "NEED_HUMAN_METRIC_OR_UNIT_CONFIRM"
    if predicate.get("predicate_type") == "threshold_range":
        return "DRAFT_RANGE_PREDICATE_NEED_BOUNDARY_CONFIRM"
    return "DRAFT_THRESHOLD_PREDICATE_NEED_SOURCE_CONFIRM"


def threshold_values(predicate):
    if predicate.get("predicate_type") == "threshold_range":
        return {
            "value": "",
            "unit": "",
            "lower_value": predicate.get("lower_value", ""),
            "lower_unit": predicate.get("lower_unit", ""),
            "lower_inclusive": predicate.get("lower_inclusive", ""),
            "upper_value": predicate.get("upper_value", ""),
            "upper_unit": predicate.get("upper_unit", ""),
            "upper_inclusive": predicate.get("upper_inclusive", ""),
            "equivalent_value": "",
            "equivalent_unit": "",
        }
    return {
        "value": predicate.get("value", ""),
        "unit": predicate.get("unit", ""),
        "lower_value": "",
        "lower_unit": "",
        "lower_inclusive": "",
        "upper_value": "",
        "upper_unit": "",
        "upper_inclusive": "",
        "equivalent_value": predicate.get("equivalent_value", ""),
        "equivalent_unit": predicate.get("equivalent_unit", ""),
    }


def build_tables():
    normalized_rows = read_csv(NORMALIZED)
    industry_index = load_industry_code_index()
    code_rows = []
    threshold_rows = []
    inherited_rows = []

    for row in normalized_rows:
        predicates = json.loads(row["normalized_predicates_json"])
        for predicate in predicates:
            if (
                predicate.get("predicate_type") == "numeric_condition_token"
                and predicate.get("token_class") == "industry_code_reference_candidate"
            ):
                token = predicate["token"]
                match = industry_index.get(token)
                code_rows.append({
                    "catalog_entry_no": row["catalog_entry_no"],
                    "major_category_text": row["major_category_text"],
                    "industry_category_text": row["industry_category_text"],
                    "gb_code_fragments": row["gb_code_fragments"],
                    "target_management": row["target_management"],
                    "candidate_code": token,
                    "candidate_code_level": match["code_level"] if match else "UNKNOWN",
                    "matched_industry_name": match["industry_name"] if match else "",
                    "raw_fragment": predicate.get("raw_fragment", ""),
                    "raw_condition": row["raw_condition"],
                    "review_status": review_status_for_code(token, match),
                    "review_question": "该数字是否为名录条件中的行业代码范围/例外项，而不是规模阈值或脚注编号？",
                    "source_basis": "permit_management_catalog_table_cells.csv -> permit_condition_normalization_draft.csv; industry_catalog_base.csv GB/T 4754 base",
                    "confidence": predicate.get("confidence", "LOW"),
                    "runtime_status": "DRAFT_NOT_FOR_RUNTIME",
                    "source_page": row["source_page"],
                })
            elif predicate.get("predicate_type", "").startswith("threshold"):
                values = threshold_values(predicate)
                threshold_rows.append({
                    "catalog_entry_no": row["catalog_entry_no"],
                    "major_category_text": row["major_category_text"],
                    "industry_category_text": row["industry_category_text"],
                    "gb_code_fragments": row["gb_code_fragments"],
                    "target_management": row["target_management"],
                    "predicate_type": predicate.get("predicate_type", ""),
                    "metric": predicate.get("metric", ""),
                    "operator": predicate.get("operator", ""),
                    **values,
                    "metric_source_keyword": predicate.get("metric_source_keyword", ""),
                    "metric_inference": predicate.get("metric_inference", ""),
                    "raw_fragment": predicate.get("raw_fragment", ""),
                    "raw_condition": row["raw_condition"],
                    "governance_status": threshold_review_status(predicate),
                    "review_question": "请用名录原文、企业证照/许可或产能证明确认该阈值指标、单位、边界是否准确。",
                    "source_basis": "permit_management_catalog_table_cells.csv -> permit_condition_normalization_draft.csv",
                    "confidence": predicate.get("confidence", "MEDIUM"),
                    "runtime_status": "DRAFT_NOT_FOR_RUNTIME",
                    "source_page": row["source_page"],
                })
                if predicate.get("metric_inference") == "INHERITED_FROM_LEFT_CONTEXT":
                    inherited_rows.append({
                        "catalog_entry_no": row["catalog_entry_no"],
                        "major_category_text": row["major_category_text"],
                        "industry_category_text": row["industry_category_text"],
                        "gb_code_fragments": row["gb_code_fragments"],
                        "target_management": row["target_management"],
                        "metric": predicate.get("metric", ""),
                        "metric_source_keyword": predicate.get("metric_source_keyword", ""),
                        "operator": predicate.get("operator", ""),
                        **values,
                        "raw_fragment": predicate.get("raw_fragment", ""),
                        "raw_condition": row["raw_condition"],
                        "inheritance_rule": "并列物料阈值继承左侧最近的年加工能力/年使用/年产等指标词",
                        "review_question": "该阈值是否确实继承左侧指标词，且适用于其后的物料/工序对象？",
                        "source_basis": "permit_management_catalog_table_cells.csv -> permit_condition_normalization_draft.csv",
                        "confidence": "LOW",
                        "runtime_status": "DRAFT_NOT_FOR_RUNTIME",
                        "source_page": row["source_page"],
                    })

    return code_rows, threshold_rows, inherited_rows


def summarize(code_rows, threshold_rows, inherited_rows):
    def counts(rows, key):
        result = {}
        for row in rows:
            result[row[key]] = result.get(row[key], 0) + 1
        return dict(sorted(result.items()))

    errors = []
    if not code_rows:
        errors.append("industry code review table is empty")
    if not threshold_rows:
        errors.append("threshold governance table is empty")
    if any(row["runtime_status"] != "DRAFT_NOT_FOR_RUNTIME" for row in code_rows + threshold_rows + inherited_rows):
        errors.append("unexpected runtime status")

    return {
        "industry_code_reference_review_count": len(code_rows),
        "threshold_predicate_governance_count": len(threshold_rows),
        "parallel_material_threshold_inheritance_count": len(inherited_rows),
        "candidate_code_level_counts": counts(code_rows, "candidate_code_level"),
        "code_review_status_counts": counts(code_rows, "review_status"),
        "threshold_metric_counts": counts(threshold_rows, "metric"),
        "threshold_governance_status_counts": counts(threshold_rows, "governance_status"),
        "runtime_status": "DRAFT_NOT_FOR_RUNTIME",
        "validation_status": "PASS" if not errors else "FAIL",
        "errors": errors,
    }


def main():
    code_rows, threshold_rows, inherited_rows = build_tables()
    code_fields = [
        "catalog_entry_no",
        "major_category_text",
        "industry_category_text",
        "gb_code_fragments",
        "target_management",
        "candidate_code",
        "candidate_code_level",
        "matched_industry_name",
        "raw_fragment",
        "raw_condition",
        "review_status",
        "review_question",
        "source_basis",
        "confidence",
        "runtime_status",
        "source_page",
    ]
    threshold_fields = [
        "catalog_entry_no",
        "major_category_text",
        "industry_category_text",
        "gb_code_fragments",
        "target_management",
        "predicate_type",
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
        "metric_source_keyword",
        "metric_inference",
        "raw_fragment",
        "raw_condition",
        "governance_status",
        "review_question",
        "source_basis",
        "confidence",
        "runtime_status",
        "source_page",
    ]
    inherited_fields = [
        "catalog_entry_no",
        "major_category_text",
        "industry_category_text",
        "gb_code_fragments",
        "target_management",
        "metric",
        "metric_source_keyword",
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
        "raw_fragment",
        "raw_condition",
        "inheritance_rule",
        "review_question",
        "source_basis",
        "confidence",
        "runtime_status",
        "source_page",
    ]
    write_csv(artifact_path("permit_industry_code_reference_review.csv"), code_rows, code_fields)
    write_csv(artifact_path("permit_threshold_predicate_governance.csv"), threshold_rows, threshold_fields)
    write_csv(artifact_path("permit_parallel_material_threshold_inheritance_review.csv"), inherited_rows, inherited_fields)
    (artifact_path("permit_industry_code_reference_review.json")).write_text(
        json.dumps(code_rows, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (artifact_path("permit_threshold_predicate_governance.json")).write_text(
        json.dumps(threshold_rows, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (artifact_path("permit_parallel_material_threshold_inheritance_review.json")).write_text(
        json.dumps(inherited_rows, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    validation = summarize(code_rows, threshold_rows, inherited_rows)
    (artifact_path("permit_condition_governance_validation.json")).write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (artifact_path("permit_condition_governance_README.md")).write_text(
        "# 排污许可条件治理台账\n\n"
        "本批文件从 `permit_condition_normalization_draft.csv` 派生，用于把二次规则化结果拆成两类可审计台账。\n\n"
        "## 文件\n\n"
        "- `permit_industry_code_reference_review.csv/json`：只收 `industry_code_reference_candidate`，用于复核名录条件中的行业代码引用、例外和范围。\n"
        "- `permit_threshold_predicate_governance.csv/json`：只收 `threshold` / `threshold_range`，用于治理阈值指标、单位、上下界和证据口径。\n"
        "- `permit_parallel_material_threshold_inheritance_review.csv/json`：只收同句并列物料阈值继承草案，必须人工确认。\n"
        "- `permit_condition_governance_validation.json`：生成与计数校验。\n\n"
        "## 边界\n\n"
        "- 所有行均为 `DRAFT_NOT_FOR_RUNTIME`。\n"
        "- 这些文件不生成正式 `permit_type`，不接入 EcoCheck 小程序，不生成正式检查模板。\n"
        "- `review_status` / `governance_status` 是人工复核路由，不是法规结论。\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
