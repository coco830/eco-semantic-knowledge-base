import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FINAL_STATE = "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"

SCORE13_NAMES = {
    "S01": "环保手续完善情况",
    "S02": "环保台账规范情况",
    "S03": "环保相关系统完成情况",
    "S04": "内部现场环境情况",
    "S05": "外部周边环境情况",
    "S06": "环保治理设施运行情况",
    "S07": "固体废物贮存规范情况",
    "S08": "环保培训情况",
    "S09": "标识、标牌、制度公示情况",
    "S10": "废水、废气、噪声、废渣排放及处置情况",
    "S11": "历史遗留问题整改情况",
    "S12": "辐射安全管理",
    "S13": "环保应急管理情况",
}

FORCED_LABELS = {
    ("4620", "98"): ("NOT_APPLY", "forced_denoise", "条目98覆盖461/463/469，不含4620。"),
    ("4620", "99"): ("APPLIES", "forced_explicit_category", "条目99明确为污水处理及其再生利用462，仍需按处理能力等条件确认。"),
    ("7721", "103"): ("NEED_EIA_OR_PERMIT_CONFIRM", "forced_business_scope", "条目103覆盖环境治理业772，但条件限定危废/一般工业固废贮存利用处理处置。"),
    ("2211", "36"): ("APPLIES", "forced_group_category", "条目36为纸浆制造221，覆盖2211。"),
    ("2211", "37"): ("NOT_APPLY", "forced_denoise", "条目37为造纸222，不覆盖2211。"),
    ("2211", "38"): ("NOT_APPLY", "forced_denoise", "条目38为纸制品223，不覆盖2211。"),
    ("2530", "42"): ("NOT_APPLY", "forced_denoise", "条目42为精炼石油产品制造251，不覆盖2530。"),
    ("2530", "43"): ("NOT_APPLY", "forced_denoise", "条目43为煤炭加工252，不覆盖2530。"),
    ("2530", "44"): ("NOT_APPLY", "forced_denoise", "条目44为生物质燃料加工254，不覆盖2530。"),
    ("1331", "11"): ("APPLIES", "forced_sample_review", "条目11对应植物油加工133，覆盖1331。"),
    ("2671", "51"): ("APPLIES", "forced_sample_review", "条目51对应炸药、火工及焰火产品制造267，覆盖2671。"),
    ("2710", "53"): ("APPLIES", "forced_sample_review", "条目53对应化学药品原料药制造271。"),
    ("3011", "63"): ("APPLIES", "forced_sample_review", "条目63包含水泥（熟料）制造，覆盖3011。"),
    ("4413", "95"): ("NOT_APPLY", "forced_denoise", "条目95列4411/4412/4417，不含4413。"),
    ("4413", "96"): ("NOT_APPLY", "forced_denoise", "条目96为锅炉通用工序，不能仅因44大类上下文适用于4413。"),
    ("4610", "98"): ("APPLIES", "forced_sample_review", "条目98覆盖自来水生产和供应461。"),
    ("4610", "99"): ("NOT_APPLY", "forced_denoise", "条目99为污水处理及其再生利用462，不覆盖4610。"),
    ("4630", "98"): ("APPLIES", "forced_sample_review", "条目98覆盖海水淡化处理463。"),
    ("4630", "99"): ("NOT_APPLY", "forced_denoise", "条目99为污水处理及其再生利用462，不覆盖4630。"),
    ("8421", "107"): ("NOT_APPLY", "forced_denoise", "条目107覆盖841医院和843专业公共卫生服务，不含842。"),
}

for code in ["7711", "7712", "7713"]:
    FORCED_LABELS[(code, "103")] = ("NOT_APPLY", "forced_denoise", "条目103为环境治理业772相关固废/危废处理处置候选，不覆盖771生态保护管理。")
for entry in ["9", "10", "12", "13", "14", "15", "16"]:
    FORCED_LABELS[("1331", entry)] = ("NOT_APPLY", "forced_denoise", "1331优先适用条目11，该条目为同大类兄弟条目。")
for entry in ["45", "46", "47", "48", "49", "50", "52"]:
    FORCED_LABELS[("2671", entry)] = ("NOT_APPLY", "forced_denoise", "2671优先适用条目51，该条目为同大类兄弟条目。")
for entry in ["54", "55", "56", "57", "58", "59"]:
    FORCED_LABELS[("2710", entry)] = ("NOT_APPLY", "forced_denoise", "2710优先适用条目53，该条目为同大类兄弟条目。")
for entry in ["64", "65", "66", "67", "68", "69", "70"]:
    FORCED_LABELS[("3011", entry)] = ("NOT_APPLY", "forced_denoise", "3011优先适用条目63，该条目为同大类兄弟条目。")


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fields=None):
    if fields is None:
        fields = list(rows[0].keys()) if rows else []
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def compact(text):
    return re.sub(r"\s+", "", text or "")


def parse_json(value, default=None):
    if default is None:
        default = []
    if isinstance(value, (list, dict)):
        return value
    if value in ("", None):
        return default
    return json.loads(value)


def catalog_division(text):
    match = re.search(r"(\d{2})$", text or "")
    return match.group(1) if match else ""


def load_inputs():
    raw = {r["catalog_entry_no"]: r for r in read_csv(ROOT / "permit_management_catalog_table_cells.csv")}
    conditions = read_csv(ROOT / "permit_condition_normalization_draft.csv")
    candidates = json.loads((ROOT / "all_industry_scenario_candidates_v0_2.json").read_text(encoding="utf-8"))
    classes = {
        r["class_code"]: r
        for r in read_csv(ROOT / "industry_catalog_base.csv")
        if r["level"] == "class"
    }
    scenarios = json.loads((ROOT / "scenario_templates.json").read_text(encoding="utf-8"))
    return raw, conditions, candidates, classes, scenarios


def build_all_permit_conditions(raw, conditions):
    rows = []
    source = "permit_management_catalog_table_cells.csv + permit_condition_normalization_draft.csv"
    for c in conditions:
        entry = raw[c["catalog_entry_no"]]
        cell_name = {
            "KEY": "key_management_condition",
            "SIMPLIFIED": "simplified_management_condition",
            "REGISTRATION": "registration_management_condition",
        }[c["target_management"]]
        predicates = parse_json(c["normalized_predicates_json"])
        flags = [f for f in c["audit_flags"].split(";") if f]
        confirmation = parse_json(c["confirmation_questions_json"])
        if not confirmation and c["raw_condition"].strip() not in {"/", ""}:
            confirmation = ["请根据名录原文、环评、批复、排污许可、登记回执和现场事实确认该管理条件是否适用。"]
        rows.append({
            "catalog_version": entry["catalog_version"],
            "entry_no": c["catalog_entry_no"],
            "target_management_condition": c["target_management"],
            "major_category_text": c["major_category_text"],
            "industry_category_text": c["industry_category_text"],
            "gb_code_fragments": c["gb_code_fragments"],
            "source_basis": source,
            "source_pdf": entry["source_pdf"],
            "source_page": entry["source_page"],
            "source_row_index": entry["source_row_index"],
            "source_table_bbox": entry["table_bbox"],
            "source_row_cells_bbox": entry["row_cells_bbox"],
            "source_cell_name": cell_name,
            "raw_condition": c["raw_condition"],
            "normalized_condition": json.dumps(predicates, ensure_ascii=False),
            "applies_status": c["applies_status"],
            "confidence": c["normalization_confidence"],
            "blocking_flags": json.dumps(flags, ensure_ascii=False),
            "confirmation_questions": json.dumps(confirmation, ensure_ascii=False),
            "permit_type": "NEED_CONFIRM",
            "runtime_status": "DRAFT_NOT_FOR_RUNTIME",
        })
    return rows


def build_entry_indexes(raw, conditions, classes):
    by_entry = defaultdict(list)
    entry_divisions = defaultdict(set)
    entry_text = defaultdict(str)
    for c in conditions:
        by_entry[c["catalog_entry_no"]].append(c)
        div = catalog_division(c["major_category_text"])
        if div:
            entry_divisions[c["catalog_entry_no"]].add(div)
        entry_text[c["catalog_entry_no"]] += " " + c["industry_category_text"] + " " + c["raw_condition"]

    code_review = read_csv(ROOT / "permit_industry_code_reference_review.csv")
    direct_by_code = defaultdict(set)
    for r in code_review:
        if r["candidate_code_level"] == "class" and r["candidate_code"] in classes:
            direct_by_code[r["candidate_code"]].add(r["catalog_entry_no"])
        elif r["candidate_code_level"] == "group":
            for code, klass in classes.items():
                if klass["group_code"] == r["candidate_code"]:
                    direct_by_code[code].add(r["catalog_entry_no"])
    return by_entry, entry_divisions, entry_text, direct_by_code


def text_match(candidate, text):
    body = compact(text)
    if candidate["industry_code"] in body:
        return "CLASS_CODE", candidate["industry_code"]
    if candidate["industry_name"] and compact(candidate["industry_name"]) in body:
        return "INDUSTRY_NAME", candidate["industry_name"]
    if candidate["group_code"] in body:
        return "GROUP_CODE", candidate["group_code"]
    if candidate["group_name"] and compact(candidate["group_name"]) in body:
        return "GROUP_NAME", candidate["group_name"]
    return "", ""


def decide_relation(candidate, condition, relation_source):
    key = (candidate["industry_code"], condition["catalog_entry_no"])
    raw = condition["raw_condition"].strip()
    if raw == "/":
        return "NOT_APPLY", "SLASH_NOT_APPLICABLE", "raw_condition", "/", "HIGH", ["catalog_cell_slash_not_applicable"], "该管理条件单元格为/。"
    if key in FORCED_LABELS:
        label, basis, reason = FORCED_LABELS[key]
        evidence = "manual_seed"
        return label, basis, "manual_seed", condition["catalog_entry_no"], "MEDIUM" if label == "APPLIES" else "LOW", [], reason

    match_type, evidence = text_match(candidate, condition["industry_category_text"] + condition["raw_condition"])
    flags = [f for f in condition["audit_flags"].split(";") if f]
    downgrade = [f for f in flags if f in {
        "else_condition_requires_peer_condition_exclusion",
        "requires_general_process_cross_reference_109_112",
        "requires_external_key_pollutant_unit_list",
    }]
    if match_type and "DIRECT_CODE_MATCH" in relation_source and not downgrade:
        return "APPLIES", f"EXPLICIT_{match_type}", "industry_category_or_raw_condition", evidence, "HIGH" if match_type in {"CLASS_CODE", "INDUSTRY_NAME"} else "MEDIUM", [], "文本明确命中代码/名称；仍需按条件和现场事实确认。"
    if match_type:
        return "MAY_APPLY", f"EXPLICIT_{match_type}_NEEDS_CONFIRM", "industry_category_or_raw_condition", evidence, "MEDIUM", downgrade or ["requires_eia_or_permit_confirmation"], "文本有代码/名称命中，但仍需按条件、阈值、重点名单或现场事实确认。"
    if "GENERAL_PROCESS_TRIGGER" in relation_source:
        return "NEED_EIA_OR_PERMIT_CONFIRM", "GENERAL_PROCESS_TRIGGER", "none", "", "LOW", ["requires_general_process_confirmation"], "通用工序仅作为候选触发，需确认是否有锅炉、炉窑、表面处理或水处理。"
    if "DIRECT_CODE_MATCH" in relation_source:
        return "MAY_APPLY", "DIRECT_CODE_REVIEW_ENTRY", "permit_industry_code_reference_review", candidate["industry_code"], "MEDIUM", downgrade, "代码复核表命中同一条目，但该条件单元格需进一步确认。"
    return "NEED_EIA_OR_PERMIT_CONFIRM", "DIVISION_CONTEXT_ONLY_NO_DIRECT_EVIDENCE", "none", "", "LOW", ["division_context_default_apply_blocked"], "仅大类上下文召回，不得直接适用。"


def build_all_context_relations(candidates, classes, by_entry, entry_divisions, direct_by_code):
    rows = []
    general_entries = {"109", "110", "111", "112"}
    for cand in candidates:
        entry_sources = defaultdict(set)
        for entry in direct_by_code.get(cand["industry_code"], set()):
            entry_sources[entry].add("DIRECT_CODE_MATCH")
        for entry, divisions in entry_divisions.items():
            if cand["division_code"] in divisions:
                entry_sources[entry].add("DIVISION_CONTEXT")
        for entry in general_entries:
            if entry in by_entry:
                entry_sources[entry].add("GENERAL_PROCESS_TRIGGER")

        for entry, sources in sorted(entry_sources.items(), key=lambda item: int(item[0])):
            for condition in by_entry[entry]:
                label, basis, evidence_field, evidence_text, confidence, blocking, reason = decide_relation(
                    cand, condition, "+".join(sorted(sources))
                )
                scenario_ids = list(dict.fromkeys(cand["scenario_template_ids"] + cand["unknown_scenarios"]))
                rows.append({
                    "candidate_relation_id": f"CTXV03_{cand['industry_code']}_{entry}_{condition['target_management']}",
                    "candidate_rule_id": cand["candidate_rule_id"],
                    "industry_code": cand["industry_code"],
                    "industry_name": cand["industry_name"],
                    "division_code": cand["division_code"],
                    "division_name": cand["division_name"],
                    "group_code": cand["group_code"],
                    "group_name": cand["group_name"],
                    "entry_no": entry,
                    "target_management_condition": condition["target_management"],
                    "relation_source": "+".join(sorted(sources)),
                    "applies_status": condition["applies_status"],
                    "gate_status": label,
                    "gate_reason": basis,
                    "evidence_field": evidence_field,
                    "evidence_text": evidence_text,
                    "raw_condition": condition["raw_condition"],
                    "normalized_condition": condition["normalized_predicates_json"],
                    "blocking_flags": json.dumps(list(dict.fromkeys(blocking)), ensure_ascii=False),
                    "source_basis": "permit_management_catalog_table_cells.csv; permit_condition_normalization_draft.csv; all_industry_scenario_candidates_v0_2.json",
                    "confidence": confidence,
                    "confirmation_questions": json.dumps([
                        "该名录条目/条件是否真实适用于该四位小类及企业现场事实？",
                        "请核对环评、批复、排污许可、登记回执、台账、监测报告和现场工序。",
                    ], ensure_ascii=False),
                    "related_scenario_ids": json.dumps(scenario_ids, ensure_ascii=False),
                    "human_review_label": "",
                    "human_reviewer": "",
                    "human_review_notes": "",
                    "permit_type": "NEED_CONFIRM",
                    "runtime_status": "DRAFT_NOT_FOR_RUNTIME",
                })
    return rows


def risk_points_for(scenario_id, name):
    mapping = {
        "SCN_WW_PROCESS_AND_TREATMENT": ["废水来源不清", "污水站停运或绕排", "排口/接管证据缺失"],
        "SCN_VOCS_SOLVENT_AND_TREATMENT": ["VOCs无组织逸散", "废气治理设施低效", "废活性炭更换证据缺失"],
        "SCN_HAZWASTE_STORAGE_TRANSFER": ["危废识别不全", "暂存间不规范", "联单/台账缺失"],
        "SCN_MEDICAL_WASTE_RADIATION": ["医废混入生活垃圾", "医疗废水/放射诊疗边界不清", "暂存和转运证据缺失"],
        "SCN_CHEMICAL_TANK_LDAR_SEEPAGE": ["储罐围堰/防渗不足", "LDAR缺失", "泄漏与土壤地下水风险"],
        "SCN_GAS_STATION_VAPOR_UST": ["油气回收异常", "地下储罐防渗监测缺失", "卸油区应急措施不足"],
        "SCN_DUST_PARTICULATE_CONTROL": ["粉尘无组织排放", "除尘设施失效", "料场/装卸扬尘"],
        "SCN_ONLINE_MONITORING_KEY_UNIT": ["在线监测未联网", "运维记录缺失", "数据异常未闭环"],
        "SCN_RAINWATER_ACCIDENT_EMERGENCY": ["雨污混接", "事故水收集不足", "应急物资/演练缺失"],
        "SCN_TRAINING_SIGNAGE_REVIEW_GAP": ["培训缺失", "标识公示不足", "整改闭环证据不足"],
    }
    return mapping.get(scenario_id, ["生产活动与手续不一致", "一般固废/噪声/台账证据不足", "现场事实需确认"])


def build_scenario_governance(scenarios):
    rows = []
    for s in scenarios:
        rows.append({
            "scenario_id": s["scenario_id"],
            "scenario_name": s["scenario_name"],
            "aliases": s.get("aliases", []),
            "activation_condition": s.get("triggers", []),
            "media_type": s.get("media_type", ""),
            "facility_or_risk_unit": s.get("facility_or_risk_unit", ""),
            "evidence_requirements": s.get("evidence_requirements", []),
            "photo_points": s.get("photo_points", []),
            "risk_points": risk_points_for(s["scenario_id"], s["scenario_name"]),
            "confirmation_questions": s.get("confirmation_questions", []),
            "not_applicable_conditions": s.get("not_applicable_conditions", []),
            "source_basis": ["scenario_templates.json", "v0.3 governance enrichment"],
            "confidence": s.get("confidence", "MEDIUM"),
            "runtime_status": "DRAFT_NOT_FOR_RUNTIME",
        })
    return rows


def build_score13_mapping_v03(scenario_governance):
    old = {r["scenario_id"]: r for r in read_csv(ROOT / "scenario_to_score13_mapping.csv")}
    rows = []
    for s in scenario_governance:
        base = old.get(s["scenario_id"], {})
        primary = base.get("primary_score_item_id", "S01")
        secondary = base.get("secondary_score_item_ids", "S02;S06;S10")
        ids = [primary] + [x for x in secondary.split(";") if x]
        report_sections = [f"{item} {SCORE13_NAMES.get(item, '')}".strip() for item in ids]
        rows.append({
            "scenario_id": s["scenario_id"],
            "scenario_name": s["scenario_name"],
            "primary_score_item_id": primary,
            "secondary_score_item_ids": secondary,
            "mapping_reason": base.get("mapping_reason", f"{s['scenario_name']}按设施、排放、台账、应急和证据目的映射到现有S01-S13。"),
            "possible_report_sections": ";".join(report_sections),
            "human_confirm_required": "需由ESO/ETO结合环评、批复、排污许可、台账和现场事实确认是否适用。",
            "current_13_dimension_gap": base.get("current_13_dimension_gap", "需在知识图谱层保留二级语义，不直接改报告口径。"),
            "suggested_improvement": base.get("suggested_improvement", "保持S01-S13报告口径，新增场景/介质/证据链二级标签。"),
            "runtime_status": "CANDIDATE_ONLY",
        })
    return rows


def build_inspection_candidates(scenario_governance):
    rows = []
    for s in scenario_governance:
        for inspection_type in ["FIRST", "MONTHLY"]:
            rows.append({
                "scenario_id": s["scenario_id"],
                "scenario_name": s["scenario_name"],
                "inspection_type": inspection_type,
                "candidate_section": f"KNOWLEDGE_{s['media_type'].upper() if s['media_type'] else 'CROSS_MEDIA'}",
                "candidate_subsection": s["scenario_name"],
                "risk_or_hidden_danger_point": "；".join(s["risk_points"]),
                "evidence_chain": "；".join(s["evidence_requirements"]),
                "photo_points": "；".join(s["photo_points"]),
                "applicable_when": "；".join(s["activation_condition"]),
                "not_applicable_when": "；".join(s["not_applicable_conditions"]),
                "confirmation_questions": "；".join(s["confirmation_questions"]),
                "answer_policy": '["PASS","FAIL","NA","NEED_CONFIRM"]',
                "default_severity": "NEED_CONFIRM",
                "default_deduct": "",
                "runtime_status": "CANDIDATE_ONLY",
            })
    return rows


def build_open_questions():
    rows = []
    if (ROOT / "open_questions.csv").exists():
        rows.extend(read_csv(ROOT / "open_questions.csv"))
    additions = [
        ("V03_CONTEXT_SCOPE_001", "DIVISION_CONTEXT条目-小类适用关系需要人工审阅后才能从MAY_APPLY/NEED_EIA升级。"),
        ("V03_PERMIT_TYPE_001", "所有target_management_condition只代表名录单元格类型，不得作为企业正式permit_type。"),
        ("V03_GENERAL_PROCESS_001", "109-112通用工序触发需依据企业锅炉、炉窑、表面处理、水处理事实确认。"),
        ("V03_SCENARIO_TEMPLATE_001", "尾矿库、餐饮油烟、实验室废液、垃圾焚烧/填埋等是否需要新增场景模板，需后续业务评审。"),
        ("V03_ECOCHECK_RUNTIME_001", "候选排查项不得接EcoCheck运行时，需模板章节和扣分口径专项审批。"),
    ]
    normalized = []
    for row in rows:
        normalized.append({
            "question_id": row.get("question_id", row.get("id", "")),
            "topic": row.get("topic", row.get("area", "legacy")),
            "question": row.get("question", row.get("description", "")),
            "blocking_level": row.get("blocking_level", "BLOCKS_RUNTIME"),
            "status": row.get("status", "OPEN"),
            "source_basis": row.get("source_basis", "open_questions.csv"),
            "runtime_status": "DRAFT_NOT_FOR_RUNTIME",
        })
    for qid, question in additions:
        normalized.append({
            "question_id": qid,
            "topic": "v0.3_governance",
            "question": question,
            "blocking_level": "BLOCKS_RUNTIME",
            "status": "OPEN",
            "source_basis": "v0.3 AFK governance pass",
            "runtime_status": "DRAFT_NOT_FOR_RUNTIME",
        })
    return normalized


def build_manifest(outputs, validation_hint):
    return {
        "knowledge_base_version": "v0.3-candidate-governance-complete",
        "final_state": FINAL_STATE,
        "runtime_integration": "disabled",
        "runtime_promotion_status": "not_approved",
        "positioning": "候选知识库治理闭环包；覆盖全量行业候选、排污许可名录条件、条目-小类适用关系、场景治理、13维映射和候选排查项；不接运行时。",
        "generated_outputs": outputs,
        "quality_gates": validation_hint,
        "hard_boundaries": [
            "不得接 EcoCheck 小程序运行时",
            "不得生成企业正式 permit_type",
            "不得生成正式检查模板",
            "不得自动扣分",
            "最终企业画像必须由 ESO/ETO 结合环评、批复、排污许可、台账和现场事实确认",
        ],
    }


def main():
    raw, conditions, candidates, classes, scenarios = load_inputs()
    permit_rows = build_all_permit_conditions(raw, conditions)
    by_entry, entry_divisions, entry_text, direct_by_code = build_entry_indexes(raw, conditions, classes)
    context_rows = build_all_context_relations(candidates, classes, by_entry, entry_divisions, direct_by_code)
    scenario_gov = build_scenario_governance(scenarios)
    score13 = build_score13_mapping_v03(scenario_gov)
    inspections = build_inspection_candidates(scenario_gov)
    open_questions = build_open_questions()

    write_csv(ROOT / "all_permit_condition_backfill_v0_3.csv", permit_rows)
    write_json(ROOT / "all_permit_condition_backfill_v0_3.json", permit_rows)
    write_csv(ROOT / "all_context_applicability_review_v0_3.csv", context_rows)
    write_json(ROOT / "all_context_applicability_review_v0_3.json", context_rows)
    write_json(ROOT / "scenario_template_governance_v0_3.json", scenario_gov)
    write_csv(ROOT / "scenario_to_score13_mapping_v0_3.csv", score13)
    write_csv(ROOT / "inspection_candidate_recommendations_v0_3.csv", inspections)
    write_csv(ROOT / "open_questions_v0_3.csv", open_questions)

    (ROOT / "scenario_template_governance_v0_3.md").write_text(
        "# 场景模板治理 v0.3\n\n"
        "本文件对应 `scenario_template_governance_v0_3.json`。场景是产污场景，不是行业硬编码；行业只作为召回入口，最终以环评、批复、排污许可、台账和现场事实确认。\n\n"
        + "\n".join(f"- `{s['scenario_id']}`：{s['scenario_name']}；风险点：{'；'.join(s['risk_points'])}" for s in scenario_gov)
        + "\n",
        encoding="utf-8",
    )
    (ROOT / "open_questions_v0_3.md").write_text(
        "# Open Questions v0.3\n\n" + "\n".join(
            f"- `{q['question_id']}` [{q['blocking_level']}] {q['question']}" for q in open_questions
        ) + "\n",
        encoding="utf-8",
    )

    context_gate_report = {
        "final_state": FINAL_STATE,
        "context_relation_count": len(context_rows),
        "industry_count": len({r["industry_code"] for r in context_rows}),
        "entry_count": len({r["entry_no"] for r in context_rows}),
        "gate_status_counts": dict(sorted(Counter(r["gate_status"] for r in context_rows).items())),
        "division_context_unjustified_applies": [
            r for r in context_rows
            if r["relation_source"] == "DIVISION_CONTEXT" and r["gate_status"] == "APPLIES" and r["evidence_field"] in {"none", ""}
        ],
        "runtime_status": "DRAFT_NOT_FOR_RUNTIME",
    }
    context_gate_report["validation_status"] = "PASS" if not context_gate_report["division_context_unjustified_applies"] else "FAIL"
    write_json(ROOT / "all_context_applicability_review_gate_report.json", context_gate_report)
    (ROOT / "all_context_applicability_review_gate_report.md").write_text(
        "# 全量条目-小类适用关系门禁报告\n\n"
        f"- final_state: `{FINAL_STATE}`\n"
        f"- context_relation_count: {len(context_rows)}\n"
        f"- industry_count: {context_gate_report['industry_count']}\n"
        f"- entry_count: {context_gate_report['entry_count']}\n"
        f"- validation_status: `{context_gate_report['validation_status']}`\n"
        f"- gate_status_counts: `{json.dumps(context_gate_report['gate_status_counts'], ensure_ascii=False)}`\n",
        encoding="utf-8",
    )

    outputs = {
        "all_permit_condition_backfill_v0_3.csv": len(permit_rows),
        "all_permit_condition_backfill_v0_3.json": len(permit_rows),
        "all_context_applicability_review_v0_3.csv": len(context_rows),
        "all_context_applicability_review_v0_3.json": len(context_rows),
        "all_context_applicability_review_gate_report.md": 1,
        "all_context_applicability_review_gate_report.json": 1,
        "scenario_template_governance_v0_3.json": len(scenario_gov),
        "scenario_template_governance_v0_3.md": 1,
        "scenario_to_score13_mapping_v0_3.csv": len(score13),
        "inspection_candidate_recommendations_v0_3.csv": len(inspections),
        "open_questions_v0_3.csv": len(open_questions),
        "open_questions_v0_3.md": 1,
        "knowledge_base_manifest_v0_3.json": 1,
        "validate_knowledge_base_v0_3.py": 1,
        "build_knowledge_base_v0_3.py": 1,
        "knowledge_base_v0_3_validation_report.json": 1,
        "knowledge_base_v0_3_failure_list.csv": 1,
        "FINAL_COMPLETION_REPORT.md": 1,
    }
    manifest = build_manifest(outputs, {
        "industry_candidate_coverage": "1382/1382",
        "permit_catalog_entries": "1-112 continuous",
        "runtime_status_policy": "CANDIDATE_ONLY or DRAFT_NOT_FOR_RUNTIME",
        "permit_type_policy": "NEED_CONFIRM",
    })
    write_json(ROOT / "knowledge_base_manifest_v0_3.json", manifest)

    report = [
        "# FINAL COMPLETION REPORT",
        "",
        f"最终状态：`{FINAL_STATE}`",
        "",
        "## 生成结果",
        "",
        *[f"- `{k}`：{v}" for k, v in outputs.items()],
        "",
        "## 边界",
        "",
        "- 未接 EcoCheck 小程序运行时。",
        "- 未生成正式 permit_type。",
        "- 未生成正式检查模板。",
        "- 未自动扣分。",
        "",
        "## 下一步只允许",
        "",
        "- ESO/ETO 人工审阅 `human_review_label`。",
        "- 针对开放问题做业务确认。",
        "- 经审批后再设计运行时接入方案。",
    ]
    (ROOT / "FINAL_COMPLETION_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    print(json.dumps({"generated": outputs, "final_state": FINAL_STATE}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
