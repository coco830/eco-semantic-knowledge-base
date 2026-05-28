import csv
import json
from pathlib import Path
from kb_paths import artifact_path


ROOT = Path(__file__).resolve().parent


def count_json(path):
    p = ROOT / path
    if not p.exists():
        return 0
    return len(json.loads(p.read_text(encoding="utf-8")))


def validate_batch(path):
    p = ROOT / path
    if not p.exists():
        return {"exists": False}
    rows = json.loads(p.read_text(encoding="utf-8"))
    templates = {t["scenario_id"] for t in json.loads((artifact_path("scenario_templates.json")).read_text(encoding="utf-8"))}
    bad_refs = []
    for row in rows:
        for scenario_id in row["scenario_template_ids"] + row["unknown_scenarios"]:
            if scenario_id not in templates:
                bad_refs.append((row["candidate_rule_id"], scenario_id))
    return {
        "exists": True,
        "count": len(rows),
        "bad_refs": bad_refs,
        "all_candidate_only": all(row.get("runtime_status") == "CANDIDATE_ONLY" for row in rows),
        "all_need_confirm": all(row.get("permit_type") == "NEED_CONFIRM" for row in rows),
    }


def main():
    batches = {
        "Batch1": validate_batch("batch1_industry_scenario_candidates.json"),
        "Batch2": validate_batch("batch2_industry_scenario_candidates.json"),
        "Batch3": validate_batch("batch3_industry_scenario_candidates.json"),
    }
    table_validation_path = artifact_path("permit_management_catalog_table_cells_validation.json")
    table_validation = json.loads(table_validation_path.read_text(encoding="utf-8")) if table_validation_path.exists() else None
    total_candidates = sum(v.get("count", 0) for v in batches.values())

    lines = [
        "# 候选知识库覆盖报告",
        "",
        "## 当前定位",
        "",
        "本报告汇总 v0.1 候选知识库扩展进展。所有 Batch 规则均为候选召回，不是正式运行时规则。",
        "",
        "## 批次覆盖",
        "",
    ]
    for name, result in batches.items():
        lines.append(f"- {name}：{result.get('count', 0)} 条；`CANDIDATE_ONLY={result.get('all_candidate_only')}`；`NEED_CONFIRM={result.get('all_need_confirm')}`；悬空模板引用 `{len(result.get('bad_refs', []))}`")
    lines.extend([
        f"- 合计候选规则：{total_candidates} 条",
        "",
        "## 许可名录审计源",
        "",
    ])
    if table_validation:
        lines.extend([
            f"- 表格级抽取条目：{table_validation['entry_count']}",
            f"- 编号范围：{table_validation['min_entry_no']}-{table_validation['max_entry_no']}",
            f"- 缺号：{table_validation['missing_entry_nos']}",
            f"- 重号：{table_validation['duplicate_entry_nos']}",
            f"- 验证状态：`{table_validation['validation_status']}`",
            "- 运行时状态：`NOT_FOR_RUNTIME_RAW_AUDIT_ONLY`",
        ])
    else:
        lines.append("- 表格级抽取尚未生成。")
    lines.extend([
        "",
        "## 硬边界",
        "",
        "- 不改 EcoCheck 小程序。",
        "- 不生成正式检查模板。",
        "- 不从候选规则推断正式 `permit_type`。",
        "- 不新增场景模板；扩展批次只复用 `scenario_templates.json` 里的 `SCN_*`。",
        "- 排污许可名录表格级 raw 条件必须二次规则化和人工抽检后，才能进入正式规则。",
    ])
    (artifact_path("candidate_coverage_report.md")).write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({
        "total_candidates": total_candidates,
        "batches": batches,
        "permit_table_validation": table_validation,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
