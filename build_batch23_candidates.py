import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent

BATCHES = {
    "batch2": {"17", "18", "19", "20", "21", "23", "29"},
    "batch3": {"30", "31", "32", "33"},
}


def load_classes(divisions):
    with (ROOT / "industry_catalog_base.csv").open(encoding="utf-8-sig", newline="") as f:
        return [r for r in csv.DictReader(f) if r["level"] == "class" and r["division_code"] in divisions]


def base(row, batch):
    return {
        "candidate_rule_id": f"{batch.upper()}_GB4754_{row['class_code']}",
        "industry_code": row["class_code"],
        "industry_name": row["class_name"],
        "division_code": row["division_code"],
        "division_name": row["division_name"],
        "group_code": row["group_code"],
        "group_name": row["group_name"],
        "permit_type": "NEED_CONFIRM",
        "scenario_template_ids": ["SCN_BASE_PRODUCTION_SOLID_NOISE_LEDGER"],
        "unknown_scenarios": ["SCN_RAINWATER_ACCIDENT_EMERGENCY"],
        "source_basis": ["GB/T 4754-2017", "固定污染源排污许可分类管理名录(2019年版)相关条目待表格级抽取确认"],
        "confidence": "MEDIUM",
        "confirmation_questions": [
            "是否存在实际生产、加工、清洗、涂布、喷涂、染整、粉磨、冶炼、铸造或包装等产污活动？",
            "环评、批复、排污许可或登记回执中载明的主要污染物和治理设施是什么？",
            "是否存在锅炉、工业炉窑、污水处理、表面处理、水处理等通用工序？",
        ],
        "runtime_status": "CANDIDATE_ONLY",
        "notes": "",
    }


def add(row, sure=None, unknown=None, questions=None, notes=None):
    if sure:
        for s in sure:
            if s not in row["scenario_template_ids"]:
                row["scenario_template_ids"].append(s)
            if s in row["unknown_scenarios"]:
                row["unknown_scenarios"].remove(s)
    if unknown:
        for s in unknown:
            if s not in row["scenario_template_ids"] and s not in row["unknown_scenarios"]:
                row["unknown_scenarios"].append(s)
    if questions:
        row["confirmation_questions"].extend(q for q in questions if q not in row["confirmation_questions"])
    if notes:
        row["notes"] = (row["notes"] + " " + notes).strip()


def profile_batch2(row):
    r = base(row, "batch2")
    division = row["division_code"]
    group = row["group_code"]

    if division == "17":
        add(r,
            unknown=["SCN_WW_PROCESS_AND_TREATMENT", "SCN_VOCS_SOLVENT_AND_TREATMENT", "SCN_HAZWASTE_STORAGE_TRANSFER"],
            questions=["是否有前处理、染色、印花、洗毛、麻脱胶、缫丝、喷水织造或整理工序？", "是否使用染料、助剂、定型油烟或有机溶剂？"],
            notes="Batch2候选：纺织业污染场景高度依赖前处理/染整/印花/喷水织造等工序，全部需现场确认。")
    elif division == "18":
        add(r,
            unknown=["SCN_WW_PROCESS_AND_TREATMENT", "SCN_VOCS_SOLVENT_AND_TREATMENT", "SCN_HAZWASTE_STORAGE_TRANSFER"],
            questions=["是否有水洗、湿法印花、染色、喷胶、整烫或有机溶剂使用？"],
            notes="Batch2候选：服装服饰通常不默认VOCs或废水，水洗/印花/染色/喷胶触发确认。")
    elif division == "19":
        add(r,
            unknown=["SCN_WW_PROCESS_AND_TREATMENT", "SCN_VOCS_SOLVENT_AND_TREATMENT", "SCN_HAZWASTE_STORAGE_TRANSFER", "SCN_RAINWATER_ACCIDENT_EMERGENCY"],
            questions=["是否有鞣制、水洗、涂饰、喷胶、胶粘剂或处理剂使用？", "是否产生含铬污泥、废溶剂、废胶粘剂包装或其他危废？"],
            notes="Batch2候选：皮革/毛皮/制鞋以废水、VOCs、危废为确认重点，不能默认YES。")
    elif division == "20":
        add(r,
            unknown=["SCN_VOCS_SOLVENT_AND_TREATMENT", "SCN_HAZWASTE_STORAGE_TRANSFER", "SCN_DUST_PARTICULATE_CONTROL"],
            questions=["是否有人造板胶合、涂胶、热压、喷漆、砂光、木粉尘或除尘设施？"],
            notes="Batch2候选：木材加工和人造板需确认胶黏剂、粉尘和废气治理。")
    elif division == "21":
        add(r,
            unknown=["SCN_VOCS_SOLVENT_AND_TREATMENT", "SCN_HAZWASTE_STORAGE_TRANSFER", "SCN_DUST_PARTICULATE_CONTROL", "SCN_WW_PROCESS_AND_TREATMENT"],
            questions=["是否喷涂、涂胶、打磨、砂光、磷化或水帘喷漆？", "溶剂型涂料/胶黏剂或水性涂料年用量是多少？"],
            notes="Batch2候选：家具许可和场景高度依赖涂料/胶黏剂用量、磷化和喷涂事实。")
    elif division == "23":
        add(r,
            sure=["SCN_VOCS_SOLVENT_AND_TREATMENT", "SCN_HAZWASTE_STORAGE_TRANSFER"] if group == "231" else None,
            unknown=["SCN_VOCS_SOLVENT_AND_TREATMENT", "SCN_HAZWASTE_STORAGE_TRANSFER", "SCN_ONLINE_MONITORING_KEY_UNIT"],
            questions=["是否为包装装潢印刷？", "溶剂型油墨、涂料或稀释剂年用量是多少？", "是否纳入重点排污单位名录？"],
            notes="Batch2候选：印刷复制扩展沿用VOCs/危废模板，许可类型按重点名单和用量确认。")
    elif division == "29":
        add(r,
            unknown=["SCN_VOCS_SOLVENT_AND_TREATMENT", "SCN_HAZWASTE_STORAGE_TRANSFER", "SCN_DUST_PARTICULATE_CONTROL", "SCN_WW_PROCESS_AND_TREATMENT"],
            questions=["是否有橡胶炼胶、硫化、塑料改性、发泡、涂布、清洗或废气治理设施？", "年产量是否达到名录阈值？"],
            notes="Batch2候选：橡胶塑料扩展需确认炼胶/硫化/发泡/改性/涂布等事实。")
    return r


def profile_batch3(row):
    r = base(row, "batch3")
    division = row["division_code"]
    group = row["group_code"]

    if division == "30":
        add(r,
            unknown=["SCN_DUST_PARTICULATE_CONTROL", "SCN_ONLINE_MONITORING_KEY_UNIT", "SCN_HAZWASTE_STORAGE_TRANSFER", "SCN_WW_PROCESS_AND_TREATMENT"],
            questions=["是否有破碎、粉磨、筛分、烧成、熔化、窑炉、散装粉料装卸或除尘设施？", "是否为水泥熟料、水泥粉磨、玻璃、陶瓷、砖瓦、石墨或其他非金属矿物制品？"],
            notes="Batch3候选：非金属矿物以粉尘/炉窑/除尘为确认主线，在线监测按重点管理和地方要求确认。")
    elif division == "31":
        add(r,
            unknown=["SCN_DUST_PARTICULATE_CONTROL", "SCN_WW_PROCESS_AND_TREATMENT", "SCN_HAZWASTE_STORAGE_TRANSFER", "SCN_ONLINE_MONITORING_KEY_UNIT", "SCN_RAINWATER_ACCIDENT_EMERGENCY"],
            questions=["是否有烧结、球团、炼铁、炼钢、轧钢、酸洗、涂镀或工业炉窑？", "是否产生含重金属粉尘、污泥、废酸或除尘灰？"],
            notes="Batch3候选：黑色金属冶炼专门因子复杂，全部保留NEED_CONFIRM，不新增模板。")
    elif division == "32":
        add(r,
            unknown=["SCN_DUST_PARTICULATE_CONTROL", "SCN_WW_PROCESS_AND_TREATMENT", "SCN_HAZWASTE_STORAGE_TRANSFER", "SCN_ONLINE_MONITORING_KEY_UNIT", "SCN_RAINWATER_ACCIDENT_EMERGENCY"],
            questions=["是否有熔炼、精炼、电解、湿法冶炼、酸碱浸出、表面处理或工业炉窑？", "是否产生含重金属废水、污泥、烟尘或危废？"],
            notes="Batch3候选：有色金属涉及重金属和湿法/火法工艺，不能靠行业代码定型。")
    elif division == "33":
        add(r,
            unknown=["SCN_DUST_PARTICULATE_CONTROL", "SCN_VOCS_SOLVENT_AND_TREATMENT", "SCN_WW_PROCESS_AND_TREATMENT", "SCN_HAZWASTE_STORAGE_TRANSFER", "SCN_ONLINE_MONITORING_KEY_UNIT"],
            questions=["是否有铸造、熔化、抛丸、打磨、喷涂、酸洗、磷化、电镀、热浸镀或表面处理？", "是否产生废砂、除尘灰、废酸碱、含重金属污泥或废涂料包装？"],
            notes="Batch3候选：金属制品需把铸造/表面处理/喷涂/酸洗等作为现场确认触发。")
    return r


def write_outputs(name, rows):
    (ROOT / f"{name}_industry_scenario_candidates.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    with (ROOT / f"{name}_industry_scenario_candidates.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        for row in rows:
            flat = row.copy()
            for key in ["scenario_template_ids", "unknown_scenarios", "source_basis", "confirmation_questions"]:
                flat[key] = json.dumps(flat[key], ensure_ascii=False)
            writer.writerow(flat)

    by_division = {}
    for row in rows:
        by_division.setdefault(f"{row['division_code']} {row['division_name']}", 0)
        by_division[f"{row['division_code']} {row['division_name']}"] += 1
    audit = [
        f"# {name.capitalize()} 质量审计",
        "",
        "## 范围",
        "",
        "本批为候选迁移，不是正式运行时规则；只复用现有场景模板，不新增 `SCN_*`。",
        "",
        "## 统计",
        "",
        f"- 候选规则数：{len(rows)}",
        *[f"- {k}：{v} 条" for k, v in by_division.items()],
        f"- NEED_CONFIRM：{len(rows)} 条",
        "",
        "## 强制边界",
        "",
        "- 全部 `permit_type=NEED_CONFIRM`，不得作为排污许可类别。",
        "- 全部 `runtime_status=CANDIDATE_ONLY`，不得接入小程序或生成正式模板。",
        "- 污染机制超出现有模板时只写确认问题，不新增模板。",
        "- 排污许可条件待 2019 名录 1-112 表格级抽取完成后再做正式拆分。",
    ]
    if name == "batch2":
        audit.extend([
            "",
            "## 范围提醒",
            "",
            "- 本轮 Batch2 产物包含 23、29 大类的跨批次抽审候选；它们用于知识库连续性，不代表正式 Batch2 范围已经冻结。",
            "- 23 印刷与 Batch1 相邻；29 橡胶塑料也可和后续高风险/化工扩展联动复核。",
        ])
    (ROOT / f"{name}_quality_audit.md").write_text("\n".join(audit) + "\n", encoding="utf-8")


def main():
    batch2 = [profile_batch2(r) for r in load_classes(BATCHES["batch2"])]
    batch3 = [profile_batch3(r) for r in load_classes(BATCHES["batch3"])]
    write_outputs("batch2", batch2)
    write_outputs("batch3", batch3)
    print(json.dumps({
        "batch2_candidates": len(batch2),
        "batch3_candidates": len(batch3),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
