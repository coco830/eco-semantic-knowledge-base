import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from kb_paths import artifact_path


ROOT = Path(__file__).resolve().parent
CANDIDATES_JSON = artifact_path("all_industry_scenario_candidates_v0_2.json")
BASE_CSV = artifact_path("industry_catalog_base.csv")
SCENARIOS_JSON = artifact_path("scenario_templates.json")

ALLOWED_CONFIDENCE = {"HIGH", "MEDIUM", "LOW", "NEED_CONFIRM"}
FORMAL_PERMIT_VALUES = {"KEY", "SIMPLIFIED", "REGISTRATION", "重点管理", "简化管理", "登记管理", "NONE", "UNKNOWN_AS_NO"}
SERVICE_DIVISIONS = {f"{i:02d}" for i in range(51, 98)}
SERVICE_HEAVY_ALLOWLIST = {"52", "55", "59", "77", "80", "81", "84", "85"}
HEAVY_SCENARIOS = {
    "SCN_DUST_PARTICULATE_CONTROL",
    "SCN_CHEMICAL_TANK_LDAR_SEEPAGE",
    "SCN_ONLINE_MONITORING_KEY_UNIT",
    "SCN_GAS_STATION_VAPOR_UST",
}
SERVICE_TRIGGER_WORDS = [
    "维修",
    "洗染",
    "诊疗",
    "医疗",
    "实验室",
    "仓储",
    "危化",
    "加油",
    "储罐",
    "污水处理",
    "垃圾处理",
    "餐饮",
    "油烟",
    "食堂",
    "锅炉",
    "机房",
    "物业",
    "运维",
]


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def load_base_classes():
    rows = read_csv(BASE_CSV)
    return {
        row["class_code"]: row
        for row in rows
        if row["level"] == "class"
    }


def load_template_ids():
    scenarios = json.loads(SCENARIOS_JSON.read_text(encoding="utf-8"))
    return {row["scenario_id"] for row in scenarios}


def as_list(value):
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return json.loads(value)
    return []


def main():
    base_classes = load_base_classes()
    template_ids = load_template_ids()
    candidates = json.loads(CANDIDATES_JSON.read_text(encoding="utf-8"))

    base_codes = set(base_classes)
    candidate_codes = [row.get("industry_code", "") for row in candidates]
    candidate_rule_ids = [row.get("candidate_rule_id", "") for row in candidates]
    code_counts = Counter(candidate_codes)
    id_counts = Counter(candidate_rule_ids)

    duplicate_codes = sorted([code for code, count in code_counts.items() if count > 1])
    duplicate_ids = sorted([rule_id for rule_id, count in id_counts.items() if count > 1])
    missing_codes = sorted(base_codes - set(candidate_codes))
    extra_codes = sorted(set(candidate_codes) - base_codes)

    permit_type_violations = []
    runtime_status_violations = []
    orphan_scenario_refs = []
    overlap_confirmed_and_unknown = []
    missing_required_fields = []
    invalid_confidence_values = []
    formal_permit_leaks = []
    service_overweight_violations = []
    service_review_items = []
    scenario_usage = Counter()
    confidence_distribution = Counter()
    coverage_by_section = Counter()
    coverage_by_division = Counter()

    for row in candidates:
        code = row.get("industry_code", "")
        base = base_classes.get(code, {})
        division = row.get("division_code", "")
        section = base.get("section_code", "")
        coverage_by_section[section] += 1
        coverage_by_division[f"{division} {row.get('division_name', '')}"] += 1

        confirmed = as_list(row.get("scenario_template_ids", []))
        unknown = as_list(row.get("unknown_scenarios", []))
        source_basis = as_list(row.get("source_basis", []))
        questions = as_list(row.get("confirmation_questions", []))
        confidence = row.get("confidence", "")
        confidence_distribution[confidence] += 1

        if row.get("permit_type") != "NEED_CONFIRM":
            permit_type_violations.append(code)
        if row.get("runtime_status") != "CANDIDATE_ONLY":
            runtime_status_violations.append(code)
        if row.get("permit_type") in FORMAL_PERMIT_VALUES:
            formal_permit_leaks.append(code)
        for scenario in confirmed + unknown:
            scenario_usage[scenario] += 1
            if scenario not in template_ids:
                orphan_scenario_refs.append({"industry_code": code, "scenario_id": scenario})
        for scenario in sorted(set(confirmed) & set(unknown)):
            overlap_confirmed_and_unknown.append({"industry_code": code, "scenario_id": scenario})
        if len(confirmed) != len(set(confirmed)) or len(unknown) != len(set(unknown)):
            overlap_confirmed_and_unknown.append({"industry_code": code, "scenario_id": "DUPLICATE_WITHIN_ARRAY"})
        if confidence not in ALLOWED_CONFIDENCE:
            invalid_confidence_values.append({"industry_code": code, "confidence": confidence})
        if not source_basis or not any("GB/T 4754-2017" in item for item in source_basis):
            missing_required_fields.append({"industry_code": code, "field": "source_basis"})
        if not questions or len(questions) < 2:
            missing_required_fields.append({"industry_code": code, "field": "confirmation_questions"})
        if not row.get("notes"):
            missing_required_fields.append({"industry_code": code, "field": "notes"})

        if division in SERVICE_DIVISIONS:
            confirmed_heavy = sorted(set(confirmed) & HEAVY_SCENARIOS)
            trigger_text = " ".join(questions + [row.get("notes", "")])
            has_trigger_words = any(word in trigger_text for word in SERVICE_TRIGGER_WORDS)
            if confirmed_heavy:
                service_overweight_violations.append({
                    "industry_code": code,
                    "division_code": division,
                    "confirmed_heavy_scenarios": confirmed_heavy,
                })
            if division not in SERVICE_HEAVY_ALLOWLIST and not has_trigger_words:
                service_review_items.append({
                    "industry_code": code,
                    "division_code": division,
                    "reason": "service_light_profile_questions_need_trigger_review",
                })

    blocking_errors = []
    if len(candidates) != 1382:
        blocking_errors.append(f"candidate_count={len(candidates)} expected=1382")
    if missing_codes:
        blocking_errors.append(f"missing_codes={len(missing_codes)}")
    if extra_codes:
        blocking_errors.append(f"extra_codes={len(extra_codes)}")
    if duplicate_codes:
        blocking_errors.append(f"duplicate_codes={len(duplicate_codes)}")
    if duplicate_ids:
        blocking_errors.append(f"duplicate_candidate_rule_ids={len(duplicate_ids)}")
    if permit_type_violations or runtime_status_violations or formal_permit_leaks:
        blocking_errors.append("runtime_or_permit_boundary_violation")
    if orphan_scenario_refs or overlap_confirmed_and_unknown:
        blocking_errors.append("scenario_reference_violation")
    if missing_required_fields or invalid_confidence_values:
        blocking_errors.append("required_field_violation")
    if service_overweight_violations:
        blocking_errors.append("service_overweight_violation")

    report = {
        "validation_status": "PASS" if not blocking_errors else "BLOCK",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_files": [
            str(CANDIDATES_JSON.name),
            str(BASE_CSV.name),
            str(SCENARIOS_JSON.name),
        ],
        "base_class_count": len(base_classes),
        "candidate_count": len(candidates),
        "covered_class_count": len(set(candidate_codes) & base_codes),
        "missing_industry_codes": missing_codes,
        "extra_industry_codes": extra_codes,
        "duplicate_industry_codes": duplicate_codes,
        "duplicate_candidate_rule_ids": duplicate_ids,
        "permit_type_violations": permit_type_violations,
        "runtime_status_violations": runtime_status_violations,
        "formal_permit_leaks": formal_permit_leaks,
        "orphan_scenario_refs": orphan_scenario_refs,
        "overlap_confirmed_and_unknown_scenarios": overlap_confirmed_and_unknown,
        "missing_required_fields": missing_required_fields,
        "invalid_confidence_values": invalid_confidence_values,
        "service_overweight_violations": service_overweight_violations,
        "service_review_items": service_review_items,
        "scenario_usage_summary": dict(sorted(scenario_usage.items())),
        "confidence_distribution": dict(sorted(confidence_distribution.items())),
        "coverage_by_section": dict(sorted(coverage_by_section.items())),
        "coverage_by_division": dict(sorted(coverage_by_division.items())),
        "sample_blocking_rows": (
            duplicate_codes[:10]
            + permit_type_violations[:10]
            + runtime_status_violations[:10]
        ),
        "quality_gate_notes": [
            "All candidates must remain NEED_CONFIRM/CANDIDATE_ONLY.",
            "Service-heavy scenarios may only appear in unknown_scenarios unless explicit allowlist and confirmation questions justify them.",
            "This gate verifies candidate KB hygiene only; it does not legalize permit type or enterprise profile.",
        ],
        "runtime_boundary": "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY",
        "blocking_errors": blocking_errors,
    }

    (artifact_path("all_industry_scenario_candidates_v0_2_gate_report.json")).write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    md = [
        "# 全量行业候选规则 v0.2 门禁报告",
        "",
        f"- 校验状态：`{report['validation_status']}`",
        f"- 四位小类底表：{report['base_class_count']}",
        f"- 候选规则：{report['candidate_count']}",
        f"- 覆盖四位小类：{report['covered_class_count']}",
        f"- 缺失：{len(missing_codes)}",
        f"- 额外：{len(extra_codes)}",
        f"- 行业代码重复：{len(duplicate_codes)}",
        f"- candidate_rule_id 重复：{len(duplicate_ids)}",
        f"- permit/runtime 违规：{len(permit_type_violations) + len(runtime_status_violations)}",
        f"- 悬空/冲突场景引用：{len(orphan_scenario_refs) + len(overlap_confirmed_and_unknown)}",
        f"- 服务业过重 BLOCK：{len(service_overweight_violations)}",
        f"- 服务业 REVIEW：{len(service_review_items)}",
        "",
        "## 运行时边界",
        "",
        "`NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY`。不得生成正式 `permit_type`，不得接 EcoCheck 小程序，不得生成正式检查模板。",
        "",
        "## 阻塞错误",
        "",
        *(f"- {item}" for item in blocking_errors),
    ]
    if not blocking_errors:
        md.append("- 无")
    (artifact_path("all_industry_scenario_candidates_v0_2_gate_report.md")).write_text(
        "\n".join(md) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "validation_status": report["validation_status"],
        "candidate_count": report["candidate_count"],
        "covered_class_count": report["covered_class_count"],
        "blocking_errors": blocking_errors,
        "service_review_items": len(service_review_items),
    }, ensure_ascii=False, indent=2))
    if blocking_errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
