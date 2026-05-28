import csv
import json
from pathlib import Path
from kb_paths import artifact_path


ROOT = Path(__file__).resolve().parent

EXISTING_BATCH_FILES = [
    "batch1_industry_scenario_candidates.csv",
    "batch2_industry_scenario_candidates.csv",
    "batch3_industry_scenario_candidates.csv",
]

BATCHES = {
    "batch4": {"01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "16"},
    "batch5": {"24", "25", "26", "27", "28"},
    "batch6": {"34", "35", "36", "37", "38", "39", "40", "41", "42", "43"},
    "batch7": {"44", "45", "46", "47", "48", "49", "50"},
    "batch8": {"51", "52", "53", "54", "55", "56", "57", "58", "59", "60", "61", "62"},
    "batch9": {"63", "64", "65", "66", "67", "68", "69", "70", "71", "72", "73", "74", "75", "76", "77", "78", "79", "80", "81", "82"},
    "batch10": {"83", "84", "85", "86", "87", "88", "89", "90", "91", "92", "93", "94", "95", "96", "97"},
}

SCN_BASE = "SCN_BASE_PRODUCTION_SOLID_NOISE_LEDGER"
SCN_WW = "SCN_WW_PROCESS_AND_TREATMENT"
SCN_VOCS = "SCN_VOCS_SOLVENT_AND_TREATMENT"
SCN_HAZ = "SCN_HAZWASTE_STORAGE_TRANSFER"
SCN_MED = "SCN_MEDICAL_WASTE_RADIATION"
SCN_TANK = "SCN_CHEMICAL_TANK_LDAR_SEEPAGE"
SCN_GAS = "SCN_GAS_STATION_VAPOR_UST"
SCN_DUST = "SCN_DUST_PARTICULATE_CONTROL"
SCN_ONLINE = "SCN_ONLINE_MONITORING_KEY_UNIT"
SCN_EMERGENCY = "SCN_RAINWATER_ACCIDENT_EMERGENCY"
SCN_TRAINING = "SCN_TRAINING_SIGNAGE_REVIEW_GAP"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        for row in rows:
            flat = row.copy()
            for key in ["scenario_template_ids", "unknown_scenarios", "source_basis", "confirmation_questions"]:
                flat[key] = json.dumps(flat[key], ensure_ascii=False)
            writer.writerow(flat)


def load_classes(divisions=None):
    rows = read_csv(artifact_path("industry_catalog_base.csv"))
    return [
        r for r in rows
        if r["level"] == "class" and (divisions is None or r["division_code"] in divisions)
    ]


def load_template_ids():
    data = json.loads((artifact_path("scenario_templates.json")).read_text(encoding="utf-8"))
    return {row["scenario_id"] for row in data}


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
        "scenario_template_ids": [SCN_BASE],
        "unknown_scenarios": [],
        "source_basis": [
            "GB/T 4754-2017 industry_catalog_base.csv",
            "固定污染源排污许可分类管理名录(2019年版)表格级抽取与条件规则化草案，仅作为候选召回依据",
            "scenario_templates.json v0.1 复用；不新增运行时模板",
        ],
        "confidence": "MEDIUM",
        "confirmation_questions": [
            "企业实际经营、生产、服务或作业活动是否与营业执照行业一致？",
            "环评、批复、排污许可、登记回执、监测报告或现场事实中载明的主要污染物、设施和排口是什么？",
            "是否涉及锅炉、工业炉窑、污水处理、表面处理、喷涂、危废暂存、在线监测、事故水或其他通用工序？",
        ],
        "runtime_status": "CANDIDATE_ONLY",
        "notes": "",
    }


def add(row, sure=None, unknown=None, questions=None, notes=None, confidence=None):
    for scenario in sure or []:
        if scenario not in row["scenario_template_ids"]:
            row["scenario_template_ids"].append(scenario)
        if scenario in row["unknown_scenarios"]:
            row["unknown_scenarios"].remove(scenario)
    for scenario in unknown or []:
        if scenario not in row["scenario_template_ids"] and scenario not in row["unknown_scenarios"]:
            row["unknown_scenarios"].append(scenario)
    for question in questions or []:
        if question not in row["confirmation_questions"]:
            row["confirmation_questions"].append(question)
    if notes:
        row["notes"] = (row["notes"] + " " + notes).strip()
    if confidence:
        row["confidence"] = confidence


def profile(row, batch):
    r = base(row, batch)
    division = row["division_code"]
    group = row["group_code"]
    code = row["class_code"]

    if division in {"01", "02", "03", "04", "05"}:
        add(r,
            unknown=[SCN_WW, SCN_DUST, SCN_HAZ, SCN_EMERGENCY],
            questions=[
                "是否存在规模化养殖、水产养殖、农产品初加工、清洗、烘干、堆肥、病死动物处置或农药/兽药包装物暂存？",
                "是否有粪污、养殖尾水、清洗废水、恶臭、粉尘、锅炉或烘干设施？",
            ],
            notes="Batch4候选：一产及辅助活动不得仅按行业代码判定污染场景，养殖/清洗/烘干/农药兽药包装等均需现场确认。")
        if division == "03":
            add(r, unknown=[SCN_WW, SCN_EMERGENCY], questions=["养殖规模是否达到名录或地方畜禽养殖污染防治管理要求？"])
    elif division in {"06", "08", "09", "10", "11", "12"}:
        add(r,
            unknown=[SCN_DUST, SCN_WW, SCN_HAZ, SCN_ONLINE, SCN_EMERGENCY],
            questions=[
                "是否存在采掘、洗选、破碎、筛分、堆场、尾矿库、矿井水、酸性废水或除尘设施？",
                "是否产生废石、尾矿、除尘灰、含重金属污泥或其他危险废物？",
            ],
            notes="Batch4候选：采矿类以粉尘、矿井水/选矿废水、固废堆场和生态环境风险确认。")
    elif division == "07":
        add(r,
            unknown=[SCN_TANK, SCN_VOCS, SCN_WW, SCN_HAZ, SCN_ONLINE, SCN_EMERGENCY],
            questions=["是否涉及油气开采、集输、储罐、含油污水、伴生气、LDAR、井场防渗或应急池？"],
            notes="Batch4候选：油气开采和辅助活动触发储罐/LDAR/含油废水/防渗风险需资料和现场确认。")
    elif division == "16":
        add(r,
            unknown=[SCN_DUST, SCN_VOCS, SCN_WW, SCN_HAZ, SCN_ONLINE],
            questions=["是否存在烟叶复烤、卷烟制造、香精香料使用、除尘、废气或废水治理设施？"],
            notes="Batch4候选：烟草制品需按复烤/卷烟/辅料和通用工序确认。")
    elif division == "24":
        add(r,
            unknown=[SCN_VOCS, SCN_DUST, SCN_HAZ, SCN_WW],
            questions=["是否涉及印刷、喷涂、胶粘剂、树脂、打磨、粉尘、清洗或表面处理？"],
            notes="Batch5候选：文教工美体育娱乐用品制造形态差异大，VOCs/粉尘/危废只作为触发确认。")
    elif division in {"25", "26", "27", "28"}:
        add(r,
            unknown=[SCN_TANK, SCN_VOCS, SCN_WW, SCN_HAZ, SCN_ONLINE, SCN_EMERGENCY, SCN_DUST],
            questions=[
                "是否涉及化学反应、精馏、萃取、发酵、合成、储罐、装卸、LDAR或危险化学品仓储？",
                "是否产生高浓度有机废水、VOCs、恶臭、危险废物、废活性炭、废母液、废催化剂或污泥？",
            ],
            notes="Batch5候选：石化、化工、医药、化纤为高风险行业，只能做候选召回，许可类型和场景均需名录条件与现场确认。")
    elif division in {"34", "35", "36", "37", "38", "39", "40", "41"}:
        add(r,
            unknown=[SCN_VOCS, SCN_HAZ, SCN_WW, SCN_DUST, SCN_ONLINE],
            questions=[
                "是否有喷涂、涂装、胶粘、清洗、酸洗、磷化、电镀、热处理、焊接、打磨、抛丸或机加工？",
                "是否产生废切削液、废油、漆渣、废活性炭、废酸碱、含重金属污泥、焊烟或粉尘？",
            ],
            notes="Batch6候选：装备、电气、电子、仪表和其他制造需按表面处理/喷涂/清洗/焊接/机加工事实触发。")
    elif division == "42":
        add(r,
            unknown=[SCN_DUST, SCN_WW, SCN_HAZ, SCN_VOCS, SCN_ONLINE, SCN_EMERGENCY],
            questions=["是否涉及废弃资源分拣、破碎、清洗、熔融、再生、危废属性识别或废水废气治理？"],
            notes="Batch6候选：废弃资源综合利用需严控危废属性、粉尘、清洗废水和再生工艺，不得默认低风险。")
    elif division == "43":
        add(r,
            unknown=[SCN_VOCS, SCN_HAZ, SCN_WW, SCN_DUST],
            questions=["是否有维修喷涂、清洗、焊接、切割、打磨、废油/废切削液/废过滤棉/废活性炭暂存？"],
            notes="Batch6候选：维修业按具体维修工序触发，不能与制造业直接等同。")
    elif division == "44":
        add(r,
            unknown=[SCN_DUST, SCN_WW, SCN_HAZ, SCN_ONLINE, SCN_EMERGENCY],
            questions=["是否有燃煤/燃气/生物质锅炉、脱硫脱硝除尘、灰渣、冷却水、在线监测或危废暂存？"],
            notes="Batch7候选：电力热力按燃料、机组、锅炉和治理设施确认。")
    elif division == "45":
        add(r,
            unknown=[SCN_TANK, SCN_VOCS, SCN_HAZ, SCN_EMERGENCY],
            questions=["是否涉及燃气制备、储配站、调压站、储罐、加臭剂、泄漏检测或应急设施？"],
            notes="Batch7候选：燃气生产供应以储配和风险单元确认，现有模板只能近似承载。")
    elif division == "46":
        add(r,
            unknown=[SCN_WW, SCN_HAZ, SCN_ONLINE, SCN_EMERGENCY],
            questions=["是否为自来水、污水处理、再生水、海水淡化或其他水处理设施？污泥、药剂和在线监测如何管理？"],
            notes="Batch7候选：水生产供应尤其污水处理需按设施类型、规模和许可条件确认。")
    elif division in {"47", "48", "49", "50"}:
        add(r,
            unknown=[SCN_DUST, SCN_HAZ, SCN_WW, SCN_EMERGENCY],
            questions=["是否为临时施工项目、固定预制/拌合场、装修喷涂、建筑垃圾堆场、洗车废水或扬尘治理？"],
            notes="Batch7候选：建筑业多为项目制或临时源，不能直接当固定污染源正式规则。")
    elif division in {"51", "52"}:
        unknown = [SCN_HAZ, SCN_WW, SCN_VOCS]
        questions = ["是否仅贸易/零售，还是存在仓储、分装、维修、清洗、冷库、加油站或危险化学品经营？"]
        if group == "526" or code.startswith("526"):
            unknown += [SCN_GAS, SCN_TANK, SCN_EMERGENCY]
            questions.append("是否为机动车燃油/燃气/充电相关站点，是否有地下储罐、油气回收或危化品经营许可？")
        add(r, unknown=unknown, questions=questions, confidence="LOW",
            notes="Batch8候选：批发零售默认轻画像；存在加油站、危化品、维修、冷链或分装时才触发专项场景。")
    elif division in {"53", "54", "55", "56", "57", "58", "59", "60"}:
        add(r,
            unknown=[SCN_DUST, SCN_HAZ, SCN_WW, SCN_VOCS, SCN_TANK, SCN_EMERGENCY],
            questions=["是否有车辆/船舶/航空器维修、清洗、油品储存、危化品仓储、散货堆场、港口码头或装卸粉尘？"],
            notes="Batch8候选：交通仓储邮政按维修、清洗、储油、危化品、散货码头和堆场触发。")
    elif division in {"61", "62"}:
        add(r,
            unknown=[SCN_WW, SCN_HAZ, SCN_EMERGENCY],
            questions=["是否有餐饮油烟、隔油设施、清洗废水、锅炉、中央厨房、废油脂或厨余垃圾管理？"],
            confidence="LOW",
            notes="Batch8候选：住宿餐饮通常为轻画像，餐饮油烟/隔油/废油脂需现场确认。")
    elif division in {"63", "64", "65", "66", "67", "68", "69", "70", "72", "75", "79"}:
        add(r,
            unknown=[SCN_TRAINING],
            questions=["是否仅办公/信息/金融/商务/管理活动，是否存在食堂、实验室、机房柴油发电机、冷却塔或物业运维污染源？"],
            confidence="LOW",
            notes="Batch9候选：低污染服务业只保留基础经营画像和确认问题，不默认废水/VOCs/危废专项。")
    elif division == "71":
        add(r,
            unknown=[SCN_HAZ, SCN_WW, SCN_VOCS],
            questions=["租赁标的是否包含车辆、设备、机械，是否存在维修、清洗、喷涂、油品或危废暂存？"],
            confidence="LOW",
            notes="Batch9候选：租赁业污染场景依赖是否自带维修/清洗/油品管理。")
    elif division in {"73", "74"}:
        add(r,
            unknown=[SCN_WW, SCN_HAZ, SCN_VOCS, SCN_MED],
            questions=["是否有实验室、检测分析、试剂、样品消解、废液、废试剂瓶、生物安全或放射源/射线装置？"],
            notes="Batch9候选：研究试验和专业技术服务按实验室/检测/放射源触发，不能仅按服务业低风险处理。")
    elif division in {"76", "78"}:
        add(r,
            unknown=[SCN_WW, SCN_DUST, SCN_HAZ, SCN_EMERGENCY],
            questions=["是否有水利设施运维、市政污水/雨水、泵站、园林绿化废弃物、施工扬尘或药剂暂存？"],
            confidence="LOW",
            notes="Batch9候选：水利和公共设施管理以运维设施和项目事实确认。")
    elif division == "77":
        add(r,
            unknown=[SCN_WW, SCN_HAZ, SCN_DUST, SCN_ONLINE, SCN_EMERGENCY],
            questions=["是否涉及污水、固废、危废、生态修复、污染治理设施运营、渗滤液、药剂或在线监测？"],
            notes="Batch9候选：生态保护和环境治理可能直接运营污染治理设施，需高优先复核。")
    elif division in {"80", "81", "82"}:
        add(r,
            unknown=[SCN_WW, SCN_VOCS, SCN_HAZ, SCN_DUST],
            questions=["是否有洗染、汽车维修、喷涂、清洗、废机油、废滤芯、废活性炭、胶粘剂或电子产品拆修？"],
            notes="Batch9候选：居民服务和修理业按洗染/维修/喷涂/废油危废触发。")
    elif division == "83":
        add(r,
            unknown=[SCN_WW, SCN_HAZ, SCN_MED],
            questions=["是否有实验室、医务室、食堂、锅炉、废液、试剂瓶、动物实验或放射源/射线装置？"],
            confidence="LOW",
            notes="Batch10候选：教育机构多为轻画像，实验室/医务室/食堂触发专项。")
    elif division == "84":
        add(r,
            sure=[SCN_MED],
            unknown=[SCN_WW, SCN_HAZ, SCN_ONLINE],
            questions=["是否为医疗机构、疾控、妇幼、专科诊疗、放射诊疗、检验实验室或床位达到许可名录阈值？"],
            notes="Batch10候选：卫生行业医疗废物/医疗废水/放射诊疗为强确认场景，但许可类型仍按床位、机构类别和名录条件确认。")
    elif division == "85":
        add(r,
            unknown=[SCN_MED, SCN_WW, SCN_HAZ],
            questions=["是否提供医疗护理、康复、养老院内诊疗、医废产生、污水处理或药品/锐器管理？"],
            confidence="LOW",
            notes="Batch10候选：社会工作机构是否产生医废/医疗废水必须由服务内容确认。")
    elif division in {"86", "87"}:
        add(r,
            unknown=[SCN_VOCS, SCN_HAZ],
            questions=["是否有印刷出版、影视制作化妆/布景喷涂、洗印、录音棚噪声或危废暂存？"],
            confidence="LOW",
            notes="Batch10候选：新闻出版和影视制作默认轻画像，印刷/制作工序触发VOCs/危废。")
    elif division in {"88", "89", "90"}:
        add(r,
            unknown=[SCN_WW, SCN_HAZ],
            questions=["是否有大型场馆、泳池水处理、餐饮、舞台烟雾/喷涂、噪声扰民或危废暂存？"],
            confidence="LOW",
            notes="Batch10候选：文化体育娱乐以公共场所运营和噪声/污水/药剂确认。")
    else:
        add(r,
            unknown=[SCN_TRAINING],
            questions=["是否仅为机关、社团、基层组织或国际组织办公，是否存在食堂、锅炉、实验室、医疗点或物业运维污染源？"],
            confidence="LOW",
            notes="Batch10候选：公共管理和组织类默认轻画像，不得按工业固定污染源正式化。")

    if not r["unknown_scenarios"]:
        add(r, unknown=[SCN_TRAINING], notes="无明确专项模板时仅保留治理制度/标识培训等二级确认。")
    r["scenario_template_ids"] = list(dict.fromkeys(r["scenario_template_ids"]))
    r["unknown_scenarios"] = [s for s in dict.fromkeys(r["unknown_scenarios"]) if s not in r["scenario_template_ids"]]
    return r


def write_batch(name, divisions):
    rows = [profile(row, name) for row in load_classes(divisions)]
    rows.sort(key=lambda r: r["industry_code"])
    (ROOT / f"{name}_industry_scenario_candidates.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_csv(ROOT / f"{name}_industry_scenario_candidates.csv", rows)

    by_division = {}
    for row in rows:
        by_division.setdefault(f"{row['division_code']} {row['division_name']}", 0)
        by_division[f"{row['division_code']} {row['division_name']}"] += 1

    audit = [
        f"# {name.capitalize()} 质量审计",
        "",
        "## 范围",
        "",
        "本批为全量行业底座候选扩展，不是正式运行时规则；只复用现有 `scenario_templates.json` 场景模板。",
        "",
        "## 统计",
        "",
        f"- 候选规则数：{len(rows)}",
        *[f"- {k}：{v} 条" for k, v in by_division.items()],
        f"- NEED_CONFIRM：{len(rows)} 条",
        f"- CANDIDATE_ONLY：{len(rows)} 条",
        "",
        "## 门禁边界",
        "",
        "- 全部 `permit_type=NEED_CONFIRM`。",
        "- 全部 `runtime_status=CANDIDATE_ONLY`。",
        "- `unknown_scenarios` 只代表现场/资料确认入口，不代表企业实际适用。",
        "- 服务业、机关组织、教育文化等低污染行业不得按工业生产场景正式化。",
        "- 涉及许可名录阈值、重点排污单位、床位、产能、面积、通用工序时必须回到表格级许可条件草案和人工复核台账。",
    ]
    (ROOT / f"{name}_quality_audit.md").write_text("\n".join(audit) + "\n", encoding="utf-8")
    return rows


def parse_existing_row(row):
    parsed = row.copy()
    for key in ["scenario_template_ids", "unknown_scenarios", "source_basis", "confirmation_questions"]:
        value = parsed[key]
        if isinstance(value, str):
            parsed[key] = json.loads(value)
    return parsed


def combine_all(new_batches):
    class_rows = load_classes()
    all_codes = {row["class_code"] for row in class_rows}
    preferred = {}
    legacy_duplicates = []
    preferred_divisions = {
        "batch1": {"13", "14", "15", "22", "23"},
        "batch2": {"17", "18", "19", "20", "21", "29"},
        "batch3": {"30", "31", "32", "33"},
    }
    for file in EXISTING_BATCH_FILES:
        batch = file.split("_", 1)[0]
        for row in read_csv(artifact_path(file)):
            parsed = parse_existing_row(row)
            code = parsed["industry_code"]
            if parsed["division_code"] not in preferred_divisions[batch]:
                legacy_duplicates.append({
                    "industry_code": code,
                    "source_file": file,
                    "reason": "legacy_cross_batch_duplicate_excluded_from_v0_2_combined",
                })
                continue
            if code in preferred:
                legacy_duplicates.append({
                    "industry_code": code,
                    "source_file": file,
                    "reason": "duplicate_excluded_from_v0_2_combined",
                })
                continue
            preferred[code] = parsed

    for rows in new_batches.values():
        for row in rows:
            code = row["industry_code"]
            if code in preferred:
                legacy_duplicates.append({
                    "industry_code": code,
                    "source_file": row["candidate_rule_id"],
                    "reason": "unexpected_duplicate_excluded_from_v0_2_combined",
                })
                continue
            preferred[code] = row

    combined = [preferred[code] for code in sorted(preferred)]
    missing = sorted(all_codes - set(preferred))
    extra = sorted(set(preferred) - all_codes)
    return combined, missing, extra, legacy_duplicates


def validate(rows, missing, extra, legacy_duplicates):
    template_ids = load_template_ids()
    seen = set()
    duplicate_codes = []
    bad_refs = []
    bad_status = []
    missing_required = []
    for row in rows:
        code = row["industry_code"]
        if code in seen:
            duplicate_codes.append(code)
        seen.add(code)
        if row["permit_type"] != "NEED_CONFIRM" or row["runtime_status"] != "CANDIDATE_ONLY":
            bad_status.append(code)
        for scenario in row["scenario_template_ids"] + row["unknown_scenarios"]:
            if scenario not in template_ids:
                bad_refs.append({"industry_code": code, "scenario_id": scenario})
        for field in ["source_basis", "confidence", "confirmation_questions", "notes"]:
            if not row.get(field):
                missing_required.append({"industry_code": code, "field": field})
    errors = []
    if len(rows) != 1382:
        errors.append(f"expected 1382 combined candidates, got {len(rows)}")
    if missing:
        errors.append(f"missing class codes: {len(missing)}")
    if extra:
        errors.append(f"extra class codes: {len(extra)}")
    if duplicate_codes:
        errors.append(f"duplicate class codes: {len(duplicate_codes)}")
    if bad_refs:
        errors.append(f"bad scenario references: {len(bad_refs)}")
    if bad_status:
        errors.append(f"bad permit/runtime status: {len(bad_status)}")
    if missing_required:
        errors.append(f"missing required fields: {len(missing_required)}")
    return {
        "combined_candidate_count": len(rows),
        "expected_class_count": 1382,
        "missing_class_codes": missing,
        "extra_class_codes": extra,
        "duplicate_class_codes": sorted(set(duplicate_codes)),
        "bad_scenario_references": bad_refs,
        "bad_status_codes": bad_status,
        "missing_required_fields": missing_required,
        "legacy_duplicate_rows_excluded": legacy_duplicates,
        "permit_type_all_need_confirm": not bad_status,
        "runtime_status_all_candidate_only": not bad_status,
        "runtime_integration": "disabled",
        "validation_status": "PASS" if not errors else "FAIL",
        "errors": errors,
    }


def write_combined(rows, validation):
    (artifact_path("all_industry_scenario_candidates_v0_2.json")).write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_csv(artifact_path("all_industry_scenario_candidates_v0_2.csv"), rows)
    (artifact_path("all_industry_scenario_candidates_v0_2_validation.json")).write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    by_division = {}
    for row in rows:
        by_division.setdefault(f"{row['division_code']} {row['division_name']}", 0)
        by_division[f"{row['division_code']} {row['division_name']}"] += 1
    report = [
        "# 全量行业场景候选规则 v0.2 覆盖报告",
        "",
        "## 定位",
        "",
        "本报告对应 `all_industry_scenario_candidates_v0_2.*`，它是 GB/T 4754 四位小类全量候选召回底座，不是正式企业画像，不是运行时规则。",
        "",
        "## 覆盖",
        "",
        f"- 四位小类候选规则：{len(rows)} / 1382",
        f"- 覆盖大类：{len(by_division)} / 97",
        f"- 校验状态：`{validation['validation_status']}`",
        f"- 排除的历史跨批重复行：{len(validation['legacy_duplicate_rows_excluded'])}",
        "",
        "## 分大类计数",
        "",
        *[f"- {k}：{v} 条" for k, v in by_division.items()],
        "",
        "## 强制门禁",
        "",
        "- 全部 `permit_type=NEED_CONFIRM`。",
        "- 全部 `runtime_status=CANDIDATE_ONLY`。",
        "- 只复用 `scenario_templates.json` 已有 `SCN_*`。",
        "- 不接入 EcoCheck 小程序，不生成正式检查模板，不生成正式 `permit_type`。",
        "- 低污染服务业和机关组织类只做轻画像确认，不能按工业场景默认适用。",
        "- 最终企业画像必须由 ESO/ETO 根据环评、批复、排污许可、台账和现场事实确认。",
    ]
    (artifact_path("all_industry_scenario_candidates_v0_2_coverage_report.md")).write_text(
        "\n".join(report) + "\n",
        encoding="utf-8",
    )


def main():
    new_batches = {}
    for name, divisions in BATCHES.items():
        new_batches[name] = write_batch(name, divisions)
    combined, missing, extra, legacy_duplicates = combine_all(new_batches)
    validation = validate(combined, missing, extra, legacy_duplicates)
    write_combined(combined, validation)
    print(json.dumps({
        "new_batches": {name: len(rows) for name, rows in new_batches.items()},
        "combined_candidate_count": len(combined),
        "validation_status": validation["validation_status"],
        "errors": validation["errors"],
    }, ensure_ascii=False, indent=2))
    if validation["validation_status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
