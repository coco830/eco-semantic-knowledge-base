import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from kb_paths import artifact_path


ROOT = Path(__file__).resolve().parent
HIGH_PRIORITY_DIVISIONS = {"13", "22", "25", "26", "27", "28", "29", "30", "44", "46", "77", "84"}


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fieldnames):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_json_field(value):
    if isinstance(value, list):
        return value
    return json.loads(value)


def catalog_division(text):
    match = re.search(r"(\d{2})$", text or "")
    return match.group(1) if match else ""


def load_base_classes():
    rows = read_csv(artifact_path("industry_catalog_base.csv"))
    return {
        row["class_code"]: row
        for row in rows
        if row["level"] == "class"
    }


def load_candidates():
    rows = json.loads((artifact_path("all_industry_scenario_candidates_v0_2.json")).read_text(encoding="utf-8"))
    return [row for row in rows if row["division_code"] in HIGH_PRIORITY_DIVISIONS]


def load_conditions():
    rows = read_csv(artifact_path("permit_condition_normalization_draft.csv"))
    by_entry = defaultdict(list)
    entry_divisions = defaultdict(set)
    for row in rows:
        entry_no = row["catalog_entry_no"]
        by_entry[entry_no].append(row)
        div = catalog_division(row["major_category_text"])
        if div:
            entry_divisions[entry_no].add(div)
    return by_entry, entry_divisions


def load_thresholds():
    rows = read_csv(artifact_path("permit_threshold_predicate_governance.csv"))
    by_entry_target = defaultdict(list)
    for row in rows:
        by_entry_target[(row["catalog_entry_no"], row["target_management"])].append({
            "predicate_type": row["predicate_type"],
            "metric": row["metric"],
            "operator": row["operator"],
            "value": row["value"],
            "unit": row["unit"],
            "lower_value": row["lower_value"],
            "lower_unit": row["lower_unit"],
            "upper_value": row["upper_value"],
            "upper_unit": row["upper_unit"],
            "metric_source_keyword": row.get("metric_source_keyword", ""),
            "metric_inference": row.get("metric_inference", ""),
            "raw_fragment": row["raw_fragment"],
            "governance_status": row["governance_status"],
        })
    return by_entry_target


def load_inheritance_reviews():
    path = artifact_path("permit_parallel_material_threshold_inheritance_review.csv")
    if not path.exists():
        return defaultdict(list)
    rows = read_csv(path)
    by_entry_target = defaultdict(list)
    for row in rows:
        by_entry_target[(row["catalog_entry_no"], row["target_management"])].append({
            "metric": row["metric"],
            "metric_source_keyword": row["metric_source_keyword"],
            "value": row["value"],
            "unit": row["unit"],
            "raw_fragment": row["raw_fragment"],
            "inheritance_rule": row["inheritance_rule"],
            "confidence": row["confidence"],
        })
    return by_entry_target


def load_code_review(base_classes):
    rows = read_csv(artifact_path("permit_industry_code_reference_review.csv"))
    by_class_code = defaultdict(list)
    for row in rows:
        matched_class_codes = []
        if row["candidate_code_level"] == "class" and row["candidate_code"] in base_classes:
            matched_class_codes = [row["candidate_code"]]
        elif row["candidate_code_level"] == "group":
            matched_class_codes = [
                code for code, base in base_classes.items()
                if base["group_code"] == row["candidate_code"]
            ]
        for code in matched_class_codes:
            if base_classes[code]["division_code"] in HIGH_PRIORITY_DIVISIONS:
                by_class_code[code].append(row)
    return by_class_code


def entry_refs_for_candidate(candidate, code_reviews, condition_entry_divisions):
    direct_entry_nos = {row["catalog_entry_no"] for row in code_reviews}
    division_entry_nos = {
        entry_no
        for entry_no, divisions in condition_entry_divisions.items()
        if candidate["division_code"] in divisions
    }
    refs = []
    for entry_no in sorted(direct_entry_nos | division_entry_nos, key=int):
        scope = []
        if entry_no in direct_entry_nos:
            scope.append("CODE_MATCH")
        if entry_no in division_entry_nos:
            scope.append("DIVISION_CONTEXT")
        refs.append({
            "catalog_entry_no": int(entry_no),
            "scope": "+".join(scope),
        })
    return refs


def condition_payload(entry_no, condition_rows, thresholds_by_entry_target, inheritance_by_entry_target):
    payload = []
    for row in sorted(condition_rows, key=lambda item: item["target_management"]):
        key = (entry_no, row["target_management"])
        payload.append({
            "catalog_entry_no": int(entry_no),
            "major_category_text": row["major_category_text"],
            "industry_category_text": row["industry_category_text"],
            "target_management_condition": row["target_management"],
            "raw_condition": row["raw_condition"],
            "applies_status": row["applies_status"],
            "audit_flags": [flag for flag in row["audit_flags"].split(";") if flag],
            "threshold_predicates": thresholds_by_entry_target.get(key, []),
            "parallel_material_inheritance_reviews": inheritance_by_entry_target.get(key, []),
            "normalization_confidence": row["normalization_confidence"],
            "runtime_status": row["runtime_status"],
            "source_page": row["source_page"],
        })
    return payload


def backfill_confirmation_questions(candidate, payload):
    questions = list(candidate["confirmation_questions"])
    flags = {flag for condition in payload for flag in condition["audit_flags"]}
    if payload:
        questions.append("是否属于回填的排污许可名录条目所列行业代码范围，且不存在贸易、研发、办公或单纯服务等不适用边界？")
    if any(condition["threshold_predicates"] for condition in payload):
        questions.append("是否满足名录条件中的产能、床位、处理能力、储罐容量、面积、锅炉吨位或其他规模阈值？")
    if "requires_external_key_pollutant_unit_list" in flags:
        questions.append("是否纳入重点排污单位名录？")
    if "requires_general_process_cross_reference_109_112" in flags:
        questions.append("是否涉及名录第109-112类通用工序，且对应通用工序管理类别是什么？")
    if "else_condition_requires_peer_condition_exclusion" in flags:
        questions.append("若条件为“其他/除重点管理以外”，是否已先排除同条目的重点管理和简化管理条件？")
    if "asterisk_footnote_requires_industrial_building_condition" in flags:
        questions.append("星号脚注是否适用，例如是否属于工业建筑内生产等附加条件？")
    if any(condition["parallel_material_inheritance_reviews"] for condition in payload):
        questions.append("并列物料阈值是否确实继承左侧指标词，例如年使用或年加工能力？")
    return list(dict.fromkeys(questions))


def build_backfill():
    base_classes = load_base_classes()
    candidates = load_candidates()
    conditions_by_entry, entry_divisions = load_conditions()
    thresholds_by_entry_target = load_thresholds()
    inheritance_by_entry_target = load_inheritance_reviews()
    code_review_by_class = load_code_review(base_classes)

    enriched = []
    for candidate in candidates:
        code_reviews = code_review_by_class.get(candidate["industry_code"], [])
        refs = entry_refs_for_candidate(candidate, code_reviews, entry_divisions)
        payload = []
        for ref in refs:
            entry_no = str(ref["catalog_entry_no"])
            conditions = condition_payload(
                entry_no,
                conditions_by_entry[entry_no],
                thresholds_by_entry_target,
                inheritance_by_entry_target,
            )
            for condition in conditions:
                condition["backfill_scope"] = ref["scope"]
            payload.extend(conditions)

        direct_entries = sorted({int(row["catalog_entry_no"]) for row in code_reviews})
        context_entries = sorted({
            int(ref["catalog_entry_no"])
            for ref in refs
            if "DIVISION_CONTEXT" in ref["scope"]
        })
        enriched.append({
            **candidate,
            "permit_catalog_entry_refs": refs,
            "permit_code_reference_reviews": code_reviews,
            "permit_condition_candidates": payload,
            "permit_catalog_direct_match_entry_nos": direct_entries,
            "permit_catalog_division_context_entry_nos": context_entries,
            "permit_backfill_status": "DRAFT_CONDITION_BACKFILL_NEED_CONFIRM",
            "permit_backfill_runtime_status": "DRAFT_NOT_FOR_RUNTIME",
            "permit_backfill_confirmation_questions": backfill_confirmation_questions(candidate, payload),
        })
    return enriched


def flatten_rows(enriched):
    rows = []
    for row in enriched:
        rows.append({
            "industry_code": row["industry_code"],
            "industry_name": row["industry_name"],
            "division_code": row["division_code"],
            "division_name": row["division_name"],
            "group_code": row["group_code"],
            "group_name": row["group_name"],
            "permit_type": row["permit_type"],
            "runtime_status": row["runtime_status"],
            "permit_backfill_status": row["permit_backfill_status"],
            "permit_backfill_runtime_status": row["permit_backfill_runtime_status"],
            "direct_entry_count": len(row["permit_catalog_direct_match_entry_nos"]),
            "division_context_entry_count": len(row["permit_catalog_division_context_entry_nos"]),
            "condition_candidate_count": len(row["permit_condition_candidates"]),
            "direct_entry_nos": json.dumps(row["permit_catalog_direct_match_entry_nos"], ensure_ascii=False),
            "division_context_entry_nos": json.dumps(row["permit_catalog_division_context_entry_nos"], ensure_ascii=False),
            "permit_catalog_entry_refs_json": json.dumps(row["permit_catalog_entry_refs"], ensure_ascii=False),
            "permit_backfill_confirmation_questions_json": json.dumps(row["permit_backfill_confirmation_questions"], ensure_ascii=False),
            "scenario_template_ids_json": json.dumps(row["scenario_template_ids"], ensure_ascii=False),
            "unknown_scenarios_json": json.dumps(row["unknown_scenarios"], ensure_ascii=False),
            "notes": row["notes"],
        })
    return rows


def detail_rows(enriched):
    rows = []
    for row in enriched:
        for condition in row["permit_condition_candidates"]:
            rows.append({
                "industry_code": row["industry_code"],
                "industry_name": row["industry_name"],
                "division_code": row["division_code"],
                "division_name": row["division_name"],
                "group_code": row["group_code"],
                "group_name": row["group_name"],
                "catalog_entry_no": condition["catalog_entry_no"],
                "major_category_text": condition["major_category_text"],
                "industry_category_text": condition["industry_category_text"],
                "backfill_scope": condition["backfill_scope"],
                "target_management_condition": condition["target_management_condition"],
                "raw_condition": condition["raw_condition"],
                "applies_status": condition["applies_status"],
                "audit_flags_json": json.dumps(condition["audit_flags"], ensure_ascii=False),
                "threshold_predicates_json": json.dumps(condition["threshold_predicates"], ensure_ascii=False),
                "parallel_material_inheritance_reviews_json": json.dumps(condition["parallel_material_inheritance_reviews"], ensure_ascii=False),
                "normalization_confidence": condition["normalization_confidence"],
                "condition_runtime_status": condition["runtime_status"],
                "permit_type": row["permit_type"],
                "runtime_status": row["runtime_status"],
                "permit_backfill_status": row["permit_backfill_status"],
                "permit_backfill_runtime_status": row["permit_backfill_runtime_status"],
                "source_page": condition["source_page"],
            })
    return rows


def audit_samples(enriched):
    samples = []
    by_division = defaultdict(list)
    for row in enriched:
        by_division[row["division_code"]].append(row)
    for division, rows in sorted(by_division.items()):
        direct = [row for row in rows if row["permit_catalog_direct_match_entry_nos"]]
        context_only = [row for row in rows if not row["permit_catalog_direct_match_entry_nos"]]
        selected = direct[:2] + context_only[:1]
        if division in {"46", "77"}:
            selected = rows[: min(3, len(rows))]
        for row in selected:
            samples.append({
                "industry_code": row["industry_code"],
                "industry_name": row["industry_name"],
                "division_code": row["division_code"],
                "division_name": row["division_name"],
                "sample_reason": "DIRECT_CODE_MATCH" if row["permit_catalog_direct_match_entry_nos"] else "DIVISION_CONTEXT_ONLY",
                "direct_entry_nos": json.dumps(row["permit_catalog_direct_match_entry_nos"], ensure_ascii=False),
                "division_context_entry_nos": json.dumps(row["permit_catalog_division_context_entry_nos"], ensure_ascii=False),
                "audit_question": "核对该行业候选回填的名录条目、三类管理条件、阈值和确认问题是否只作为候选触发，未被正式化。",
                "runtime_status": "DRAFT_NOT_FOR_RUNTIME",
            })
    return samples


def validate(enriched):
    errors = []
    expected = 201
    if len(enriched) != expected:
        errors.append(f"expected {expected} high priority class rows, got {len(enriched)}")
    bad_status = [
        row["industry_code"]
        for row in enriched
        if row["permit_type"] != "NEED_CONFIRM"
        or row["runtime_status"] != "CANDIDATE_ONLY"
        or row["permit_backfill_runtime_status"] != "DRAFT_NOT_FOR_RUNTIME"
    ]
    if bad_status:
        errors.append(f"bad runtime/permit/backfill status: {len(bad_status)}")
    no_conditions = [row["industry_code"] for row in enriched if not row["permit_condition_candidates"]]
    if no_conditions:
        errors.append(f"rows without condition candidates: {len(no_conditions)}")
    condition_runtime_bad = []
    for row in enriched:
        for condition in row["permit_condition_candidates"]:
            if condition["runtime_status"] != "DRAFT_NOT_FOR_RUNTIME":
                condition_runtime_bad.append(row["industry_code"])
    if condition_runtime_bad:
        errors.append(f"condition runtime status bad: {len(condition_runtime_bad)}")

    division_counts = Counter(row["division_code"] for row in enriched)
    direct_match_counts = Counter()
    condition_counts = Counter()
    for row in enriched:
        if row["permit_catalog_direct_match_entry_nos"]:
            direct_match_counts[row["division_code"]] += 1
        condition_counts[row["division_code"]] += len(row["permit_condition_candidates"])
    return {
        "high_priority_divisions": sorted(HIGH_PRIORITY_DIVISIONS),
        "high_priority_candidate_count": len(enriched),
        "division_counts": dict(sorted(division_counts.items())),
        "direct_match_candidate_counts": dict(sorted(direct_match_counts.items())),
        "condition_candidate_counts": dict(sorted(condition_counts.items())),
        "rows_without_condition_candidates": no_conditions,
        "permit_type_all_need_confirm": not bad_status,
        "runtime_status_all_candidate_only": not bad_status,
        "permit_backfill_runtime_status": "DRAFT_NOT_FOR_RUNTIME",
        "validation_status": "PASS" if not errors else "FAIL",
        "errors": errors,
    }


def main():
    enriched = build_backfill()
    flat = flatten_rows(enriched)
    details = detail_rows(enriched)
    samples = audit_samples(enriched)
    validation = validate(enriched)

    (artifact_path("high_priority_permit_condition_backfill_v0_2.json")).write_text(
        json.dumps(enriched, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_csv(artifact_path("high_priority_permit_condition_backfill_v0_2.csv"), flat, list(flat[0].keys()))
    write_csv(artifact_path("high_priority_permit_condition_backfill_detail_v0_2.csv"), details, list(details[0].keys()))
    write_csv(artifact_path("high_priority_permit_condition_backfill_audit_samples.csv"), samples, list(samples[0].keys()))
    (artifact_path("high_priority_permit_condition_backfill_validation.json")).write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    md = [
        "# 高优先行业许可名录条件回填与抽检",
        "",
        "## 定位",
        "",
        "本批是针对高优先大类的许可名录条件回填 overlay，不是正式许可类型，不是运行时规则。",
        "",
        "## 覆盖",
        "",
        f"- 高优先四位小类：{len(enriched)}",
        f"- 条件明细行：{len(details)}",
        f"- 覆盖大类：{', '.join(sorted(HIGH_PRIORITY_DIVISIONS))}",
        f"- 校验状态：`{validation['validation_status']}`",
        f"- 抽检样本：{len(samples)} 条",
        "",
        "## 强制边界",
        "",
        "- 全部主候选仍为 `permit_type=NEED_CONFIRM`。",
        "- 全部主候选仍为 `runtime_status=CANDIDATE_ONLY`。",
        "- 回填层为 `DRAFT_CONDITION_BACKFILL_NEED_CONFIRM` / `DRAFT_NOT_FOR_RUNTIME`。",
        "- `target_management_condition` 只表示名录单元格类型，不得当成企业许可类型。",
        "- 直接代码匹配和大类上下文回填都必须由 ESO/ETO 根据环评、批复、排污许可、台账和现场事实确认。",
        "",
        "## 抽检方法",
        "",
        "- 每个高优先大类至少抽取直接代码匹配样本；无直接代码匹配的大类抽取上下文样本。",
        "- 抽检重点：行业代码范围、三类管理条件、阈值、重点排污单位、通用工序、其他/兜底排除关系。",
    ]
    (artifact_path("high_priority_permit_condition_backfill_audit.md")).write_text(
        "\n".join(md) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    if validation["validation_status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
