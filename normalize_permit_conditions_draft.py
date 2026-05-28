import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "permit_management_catalog_table_cells.csv"


CN_NUM = {
    "一": 1,
    "二": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
    "十": 10,
}


METRIC_KEYWORDS = [
    ("床位", "bed_count", "bed"),
    ("年屠宰生猪", "annual_slaughter_pig", "head_per_year"),
    ("年屠宰肉牛", "annual_slaughter_cattle", "head_per_year"),
    ("年屠宰肉羊", "annual_slaughter_sheep", "head_per_year"),
    ("年屠宰禽类", "annual_slaughter_poultry", "head_per_year"),
    ("年加工肉禽类", "annual_meat_poultry_processing", "ton_per_year"),
    ("日处理能力", "daily_treatment_capacity", "ton_per_day"),
    ("日加工糖料能力", "daily_sugar_processing_capacity", "ton_per_day"),
    ("日转运能力", "daily_transfer_capacity", "ton_per_day"),
    ("单台或者合计出力", "boiler_capacity_single_or_total", "ton_per_hour"),
    ("单台且合计出力", "boiler_capacity_single_and_total", "ton_per_hour"),
    ("年加工能力", "annual_processing_capacity", "ton_per_year"),
    ("年使用", "annual_material_use", "ton_per_year"),
    ("年产", "annual_output", "ton_per_year"),
    ("年生产能力", "annual_production_capacity", "kiloliter_per_year"),
    ("年加工", "annual_processing_capacity", "ton_per_year"),
    ("年耗胶量", "annual_rubber_consumption", "ton_per_year"),
    ("总容量", "storage_total_capacity", "cubic_meter"),
    ("单个泊位", "single_berth_tonnage", "tonnage_class"),
    ("营业面积", "business_area", "square_meter"),
]


FLAG_PATTERNS = [
    ("纳入重点排污单位名录", "dynamic_key_pollutant_unit_list"),
    ("涉及通用工序重点管理", "general_process_key_management"),
    ("涉及通用工序简化管理", "general_process_simplified_management"),
    ("涉及通用工序登记管理", "general_process_registration_management"),
    ("涉及通用工序", "references_general_process_109_112"),
    ("其他", "else_condition"),
    ("﹡", "industrial_building_footnote"),
    ("单纯混合或者分装", "simple_mixing_or_packaging"),
    ("不含单纯混合或者分装", "excludes_simple_mixing_or_packaging"),
    ("工业废水", "industrial_wastewater_condition"),
    ("废气", "exhaust_condition"),
    ("有发酵工艺", "fermentation_process"),
    ("无发酵工艺", "no_fermentation_process"),
    ("有电镀工序", "electroplating_process"),
    ("酸洗", "pickling_process"),
    ("抛光", "polishing_process"),
    ("热浸镀", "hot_dip_plating_process"),
    ("淬火", "quenching_process"),
    ("钝化", "passivation_process"),
    ("有水洗工序", "washing_process"),
    ("无水洗工序", "no_washing_process"),
    ("有鞣制工序", "tanning_process"),
    ("无鞣制工序", "no_tanning_process"),
    ("有前处理", "pretreatment_process"),
    ("染色", "dyeing_process"),
    ("印花", "printing_process"),
    ("洗毛", "wool_washing_process"),
    ("麻脱胶", "hemp_degumming_process"),
    ("缫丝", "silk_reeling_process"),
    ("喷水织造", "water_jet_weaving_process"),
]


UNIT_MULTIPLIERS = {
    "万头": 10000,
    "万只": 10000,
    "万吨": 10000,
    "万立方米": 10000,
    "万件": 10000,
    "万吨级": 10000,
    "吨": 1,
    "吨级": 1,
    "平方米": 1,
    "千升": 1,
    "张": 1,
    "兆瓦": 1,
}


def clean(text):
    return re.sub(r"\s+", "", text or "")


def normalize_raw(text):
    return re.sub(r"\s+", " ", text or "").strip()


def classify_applies(raw):
    compact = clean(raw)
    if compact == "/":
        return "NOT_APPLICABLE_IN_CATALOG"
    if "其他" in compact:
        return "ELSE_CONDITION"
    return "APPLIES_IF_CONDITION_MET"


def detect_metric(prefix):
    for keyword, metric, default_unit in METRIC_KEYWORDS:
        if keyword in prefix:
            return metric, default_unit, keyword, "DIRECT_PREFIX"
    if "能力" in prefix:
        return "capacity", "UNKNOWN", "能力", "DIRECT_PREFIX"
    return "threshold_metric", "UNKNOWN", "", "UNKNOWN"


def inherit_metric_from_left_context(compact, start):
    left_context = compact[:start]
    best = None
    for keyword, metric, default_unit in METRIC_KEYWORDS:
        pos = left_context.rfind(keyword)
        if pos >= 0 and (best is None or pos > best["pos"]):
            best = {
                "pos": pos,
                "keyword": keyword,
                "metric": metric,
                "default_unit": default_unit,
            }
    if not best:
        return "threshold_metric", "UNKNOWN", "", "UNKNOWN"
    return best["metric"], best["default_unit"], best["keyword"], "INHERITED_FROM_LEFT_CONTEXT"


def normalize_number(value, unit):
    number = float(value)
    multiplier = UNIT_MULTIPLIERS.get(unit, 1)
    normalized = number * multiplier
    if normalized.is_integer():
        normalized = int(normalized)
    return normalized


def resolved_unit(default_unit, matched_unit):
    unit_map = {
        "万立方米": "cubic_meter_per_year" if default_unit.endswith("_per_year") else "cubic_meter",
        "万件": "piece_per_year" if default_unit.endswith("_per_year") else "piece",
        "万吨级": "tonnage_class",
        "吨级": "tonnage_class",
        "平方米": "square_meter",
        "万吨": "ton_per_year" if default_unit.endswith("_per_year") else "ton",
        "吨": default_unit if default_unit != "UNKNOWN" else "ton",
        "万头": default_unit if default_unit != "UNKNOWN" else "head",
        "万只": default_unit if default_unit != "UNKNOWN" else "head",
        "千升": default_unit if default_unit != "UNKNOWN" else "kiloliter",
        "张": default_unit if default_unit != "UNKNOWN" else "bed",
        "兆瓦": "megawatt",
    }
    return unit_map.get(matched_unit, default_unit if default_unit != "UNKNOWN" else matched_unit)


def parse_threshold_operator(op_text):
    if op_text in {"及以上", "以上"}:
        return "gte", op_text == "及以上"
    if op_text in {"及以下", "以下"}:
        return "lte" if op_text == "及以下" else "lt", op_text == "及以下"
    return "UNKNOWN", False


def threshold_predicates(compact, target_management):
    predicates = []

    # Boiler entries use paired capacity units such as 20吨/小时（14兆瓦）及以上.
    boiler_pattern = re.compile(
        r"(?P<prefix>[^，、；。]*?)(?P<ton_value>\d+(?:\.\d+)?)吨/小时"
        r"（(?P<mw_value>\d+(?:\.\d+)?)兆瓦）(?P<op>及以上|以上|及以下|以下)"
    )
    for match in boiler_pattern.finditer(compact):
        metric, _default_unit, source_keyword, metric_inference = detect_metric(match.group("prefix"))
        op_text = match.group("op")
        operator, inclusive = parse_threshold_operator(op_text)
        predicates.append({
            "predicate_type": "threshold",
            "metric": metric,
            "operator": operator,
            "value": normalize_number(match.group("ton_value"), "吨"),
            "unit": "ton_per_hour",
            "equivalent_value": normalize_number(match.group("mw_value"), "兆瓦"),
            "equivalent_unit": "megawatt",
            "inclusive": inclusive,
            "target_management": target_management,
            "raw_fragment": match.group(0),
            "metric_source_keyword": source_keyword,
            "metric_inference": metric_inference,
            "confidence": "MEDIUM",
        })

    # Range pattern, e.g. 年屠宰生猪2万头及以上10万头以下
    unit_pattern = r"万立方米|万头|万只|万吨级|万吨|万件|吨级|吨|平方米|千升|张|兆瓦"
    range_pattern = re.compile(
        rf"(?P<prefix>[^，、；。]*?)(?P<lower>\d+(?:\.\d+)?)(?P<lower_unit>{unit_pattern})"
        rf"及以上(?P<upper>\d+(?:\.\d+)?)(?P<upper_unit>{unit_pattern})以下"
    )
    for match in range_pattern.finditer(compact):
        metric, default_unit, source_keyword, metric_inference = detect_metric(match.group("prefix"))
        if metric == "threshold_metric":
            metric, default_unit, source_keyword, metric_inference = inherit_metric_from_left_context(compact, match.start())
        lower_unit = match.group("lower_unit")
        upper_unit = match.group("upper_unit")
        predicates.append({
            "predicate_type": "threshold_range",
            "metric": metric,
            "operator": "gte_and_lt",
            "lower_value": normalize_number(match.group("lower"), lower_unit),
            "lower_unit": resolved_unit(default_unit, lower_unit),
            "lower_inclusive": True,
            "upper_value": normalize_number(match.group("upper"), upper_unit),
            "upper_unit": resolved_unit(default_unit, upper_unit),
            "upper_inclusive": False,
            "target_management": target_management,
            "raw_fragment": match.group(0),
            "metric_source_keyword": source_keyword,
            "metric_inference": metric_inference,
            "confidence": "MEDIUM",
        })

    # Single threshold patterns.
    single_pattern = re.compile(
        rf"(?P<prefix>[^，、；。]*?)(?P<value>\d+(?:\.\d+)?)(?P<unit>{unit_pattern})(?P<op>及以上|以上|及以下|以下)"
    )
    for match in single_pattern.finditer(compact):
        raw_fragment = match.group(0)
        if any(raw_fragment in p.get("raw_fragment", "") for p in predicates):
            continue
        metric, default_unit, source_keyword, metric_inference = detect_metric(match.group("prefix"))
        if metric == "threshold_metric":
            metric, default_unit, source_keyword, metric_inference = inherit_metric_from_left_context(compact, match.start())
        op_text = match.group("op")
        operator, inclusive = parse_threshold_operator(op_text)
        predicates.append({
            "predicate_type": "threshold",
            "metric": metric,
            "operator": operator,
            "value": normalize_number(match.group("value"), match.group("unit")),
            "unit": resolved_unit(default_unit, match.group("unit")),
            "inclusive": inclusive,
            "target_management": target_management,
            "raw_fragment": raw_fragment,
            "metric_source_keyword": source_keyword,
            "metric_inference": metric_inference,
            "confidence": "MEDIUM",
        })

    return predicates


def process_predicates(compact, target_management):
    predicates = []
    for keyword, flag in FLAG_PATTERNS:
        if keyword in compact:
            predicates.append({
                "predicate_type": "process_or_flag",
                "flag": flag,
                "operator": "present",
                "target_management": target_management,
                "raw_fragment": keyword,
                "confidence": "MEDIUM" if flag not in {"else_condition", "references_general_process_109_112"} else "HIGH",
            })
    return predicates


NUMERIC_TOKEN_PATTERN = re.compile(r"\d+(?:\.\d+)?")


def threshold_token_values(predicates):
    tokens = set()
    for predicate in predicates:
        if not predicate["predicate_type"].startswith("threshold"):
            continue
        raw_fragment = predicate.get("raw_fragment", "")
        tokens.update(NUMERIC_TOKEN_PATTERN.findall(raw_fragment))
    return tokens


def classify_numeric_token(compact, match, covered_threshold_tokens):
    token = match.group(0)
    start, end = match.span()
    before = compact[max(0, start - 8):start]
    after = compact[end:end + 8]
    context = before + token + after

    if token in covered_threshold_tokens:
        return "threshold_or_capacity_number", "covered_by_threshold_predicate", "HIGH"
    if re.match(r"(万立方米|万头|万只|万吨级|万吨|万件|吨/小时|吨级|吨|平方米|千升|张|兆瓦|床位|头|只|小时|日)", after):
        return "capacity_or_threshold_number", "requires_threshold_parser_review", "MEDIUM"
    if re.search(r"(年屠宰|年加工|年使用|年产|年生产能力|日处理能力|单台|合计出力|床位)$", before):
        return "capacity_or_threshold_number", "requires_threshold_parser_review", "MEDIUM"
    if len(token.replace(".", "")) in {3, 4} and "." not in token:
        return "industry_code_reference_candidate", "review_industry_code_scope", "LOW"
    return "unclassified_numeric_token", "review_numeric_context", "LOW"


def numeric_token_predicates(compact, target_management, covered_threshold_tokens):
    predicates = []
    seen = set()
    for match in NUMERIC_TOKEN_PATTERN.finditer(compact):
        token = match.group(0)
        if (token, match.start()) in seen:
            continue
        seen.add((token, match.start()))
        token_class, operator, confidence = classify_numeric_token(compact, match, covered_threshold_tokens)
        predicates.append({
            "predicate_type": "numeric_condition_token",
            "token": token,
            "token_class": token_class,
            "operator": operator,
            "target_management": target_management,
            "confidence": confidence,
            "raw_fragment": compact[max(0, match.start() - 8): min(len(compact), match.end() + 8)],
        })
    return predicates


def build_confirmation_questions(raw, predicates, target_management):
    compact = clean(raw)
    questions = []
    if compact == "/":
        return questions
    if "纳入重点排污单位名录" in compact:
        questions.append("是否被纳入重点排污单位名录？")
    if "涉及通用工序" in compact:
        questions.append("是否涉及名录第109-112类通用工序，且对应通用工序管理类别是什么？")
    if "其他" in compact:
        questions.append("是否不满足同一名录条目的重点管理和简化管理条件，从而落入其他/兜底条件？")
    if "﹡" in compact:
        questions.append("是否属于注1所限定的工业建筑中生产的排污单位？")
    for p in predicates:
        if p["predicate_type"].startswith("threshold"):
            metric = p["metric"]
            questions.append(f"请确认 {metric} 对应的实际规模/用量/产能，并提供证据。")
    if "工业废水" in compact or "废气" in compact:
        questions.append("是否实际存在工业废水或废气排放？")
    if any(k in compact for k in ["电镀", "酸洗", "抛光", "热浸镀", "淬火", "钝化"]):
        questions.append("是否存在电镀、酸洗、抛光、热浸镀、淬火或钝化等表面处理工序？")
    if any(k in compact for k in ["染色", "印花", "水洗", "鞣制", "发酵"]):
        questions.append("是否存在对应的染色、印花、水洗、鞣制或发酵工序？")
    # De-duplicate while preserving order.
    return list(dict.fromkeys(questions))


def normalize_condition(entry, target_management, raw_condition):
    raw = normalize_raw(raw_condition)
    compact = clean(raw_condition)
    applies = classify_applies(raw_condition)
    predicates = []
    predicates.extend(process_predicates(compact, target_management))
    threshold_items = threshold_predicates(compact, target_management)
    predicates.extend(threshold_items)
    predicates.extend(numeric_token_predicates(compact, target_management, threshold_token_values(threshold_items)))

    audit_flags = []
    if applies == "NOT_APPLICABLE_IN_CATALOG":
        audit_flags.append("catalog_cell_slash_not_applicable")
    if applies == "ELSE_CONDITION":
        audit_flags.append("else_condition_requires_peer_condition_exclusion")
    if "﹡" in compact:
        audit_flags.append("asterisk_footnote_requires_industrial_building_condition")
    if "涉及通用工序" in compact:
        audit_flags.append("requires_general_process_cross_reference_109_112")
    if "纳入重点排污单位名录" in compact:
        audit_flags.append("requires_external_key_pollutant_unit_list")
    token_classes = {
        p["token_class"]
        for p in predicates
        if p["predicate_type"] == "numeric_condition_token"
    }
    if "industry_code_reference_candidate" in token_classes:
        audit_flags.append("condition_contains_industry_code_candidate_review_needed")
    if "capacity_or_threshold_number" in token_classes:
        audit_flags.append("condition_contains_unparsed_capacity_or_threshold_review_needed")
    if "unclassified_numeric_token" in token_classes:
        audit_flags.append("condition_contains_unclassified_numeric_token_review_needed")
    if compact not in {"/", "其他", "其他﹡"} and not predicates:
        audit_flags.append("need_human_normalization")

    confidence = "HIGH"
    if any(flag in audit_flags for flag in [
        "requires_general_process_cross_reference_109_112",
        "requires_external_key_pollutant_unit_list",
        "else_condition_requires_peer_condition_exclusion",
        "need_human_normalization",
    ]):
        confidence = "MEDIUM"
    if any(p.get("confidence") == "LOW" for p in predicates):
        confidence = "LOW"

    return {
        "target_management": target_management,
        "raw_condition": raw,
        "applies_status": applies,
        "normalized_predicates": predicates,
        "confirmation_questions": build_confirmation_questions(raw_condition, predicates, target_management),
        "audit_flags": list(dict.fromkeys(audit_flags)),
        "normalization_confidence": confidence,
        "runtime_status": "DRAFT_NOT_FOR_RUNTIME",
    }


def normalize_entry(entry):
    conditions = [
        normalize_condition(entry, "KEY", entry["key_management_condition"]),
        normalize_condition(entry, "SIMPLIFIED", entry["simplified_management_condition"]),
        normalize_condition(entry, "REGISTRATION", entry["registration_management_condition"]),
    ]
    all_flags = []
    for condition in conditions:
        all_flags.extend(condition["audit_flags"])
    needs_human = any(
        flag in set(all_flags)
        for flag in [
            "need_human_normalization",
            "requires_general_process_cross_reference_109_112",
            "requires_external_key_pollutant_unit_list",
            "else_condition_requires_peer_condition_exclusion",
        ]
    )
    return {
        "catalog_version": entry["catalog_version"],
        "catalog_entry_no": int(entry["catalog_entry_no"]),
        "major_category_text": entry["major_category_text"],
        "industry_category_text": entry["industry_category_text"],
        "gb_code_fragments": [c for c in entry["gb_code_fragments"].split(";") if c],
        "condition_code_fragments": [c for c in entry.get("condition_code_fragments", "").split(";") if c],
        "conditions": conditions,
        "entry_audit_flags": sorted(set(all_flags)),
        "needs_human_review": needs_human,
        "normalization_stage": "DRAFT_RAW_CONDITION_TO_PREDICATES",
        "runtime_status": "DRAFT_NOT_FOR_RUNTIME",
        "source_page": int(entry["source_page"]),
    }


def flatten_rows(entries):
    rows = []
    for entry in entries:
        for condition in entry["conditions"]:
            predicates = condition["normalized_predicates"]
            rows.append({
                "catalog_entry_no": entry["catalog_entry_no"],
                "major_category_text": entry["major_category_text"],
                "industry_category_text": entry["industry_category_text"],
                "gb_code_fragments": ";".join(entry["gb_code_fragments"]),
                "target_management": condition["target_management"],
                "raw_condition": condition["raw_condition"],
                "applies_status": condition["applies_status"],
                "predicate_count": len(predicates),
                "normalized_predicates_json": json.dumps(predicates, ensure_ascii=False),
                "confirmation_questions_json": json.dumps(condition["confirmation_questions"], ensure_ascii=False),
                "audit_flags": ";".join(condition["audit_flags"]),
                "normalization_confidence": condition["normalization_confidence"],
                "runtime_status": condition["runtime_status"],
                "source_page": entry["source_page"],
            })
    return rows


def write_csv(path, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def validate(entries, condition_rows):
    entry_nos = [entry["catalog_entry_no"] for entry in entries]
    condition_status_counts = {}
    flag_counts = {}
    numeric_token_class_counts = {}
    for row in condition_rows:
        condition_status_counts[row["applies_status"]] = condition_status_counts.get(row["applies_status"], 0) + 1
        for flag in row["audit_flags"].split(";"):
            if flag:
                flag_counts[flag] = flag_counts.get(flag, 0) + 1
        for predicate in json.loads(row["normalized_predicates_json"]):
            if predicate.get("predicate_type") == "numeric_condition_token":
                token_class = predicate["token_class"]
                numeric_token_class_counts[token_class] = numeric_token_class_counts.get(token_class, 0) + 1
    errors = []
    if len(entries) != 112:
        errors.append(f"expected 112 entries, got {len(entries)}")
    if set(entry_nos) != set(range(1, 113)):
        errors.append("catalog entries are not exactly 1-112")
    if len(condition_rows) != 336:
        errors.append(f"expected 336 condition rows, got {len(condition_rows)}")
    return {
        "entry_count": len(entries),
        "condition_row_count": len(condition_rows),
        "missing_entry_nos": sorted(set(range(1, 113)) - set(entry_nos)),
        "condition_status_counts": condition_status_counts,
        "audit_flag_counts": flag_counts,
        "numeric_token_class_counts": numeric_token_class_counts,
        "runtime_status": "DRAFT_NOT_FOR_RUNTIME",
        "validation_status": "PASS" if not errors else "FAIL",
        "errors": errors,
    }


def main():
    with INPUT.open(encoding="utf-8-sig", newline="") as f:
        raw_entries = list(csv.DictReader(f))
    entries = [normalize_entry(entry) for entry in raw_entries]
    entries.sort(key=lambda item: item["catalog_entry_no"])
    condition_rows = flatten_rows(entries)
    validation = validate(entries, condition_rows)
    if validation["validation_status"] != "PASS":
        print(json.dumps(validation, ensure_ascii=False, indent=2))
        raise SystemExit(1)

    (ROOT / "permit_condition_normalization_draft.json").write_text(
        json.dumps(entries, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_csv(ROOT / "permit_condition_normalization_draft.csv", condition_rows)
    (ROOT / "permit_condition_normalization_validation.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (ROOT / "permit_condition_normalization_README.md").write_text(
        "# 排污许可名录条件二次规则化草案\n\n"
        "本产物把 `permit_management_catalog_table_cells.csv` 的三类管理条件从 raw text 转成 `normalized_predicates` 草案。"
        "它是治理中间层，不是运行时规则库。\n\n"
        "## 设计原则\n\n"
        "- `raw_condition` 永远保留原文。\n"
        "- 能稳定识别的阈值、区间、通用工序、重点排污单位、星号、其他兜底、常见工序会进入 `normalized_predicates` 或 `audit_flags`。\n"
        "- 无法稳定识别的内容标 `need_human_normalization`，不做猜测式解释。\n"
        "- 数字 token 统一进入 `numeric_condition_token`，并拆成 `threshold_or_capacity_number`、`capacity_or_threshold_number`、"
        "`industry_code_reference_candidate`、`unclassified_numeric_token`，避免把规模阈值误当行业代码。\n"
        "- `condition_code_fragments` 只保留在条目级原始审计信息中，不再直接灌入每个管理条件的谓词。\n\n"
        "## 禁止用途\n\n"
        "- 不得直接生成正式 `permit_type`。\n"
        "- 不得接入 EcoCheck 小程序或正式检查模板。\n"
        "- 带 `requires_general_process_cross_reference_109_112`、`requires_external_key_pollutant_unit_list`、`else_condition_requires_peer_condition_exclusion` 的条件必须人工复核。\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
