import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


BATCH1_DIVISIONS = {"13", "14", "15", "22", "23"}


def load_industry_classes():
    with (ROOT / "industry_catalog_base.csv").open(encoding="utf-8-sig", newline="") as f:
        return [row for row in csv.DictReader(f) if row["level"] == "class" and row["division_code"] in BATCH1_DIVISIONS]


def profile_for(row):
    code = row["class_code"]
    group = row["group_code"]
    division = row["division_code"]
    scenarios = ["SCN_BASE_PRODUCTION_SOLID_NOISE_LEDGER"]
    unknown = ["SCN_RAINWATER_ACCIDENT_EMERGENCY"]
    confirmation = [
        "是否存在实际生产、加工、清洗、发酵、蒸煮、印刷或包装等产污活动？",
        "环评、批复、排污许可或登记回执中载明的主要污染物和治理设施是什么？",
        "是否存在锅炉、工业炉窑、污水处理、表面处理等通用工序？",
    ]
    notes = []
    confidence = "MEDIUM"
    permit_basis = []

    if division == "13":
        unknown.append("SCN_WW_PROCESS_AND_TREATMENT")
        unknown.append("SCN_HAZWASTE_STORAGE_TRANSFER")
        permit_basis.append("2019名录第9-16条，农副食品加工业多按产能、发酵、通用工序或是否工业建筑生产触发。")
        confirmation += ["年加工/屠宰/生产能力是多少？", "是否有清洗、蒸煮、屠宰、冷冻、淀粉、发酵或高浓度有机废水？"]
        if group in {"134", "135", "136", "137", "139"}:
            scenarios.append("SCN_WW_PROCESS_AND_TREATMENT")
        notes.append("Batch1候选：农副食品废水强相关，但具体管理类别需按产能/工序确认。")

    elif division == "14":
        unknown += ["SCN_WW_PROCESS_AND_TREATMENT", "SCN_HAZWASTE_STORAGE_TRANSFER"]
        permit_basis.append("2019名录第17-20条，食品制造按发酵、产能、是否单纯混合分装、通用工序等触发。")
        confirmation += ["是否有发酵、蒸煮、清洗、CIP、冷却或高浓度有机废水？", "是否仅手工制作、单纯混合或分装？"]
        if group in {"144", "146"}:
            scenarios.append("SCN_WW_PROCESS_AND_TREATMENT")
        notes.append("Batch1候选：食品制造不默认全部有污水站，湿法/发酵/清洗进入确认。")

    elif division == "15":
        unknown += ["SCN_WW_PROCESS_AND_TREATMENT", "SCN_ONLINE_MONITORING_KEY_UNIT", "SCN_HAZWASTE_STORAGE_TRANSFER"]
        permit_basis.append("2019名录第21-23条，酒/饮料/茶按发酵、原汁生产、产能或通用工序触发。")
        confirmation += ["是否有发酵工艺或原汁生产？", "年生产能力是否达到名录阈值？", "是否为单纯混合或分装？"]
        if group in {"151", "152"}:
            scenarios.append("SCN_WW_PROCESS_AND_TREATMENT")
        if code == "1512":
            notes.append("NEED_CONFIRM: GB/T 4754-2017中1512为白酒制造，不能继续作为啤酒制造使用。")
            confidence = "LOW"
        if code == "1513":
            notes.append("1513为啤酒制造，应作为啤酒样板的优先修正候选。")
        notes.append("Batch1候选：酒饮料以废水/污水站为主，在线监测只按重点/地方要求确认。")

    elif division == "22":
        unknown += ["SCN_WW_PROCESS_AND_TREATMENT", "SCN_HAZWASTE_STORAGE_TRANSFER", "SCN_ONLINE_MONITORING_KEY_UNIT"]
        permit_basis.append("2019名录第36-38条，纸浆制造全部重点；造纸和纸制品按工业废水/废气排放条件区分。")
        confirmation += ["是否为纸浆制造、机制纸及纸板制造、加工纸或纸制品制造？", "是否有工业废水或废气排放？", "是否纳入重点排污单位或安装在线监测？"]
        if group in {"221", "222"}:
            scenarios.append("SCN_WW_PROCESS_AND_TREATMENT")
            scenarios.append("SCN_ONLINE_MONITORING_KEY_UNIT")
            confidence = "MEDIUM"
        if group == "223":
            notes.append("NEED_CONFIRM: 纸制品223需确认是否有工业废水或废气排放，不能默认登记或简化。")
        notes.append("Batch1候选：造纸强废水场景，纸制品取决于工业废水/废气。")

    elif division == "23":
        unknown += ["SCN_VOCS_SOLVENT_AND_TREATMENT", "SCN_HAZWASTE_STORAGE_TRANSFER", "SCN_ONLINE_MONITORING_KEY_UNIT"]
        permit_basis.append("2019名录第39-40条，印刷按重点排污单位、溶剂型油墨/稀释剂用量或通用工序触发。")
        confirmation += ["是否为包装装潢印刷？", "溶剂型油墨、涂料、稀释剂年用量是多少？", "是否纳入重点排污单位名录？"]
        if group == "231":
            scenarios.append("SCN_VOCS_SOLVENT_AND_TREATMENT")
            scenarios.append("SCN_HAZWASTE_STORAGE_TRANSFER")
        notes.append("Batch1候选：印刷VOCs/危废场景强相关，但许可类型需按用量和重点名单确认。")

    scenarios = list(dict.fromkeys(scenarios))
    unknown = [s for s in dict.fromkeys(unknown) if s not in scenarios]
    return {
        "candidate_rule_id": f"BATCH1_GB4754_{code}",
        "industry_code": code,
        "industry_name": row["class_name"],
        "division_code": division,
        "division_name": row["division_name"],
        "group_code": group,
        "group_name": row["group_name"],
        "permit_type": "NEED_CONFIRM",
        "scenario_template_ids": scenarios,
        "unknown_scenarios": unknown,
        "source_basis": ["GB/T 4754-2017", *permit_basis],
        "confidence": confidence,
        "confirmation_questions": confirmation,
        "runtime_status": "CANDIDATE_ONLY",
        "notes": " ".join(notes),
    }


def write_csv(path, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        for row in rows:
            flat = row.copy()
            for key in ["scenario_template_ids", "unknown_scenarios", "source_basis", "confirmation_questions"]:
                flat[key] = json.dumps(flat[key], ensure_ascii=False)
            writer.writerow(flat)


def main():
    rows = [profile_for(row) for row in load_industry_classes()]
    (ROOT / "batch1_industry_scenario_candidates.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_csv(ROOT / "batch1_industry_scenario_candidates.csv", rows)

    by_division = {}
    for row in rows:
        by_division.setdefault(f"{row['division_code']} {row['division_name']}", 0)
        by_division[f"{row['division_code']} {row['division_name']}"] += 1
    need_confirm = [r for r in rows if r["permit_type"] == "NEED_CONFIRM" or "NEED_CONFIRM" in r["notes"]]
    low = [r for r in rows if r["confidence"] == "LOW"]

    audit = [
        "# Batch 1 质量审计",
        "",
        "## 范围",
        "",
        "本批为候选迁移，不是正式运行时规则。覆盖 GB/T 4754-2017 大类 13、14、15、22、23 的全部四位小类。",
        "",
        "## 统计",
        "",
        f"- 候选规则数：{len(rows)}",
        *[f"- {k}：{v} 条" for k, v in by_division.items()],
        f"- NEED_CONFIRM：{len(need_confirm)} 条",
        f"- LOW confidence：{len(low)} 条",
        "",
        "## 强制边界",
        "",
        "- 全部 `permit_type` 暂为 `NEED_CONFIRM`，不得直接作为排污许可类别。",
        "- 只复用现有 `SCN_*` 模板，不新增场景模板。",
        "- `1512` 白酒/啤酒冲突仍阻塞运行时；`1513` 已作为啤酒制造修正候选。",
        "- 食品、酒饮料、农副食品大量条件依赖产能、发酵、单纯混合分装、通用工序，必须由现场和资料确认。",
        "- 纸制品 `223`、印刷 `231` 等中类条件不能无脑下沉到某个四位小类。",
        "",
        "## 抽检建议",
        "",
        "- 抽检不少于 10%，且不得少于 8 条。",
        "- `LOW`、`NEED_CONFIRM`、含 `SCN_WW_PROCESS_AND_TREATMENT`、`SCN_VOCS_SOLVENT_AND_TREATMENT`、`SCN_ONLINE_MONITORING_KEY_UNIT` 的规则 100% 抽检。",
        "- 每条抽检核对 GB 行业名称、2019 名录条目、场景模板复用、confirmation_questions 是否覆盖触发条件。",
    ]
    (ROOT / "batch1_quality_audit.md").write_text("\n".join(audit) + "\n", encoding="utf-8")

    print(json.dumps({
        "batch1_candidates": len(rows),
        "by_division": by_division,
        "need_confirm": len(need_confirm),
        "low_confidence": len(low),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
