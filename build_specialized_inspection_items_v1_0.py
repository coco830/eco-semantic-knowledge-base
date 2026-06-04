import csv
import hashlib
import json
import re
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VERSION = "v1.0-approved-specialized-inspection-items"
SCHEMA_VERSION = "approved-specialized-inspection-items.v1_0"
FINAL_STATE = "APPROVED_SPECIALIZED_INSPECTION_ITEMS_BASELINE"
RUNTIME_STATUS = "APPROVED_BASELINE"
RUNTIME_INTEGRATION = "approved_baseline_export_ready"
APPROVAL_STATUS = "HUMAN_APPROVED_BASELINE"
APPROVAL_SOURCE = "ETO_APPROVED_SPECIALIZED_INSPECTION_ITEMS_P1_2026-06-04"
SOURCE_FINAL_STATE = "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"
SOURCE_RUNTIME_INTEGRATION = "disabled"
TARGET_REPOSITORY = "coco830/eco-semantic-knowledge-base"

OUT_CSV = ROOT / "data" / "approved_baseline" / "approved_specialized_inspection_items_v1_0.csv"
OUT_MANIFEST = ROOT / "manifests" / "approved_specialized_inspection_items_manifest_v1_0.json"
OUT_GATE = ROOT / "reports" / "approved_specialized_inspection_items_gate_report_v1_0.json"
PROCESS_TRIGGER_CSV = ROOT / "data" / "process_evidence" / "process_trigger_dictionary_v1_1.csv"
ETO_REVIEW_MD = ROOT / "reports" / "ETO_SPECIALIZED_INSPECTION_ITEMS_REVIEW_PLAIN_v1_0.md"

FIELDS = [
    "item_id",
    "priority",
    "industry",
    "scenario",
    "chapter",
    "dimension",
    "title",
    "content",
    "threshold_text",
    "source_basis",
    "photo_points",
    "evidence_chain",
    "answer_policy",
    "source_process_id",
    "trigger_keywords",
    "not_applicable_when",
    "eto_review_decision",
    "eto_review_note",
    "approval_status",
    "approval_source",
    "runtime_status",
    "final_state",
    "runtime_integration",
    "approved_baseline_version",
    "source_candidate_boundary",
    "source_final_state",
    "source_runtime_integration",
    "knowledge_base_target_repository",
    "source_hash",
]

PROCESS_DIMENSION_MAP = {
    "spraying_coating": ("S10", "vocs_emission"),
    "electroplating_acid_pickling": ("S06", "wastewater_discharge_route"),
    "fermentation_distillation": ("S06", "wastewater_generation"),
    "printing_gluing": ("S10", "vocs_emission"),
    "boiler_combustion": ("S10", "boiler_combustion"),
    "wastewater_treatment_station": ("S06", "wastewater_station"),
    "medical_wastewater_waste_radiation": ("S06", "medical_waste"),
    "laboratory_waste_liquid": ("S07", "hazardous_waste"),
    "tailings_storage": ("S06", "rainwater_accident_risk"),
    "waste_incineration_landfill": ("S10", "dust_particulate"),
    "industrial_noise_source": ("S10", "noise_source"),
    "boundary_noise_monitoring": ("S10", "noise_source"),
    "night_operation_sensitive_receptor": ("S10", "noise_source"),
    "social_life_noise_source": ("S10", "noise_source"),
    "radiation_device_source": ("S12", "radiation"),
    "sealed_radioactive_source": ("S12", "radiation"),
    "radioactive_waste_storage": ("S12", "radiation"),
    "radioactive_waste_package_container": ("S12", "radiation"),
    "radioactive_waste_disposal_facility": ("S12", "radiation"),
    "radioactive_material_transport": ("S12", "radiation"),
    "norm_industrial_residue_radioactivity": ("S12", "radiation"),
    "uranium_thorium_mining_rad_waste": ("S12", "radiation"),
    "nuclear_fuel_effluent_decommissioning": ("S12", "radiation"),
    "building_material_slag_radionuclide": ("S12", "radiation"),
}

PROCESS_DETAIL_ITEMS = [
    {
        "process_id": "spraying_coating",
        "suffix": "LOW_VOCS_MSDS_LEDGER",
        "node": "源头替代与辅料台账",
        "title": "低VOCs涂料/油墨/胶黏剂替代及MSDS核查",
        "content": "核查调漆室、库房的涂料、稀释剂、固化剂包装标签及MSDS，确认是否符合国家低VOCs含量限值标准；对比采购台账、消耗台账与库存，防范企业隐瞒高VOCs溶剂使用。",
        "threshold_text": "低VOCs原辅料标签、MSDS、采购/消耗/库存台账应相互印证；发现高VOCs溶剂或台账不一致应判FAIL或NEED_CONFIRM",
        "photo_points": "原辅料包装桶清晰标签；MSDS手册关键页；出入库台账本",
        "evidence_chain": "原辅料包装标签；MSDS；采购台账；消耗台账；库存记录",
    },
    {
        "process_id": "spraying_coating",
        "suffix": "ENCLOSURE_MICRO_NEGATIVE_PRESSURE",
        "node": "无组织废气收集",
        "title": "调漆、喷涂、流平、烘干全流程封闭与微负压核查",
        "content": "检查调漆室、喷涂房和流平室是否完全封闭，门窗是否在非进出状态下常闭；使用风速仪或微压计确认开口处是否呈微负压；烘干废气是否单独收集处理。",
        "threshold_text": "开口控制风速≥0.3m/s；烘干废气应单独收集处理；无法实测时保守判NEED_CONFIRM",
        "photo_points": "密闭房门窗关闭状态；微压计/风速仪读数特写；车间整体集气管网",
        "evidence_chain": "密闭空间现场照片；风速仪或微压计读数；集气管网；烘干废气收集管线",
    },
    {
        "process_id": "spraying_coating",
        "suffix": "VOCS_TREATMENT_PARAMETERS",
        "node": "废气治理设施运行",
        "title": "末端VOCs处理设施关键运行参数闭环核查",
        "content": "燃烧类治理设施核查燃烧室温度是否达标、天然气消耗量是否合理；吸附类治理设施核查活性炭碘值、填充量、压差计读数及更换频次，并与危废产生量交叉比对。",
        "threshold_text": "RTO燃烧室温度通常应≥760℃；活性炭碘值、填充量、压差和更换记录应闭环；具体适用值以环评/设计/许可和设施说明为准",
        "photo_points": "RTO控制柜温度显示屏；天然气表读数；活性炭箱压差计；活性炭更换记录表",
        "evidence_chain": "治理设施控制参数；能源消耗记录；活性炭参数资料；更换记录；危废台账",
    },
    {
        "process_id": "electroplating_acid_pickling",
        "suffix": "HEAVY_METAL_SPECIAL_WASTEWATER_SEPARATION",
        "node": "废水分类分质收集",
        "title": "一类重金属及特殊废水（含氰、含铬、含镍）独立收集与防腐防渗核查",
        "content": "核实含氰废水、含六价铬废水、含镍废水是否在车间排口单独收集、单独预处理，严禁与其他废水混排；检查槽体下方、防腐蚀明管明沟的破损与渗漏情况。",
        "threshold_text": "含氰、含铬、含镍等特殊废水应独立收集、独立预处理；混排或防腐防渗破损应判FAIL",
        "photo_points": "各管线颜色或名称标识；车间排口采样点；槽下地沟防腐防渗层",
        "evidence_chain": "废水管线标识；车间排口；预处理设施；防腐防渗现场；运行记录",
    },
    {
        "process_id": "electroplating_acid_pickling",
        "suffix": "ACID_MIST_HOOD_SCRUBBER_DOSING",
        "node": "酸雾废气收集与处理",
        "title": "侧吸风罩收集效果及洗涤塔加药核查",
        "content": "检查表面处理槽边侧吸风罩是否有严重腐蚀、结晶、堵塞，抽风是否有效；核查酸雾洗涤塔循环水箱pH值，以及碱液自动加药装置是否正常工作。",
        "threshold_text": "侧吸风罩应有效收集且无严重堵塞；喷淋塔pH和加药记录应支持设施正常运行",
        "photo_points": "槽边吸风罩及结晶情况；喷淋塔循环液pH试纸/仪读数；加药桶液位及投加记录",
        "evidence_chain": "槽边吸风罩；喷淋塔pH读数；加药装置；投加记录；巡检记录",
    },
    {
        "process_id": "wastewater_treatment_station",
        "suffix": "DOSING_BIOCHEMICAL_OPERATION",
        "node": "加药与生化系统运行",
        "title": "药剂消耗闭环与生化池运行状态核查",
        "content": "对比PAC、PAM、碳源、酸碱药剂的采购清单与每日投加记录，防范设施空转；现场观察好氧池曝气是否均匀，厌氧/缺氧池搅拌是否正常，二沉池是否有大量翻泥跑泥现象。",
        "threshold_text": "药剂采购、库存、投加记录应闭环；曝气、搅拌、二沉池运行异常应判FAIL或NEED_CONFIRM",
        "photo_points": "药剂堆放区全景及标签；加药泵运行状态；生化池曝气/水色全景；二沉池出水堰口",
        "evidence_chain": "药剂采购清单；投加记录；加药泵状态；生化池现场；二沉池现场",
    },
    {
        "process_id": "wastewater_treatment_station",
        "suffix": "SLUDGE_DEWATERING_HAZWASTE_ATTRIBUTE",
        "node": "污泥处理与处置",
        "title": "脱水系统运行及污泥危废属性核查",
        "content": "检查板框或离心压滤机运行记录与台账产泥量是否匹配；核查污泥暂存库防渗防雨措施；涉重金属、化工、制药等行业的污泥必须核查是否按危废管理并建立转移联单闭环。",
        "threshold_text": "脱水运行记录与产泥台账应匹配；涉重金属/化工/制药污泥属性不清时应判NEED_CONFIRM并交ETO复核",
        "photo_points": "压滤机运行状态；现场脱水污泥存放形态；污泥库防渗措施；转移台账/电子联单",
        "evidence_chain": "压滤机运行记录；产泥台账；污泥库防渗防雨；属性判定资料；转移联单",
    },
    {
        "process_id": "boiler_combustion",
        "suffix": "DESULFURIZATION_DENITRATION_BYPRODUCTS",
        "node": "脱硫脱硝治理与副产物",
        "title": "氨水/尿素消耗、氨逃逸及脱硫药剂核查",
        "content": "检查SNCR/SCR脱硝系统的尿素或氨水消耗量是否与锅炉负荷匹配，是否存在氨逃逸过量造成二次污染；核对脱硫系统加药记录及脱硫石膏去向台账。",
        "threshold_text": "尿素/氨水消耗应与锅炉负荷匹配；氨逃逸、脱硫药剂和副产物去向应有记录闭环",
        "photo_points": "氨水/尿素储罐液位计；脱硝控制柜加药量截屏；在线监测氨逃逸数据；脱硫石膏暂存堆场",
        "evidence_chain": "脱硝加药记录；锅炉负荷；氨逃逸数据；脱硫加药记录；脱硫石膏去向台账",
    },
    {
        "process_id": "printing_gluing",
        "suffix": "CLEANING_SOLVENT_HAZWASTE_CLOSURE",
        "node": "清洗溶剂与危废管理",
        "title": "洗车水/洗版废液、废擦拭布及废包装物收集闭环核查",
        "content": "核查清洗设备时使用的洗车水、洗版液去向，现场废液收集桶是否密闭并置于防溢漏托盘上；沾染油墨的废擦拭布、废手套是否分类按危废收集；严防含VOCs废液混入下水道。",
        "threshold_text": "含VOCs废液、废擦拭布、废手套和废包装物应密闭分类收集并纳入危废台账；混入下水道应判FAIL",
        "photo_points": "印刷机旁废液收集桶及托盘；废擦拭布专用收集箱；危废台账洗车水转移记录",
        "evidence_chain": "废液收集桶；防溢漏托盘；废擦拭布收集箱；危废台账；转移记录",
    },
    {
        "process_id": "laboratory_waste_liquid",
        "suffix": "WASTE_LIQUID_COMPATIBILITY_STORAGE",
        "node": "废液相容性与安全贮存",
        "title": "含卤素、重金属及酸碱废液隔离贮存核查",
        "content": "严查实验室废液桶是否规范张贴成分明细标签；含卤素废液与非卤废液是否混放；酸性废液与氰化物、硫化物等极易产生有毒气体的废液是否严格物理隔离；废液桶是否配备防排气阀门。",
        "threshold_text": "废液桶应有成分明细标签；不相容废液应物理隔离；无标签或混放应判FAIL",
        "photo_points": "废液桶成分明细标签；不同废液隔离存放区；防爆或排气阀盖；二次防溢漏托盘",
        "evidence_chain": "废液标签；分类贮存区；不相容隔离措施；排气阀盖；二次防溢漏托盘",
    },
]


def basis_hash(source_basis):
    return "sha256:" + hashlib.sha256(source_basis.encode("utf-8")).hexdigest()


def read_eto_review():
    if not ETO_REVIEW_MD.exists():
        return {}
    text = ETO_REVIEW_MD.read_text(encoding="utf-8")
    marker = "`**ETO审核批复**`"
    marker_pos = text.find(marker)
    if marker_pos < 0:
        return {}
    payload = text[marker_pos + len(marker):].strip()
    try:
        decisions = json.loads(payload)
    except json.JSONDecodeError:
        return {}
    by_id = {}
    for item in decisions:
        system_id = str(item.get("系统 ID") or "").strip()
        if not system_id:
            continue
        by_id[system_id] = {
            "decision": str(item.get("ETO 结论") or item.get("ETO结论") or "").strip(),
            "note": str(item.get("修改意见") or item.get("说明") or "").strip(),
        }
    return by_id


ETO_REVIEW = read_eto_review()


def process_package_id(process_id):
    return "PROCESS_SPEC_" + re.sub(r"[^A-Z0-9]+", "_", process_id.upper()).strip("_")


def process_item_id(process_id, chapter):
    suffix = re.sub(r"[^A-Z0-9]+", "_", process_id.upper()).strip("_")
    return f"FIRST_{chapter}_SPEC_PROCESS_{suffix}"


def process_detail_item_id(process_id, chapter, detail_suffix):
    process_suffix = re.sub(r"[^A-Z0-9]+", "_", process_id.upper()).strip("_")
    detail = re.sub(r"[^A-Z0-9]+", "_", detail_suffix.upper()).strip("_")
    return f"FIRST_{chapter}_SPEC_PROCESS_{process_suffix}_{detail}"


def row(
    item_id,
    industry,
    scenario,
    chapter,
    dimension,
    title,
    content,
    threshold_text,
    source_basis,
    photo_points,
    evidence_chain,
    review_id=None,
    source_process_id="",
    trigger_keywords="",
    not_applicable_when="",
    source_candidate_boundary="approved from specialized P1 candidate review; source candidate remains not runtime",
):
    review = ETO_REVIEW.get(review_id or item_id, {})
    review_note = review.get("note", "")
    if review_note and "ETO批复口径" not in content:
        content = f"{content} ETO批复口径：{review_note}"
    return {
        "item_id": item_id,
        "priority": "P1",
        "industry": industry,
        "scenario": scenario,
        "chapter": chapter,
        "dimension": dimension,
        "title": title,
        "content": content,
        "threshold_text": threshold_text,
        "source_basis": source_basis,
        "photo_points": photo_points,
        "evidence_chain": evidence_chain,
        "answer_policy": '["PASS","FAIL","NA","NEED_CONFIRM"]',
        "source_process_id": source_process_id,
        "trigger_keywords": trigger_keywords,
        "not_applicable_when": not_applicable_when,
        "eto_review_decision": review.get("decision", ""),
        "eto_review_note": review_note,
        "approval_status": APPROVAL_STATUS,
        "approval_source": APPROVAL_SOURCE,
        "runtime_status": RUNTIME_STATUS,
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
        "approved_baseline_version": VERSION,
        "source_candidate_boundary": source_candidate_boundary,
        "source_final_state": SOURCE_FINAL_STATE,
        "source_runtime_integration": SOURCE_RUNTIME_INTEGRATION,
        "knowledge_base_target_repository": TARGET_REPOSITORY,
        "source_hash": basis_hash(source_basis),
    }


def base_rows():
    haz_basis = "GB 18597-2023《危险废物贮存污染控制标准》；HJ 1276-2022《危险废物识别标志设置技术规范》；HJ 1259-2022《危险废物管理计划和管理台账制定技术导则》"
    solid_law_basis = "《中华人民共和国固体废物污染环境防治法》；GB 18597-2023《危险废物贮存污染控制标准》；HJ 1259-2022《危险废物管理计划和管理台账制定技术导则》"
    med_basis = "《医疗废物管理条例》；HJ 421-2008《医疗废物专用包装袋、容器和警示标志标准》；医疗废物集中处置技术规范（试行）"
    water_basis = "GB 18466-2005《医疗机构水污染物排放标准》"
    return [
        row(
            "FIRST_S07_SPEC_HAZWASTE_FIVE_CODE_CONTAINER_QR",
            "危废产生企业",
            "危废五即一码",
            "S07",
            "solid_waste_hazardous_waste",
            "危废包装容器一物一码",
            "核查危险废物包装容器是否落实五即一码中的一物一码管理，容器标签或二维码应与危废类别、代码、重量、产生批次和贮存位置一致。",
            "每个危废包装容器一个数字识别码；不替代危废类别和标签内容核查",
            haz_basis,
            "危废包装容器二维码近照；危废标签全景；扫码页面或系统记录；同批次包装称重记录",
            "危废标签；二维码/数字识别码；称重记录；入库记录；危废管理平台记录",
        ),
        row(
            "FIRST_S07_SPEC_HAZWASTE_FIVE_CODE_WEIGHING",
            "危废产生企业",
            "危废五即一码",
            "S07",
            "solid_waste_hazardous_waste",
            "危废产生后即时称重",
            "核查危险废物产生后是否及时包装、称重并形成批次重量记录，现场重量、标签重量和台账重量应可相互追溯。",
            "称重记录应与容器码、入库记录、台账数量一致",
            haz_basis,
            "危废称重设备；称重单；标签重量字段；台账重量字段",
            "称重记录；容器码；入库单；危废管理台账",
        ),
        row(
            "FIRST_S07_SPEC_HAZWASTE_FIVE_CODE_INBOUND_SCAN",
            "危废产生企业",
            "危废五即一码",
            "S07",
            "solid_waste_hazardous_waste",
            "危废入库扫码与贮存位置绑定",
            "核查危废入库时是否扫码登记，系统记录应能对应贮存分区、容器码、危废代码、入库时间和经办人员。",
            "入库扫码记录应覆盖现场在库危废容器",
            haz_basis,
            "危废暂存间分区；扫码入库记录；容器码与分区标识同框照片",
            "扫码入库记录；分区标识；危废标签；库存台账",
        ),
        row(
            "FIRST_S07_SPEC_HAZWASTE_FIVE_CODE_STORAGE_SIGN",
            "危废产生企业",
            "危废五即一码",
            "S07",
            "solid_waste_hazardous_waste",
            "危废贮存设施和分区识别标志",
            "核查危废贮存设施、贮存分区、包装容器和标签是否按规范设置识别标志，五即一码不得替代现场标志和分区管理。",
            "贮存设施、分区、容器和包装物均需有对应识别标志",
            haz_basis,
            "贮存设施门牌；分区标志；危废标签；二维码；包装容器全景",
            "贮存设施标志；分区标志；危险废物标签；现场分区台账",
        ),
        row(
            "FIRST_S07_SPEC_HAZWASTE_FIVE_CODE_TRANSFER_LEDGER",
            "危废产生企业",
            "危废五即一码",
            "S07",
            "solid_waste_hazardous_waste",
            "危废出库转移联单与容器码闭环",
            "核查危废出库、转移联单、处置合同和容器码是否闭环一致，不得出现已转移但库存仍在、现场在库但系统无记录等异常。",
            "出库数量、联单数量、台账库存和容器码应闭环一致",
            haz_basis,
            "转移联单；出库扫码记录；库存台账；处置合同或接收证明",
            "电子联单；出库记录；处置合同；库存台账；容器码记录",
        ),
        row(
            "FIRST_S07_SPEC_HAZWASTE_CLASSIFIED_STORAGE",
            "危废产生企业",
            "危废暂存规范",
            "S07",
            "solid_waste_hazardous_waste",
            "危废分类分区贮存",
            "核查不同类别、形态和污染防治要求的危险废物是否分类分区贮存，避免相互混放、混装或与一般固废混存。",
            "不得与一般固废、生活垃圾或不相容危废混存",
            solid_law_basis,
            "危废间分区全景；各分区标签；一般固废点位；不同危废包装同框照片",
            "危废清单；贮存分区图；现场照片；危废管理台账",
        ),
        row(
            "FIRST_S07_SPEC_HAZWASTE_COMPATIBILITY_SEPARATION",
            "危废产生企业",
            "危废暂存规范",
            "S07",
            "solid_waste_hazardous_waste",
            "不相容危废隔离贮存",
            "核查酸碱、氧化还原、含水含油、易燃和反应性危废是否按相容性要求采取隔离、分区或独立包装措施。",
            "不相容危险废物不得无隔离混放",
            solid_law_basis,
            "酸碱废液分区；易燃危废区域；隔离托盘；包装密闭状态",
            "危废成分清单；MSDS；分区记录；现场照片",
        ),
        row(
            "FIRST_S07_SPEC_HAZWASTE_LEAKAGE_COLLECTION",
            "危废产生企业",
            "危废暂存规范",
            "S07",
            "solid_waste_hazardous_waste",
            "危废暂存防渗和泄漏收集",
            "核查危废贮存场所是否具备防渗、防雨、防流失、围堰或托盘等泄漏收集措施，地面和包装不得有明显渗漏痕迹。",
            "现场不得存在未收集的渗漏液或破损包装",
            solid_law_basis,
            "防渗地面；围堰或托盘；泄漏应急物资；破损包装或渗漏点",
            "现场设施照片；巡检记录；应急物资清单；整改记录",
        ),
        row(
            "FIRST_S13_SPEC_HAZWASTE_EMERGENCY_MATERIALS",
            "危废产生企业",
            "危废环境应急",
            "S13",
            "environmental_emergency_hazardous_waste",
            "危废泄漏应急物资和演练记录",
            "核查危废暂存间是否配置吸附棉、围堵物、收集桶、防护用品等应急物资，并有泄漏处置流程、培训或演练记录。",
            "应急物资应可用且与危废风险相匹配",
            solid_law_basis,
            "应急物资柜；吸附材料；收集桶；个人防护用品；演练记录",
            "应急预案；物资清单；培训记录；演练记录；现场照片",
        ),
        row(
            "FIRST_S07_SPEC_MEDWASTE_TEMP_STORAGE_SIGNAGE",
            "医疗机构",
            "医疗废物暂存",
            "S07",
            "solid_waste_medical_waste",
            "医废暂存间警示标志和专用包装",
            "核查医疗废物暂存间、周转箱、包装袋和警示标志是否规范，医疗废物不得混入生活垃圾或一般固废。",
            "医疗废物应使用专用包装、容器和警示标志",
            med_basis,
            "医废暂存间门牌；警示标志；黄色包装袋；周转箱；生活垃圾点位",
            "医废分类收集记录；包装容器照片；暂存间照片；交接登记",
        ),
        row(
            "FIRST_S07_SPEC_MEDWASTE_48H_TRANSFER",
            "医疗机构",
            "医疗废物暂存",
            "S07",
            "solid_waste_medical_waste",
            "医疗废物48小时内转运核查",
            "核查医疗废物收集、暂存和转运记录，重点确认暂存时间、交接登记和转运去向是否闭环。",
            "医疗废物原则上不超过48小时转运；特殊低温或集中处置规范另行核实",
            med_basis,
            "医废交接登记；暂存间库存；转运车辆或接收单；最近一次转运时间",
            "医废交接登记；转运联单；处置合同；暂存间库存照片",
        ),
        row(
            "FIRST_S07_SPEC_MEDWASTE_SHARPS_CONTAINER",
            "医疗机构",
            "医疗废物分类收集",
            "S07",
            "solid_waste_medical_waste",
            "损伤性医疗废物利器盒管理",
            "核查针头、刀片、玻片等损伤性医疗废物是否进入利器盒，利器盒是否防刺穿、密闭并及时封口转运。",
            "损伤性医疗废物不得散放或混入普通包装袋",
            med_basis,
            "治疗室利器盒；封口状态；暂存间利器盒；科室交接记录",
            "科室收集记录；利器盒照片；医废交接登记",
        ),
        row(
            "FIRST_S06_SPEC_HOSPITAL_RESIDUAL_CHLORINE_3_10",
            "医院",
            "医疗废水消毒",
            "S06",
            "wastewater_treatment_medical_disinfection",
            "医疗废水消毒接触池出口总余氯",
            "核查医院采用含氯消毒剂消毒时，消毒接触池出口总余氯是否处于工艺控制范围，并留存检测记录。",
            "3–10 mg/L",
            water_basis,
            "消毒接触池；加药装置；余氯检测仪或试纸；最近检测记录",
            "余氯检测记录；污水站运行台账；加药记录；排口或接触池照片",
        ),
        row(
            "FIRST_S06_SPEC_HOSPITAL_CONTACT_TIME_1H",
            "医院",
            "医疗废水消毒",
            "S06",
            "wastewater_treatment_medical_disinfection",
            "医疗废水消毒接触时间",
            "核查含氯消毒工艺的接触池设计、液位和运行记录，确认接触时间满足医疗机构水污染物排放标准的工艺控制要求。",
            "接触时间 ≥1 h",
            water_basis,
            "接触池全景；水位标尺；工艺流程图；运行台账",
            "污水站工艺图；运行台账；设计资料；现场照片",
        ),
        row(
            "FIRST_S06_SPEC_HOSPITAL_DISINFECTION_DOSING_RECORD",
            "医院",
            "医疗废水消毒",
            "S06",
            "wastewater_treatment_medical_disinfection",
            "医疗废水消毒加药和检测记录闭环",
            "核查消毒剂投加、余氯检测、污水站运行和异常处置记录是否闭环，避免仅有设备但无运行证据。",
            "加药记录、余氯检测和运行台账日期应连续可追溯",
            water_basis,
            "消毒剂桶或储罐；加药泵；运行台账；异常处置记录",
            "加药记录；余氯检测记录；污水站运行台账；异常处置记录",
        ),
    ]


def process_rows():
    with PROCESS_TRIGGER_CSV.open(encoding="utf-8-sig", newline="") as f:
        source_rows = list(csv.DictReader(f))
    out = []
    source_by_process = {}
    for source in source_rows:
        process_id = source["process_id"].strip()
        source_by_process[process_id] = source
        chapter, dimension = PROCESS_DIMENSION_MAP[process_id]
        process_name = source["process_name"].strip()
        positive_keywords = source["positive_keywords"].strip()
        negative_keywords = source["negative_keywords"].strip()
        evidence_requirements = source["evidence_requirements"].strip()
        photo_points = source["photo_points"].strip()
        source_basis = (
            "环评/批复/排污许可/台账/现场证据；"
            f"源工序包：{process_name}；"
            "ETO审核批复"
        )
        content = (
            f"核查企业是否存在【{process_name}】相关工序、设施或风险单元。"
            f"触发关键词：{positive_keywords}。"
            f"不适用条件：{negative_keywords}。"
            f"现场应核对：{evidence_requirements}。"
        )
        out.append(row(
            process_item_id(process_id, chapter),
            "工序/行业专项",
            process_name,
            chapter,
            dimension,
            f"{process_name}专项核查",
            content,
            "存在该工序/设施/风险单元即触发；明确不存在则NA；证据不足则NEED_CONFIRM",
            source_basis,
            photo_points,
            evidence_requirements,
            review_id=process_package_id(process_id),
            source_process_id=process_id,
            trigger_keywords=positive_keywords,
            not_applicable_when=negative_keywords,
            source_candidate_boundary="approved from process trigger dictionary v1.1 and ETO batch review; source candidate remains not runtime",
        ))
    for detail in PROCESS_DETAIL_ITEMS:
        process_id = detail["process_id"]
        source = source_by_process[process_id]
        chapter, dimension = PROCESS_DIMENSION_MAP[process_id]
        process_name = source["process_name"].strip()
        positive_keywords = source["positive_keywords"].strip()
        negative_keywords = source["negative_keywords"].strip()
        package_id = process_package_id(process_id)
        source_basis = (
            "ETO专项细化排查项；"
            f"源工序包：{process_name}；"
            "环评/批复/排污许可/台账/现场证据；"
            "ETO审核批复"
        )
        content = (
            f"排查节点：{detail['node']}。"
            f"核查内容：{detail['content']}"
        )
        out.append(row(
            process_detail_item_id(process_id, chapter, detail["suffix"]),
            "工序/行业专项",
            process_name,
            chapter,
            dimension,
            detail["title"],
            content,
            detail["threshold_text"],
            source_basis,
            detail["photo_points"],
            detail["evidence_chain"],
            review_id=package_id,
            source_process_id=process_id,
            trigger_keywords=positive_keywords,
            not_applicable_when=negative_keywords,
            source_candidate_boundary="approved from ETO supplied specialized detail checklist; source candidate remains not runtime",
        ))
    return out


def rows():
    return base_rows() + process_rows()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json_lf(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    tmp.replace(path)


def write_csv_lf(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    with tmp.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(data)
    tmp.replace(path)


def sha256_file(path):
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def update_artifact_manifest():
    path = ROOT / "artifact_manifest.json"
    data = read_json(path)
    artifacts = data.setdefault("artifacts", {})
    artifacts.update({
        "specialized_inspection_items_governance_v1_0.md": "docs/design/specialized_inspection_items_governance_v1_0.md",
        "approved_specialized_inspection_items_v1_0.csv": "data/approved_baseline/approved_specialized_inspection_items_v1_0.csv",
        "approved_specialized_inspection_items_manifest_v1_0.json": "manifests/approved_specialized_inspection_items_manifest_v1_0.json",
        "approved_specialized_inspection_items_gate_report_v1_0.json": "reports/approved_specialized_inspection_items_gate_report_v1_0.json",
        "ETO_SPECIALIZED_INSPECTION_ITEMS_REVIEW_PLAIN_v1_0.md": "reports/ETO_SPECIALIZED_INSPECTION_ITEMS_REVIEW_PLAIN_v1_0.md",
        "build_specialized_inspection_items_v1_0.py": "build_specialized_inspection_items_v1_0.py",
        "validate_specialized_inspection_items_v1_0.py": "validate_specialized_inspection_items_v1_0.py",
    })
    write_json_lf(path, data)


def main():
    update_artifact_manifest()
    data = rows()
    write_csv_lf(OUT_CSV, data)

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "knowledge_base_version": VERSION,
        "generated_on": date.today().isoformat(),
        "final_state": FINAL_STATE,
        "runtime_status": RUNTIME_STATUS,
        "runtime_integration": RUNTIME_INTEGRATION,
        "approval_status": APPROVAL_STATUS,
        "approval_source": APPROVAL_SOURCE,
        "approved_entry_count": len(data),
        "priority": "P1",
        "baseline_package_scope": "ECOCHECK_IMPORT_READY_KB_STAGING_ONLY",
        "downstream_target_repository": TARGET_REPOSITORY,
        "source_candidate_boundary": {
            "source_final_state": SOURCE_FINAL_STATE,
            "source_runtime_integration": SOURCE_RUNTIME_INTEGRATION,
            "not_for_runtime_boundary_preserved": True,
        },
        "runtime_contract": {
            "can_drive_specialized_inspection_item_import": True,
            "does_not_modify_runtime_integration": True,
            "does_not_auto_deduct_score": True,
            "formal_compliance_conclusion": "NOT_AUTHORIZED",
        },
        "required_coverage": {
            "hazwaste_five_code_items": 5,
            "hospital_residual_chlorine_threshold_text": "3–10 mg/L",
            "process_package_items": 24,
            "process_detail_items": len(PROCESS_DETAIL_ITEMS),
        },
        "outputs": {
            "baseline_csv": {
                "path": "data/approved_baseline/approved_specialized_inspection_items_v1_0.csv",
                "sha256": sha256_file(OUT_CSV),
            }
        },
        "source_artifacts": [
            "README.md",
            "artifact_manifest.json",
            "docs/design/specialized_inspection_items_governance_v1_0.md",
            "data/process_evidence/process_trigger_dictionary_v1_1.csv",
            "reports/ETO_SPECIALIZED_INSPECTION_ITEMS_REVIEW_PLAIN_v1_0.md",
            "manifests/approved_baseline_knowledge_manifest_v1_0.json",
            "manifests/pollutant_domain_approved_baseline_manifest_v8_5.json",
        ],
    }
    write_json_lf(OUT_MANIFEST, manifest)

    gate = {
        "validation_status": "PENDING_RUN_VALIDATE",
        "knowledge_base_version": VERSION,
        "final_state": FINAL_STATE,
        "runtime_status": RUNTIME_STATUS,
        "runtime_integration": RUNTIME_INTEGRATION,
        "approval_status": APPROVAL_STATUS,
        "approved_entry_count": len(data),
        "csv_sha256": sha256_file(OUT_CSV),
    }
    write_json_lf(OUT_GATE, gate)
    print(json.dumps(gate, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
