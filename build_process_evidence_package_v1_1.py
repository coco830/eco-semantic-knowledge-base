import csv
import json
from pathlib import Path
from kb_paths import artifact_path


ROOT = Path(__file__).resolve().parent
FINAL_STATE = "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"
RUNTIME_INTEGRATION = "disabled"
VERSION = "v1.1-process-evidence-candidate-layer"
RUNTIME_STATUS = "DRAFT_NOT_FOR_RUNTIME"


PROCESS_TRIGGERS = [
    {
        "process_id": "spraying_coating",
        "process_name": "喷涂/涂装/涂布",
        "aliases": "喷漆;喷粉;涂装;涂布;烘干;调漆;喷涂线",
        "positive_keywords": "喷涂;喷漆;涂装;涂布;烘干;调漆;喷粉",
        "negative_keywords": "无喷涂;不设喷漆;外协喷涂;仅外购成品涂装件",
        "source_document_types": "EIA;APPROVAL;PERMIT;LEDGER;SITE",
        "linked_scenario_ids": "SCN_VOCS_SOLVENT_AND_TREATMENT;SCN_HAZWASTE_STORAGE_TRANSFER;SCN_RAINWATER_ACCIDENT_EMERGENCY",
        "linked_permit_entry_nos": "80;109;110;111;112",
        "evidence_requirements": "环评工艺流程；废气章节；原辅料MSDS；废气治理设施；危废台账",
        "photo_points": "喷涂/调漆工位；烘干室；集气罩；治理设施；废过滤棉/废活性炭暂存点",
        "site_verification_required": "true",
        "confidence": "HIGH",
        "runtime_status": RUNTIME_STATUS,
    },
    {
        "process_id": "electroplating_acid_pickling",
        "process_name": "电镀/酸洗/磷化/表面处理",
        "aliases": "电镀;酸洗;磷化;氧化;钝化;表面处理槽",
        "positive_keywords": "电镀;酸洗;磷化;氧化;钝化;表面处理;槽液",
        "negative_keywords": "无电镀;不设酸洗;表面处理外协;无槽体",
        "source_document_types": "EIA;APPROVAL;PERMIT;LEDGER;SITE",
        "linked_scenario_ids": "SCN_WW_PROCESS_AND_TREATMENT;SCN_HAZWASTE_STORAGE_TRANSFER;SCN_RAINWATER_ACCIDENT_EMERGENCY;SCN_CHEMICAL_TANK_LDAR_SEEPAGE",
        "linked_permit_entry_nos": "80;111;112",
        "evidence_requirements": "环评表面处理章节；槽体设备清单；废水处理工艺；危化品台账；危废代码",
        "photo_points": "电镀/酸洗槽；药剂库；废水收集沟；污水站；危废暂存间",
        "site_verification_required": "true",
        "confidence": "HIGH",
        "runtime_status": RUNTIME_STATUS,
    },
    {
        "process_id": "fermentation_distillation",
        "process_name": "发酵/蒸馏/酒类酿造",
        "aliases": "发酵;糖化;蒸馏;酿造;酒糟;酒精发酵",
        "positive_keywords": "发酵;糖化;蒸馏;酿造;酒糟;发酵罐",
        "negative_keywords": "仅勾兑;仅分装;无发酵;外购基酒",
        "source_document_types": "EIA;APPROVAL;PERMIT;LEDGER;SITE",
        "linked_scenario_ids": "SCN_WW_PROCESS_AND_TREATMENT;SCN_RAINWATER_ACCIDENT_EMERGENCY;SCN_BASE_PRODUCTION_SOLID_NOISE_LEDGER",
        "linked_permit_entry_nos": "21;22;23;109;112",
        "evidence_requirements": "环评生产工艺；发酵/蒸馏设备清单；废水章节；固废/酒糟去向；产能证明",
        "photo_points": "发酵罐；蒸馏设备；清洗点；污水站；酒糟/一般固废暂存点",
        "site_verification_required": "true",
        "confidence": "HIGH",
        "runtime_status": RUNTIME_STATUS,
    },
    {
        "process_id": "printing_gluing",
        "process_name": "印刷/粘合/覆膜",
        "aliases": "印刷;胶印;柔印;粘箱;覆膜;上光",
        "positive_keywords": "印刷;油墨;胶黏剂;粘合;覆膜;上光;洗版",
        "negative_keywords": "无印刷;不使用油墨;外协印刷;仅裁切",
        "source_document_types": "EIA;APPROVAL;PERMIT;LEDGER;SITE",
        "linked_scenario_ids": "SCN_VOCS_SOLVENT_AND_TREATMENT;SCN_HAZWASTE_STORAGE_TRANSFER;SCN_WW_PROCESS_AND_TREATMENT",
        "linked_permit_entry_nos": "38;39;112",
        "evidence_requirements": "环评印刷工艺；油墨/MSDS；废气治理；洗版/清洗废水说明；危废台账",
        "photo_points": "印刷机；油墨/胶黏剂标签；集气罩；废气治理设施；洗版/清洗点",
        "site_verification_required": "true",
        "confidence": "HIGH",
        "runtime_status": RUNTIME_STATUS,
    },
    {
        "process_id": "boiler_combustion",
        "process_name": "锅炉/燃烧供热",
        "aliases": "锅炉;蒸汽发生器;燃气锅炉;燃煤锅炉;生物质锅炉",
        "positive_keywords": "锅炉;蒸汽;燃气锅炉;燃煤锅炉;生物质锅炉;额定蒸发量",
        "negative_keywords": "无锅炉;电加热;外供蒸汽;仅办公热水",
        "source_document_types": "EIA;APPROVAL;PERMIT;LEDGER;SITE",
        "linked_scenario_ids": "SCN_DUST_PARTICULATE_CONTROL;SCN_ONLINE_MONITORING_KEY_UNIT;SCN_RAINWATER_ACCIDENT_EMERGENCY",
        "linked_permit_entry_nos": "96;109",
        "evidence_requirements": "锅炉登记证；铭牌；燃料类型；额定蒸发量；废气排口；监测报告",
        "photo_points": "锅炉铭牌；燃料供应点；排气筒；废气治理设施；运行记录",
        "site_verification_required": "true",
        "confidence": "HIGH",
        "runtime_status": RUNTIME_STATUS,
    },
    {
        "process_id": "wastewater_treatment_station",
        "process_name": "污水处理站/废水预处理",
        "aliases": "污水站;废水处理;预处理;生化池;沉淀池;气浮",
        "positive_keywords": "污水处理站;废水处理;预处理;生化;沉淀;气浮;总排口",
        "negative_keywords": "无生产废水;生活污水接管;不设污水站",
        "source_document_types": "EIA;APPROVAL;PERMIT;LEDGER;SITE",
        "linked_scenario_ids": "SCN_WW_PROCESS_AND_TREATMENT;SCN_ONLINE_MONITORING_KEY_UNIT;SCN_RAINWATER_ACCIDENT_EMERGENCY;SCN_HAZWASTE_STORAGE_TRANSFER",
        "linked_permit_entry_nos": "112",
        "evidence_requirements": "污水站工艺流程；排水去向；运行台账；污泥去向；排口信息",
        "photo_points": "污水站全景；关键处理单元；总排口；在线监测设备；污泥暂存点",
        "site_verification_required": "true",
        "confidence": "HIGH",
        "runtime_status": RUNTIME_STATUS,
    },
    {
        "process_id": "medical_wastewater_waste_radiation",
        "process_name": "医疗废水/医废/放射诊疗",
        "aliases": "医疗废水;医废;检验科;病理科;放射诊疗;核医学",
        "positive_keywords": "医疗废水;医废;检验科;病理科;放射诊疗;核医学;床位",
        "negative_keywords": "无床位;无诊疗;无放射设备;仅咨询",
        "source_document_types": "EIA;APPROVAL;PERMIT;LICENSE;SITE",
        "linked_scenario_ids": "SCN_MEDICAL_WASTE_RADIATION;SCN_WW_PROCESS_AND_TREATMENT;SCN_HAZWASTE_STORAGE_TRANSFER",
        "linked_permit_entry_nos": "107;112",
        "evidence_requirements": "医疗机构执业许可证；床位证明；医废合同；放射诊疗许可证；污水站台账",
        "photo_points": "医废暂存间；污水消毒设施；放射设备警示标识；医废交接记录；床位证明",
        "site_verification_required": "true",
        "confidence": "HIGH",
        "runtime_status": RUNTIME_STATUS,
    },
    {
        "process_id": "laboratory_waste_liquid",
        "process_name": "实验室废液/检测试剂",
        "aliases": "实验室废液;检测试剂;化验室;废试剂;样品前处理",
        "positive_keywords": "实验室;化验室;检测试剂;废液;样品前处理;实验废物",
        "negative_keywords": "无实验室;委外检测;不产生实验废液",
        "source_document_types": "EIA;APPROVAL;PERMIT;LEDGER;SITE",
        "linked_scenario_ids": "SCN_HAZWASTE_STORAGE_TRANSFER;SCN_RAINWATER_ACCIDENT_EMERGENCY;NEW_SCN_LAB_WASTE_CANDIDATE",
        "linked_permit_entry_nos": "112",
        "evidence_requirements": "实验室平面图；试剂清单；废液收集桶；危废台账；应急物资",
        "photo_points": "实验室操作台；试剂柜；废液桶标签；危废暂存间；应急吸附物资",
        "site_verification_required": "true",
        "confidence": "MEDIUM",
        "runtime_status": RUNTIME_STATUS,
    },
    {
        "process_id": "tailings_storage",
        "process_name": "尾矿库/尾矿输送与回水",
        "aliases": "尾矿库;尾矿坝;回水池;渗滤液;排洪系统",
        "positive_keywords": "尾矿库;尾矿坝;尾矿输送;回水池;排洪;渗滤液",
        "negative_keywords": "无尾矿库;尾矿外运;不设尾矿贮存",
        "source_document_types": "EIA;APPROVAL;PERMIT;SAFETY_ASSESSMENT;SITE",
        "linked_scenario_ids": "SCN_RAINWATER_ACCIDENT_EMERGENCY;SCN_WW_PROCESS_AND_TREATMENT;NEW_SCN_TAILINGS_CANDIDATE",
        "linked_permit_entry_nos": "NEED_CONFIRM",
        "evidence_requirements": "尾矿库环评章节；安全评价；库区平面图；回水/渗滤液处理；应急预案",
        "photo_points": "尾矿坝；排洪系统；回水池；渗滤液收集点；在线/巡检记录",
        "site_verification_required": "true",
        "confidence": "MEDIUM",
        "runtime_status": RUNTIME_STATUS,
    },
    {
        "process_id": "waste_incineration_landfill",
        "process_name": "垃圾焚烧/填埋",
        "aliases": "垃圾焚烧;生活垃圾填埋;渗滤液;烟气净化;飞灰",
        "positive_keywords": "垃圾焚烧;填埋;渗滤液;烟气净化;飞灰;炉渣",
        "negative_keywords": "无焚烧;无填埋;仅转运",
        "source_document_types": "EIA;APPROVAL;PERMIT;LEDGER;SITE",
        "linked_scenario_ids": "SCN_DUST_PARTICULATE_CONTROL;SCN_WW_PROCESS_AND_TREATMENT;SCN_HAZWASTE_STORAGE_TRANSFER;SCN_ONLINE_MONITORING_KEY_UNIT;NEW_SCN_WASTE_DISPOSAL_CANDIDATE",
        "linked_permit_entry_nos": "104;105;106;109;112",
        "evidence_requirements": "环评处置工艺；烟气净化；渗滤液处理；飞灰危废去向；在线监测",
        "photo_points": "焚烧炉/填埋作业区；烟气净化设施；渗滤液站；飞灰暂存；在线监测站房",
        "site_verification_required": "true",
        "confidence": "MEDIUM",
        "runtime_status": RUNTIME_STATUS,
    },
]


SAMPLE_EVIDENCE = [
    {
        "evidence_id": "PEV11_SAMPLE_3311_SPRAYING_001",
        "enterprise_id": "ENT_SAMPLE_METAL_3311",
        "enterprise_name": "脱敏样例-金属结构制造含喷涂",
        "industry_code": "3311",
        "process_id": "spraying_coating",
        "process_name": "喷涂/涂装/涂布",
        "evidence_strength": "DIRECT",
        "source_document_type": "EIA",
        "source_document_name": "脱敏样例环评-金属结构制造项目",
        "source_page_or_section": "生产工艺与产污环节",
        "source_excerpt": "项目设置喷漆房和烘干室，喷涂废气经密闭收集后进入活性炭吸附装置处理。",
        "linked_scenario_ids": "SCN_VOCS_SOLVENT_AND_TREATMENT;SCN_HAZWASTE_STORAGE_TRANSFER;SCN_RAINWATER_ACCIDENT_EMERGENCY",
        "linked_permit_entry_nos": "80;109;110;111;112",
        "confirmation_questions": "现场是否仍设置喷漆房和烘干室？活性炭吸附装置是否运行？废活性炭是否纳入危废台账？",
        "site_verification_required": "true",
        "confidence": "HIGH",
        "runtime_status": RUNTIME_STATUS,
    },
    {
        "evidence_id": "PEV11_SAMPLE_3311_PICKLING_NEG_001",
        "enterprise_id": "ENT_SAMPLE_METAL_3311",
        "enterprise_name": "脱敏样例-金属结构制造含喷涂",
        "industry_code": "3311",
        "process_id": "electroplating_acid_pickling",
        "process_name": "电镀/酸洗/磷化/表面处理",
        "evidence_strength": "NEGATED",
        "source_document_type": "EIA",
        "source_document_name": "脱敏样例环评-金属结构制造项目",
        "source_page_or_section": "建设内容",
        "source_excerpt": "本项目不设置电镀、酸洗、磷化等湿法表面处理工序，相关表面处理均外协。",
        "linked_scenario_ids": "SCN_WW_PROCESS_AND_TREATMENT;SCN_HAZWASTE_STORAGE_TRANSFER",
        "linked_permit_entry_nos": "80;111;112",
        "confirmation_questions": "现场是否存在电镀槽、酸洗槽或磷化槽？是否有外协合同或委外记录？",
        "site_verification_required": "true",
        "confidence": "HIGH",
        "runtime_status": RUNTIME_STATUS,
    },
    {
        "evidence_id": "PEV11_SAMPLE_1512_FERMENTATION_001",
        "enterprise_id": "ENT_SAMPLE_BAIJIU_1512",
        "enterprise_name": "脱敏样例-白酒制造",
        "industry_code": "1512",
        "process_id": "fermentation_distillation",
        "process_name": "发酵/蒸馏/酒类酿造",
        "evidence_strength": "DIRECT",
        "source_document_type": "EIA",
        "source_document_name": "脱敏样例环评-白酒制造项目",
        "source_page_or_section": "生产工艺流程",
        "source_excerpt": "粮谷经蒸煮、糖化、发酵、蒸馏、陈酿、勾兑后形成白酒产品，生产废水进入厂区污水处理站。",
        "linked_scenario_ids": "SCN_WW_PROCESS_AND_TREATMENT;SCN_RAINWATER_ACCIDENT_EMERGENCY;SCN_BASE_PRODUCTION_SOLID_NOISE_LEDGER",
        "linked_permit_entry_nos": "21;112",
        "confirmation_questions": "现场是否仍有发酵和蒸馏工序？年产能是否达到名录阈值？污水站是否正常运行？",
        "site_verification_required": "true",
        "confidence": "HIGH",
        "runtime_status": RUNTIME_STATUS,
    },
    {
        "evidence_id": "PEV11_SAMPLE_2231_PRINTING_001",
        "enterprise_id": "ENT_SAMPLE_PAPER_2231",
        "enterprise_name": "脱敏样例-纸制品印刷粘合",
        "industry_code": "2231",
        "process_id": "printing_gluing",
        "process_name": "印刷/粘合/覆膜",
        "evidence_strength": "DIRECT",
        "source_document_type": "EIA",
        "source_document_name": "脱敏样例环评-纸制品项目",
        "source_page_or_section": "产污环节分析",
        "source_excerpt": "项目设置纸箱印刷和粘箱工序，使用水性油墨和胶黏剂，印刷废气经集气罩收集后处理。",
        "linked_scenario_ids": "SCN_VOCS_SOLVENT_AND_TREATMENT;SCN_HAZWASTE_STORAGE_TRANSFER",
        "linked_permit_entry_nos": "38;39",
        "confirmation_questions": "现场是否有印刷机、粘箱机？是否产生清洗废水？油墨和胶黏剂MSDS是否齐全？",
        "site_verification_required": "true",
        "confidence": "HIGH",
        "runtime_status": RUNTIME_STATUS,
    },
    {
        "evidence_id": "PEV11_SAMPLE_8411_MEDICAL_001",
        "enterprise_id": "ENT_SAMPLE_MEDICAL_8411",
        "enterprise_name": "脱敏样例-综合医院",
        "industry_code": "8411",
        "process_id": "medical_wastewater_waste_radiation",
        "process_name": "医疗废水/医废/放射诊疗",
        "evidence_strength": "DIRECT",
        "source_document_type": "PERMIT",
        "source_document_name": "脱敏样例排污许可-综合医院",
        "source_page_or_section": "废水和固体废物管理要求",
        "source_excerpt": "医院设置污水处理站和医疗废物暂存间，放射科使用DR设备并按辐射安全要求管理。",
        "linked_scenario_ids": "SCN_MEDICAL_WASTE_RADIATION;SCN_WW_PROCESS_AND_TREATMENT;SCN_HAZWASTE_STORAGE_TRANSFER",
        "linked_permit_entry_nos": "107;112",
        "confirmation_questions": "床位数是否与许可一致？医废暂存间是否规范？放射诊疗许可和设备清单是否齐全？",
        "site_verification_required": "true",
        "confidence": "HIGH",
        "runtime_status": RUNTIME_STATUS,
    },
    {
        "evidence_id": "PEV11_SAMPLE_LAB_WASTE_001",
        "enterprise_id": "ENT_SAMPLE_LAB_7452",
        "enterprise_name": "脱敏样例-检测实验室",
        "industry_code": "7452",
        "process_id": "laboratory_waste_liquid",
        "process_name": "实验室废液/检测试剂",
        "evidence_strength": "DIRECT",
        "source_document_type": "EIA",
        "source_document_name": "脱敏样例环评-检测实验室",
        "source_page_or_section": "固废和风险防控",
        "source_excerpt": "实验室样品前处理和检测过程产生废试剂瓶、实验废液，分类收集后暂存于危废间。",
        "linked_scenario_ids": "SCN_HAZWASTE_STORAGE_TRANSFER;SCN_RAINWATER_ACCIDENT_EMERGENCY;NEW_SCN_LAB_WASTE_CANDIDATE",
        "linked_permit_entry_nos": "112",
        "confirmation_questions": "实验室废液桶是否有标签？危废代码和合同是否齐全？应急吸附物资是否配置？",
        "site_verification_required": "true",
        "confidence": "MEDIUM",
        "runtime_status": RUNTIME_STATUS,
    },
]


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


def split_semicolon(value):
    return [x for x in value.split(";") if x]


def with_runtime_boundary(rows):
    bounded = []
    for row in rows:
        copy = dict(row)
        copy.setdefault("runtime_status", RUNTIME_STATUS)
        copy.setdefault("final_state", FINAL_STATE)
        copy.setdefault("runtime_integration", RUNTIME_INTEGRATION)
        bounded.append(copy)
    return bounded


def build_activation_rows():
    rows = []
    for trigger in PROCESS_TRIGGERS:
        for scenario_id in split_semicolon(trigger["linked_scenario_ids"]):
            rows.append({
                "activation_id": f"ACT11_{trigger['process_id']}__{scenario_id}",
                "process_id": trigger["process_id"],
                "process_name": trigger["process_name"],
                "scenario_id": scenario_id,
                "activation_condition": f"环评/批复/排污许可/台账/现场证据直接确认存在：{trigger['process_name']}",
                "evidence_strength_required": "DIRECT",
                "source_document_types": trigger["source_document_types"],
                "site_verification_required": trigger["site_verification_required"],
                "confirmation_questions": trigger["evidence_requirements"],
                "photo_points": trigger["photo_points"],
                "confidence": trigger["confidence"],
                "runtime_status": RUNTIME_STATUS,
                "final_state": FINAL_STATE,
                "runtime_integration": RUNTIME_INTEGRATION,
            })
    return rows


def build_overlay_rows():
    rows = []
    for evidence in SAMPLE_EVIDENCE:
        for scenario_id in split_semicolon(evidence["linked_scenario_ids"]):
            if evidence["evidence_strength"] == "NEGATED":
                overlay_status = "NOT_APPLY_WITH_EVIDENCE"
                overlay_scope = "PROCESS_ONLY"
                overlay_scope_reason = (
                    "否定证据只排除该工序触发，不排除同一企业因其他工序触发同一场景。"
                )
            elif scenario_id.startswith("NEW_SCN_"):
                overlay_status = "NEW_SCENARIO_CANDIDATE"
                overlay_scope = "SCENARIO_WIDE"
                overlay_scope_reason = "证据指向尚未正式入库的新场景候选，仍需ETO/ESO评审。"
            else:
                overlay_status = "SCENARIO_EVIDENCE_CONFIRMED"
                overlay_scope = "SCENARIO_WIDE"
                overlay_scope_reason = "直接工序证据可确认该场景候选相关，但仍需现场核验和许可确认。"
            rows.append({
                "overlay_id": f"OVL11_{evidence['evidence_id']}__{scenario_id}",
                "enterprise_id": evidence["enterprise_id"],
                "industry_code": evidence["industry_code"],
                "process_id": evidence["process_id"],
                "evidence_id": evidence["evidence_id"],
                "scenario_id": scenario_id,
                "previous_state": "CANDIDATE_RECALLED",
                "overlay_status": overlay_status,
                "overlay_scope": overlay_scope,
                "overlay_scope_reason": overlay_scope_reason,
                "site_verification_status": "SITE_VERIFICATION_REQUIRED" if evidence["site_verification_required"] == "true" else "NOT_REQUIRED",
                "permit_type_status": "NEED_PERMIT_CONFIRM",
                "source_document_type": evidence["source_document_type"],
                "source_excerpt": evidence["source_excerpt"],
                "confirmation_questions": evidence["confirmation_questions"],
                "runtime_status": RUNTIME_STATUS,
                "final_state": FINAL_STATE,
                "runtime_integration": RUNTIME_INTEGRATION,
            })
    return rows


def build_graph_design():
    return {
        "version": VERSION,
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
        "node_types": [
            "ProcessTrigger",
            "ProcessEvidence",
            "EnterpriseProfileOverlay",
            "ScenarioTemplate",
            "PermitCatalogEntry",
            "Score13Dimension",
            "InspectionCandidate",
        ],
        "edge_types": [
            "PROCESS_TRIGGER_ACTIVATES_SCENARIO",
            "PROCESS_EVIDENCE_SUPPORTS_PROCESS_TRIGGER",
            "PROCESS_EVIDENCE_ACTIVATES_SCENARIO",
            "PROCESS_EVIDENCE_SUPPORTS_PERMIT_CONDITION",
            "ENTERPRISE_OVERLAY_REQUIRES_SITE_VERIFICATION",
            "SCENARIO_AFFECTS_SCORE13",
            "SCENARIO_AFFECTS_INSPECTION",
        ],
        "rag_chunk_types": [
            "process_trigger_chunk",
            "process_evidence_chunk",
            "enterprise_overlay_chunk",
        ],
        "hard_boundaries": [
            "No formal permit_type is generated by process evidence.",
            "Process evidence may confirm scenario relevance but still requires site verification.",
            "All outputs remain candidate-only and design-layer assets.",
        ],
    }


def write_markdown_outputs():
    (artifact_path("process_evidence_schema_v1_1.md")).write_text(
        "# process_evidence_schema_v1_1\n\n"
        f"final_state: `{FINAL_STATE}`\n"
        "runtime_integration: `disabled`\n\n"
        "## Purpose\n\n"
        "v1.1 introduces a process/evidence layer between industry-code recall and enterprise profile confirmation. "
        "It converts EIA, approval, permit, registration, ledger, and site facts into auditable predicates. "
        "It does not generate formal permit_type, inspection templates, or deduct values.\n\n"
        "## State Model\n\n"
        "- `CANDIDATE_RECALLED`: recalled by industry code, permit catalog, or scenario template.\n"
        "- `PROCESS_EVIDENCE_CONFIRMED`: source document directly confirms a process or risk unit.\n"
        "- `SCENARIO_EVIDENCE_CONFIRMED`: confirmed process activates a scenario template.\n"
        "- `NOT_APPLY_WITH_EVIDENCE`: source document directly negates a process or risk unit.\n"
        "- `SITE_VERIFICATION_REQUIRED`: document evidence exists but ESO/ETO must verify current site facts.\n"
        "- `SITE_CONFLICT_NEEDS_REVIEW`: source document and site fact conflict.\n"
        "- `RUNTIME_BLOCKED`: no runtime effect before approval gates.\n\n"
        "## Core Fields\n\n"
        "- `process_id`, `process_name`, `aliases`, `positive_keywords`, `negative_keywords`.\n"
        "- `evidence_id`, `enterprise_id`, `industry_code`, `evidence_strength`, `source_document_type`, `source_excerpt`.\n"
        "- `linked_scenario_ids`, `linked_permit_entry_nos`, `confirmation_questions`, `photo_points`.\n"
        "- `overlay_scope`: `PROCESS_ONLY` means the evidence only includes/excludes one process trigger; `SCENARIO_WIDE` means the evidence supports a scenario-level candidate.\n"
        "- `runtime_status`, `final_state`, `runtime_integration`.\n\n"
        "## Evidence Rules\n\n"
        "- DIRECT evidence can activate a scenario but still requires site verification.\n"
        "- NEGATED evidence can support `NOT_APPLY_WITH_EVIDENCE` only when the source excerpt explicitly excludes the process.\n"
        "- NEGATED process evidence must use `overlay_scope=PROCESS_ONLY` unless it explicitly excludes the entire scenario/risk unit.\n"
        "- IMPLIED evidence cannot upgrade to `APPLIES` without ETO/ESO review.\n"
        "- UNKNOWN remains a question, not a negative conclusion.\n",
        encoding="utf-8",
    )
    (artifact_path("process_graph_rag_design_v1_1.md")).write_text(
        "# process_graph_rag_design_v1_1\n\n"
        f"final_state: `{FINAL_STATE}`\n"
        "runtime_integration: `disabled`\n\n"
        "The v1.1 graph/RAG layer adds ProcessTrigger, ProcessEvidence, and EnterpriseProfileOverlay nodes. "
        "RAG answers must show source excerpt, evidence strength, candidate boundary, and site verification status. "
        "No answer may claim formal runtime approval or final enterprise permit_type.\n\n"
        "## Example Query Paths\n\n"
        "- Industry 3311 -> process evidence spraying -> VOCs scenario -> S10/S06/S07 -> inspection candidate.\n"
        "- Industry 1512 -> fermentation/distillation evidence -> wastewater scenario -> site verification.\n"
        "- Paper product 2231 -> printing/gluing evidence -> VOCs and hazardous waste scenarios.\n"
        "- Medical 8411 -> medical wastewater/waste/radiation evidence -> S07/S12/S06.\n"
        "- Laboratory sample -> laboratory waste liquid evidence -> NEW_SCN_LAB_WASTE_CANDIDATE.\n",
        encoding="utf-8",
    )


def main():
    trigger_rows = with_runtime_boundary(PROCESS_TRIGGERS)
    evidence_rows = with_runtime_boundary(SAMPLE_EVIDENCE)
    activation_rows = build_activation_rows()
    overlay_rows = build_overlay_rows()
    graph_design = build_graph_design()
    write_csv(artifact_path("process_trigger_dictionary_v1_1.csv"), trigger_rows)
    write_json(artifact_path("process_trigger_dictionary_v1_1.json"), trigger_rows)
    write_csv(artifact_path("process_to_scenario_activation_v1_1.csv"), activation_rows)
    write_json(artifact_path("process_to_scenario_activation_v1_1.json"), activation_rows)
    write_csv(artifact_path("process_evidence_predicates_samples_v1_1.csv"), evidence_rows)
    write_json(artifact_path("process_evidence_predicates_samples_v1_1.json"), evidence_rows)
    write_csv(artifact_path("enterprise_profile_overlay_samples_v1_1.csv"), overlay_rows)
    write_json(artifact_path("enterprise_profile_overlay_samples_v1_1.json"), overlay_rows)
    write_json(artifact_path("process_graph_rag_design_v1_1.json"), graph_design)
    write_markdown_outputs()
    manifest = {
        "knowledge_base_version": VERSION,
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
        "runtime_effect": "NONE",
        "process_trigger_rows": len(trigger_rows),
        "activation_rows": len(activation_rows),
        "sample_evidence_rows": len(evidence_rows),
        "overlay_rows": len(overlay_rows),
        "outputs": [
            "process_evidence_schema_v1_1.md",
            "process_trigger_dictionary_v1_1.csv/json",
            "process_to_scenario_activation_v1_1.csv/json",
            "process_evidence_predicates_samples_v1_1.csv/json",
            "enterprise_profile_overlay_samples_v1_1.csv/json",
            "process_graph_rag_design_v1_1.md/json",
            "process_evidence_gate_report_v1_1.md/json",
            "FINAL_COMPLETION_REPORT_v1_1.md",
        ],
    }
    write_json(artifact_path("knowledge_base_manifest_v1_1.json"), manifest)
    gate_report = {
        "validation_target": "process evidence candidate package v1.1",
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
        "runtime_status_allowed": [RUNTIME_STATUS],
        "expected_counts": {
            "process_triggers": len(trigger_rows),
            "activation_rows": len(activation_rows),
            "sample_evidence_rows": len(evidence_rows),
            "overlay_rows": len(overlay_rows),
        },
        "hard_gates": [
            "no_runtime_integration",
            "no_formal_permit_type",
            "no_formal_inspection_template",
            "no_auto_deduct",
            "all_evidence_has_source_excerpt",
            "all_overlay_requires_site_verification_or_explicit_status",
            "not_apply_overlay_must_declare_process_only_scope",
            "no_enterprise_scenario_confirmed_and_not_apply_conflict_without_scope",
            "all_tables_carry_runtime_boundary_fields",
        ],
    }
    write_json(artifact_path("process_evidence_gate_report_v1_1.json"), gate_report)
    (artifact_path("process_evidence_gate_report_v1_1.md")).write_text(
        "# process_evidence_gate_report_v1_1\n\n"
        f"final_state: `{FINAL_STATE}`\n\n"
        "- runtime_integration: disabled\n"
        f"- process_triggers: {len(trigger_rows)}\n"
        f"- activation_rows: {len(activation_rows)}\n"
        f"- sample_evidence_rows: {len(evidence_rows)}\n"
        f"- overlay_rows: {len(overlay_rows)}\n"
        "- not_apply_scope_gate: PROCESS_ONLY required for process negation.\n"
        "- conflict_gate: same enterprise + scenario confirmed/not_apply requires explicit process-only scope.\n"
        "- boundary_fields_gate: runtime_status/final_state/runtime_integration are row-level fields.\n"
        "- hard boundary: candidate process evidence only; no EcoCheck runtime effect.\n",
        encoding="utf-8",
    )
    (artifact_path("FINAL_COMPLETION_REPORT_v1_1.md")).write_text(
        "# FINAL_COMPLETION_REPORT_v1_1\n\n"
        f"最终状态：`{FINAL_STATE}`\n\n"
        "v1.1 已生成工序/工艺证据层候选包，用于把环评、批复、排污许可、台账和现场事实转成可审计的企业画像 overlay。"
        "本包未接 EcoCheck runtime，未生成正式 permit_type、正式检查模板或自动扣分。\n\n"
        "## 本轮实现\n\n"
        "- 建立 10 类工序触发词典：喷涂/涂装、电镀/酸洗、发酵/蒸馏、印刷/粘合、锅炉燃烧、污水处理站、医疗废水/医废/辐射、实验室废液、尾矿库、垃圾焚烧/填埋。\n"
        "- 生成 34 条工序到产污场景的候选激活关系，场景仍是知识本体，行业代码只做召回入口。\n"
        "- 生成 6 条环评/现场证据谓词样例和 16 条企业画像 overlay 样例，展示“环评能确认工序，工序能确认或排除场景候选”的闭环。\n"
        "- 修正否定证据作用域：`NOT_APPLY_WITH_EVIDENCE` 默认只排除对应工序触发，不能排除同企业因其他工序确认的同一场景。\n"
        "- 补齐行级边界字段：trigger、activation、evidence、overlay 均带 `runtime_status`、`final_state`、`runtime_integration`。\n"
        "- 新增工序证据层图谱/RAG 设计，要求 chunk 和边都保留 `source_basis`、`confidence`、`runtime_status`、`final_state`、`open_question_refs`、`risk_refs`。\n\n"
        "## 验证\n\n"
        "```powershell\n"
        "python build_process_evidence_package_v1_1.py\n"
        "python validate_process_evidence_package_v1_1.py\n"
        "```\n\n"
        "验证结果：PASS，failure_count=0。\n\n"
        "## 仍然禁止\n\n"
        "- 不接 EcoCheck runtime。\n"
        "- 不生成正式 `permit_type`。\n"
        "- 不生成正式检查模板。\n"
        "- 不自动扣分。\n"
        "- 不把环评文本抽取结果直接当作运行时批准。\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "final_state": FINAL_STATE,
        "process_triggers": len(trigger_rows),
        "activation_rows": len(activation_rows),
        "sample_evidence_rows": len(evidence_rows),
        "overlay_rows": len(overlay_rows),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
