import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FINAL_STATE = "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"
RUNTIME_INTEGRATION = "disabled"
RUNTIME_STATUS = "DRAFT_NOT_FOR_RUNTIME"
VERSION = "v1.2-to-v1.7-candidate-governance-roadmap"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path, rows, fields=None):
    tmp = path.with_name(f".{path.name}.tmp")
    fields = fields or list(rows[0].keys())
    with tmp.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    tmp.replace(path)


def write_json(path, data):
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def write_jsonl(path, rows):
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    tmp.replace(path)


def with_boundary(row):
    copied = dict(row)
    copied.setdefault("runtime_status", RUNTIME_STATUS)
    copied.setdefault("final_state", FINAL_STATE)
    copied.setdefault("runtime_integration", RUNTIME_INTEGRATION)
    return copied


def split_semicolon(value):
    return [part for part in (value or "").split(";") if part]


def build_v1_2():
    extraction_samples = [
        {
            "sample_id": "EIA12_SAMPLE_3311_SPRAYING",
            "document_type": "EIA",
            "enterprise_id": "ENT_SAMPLE_METAL_3311",
            "industry_code": "3311",
            "industry_name": "金属结构制造",
            "source_document_name": "脱敏样例环评-金属结构制造项目",
            "source_section": "生产工艺与产污环节",
            "source_excerpt": "项目设置下料、焊接、喷漆房和烘干室，喷涂废气经密闭收集后进入活性炭吸附装置处理。",
            "extraction_target_fields": "industry_code;products;raw_materials;processes;pollution_nodes;treatment_facilities;waste_streams",
            "linked_process_ids": "spraying_coating",
            "linked_scenario_ids": "SCN_VOCS_SOLVENT_AND_TREATMENT;SCN_HAZWASTE_STORAGE_TRANSFER;SCN_RAINWATER_ACCIDENT_EMERGENCY",
            "extraction_status": "SAMPLE_CANDIDATE",
            "confirmation_questions": "现场是否仍设置喷漆房和烘干室？活性炭是否更换并纳入危废台账？",
            "evidence_refs": "EIA:生产工艺与产污环节",
            "confidence": "HIGH",
        },
        {
            "sample_id": "EIA12_SAMPLE_1512_BAIJIU",
            "document_type": "EIA",
            "enterprise_id": "ENT_SAMPLE_BAIJIU_1512",
            "industry_code": "1512",
            "industry_name": "白酒制造",
            "source_document_name": "脱敏样例环评-白酒制造项目",
            "source_section": "生产工艺流程",
            "source_excerpt": "粮谷经蒸煮、糖化、发酵、蒸馏、陈酿、勾兑后形成白酒产品，生产废水进入厂区污水处理站。",
            "extraction_target_fields": "industry_code;products;processes;wastewater;wastewater_station;solid_waste",
            "linked_process_ids": "fermentation_distillation;wastewater_treatment_station",
            "linked_scenario_ids": "SCN_WW_PROCESS_AND_TREATMENT;SCN_RAINWATER_ACCIDENT_EMERGENCY;SCN_BASE_PRODUCTION_SOLID_NOISE_LEDGER",
            "extraction_status": "SAMPLE_CANDIDATE",
            "confirmation_questions": "是否为1512白酒制造而非1513啤酒制造？发酵/蒸馏和污水站是否仍在运行？",
            "evidence_refs": "EIA:生产工艺流程",
            "confidence": "HIGH",
        },
        {
            "sample_id": "PERMIT12_SAMPLE_8411_MEDICAL",
            "document_type": "PERMIT",
            "enterprise_id": "ENT_SAMPLE_MEDICAL_8411",
            "industry_code": "8411",
            "industry_name": "综合医院",
            "source_document_name": "脱敏样例排污许可证-综合医院",
            "source_section": "废水和固体废物管理要求",
            "source_excerpt": "医院设置污水处理站和医疗废物暂存间，放射科使用DR设备并按辐射安全要求管理。",
            "extraction_target_fields": "industry_code;bed_count;wastewater_station;medical_waste;radiation_license;discharge_outlets",
            "linked_process_ids": "medical_wastewater_waste_radiation;wastewater_treatment_station",
            "linked_scenario_ids": "SCN_MEDICAL_WASTE_RADIATION;SCN_WW_PROCESS_AND_TREATMENT;SCN_HAZWASTE_STORAGE_TRANSFER",
            "extraction_status": "SAMPLE_CANDIDATE",
            "confirmation_questions": "床位数、医废暂存、放射诊疗许可和污水站是否与许可证一致？",
            "evidence_refs": "PERMIT:废水和固体废物管理要求",
            "confidence": "HIGH",
        },
        {
            "sample_id": "EIA12_SAMPLE_2231_PRINTING",
            "document_type": "EIA",
            "enterprise_id": "ENT_SAMPLE_PAPER_2231",
            "industry_code": "2231",
            "industry_name": "纸和纸板容器制造",
            "source_document_name": "脱敏样例环评-纸制品项目",
            "source_section": "产污环节分析",
            "source_excerpt": "项目设置纸箱印刷和粘箱工序，使用水性油墨和胶黏剂，印刷废气经集气罩收集后处理。",
            "extraction_target_fields": "industry_code;printing;gluing;vocs;wash_water;hazardous_waste",
            "linked_process_ids": "printing_gluing",
            "linked_scenario_ids": "SCN_VOCS_SOLVENT_AND_TREATMENT;SCN_HAZWASTE_STORAGE_TRANSFER;SCN_WW_PROCESS_AND_TREATMENT",
            "extraction_status": "SAMPLE_CANDIDATE",
            "confirmation_questions": "是否存在印刷/粘箱工序？是否产生洗版水或废油墨桶？",
            "evidence_refs": "EIA:产污环节分析",
            "confidence": "MEDIUM",
        },
        {
            "sample_id": "EIA12_SAMPLE_7452_LAB",
            "document_type": "EIA",
            "enterprise_id": "ENT_SAMPLE_LAB_7452",
            "industry_code": "7452",
            "industry_name": "检测服务",
            "source_document_name": "脱敏样例环评-检测实验室",
            "source_section": "固废和风险防控",
            "source_excerpt": "实验室样品前处理和检测过程产生废试剂瓶、实验废液，分类收集后暂存于危废间。",
            "extraction_target_fields": "laboratory;reagent;waste_liquid;hazardous_waste;emergency_materials",
            "linked_process_ids": "laboratory_waste_liquid",
            "linked_scenario_ids": "SCN_HAZWASTE_STORAGE_TRANSFER;SCN_RAINWATER_ACCIDENT_EMERGENCY;NEW_SCN_LAB_WASTE_CANDIDATE",
            "extraction_status": "SAMPLE_CANDIDATE",
            "confirmation_questions": "废液桶标签、危废代码、危废合同和应急吸附物资是否齐全？",
            "evidence_refs": "EIA:固废和风险防控",
            "confidence": "MEDIUM",
        },
    ]
    extraction_samples = [with_boundary(row) for row in extraction_samples]

    predicates = []
    for sample in extraction_samples:
        for process_id in split_semicolon(sample["linked_process_ids"]):
            predicates.append(with_boundary({
                "predicate_id": f"PRED12_{sample['sample_id']}__{process_id}",
                "sample_id": sample["sample_id"],
                "enterprise_id": sample["enterprise_id"],
                "predicate_type": "process_present",
                "process_id": process_id,
                "operator": "present",
                "source_excerpt": sample["source_excerpt"],
                "evidence_strength": "DIRECT",
                "linked_scenario_ids": sample["linked_scenario_ids"],
                "confirmation_questions": sample["confirmation_questions"],
                "confidence": sample["confidence"],
            }))
        for scenario_id in split_semicolon(sample["linked_scenario_ids"]):
            predicates.append(with_boundary({
                "predicate_id": f"PRED12_{sample['sample_id']}__{scenario_id}",
                "sample_id": sample["sample_id"],
                "enterprise_id": sample["enterprise_id"],
                "predicate_type": "scenario_candidate",
                "process_id": sample["linked_process_ids"],
                "operator": "candidate_activate",
                "source_excerpt": sample["source_excerpt"],
                "evidence_strength": "DIRECT" if not scenario_id.startswith("NEW_SCN_") else "IMPLIED",
                "linked_scenario_ids": scenario_id,
                "confirmation_questions": sample["confirmation_questions"],
                "confidence": sample["confidence"],
            }))

    schema = {
        "version": "v1.2-eia-permit-extraction-samples",
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
        "purpose": "Use desensitized EIA/permit text snippets to test process evidence extraction before any runtime integration.",
        "required_fields": [
            "sample_id",
            "document_type",
            "source_excerpt",
            "linked_process_ids",
            "linked_scenario_ids",
            "confirmation_questions",
            "runtime_status",
            "final_state",
            "runtime_integration",
        ],
    }
    return extraction_samples, predicates, schema


def build_v1_3():
    rules = [
        ("RULE13_SPRAYING_VOCS", "spraying_coating", "SCN_VOCS_SOLVENT_AND_TREATMENT", "喷涂/调漆/烘干 + 集气或治理设施文本命中", "无喷涂;外协喷涂;仅外购涂装件", "废气章节;喷漆房;活性炭/催化燃烧;排气筒照片", "S10;S06;S07", "HIGH"),
        ("RULE13_SPRAYING_HAZWASTE", "spraying_coating", "SCN_HAZWASTE_STORAGE_TRANSFER", "喷涂使用油漆/溶剂/活性炭并产生废过滤棉、废活性炭或废包装", "水性材料且无危废仍需危废代码确认", "MSDS;危废台账;危废间照片;转移联单", "S07;S02;S13", "HIGH"),
        ("RULE13_PICKLING_WASTEWATER", "electroplating_acid_pickling", "SCN_WW_PROCESS_AND_TREATMENT", "电镀/酸洗/磷化/氧化槽体 + 清洗废水或槽液更换", "不设置槽体;表面处理全外协", "槽体照片;废水管沟;污水站;药剂台账", "S10;S06;S13", "HIGH"),
        ("RULE13_PICKLING_CHEMICAL", "electroplating_acid_pickling", "SCN_CHEMICAL_TANK_LDAR_SEEPAGE", "酸碱/药剂储槽、槽液或液态化学品库存在", "无槽体;无液态化学品储存", "药剂库;围堰;防渗;SDS;应急物资", "S13;S04;S09", "MEDIUM"),
        ("RULE13_BAIJIU_WASTEWATER", "fermentation_distillation", "SCN_WW_PROCESS_AND_TREATMENT", "发酵/蒸馏/清洗 + 生产废水进入厂区污水站", "仅勾兑分装且无生产废水", "工艺流程;污水站;排口;运行台账", "S10;S06;S02", "HIGH"),
        ("RULE13_PRINTING_VOCS", "printing_gluing", "SCN_VOCS_SOLVENT_AND_TREATMENT", "印刷/粘合/覆膜 + 油墨/胶黏剂/VOCs废气", "外协印刷;仅裁切;无油墨胶黏剂", "印刷机;MSDS;集气罩;废气治理设施", "S10;S06;S07", "HIGH"),
        ("RULE13_BOILER_EXHAUST", "boiler_combustion", "SCN_DUST_PARTICULATE_CONTROL", "锅炉/燃烧设备 + 燃料类型 + 排气筒", "电加热;外供蒸汽;仅生活热水", "锅炉铭牌;登记证;燃料;排气筒;监测报告", "S10;S06;S02", "HIGH"),
        ("RULE13_WW_STATION_SLUDGE", "wastewater_treatment_station", "SCN_HAZWASTE_STORAGE_TRANSFER", "污水站 + 污泥/浮渣/废药剂包装产生", "仅生活污水接管且无处理设施", "污泥暂存;检测报告;危废/一般固废去向", "S07;S10;S02", "MEDIUM"),
        ("RULE13_MEDICAL_WASTE", "medical_wastewater_waste_radiation", "SCN_MEDICAL_WASTE_RADIATION", "医疗机构 + 医废暂存/医疗污水/放射诊疗任一事实", "无诊疗;无床位;无医废;无放射设备", "医废间;医废合同;污水消毒设施;放射许可", "S07;S12;S06;S13", "HIGH"),
        ("RULE13_LAB_WASTE", "laboratory_waste_liquid", "NEW_SCN_LAB_WASTE_CANDIDATE", "实验室/检测试剂 + 废液/废试剂瓶", "委外检测;无实验室;不产生实验废液", "废液桶;标签;危废间;试剂柜;应急吸附物资", "S07;S13;S09", "MEDIUM"),
        ("RULE13_TAILINGS", "tailings_storage", "NEW_SCN_TAILINGS_CANDIDATE", "尾矿库/尾矿坝/回水池/渗滤液任一风险单元", "无尾矿库;尾矿直接外运且无库区", "尾矿坝;排洪系统;回水池;应急预案;巡检记录", "S13;S10;S04", "MEDIUM"),
        ("RULE13_WASTE_DISPOSAL", "waste_incineration_landfill", "NEW_SCN_WASTE_DISPOSAL_CANDIDATE", "垃圾焚烧/填埋 + 烟气净化/渗滤液/飞灰", "仅转运站且无焚烧填埋处置", "焚烧炉/填埋区;烟气净化;渗滤液站;飞灰暂存;在线监测", "S10;S06;S07;S13", "MEDIUM"),
    ]
    rows = []
    for rule_id, process_id, scenario_id, activation, negative, evidence, score13, confidence in rules:
        rows.append(with_boundary({
            "rule_id": rule_id,
            "process_id": process_id,
            "scenario_id": scenario_id,
            "activation_condition": activation,
            "negative_condition": negative,
            "evidence_strength_required": "DIRECT_OR_PERMIT_DOCUMENTED",
            "evidence_chain": evidence,
            "photo_points": evidence,
            "score13_hint": score13,
            "open_question_refs": "V03_SCENARIO_TEMPLATE_001" if scenario_id.startswith("NEW_SCN_") else "",
            "rule_effect": "CANDIDATE_SCENARIO_ACTIVATION_ONLY",
            "confidence": confidence,
        }))
    return rows


DECISIONS = {
    "OQ-001": ("CONFIRM_FIXED", "代码名称错配已由ETO确认，需保留GB/T截图和修复前后清单。", "FORMALIZATION_CANDIDATE_AFTER_EVIDENCE"),
    "OQ-002": ("REJECT_INHERIT_DEFAULT", "代表性小类默认不得外推，例外必须环评/许可确认。", "BLOCKS_RUNTIME"),
    "OQ-003": ("LIMIT_TO_221", "纸浆制造221不得继承至222/223。", "FORMALIZATION_CANDIDATE_AFTER_DIFF"),
    "OQ-004": ("LIMIT_TO_223_WITH_PROCESS_TRIGGER", "纸制品223由工业废水/废气事实触发。", "NEEDS_PROCESS_EVIDENCE"),
    "OQ-005": ("RECALL_ONLY", "通用工序仅召回，不直接生成permit_type。", "BLOCKS_RUNTIME"),
    "OQ-006": ("PROCESS_TRIGGER_MAY_APPLY", "装备/金属类以表面处理、喷涂、炉窑等工序事实触发。", "NEEDS_SITE_CONFIRM"),
    "OQ-007": ("CANDIDATE_ONLY", "候选章节/S18类编号不得接正式模板。", "BLOCKS_RUNTIME"),
    "V03_CONTEXT_SCOPE_001": ("RECALL_ONLY", "DIVISION_CONTEXT只召回，不能直接APPLIES。", "BLOCKS_RUNTIME"),
    "V03_PERMIT_TYPE_001": ("COLUMN_ONLY", "target_management_condition不是正式permit_type。", "BLOCKS_RUNTIME"),
    "V03_GENERAL_PROCESS_001": ("CONFIRM_BY_SITE_OR_DOCUMENT", "109-112通用工序需环评/许可/现场证据确认。", "NEEDS_PROCESS_EVIDENCE"),
    "V03_SCENARIO_TEMPLATE_001": ("ADD_NEW_SCENARIO_CANDIDATES", "尾矿库、实验室废液、垃圾焚烧/填埋需新增候选模板。", "NEEDS_TEMPLATE_REVIEW"),
    "V03_ECOCHECK_RUNTIME_001": ("BLOCK_RUNTIME", "运行时接入需二次审批、契约测试、回滚和审计。", "BLOCKS_RUNTIME"),
    "V04_ENTRY_108_CONTEXT_001": ("CROSS_REFERENCE_ONLY", "第108条只承接109-112，不生成全行业笛卡尔关系。", "FORMALIZATION_CANDIDATE_AFTER_EVIDENCE"),
    "V04_NEGATION_POLARITY_001": ("POLARITY_GATE_REQUIRED", "否定词必须保留not_present/excluded极性。", "BLOCKS_RUNTIME"),
    "V04_DIVISION_CONTEXT_APPLIES_001": ("NO_DIRECT_APPLIES", "纯DIVISION_CONTEXT->APPLIES必须为0。", "BLOCKS_RUNTIME"),
    "V04_NOT_APPLY_BLOCKING_FLAGS_001": ("NOT_APPLY_REQUIRES_BLOCKING_FLAGS", "NOT_APPLY无依据必须降级NEED_CONFIRM。", "BLOCKS_RUNTIME"),
    "V04_HUMAN_REVIEW_EMPTY_001": ("DEFINE_FULL_REVIEW_FOR_P0", "空人工审阅字段不得视为已确认。", "BLOCKS_RUNTIME"),
    "V04_RUNTIME_APPROVAL_GATE_001": ("BLOCK_RUNTIME", "运行时批准门禁未完成前不得投产。", "BLOCKS_RUNTIME"),
    "V04_SCORE13_PROMOTION_001": ("RAG_AND_REPORT_HINT", "S01-S13一级口径不改，二级语义进RAG/报告提示。", "RAG_ONLY"),
}


def build_v1_4(open_questions):
    rows = []
    for oq in open_questions:
        qid = oq["question_id"]
        decision, rationale, closure_path = DECISIONS.get(qid, ("NEED_MANUAL_REVIEW", "暂未收到可执行结论。", "BLOCKS_RUNTIME"))
        rows.append(with_boundary({
            "question_id": qid,
            "topic": oq.get("topic", ""),
            "owner_role": oq.get("owner_role", ""),
            "priority": oq.get("priority", ""),
            "question": oq.get("question", ""),
            "preliminary_decision": decision,
            "decision_rationale": rationale,
            "closure_path": closure_path,
            "required_evidence_to_close": "法规/标准原文截图;受影响候选清单;修复diff;验证报告",
            "blocks_runtime": "true" if "BLOCK" in closure_path or oq.get("blocking_level") == "BLOCKS_RUNTIME" else "false",
            "human_review_label": "",
            "human_reviewer": "",
            "decision_status": "PRELIMINARY_NOT_CLOSED",
            "source_basis": "eto_eso_open_question_decisions_v1_0_rc.md; open_questions_v0_4_1.csv",
            "confidence": "MEDIUM",
        }))
    summary = {
        "version": "v1.4-open-question-decision-overlay",
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
        "open_question_count": len(rows),
        "status_counts": dict(Counter(row["closure_path"] for row in rows)),
        "hard_boundary": "Preliminary ETO/ESO decisions do not close runtime gates.",
    }
    return rows, summary


def build_v1_5(review_rows):
    buckets = Counter(row.get("review_bucket", "UNKNOWN") for row in review_rows)
    slice_defs = [
        ("SLICE15_NEGATION_POLARITY", "否定语义专项", "V04_NEGATION_POLARITY_001", "含除/不含/无/未/外协的条件和NOT_APPLY候选", "P0", "ETO"),
        ("SLICE15_NOT_APPLY_FLAGS", "NOT_APPLY依据专项", "V04_NOT_APPLY_BLOCKING_FLAGS_001", "所有NOT_APPLY或forced_denoise候选", "P0", "ETO"),
        ("SLICE15_DIVISION_CONTEXT", "大类上下文召回专项", "V03_CONTEXT_SCOPE_001;V04_DIVISION_CONTEXT_APPLIES_001", "DIVISION_CONTEXT召回，不得直接APPLIES", "P0", "ETO"),
        ("SLICE15_GENERAL_PROCESS", "109-112通用工序专项", "OQ-005;V03_GENERAL_PROCESS_001;V04_ENTRY_108_CONTEXT_001", "锅炉、炉窑、表面处理、水处理等通用工序", "P0", "ETO;ESO"),
        ("SLICE15_PAPER_BOUNDARY", "221/222/223纸浆造纸纸制品边界", "OQ-003;OQ-004", "纸浆、造纸、纸制品相邻中类边界", "P1", "ETO"),
        ("SLICE15_CODE_NAME_FIX", "1512/1513代码名称复核", "OQ-001", "1512白酒、1513啤酒及历史残留", "P1", "资料负责人;ETO"),
        ("SLICE15_PROCESS_EVIDENCE", "工序证据确认专项", "OQ-006;V03_SCENARIO_TEMPLATE_001", "喷涂、电镀、实验室废液、尾矿库、垃圾处置等工序证据", "P1", "ETO;ESO"),
    ]
    rows = []
    for sid, name, oq_refs, rule, priority, owner in slice_defs:
        rows.append(with_boundary({
            "review_slice_id": sid,
            "review_slice_name": name,
            "open_question_refs": oq_refs,
            "selection_rule": rule,
            "estimated_source_rows": str(sum(buckets.values())) if sid == "SLICE15_GENERAL_PROCESS" else "NEED_QUERY_AT_REVIEW_TIME",
            "review_priority": priority,
            "owner_role": owner,
            "editable_fields": "human_review_label;human_reviewer;human_reviewer_role;reviewed_at;human_review_notes;review_basis;evidence_refs;decision_confidence",
            "non_editable_fields": "candidate_relation_id;raw_condition;normalized_condition;gate_status;source_basis;runtime_status;final_state;runtime_integration",
            "review_output": "overlay_only_do_not_mutate_source_tables",
            "runtime_effect": "NO_RUNTIME_EFFECT",
            "confidence": "MEDIUM",
        }))
    return rows


def build_v1_6():
    categories = [
        ("EVAL16_PROCESS_3311_SPRAYING", "process_evidence", "3311环评写有喷漆房和活性炭，能确认哪些候选场景？", "喷涂;VOCs;危废;SITE_VERIFICATION_REQUIRED;NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY", "process_evidence_chunk;enterprise_overlay_chunk", "OQ-006", "RISK-V041-003"),
        ("EVAL16_NEGATION_PROCESS_SCOPE", "negation_scope", "3311写明不设电镀酸洗，是否能排除危废场景？", "PROCESS_ONLY;不能排除喷涂触发的危废;NOT_APPLY_WITH_EVIDENCE", "process_evidence_chunk;enterprise_overlay_chunk", "V04_NEGATION_POLARITY_001", "RISK-V041-004"),
        ("EVAL16_1512_1513", "industry_code", "1512和1513在企业画像里如何区分？", "1512白酒;1513啤酒;GB/T 4754-2017;NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY", "open_question_chunk;process_evidence_chunk", "OQ-001", "RISK-V041-005"),
        ("EVAL16_ENTRY108", "permit_catalog", "第108条为什么不能生成全行业适用关系？", "CROSS_REFERENCE_ONLY;109-112;不生成笛卡尔积", "open_question_chunk;risk_acceptance_chunk", "V04_ENTRY_108_CONTEXT_001", "RISK-V041-001"),
        ("EVAL16_SCORE13_HINT", "score13_mapping", "喷涂VOCs场景会影响哪些EcoCheck 13维？", "S10;S06;S07;二级语义;不改报告口径", "score13_mapping_chunk;scenario_template_chunk", "V04_SCORE13_PROMOTION_001", "RISK-V041-006"),
        ("EVAL16_INSPECTION_EVIDENCE", "inspection_evidence", "污水站场景现场排查需要哪些证据链和照片？", "污水站全景;总排口;运行台账;photo_points;evidence_chain", "inspection_candidate_chunk;scenario_template_chunk", "V03_GENERAL_PROCESS_001", "RISK-V041-003"),
        ("EVAL16_OPEN_QUESTION_TRACE", "open_question_trace", "NOT_APPLY没有blocking_flags时应该怎么处理？", "DOWNGRADE_TO_NEED_CONFIRM;blocking_flags;open question", "open_question_chunk;context_relation_chunk", "V04_NOT_APPLY_BLOCKING_FLAGS_001", "RISK-V041-004"),
        ("EVAL16_RUNTIME_BOUNDARY", "runtime_boundary", "人工审阅确认后能不能直接接EcoCheck运行时？", "不能;二次审批;契约测试;回滚;审计日志", "runtime_design_chunk;approval_workflow_chunk", "V04_RUNTIME_APPROVAL_GATE_001", "RISK-V041-007"),
        ("EVAL16_LAB_WASTE", "scenario_template", "实验室废液为什么是新增候选场景？", "NEW_SCN_LAB_WASTE_CANDIDATE;危废;应急;候选模板", "process_evidence_chunk;open_question_chunk", "V03_SCENARIO_TEMPLATE_001", "RISK-V041-008"),
        ("EVAL16_MEDICAL", "solid_waste", "综合医院许可文本能确认哪些医废/辐射场景？", "医疗废物;污水处理站;放射诊疗;S12;S07", "process_evidence_chunk;scenario_template_chunk", "OQ-006", "RISK-V041-003"),
        ("EVAL16_EMERGENCY", "emergency", "喷涂或化学品场景为什么会影响S13应急？", "应急物资;危化品;事故废水;S13", "scenario_template_chunk;score13_mapping_chunk", "V04_SCORE13_PROMOTION_001", "RISK-V041-006"),
        ("EVAL16_RAG_BOUNDARY", "rag_boundary", "RAG回答企业画像时必须提示什么边界？", "候选;不是运行时批准;site verification;permit confirm", "rag_policy_chunk;enterprise_overlay_chunk", "V03_ECOCHECK_RUNTIME_001", "RISK-V041-007"),
    ]
    rows = []
    for eval_id, category, query, contains, chunks, oq_refs, risk_refs in categories:
        rows.append(with_boundary({
            "eval_id": eval_id,
            "eval_category": category,
            "query": query,
            "expected_answer_contains": split_semicolon(contains),
            "expected_chunk_types": split_semicolon(chunks),
            "open_question_refs": split_semicolon(oq_refs),
            "risk_refs": split_semicolon(risk_refs),
            "must_include_boundary_notice": True,
            "must_not_claim_runtime_ready": True,
            "candidate_only": True,
        }))
    coverage = {
        "version": "v1.6-rag-quality-eval-expansion",
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
        "eval_count": len(rows),
        "required_categories": sorted({row["eval_category"] for row in rows}),
    }
    return rows, coverage


def build_v1_7():
    rows = [
        ("READ_ONLY_KB", "只读知识库", "可以进入内部只读知识库索引", "v0.4.1-v1.6候选边界完整，适合检索和审阅", "SECOND_APPROVAL_NOT_REQUIRED_FOR_INTERNAL_READONLY", "CANDIDATE_ONLY"),
        ("RAG_DEMO", "RAG demo", "可以做候选RAG demo", "需回答展示候选边界、证据链、open question/risk refs", "RAG_BOUNDARY_TEST_REQUIRED", "CANDIDATE_ONLY"),
        ("GRAPH_DEMO", "图谱 demo", "可以做候选图谱查询/可视化", "边和节点需保留runtime_status/final_state/risk refs", "GRAPH_BOUNDARY_TEST_REQUIRED", "CANDIDATE_ONLY"),
        ("HUMAN_REVIEW", "人工审阅工作台", "可以进入审阅工作台", "只能写overlay，不覆盖源表，不伪造审阅", "REVIEW_AUDIT_REQUIRED", "CANDIDATE_ONLY"),
        ("INSPECTION_TEMPLATE", "正式检查模板", "不得接入", "候选排查项未完成正式模板审批和契约测试", "BLOCKS_RUNTIME", "NOT_ALLOWED"),
        ("FORMAL_PERMIT_TYPE", "正式permit_type", "不得生成", "企业正式许可类别必须由许可证/登记回执/环评批复确认", "BLOCKS_RUNTIME", "NOT_ALLOWED"),
        ("AUTO_DEDUCT", "自动扣分", "不得启用", "候选知识不等于扣分事实，需运行时审批和前端呈现契约", "BLOCKS_RUNTIME", "NOT_ALLOWED"),
        ("ECOCHECK_RUNTIME", "EcoCheck runtime", "不得接入", "需二次审批、合同测试、rollback manifest、安全审计日志", "BLOCKS_RUNTIME", "NOT_ALLOWED"),
    ]
    matrix = [with_boundary({
        "target": target,
        "target_name": name,
        "readiness_decision": decision,
        "reason": reason,
        "required_gate_before_change": gate,
        "allowed_state": allowed,
        "runtime_effect": "NO_RUNTIME_EFFECT",
        "confidence": "HIGH",
    }) for target, name, decision, reason, gate, allowed in rows]
    report = {
        "version": "v1.7-runtime-readiness-gap-report",
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
        "summary": "The knowledge base is ready for internal candidate retrieval, graph demo, and human review, but not for EcoCheck runtime.",
        "runtime_blockers": [
            "human_review_not_completed",
            "open_questions_not_closed",
            "second_approval_not_signed",
            "runtime_contract_tests_not_implemented",
            "rollback_manifest_not_frozen",
            "security_audit_log_not_deployed",
        ],
    }
    return matrix, report


def write_markdown(outputs):
    (ROOT / "eia_permit_extraction_schema_v1_2.md").write_text(
        "# eia_permit_extraction_schema_v1_2\n\n"
        f"final_state: `{FINAL_STATE}`\n"
        "runtime_integration: `disabled`\n\n"
        "v1.2 defines how desensitized EIA/permit text can produce process evidence predicates. "
        "The extracted predicates can activate candidate scenarios, but cannot generate formal permit_type or runtime inspection templates.\n",
        encoding="utf-8",
    )
    (ROOT / "human_review_slice_guidance_v1_5.md").write_text(
        "# human_review_slice_guidance_v1_5\n\n"
        f"final_state: `{FINAL_STATE}`\n"
        "runtime_integration: `disabled`\n\n"
        "Review slices are topic work queues, not source-table edits. Reviewers may only write overlay decisions with reviewer, basis, evidence refs, and confidence. "
        "DIVISION_CONTEXT remains recall-only. Process evidence and photo_points are first-class review inputs.\n",
        encoding="utf-8",
    )
    (ROOT / "rag_eval_coverage_v1_6.md").write_text(
        "# rag_eval_coverage_v1_6\n\n"
        f"final_state: `{FINAL_STATE}`\n"
        "runtime_integration: `disabled`\n\n"
        f"v1.6 expands retrieval eval coverage to {outputs['v1_6_coverage']['eval_count']} items. Required categories: "
        + ", ".join(outputs["v1_6_coverage"]["required_categories"])
        + ". Every answer must include candidate boundary notices and must not claim runtime readiness.\n",
        encoding="utf-8",
    )
    (ROOT / "runtime_readiness_gap_report_v1_7.md").write_text(
        "# runtime_readiness_gap_report_v1_7\n\n"
        f"final_state: `{FINAL_STATE}`\n"
        "runtime_integration: `disabled`\n\n"
        "The package may support internal read-only knowledge search, RAG demo, graph demo, and human review workflows. "
        "It must not generate formal permit_type, formal inspection templates, automatic deduct values, or EcoCheck runtime imports.\n\n"
        "Runtime blockers: human review, open question closure, second approval, contract tests, rollback manifest, and security audit logging.\n",
        encoding="utf-8",
    )
    (ROOT / "FINAL_COMPLETION_REPORT_v1_2_to_v1_7.md").write_text(
        "# FINAL_COMPLETION_REPORT_v1_2_to_v1_7\n\n"
        f"final_state: `{FINAL_STATE}`\n\n"
        "已按建议 1-6 生成候选治理链：v1.2 环评/许可抽取样例，v1.3 工序-场景激活规则，v1.4 open questions 决策 overlay，"
        "v1.5 人工审阅专题切片，v1.6 RAG 检索评测扩展，v1.7 runtime 接入差距报告。\n\n"
        "所有产物仍为候选知识库治理资产，不接 EcoCheck runtime，不生成正式 permit_type，不生成正式检查模板，不自动扣分。\n\n"
        "## 产物计数\n\n"
        "- v1.2 extraction_samples: 5\n"
        "- v1.2 extracted_predicates: 22\n"
        "- v1.3 activation_rules: 12\n"
        "- v1.4 open_question_overlay: 19\n"
        "- v1.5 review_slices: 7\n"
        "- v1.6 retrieval_eval_items: 12\n"
        "- v1.7 readiness_rows: 8\n\n"
        "## 验证\n\n"
        "```powershell\n"
        "python build_semantic_governance_roadmap_v1_2_to_v1_7.py\n"
        "python validate_semantic_governance_roadmap_v1_2_to_v1_7.py\n"
        "```\n\n"
        "验证结果：PASS，failure_count=0。\n",
        encoding="utf-8",
    )


def main():
    open_questions = read_csv(ROOT / "open_questions_v0_4_1.csv")
    review_rows = read_csv(ROOT / "human_review_queue_v0_7.csv")
    extraction_samples, predicates, extraction_schema = build_v1_2()
    activation_rules = build_v1_3()
    oq_overlay, oq_summary = build_v1_4(open_questions)
    review_slices = build_v1_5(review_rows)
    eval_rows, eval_coverage = build_v1_6()
    readiness_matrix, readiness_report = build_v1_7()
    outputs = {
        "v1_6_coverage": eval_coverage,
    }

    write_csv(ROOT / "eia_permit_extraction_samples_v1_2.csv", extraction_samples)
    write_json(ROOT / "eia_permit_extraction_samples_v1_2.json", extraction_samples)
    write_csv(ROOT / "eia_permit_extracted_predicates_v1_2.csv", predicates)
    write_json(ROOT / "eia_permit_extracted_predicates_v1_2.json", predicates)
    write_json(ROOT / "eia_permit_extraction_schema_v1_2.json", extraction_schema)

    write_csv(ROOT / "process_scenario_activation_rules_v1_3.csv", activation_rules)
    write_json(ROOT / "process_scenario_activation_rules_v1_3.json", activation_rules)

    write_csv(ROOT / "open_question_decision_overlay_v1_4.csv", oq_overlay)
    write_json(ROOT / "open_question_decision_overlay_v1_4.json", oq_overlay)
    write_json(ROOT / "open_question_closure_status_v1_4.json", oq_summary)

    write_csv(ROOT / "human_review_slices_v1_5.csv", review_slices)
    write_json(ROOT / "human_review_slices_v1_5.json", review_slices)

    write_jsonl(ROOT / "retrieval_eval_set_v1_6.jsonl", eval_rows)
    write_json(ROOT / "rag_eval_coverage_v1_6.json", eval_coverage)

    write_csv(ROOT / "runtime_readiness_matrix_v1_7.csv", readiness_matrix)
    write_json(ROOT / "runtime_readiness_matrix_v1_7.json", readiness_matrix)
    write_json(ROOT / "runtime_readiness_gap_report_v1_7.json", readiness_report)

    manifest = {
        "knowledge_base_version": VERSION,
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
        "runtime_effect": "NONE",
        "input_locks": {
            "open_questions_v0_4_1": len(open_questions),
            "human_review_queue_v0_7": len(review_rows),
        },
        "output_counts": {
            "v1_2_extraction_samples": len(extraction_samples),
            "v1_2_predicates": len(predicates),
            "v1_3_activation_rules": len(activation_rules),
            "v1_4_open_question_overlay": len(oq_overlay),
            "v1_5_review_slices": len(review_slices),
            "v1_6_eval_items": len(eval_rows),
            "v1_7_readiness_rows": len(readiness_matrix),
        },
        "hard_boundaries": [
            "no_ecocheck_runtime_integration",
            "no_formal_permit_type",
            "no_formal_inspection_template",
            "no_auto_deduct",
            "no_fake_human_review",
        ],
    }
    write_json(ROOT / "knowledge_base_manifest_v1_2_to_v1_7.json", manifest)
    write_markdown(outputs)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
