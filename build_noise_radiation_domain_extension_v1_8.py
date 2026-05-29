import csv
import json
from pathlib import Path

from kb_paths import artifact_path


ROOT = Path(__file__).resolve().parent
FINAL_STATE = "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"
RUNTIME_INTEGRATION = "disabled"
RUNTIME_STATUS = "DRAFT_NOT_FOR_RUNTIME"
RUNTIME_CANDIDATE = "CANDIDATE_ONLY"
VERSION = "v1.8-noise-radiation-domain-extension"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path, rows, fields=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    if not rows:
        fields = fields or []
    else:
        fields = fields or list(rows[0].keys())
    with tmp.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    tmp.replace(path)


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def split_items(value):
    return [part.strip() for part in (value or "").replace("；", ";").split(";") if part.strip()]


def join_items(items):
    return ";".join(items)


def with_boundary(row, runtime_status=RUNTIME_STATUS):
    copied = dict(row)
    copied.setdefault("runtime_status", runtime_status)
    copied.setdefault("final_state", FINAL_STATE)
    copied.setdefault("runtime_integration", RUNTIME_INTEGRATION)
    return copied


NOISE_SCENARIOS = [
    {
        "scenario_id": "SCN_NOISE_SOURCE_BOUNDARY_CONTROL",
        "scenario_name": "工业企业噪声源与厂界噪声控制",
        "aliases": ["工业噪声", "厂界噪声", "高噪声设备", "隔声减振", "噪声监测"],
        "tags_24": ["noise_source", "boundary_noise", "facility_operation", "monitoring_record", "site_environment"],
        "media_type": "noise",
        "facility_or_risk_unit": "空压机、风机、泵、破碎/粉磨/冲压/切割设备、冷却塔、厂界敏感点、隔声减振设施",
        "triggers": [
            "存在生产加工设备、动力设备、风机泵类、破碎粉磨、切割冲压、冷却塔或其他明显噪声源",
            "环评、排污许可、工业噪声技术规范或监测报告中出现厂界噪声、噪声源、隔声、减振、消声等要求",
        ],
        "not_applicable_conditions": [
            "仅办公、贸易、仓储且无固定噪声源或夜间生产活动",
            "现场确认无生产设备、无动力设备、无厂界噪声管理要求",
        ],
        "confirmation_questions": [
            "主要噪声源设备有哪些，是否与环评/许可一致？",
            "是否有隔声、减振、消声、距离衰减或厂房封闭措施？",
            "厂界噪声监测点位、昼夜生产时段和监测结果是否完整？",
            "是否存在夜间生产、投诉、周边敏感点或超标整改记录？",
        ],
        "evidence_requirements": [
            "环评噪声章节或排污许可工业噪声要求",
            "主要噪声源设备清单和厂区平面布置图",
            "厂界噪声监测报告或自行监测记录",
            "隔声减振消声设施运行/维护记录",
            "投诉、整改或夜间生产证明材料",
        ],
        "photo_points": [
            "主要高噪声设备及铭牌",
            "隔声罩、减振基础、消声器或厂房封闭措施",
            "厂界监测点位和周边敏感点方向",
            "夜间生产或异常噪声源现场",
            "噪声监测报告关键页",
        ],
        "related_regulations": [
            "中华人民共和国噪声污染防治法",
            "GB 12348-2008 工业企业厂界环境噪声排放标准",
            "HJ 1301-2023 排污许可证申请与核发技术规范 工业噪声",
        ],
        "domain": "noise",
        "extension_version": VERSION,
        "confidence": "HIGH",
        "runtime_status": RUNTIME_STATUS,
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
    },
    {
        "scenario_id": "SCN_NOISE_BOUNDARY_MONITORING_LEDGER",
        "scenario_name": "厂界噪声监测、执行标准与台账",
        "aliases": ["厂界噪声监测", "自行监测", "昼夜监测", "噪声执行标准", "监测点位"],
        "tags_24": ["boundary_noise", "noise_monitoring", "self_monitoring", "ledger_record", "permit_execution"],
        "media_type": "noise",
        "facility_or_risk_unit": "厂界监测点位、声环境功能区、昼夜生产时段、自行监测方案和监测报告",
        "triggers": [
            "环评、排污许可、自行监测方案或监测报告要求厂界噪声监测",
            "存在昼夜生产、连续生产、厂界功能区类别或GB 12348执行标准判定",
        ],
        "not_applicable_conditions": [
            "无厂界噪声管理要求且仅需现场噪声源初筛",
            "社会生活噪声场景应使用SCN_SOCIAL_LIFE_NOISE_SOURCE，不混用工业厂界标准",
        ],
        "confirmation_questions": [
            "厂界噪声执行标准、功能区类别和昼夜限值如何确定？",
            "自行监测方案、点位图、频次和监测报告是否完整？",
            "是否存在超标、异常、投诉或整改闭环？",
        ],
        "evidence_requirements": [
            "自行监测方案",
            "厂界噪声监测报告",
            "监测点位图",
            "执行标准和功能区类别说明",
            "超标整改或异常说明",
        ],
        "photo_points": [
            "厂界监测点位",
            "厂界四至和敏感方向",
            "监测报告关键页",
            "监测点位示意图",
            "噪声治理设施运行记录关键页",
        ],
        "related_regulations": [
            "GB 12348-2008 工业企业厂界环境噪声排放标准",
            "HJ 1301-2023 排污许可证申请与核发技术规范 工业噪声",
        ],
        "domain": "noise",
        "extension_version": VERSION,
        "confidence": "HIGH",
        "runtime_status": RUNTIME_STATUS,
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
    },
    {
        "scenario_id": "SCN_NOISE_SENSITIVE_RECEPTOR_NIGHT_OPERATION",
        "scenario_name": "夜间生产、敏感点与噪声投诉风险",
        "aliases": ["夜间噪声", "敏感点", "噪声投诉", "扰民风险", "夜间生产"],
        "tags_24": ["night_operation", "sensitive_receptor", "noise_complaint", "boundary_noise", "issue_closure"],
        "media_type": "noise",
        "facility_or_risk_unit": "夜间运行设备、厂界外居民/学校/医院等敏感点、投诉整改记录、隔声屏障",
        "triggers": [
            "存在夜间生产、连续生产或靠近居民、学校、医院、养老机构等声环境敏感点",
            "存在噪声投诉、夜间监测、限产整改、厂界超标或环评敏感点预测",
        ],
        "not_applicable_conditions": [
            "昼间单班生产、远离敏感目标且无投诉或夜间运行证据",
            "仅道路、铁路、航空或施工噪声且非本企业固定源管理对象",
        ],
        "confirmation_questions": [
            "企业是否夜间生产或连续运行？",
            "最近敏感点距离、方向和功能是什么？",
            "是否有投诉、夜间监测、限时运行或整改记录？",
        ],
        "evidence_requirements": [
            "生产班次或夜间运行记录",
            "敏感点位置图或环评敏感目标章节",
            "投诉/整改记录",
            "夜间厂界噪声监测报告",
            "隔声屏障、封闭厂房或限时运行措施证明",
        ],
        "photo_points": [
            "厂界到敏感点方向",
            "夜间运行设备或连续运行设施",
            "隔声屏障、封闭厂房或门窗隔声措施",
            "投诉整改记录关键页",
            "平面图中敏感方向标注",
        ],
        "related_regulations": [
            "中华人民共和国噪声污染防治法",
            "GB 12348-2008 工业企业厂界环境噪声排放标准",
        ],
        "domain": "noise",
        "extension_version": VERSION,
        "confidence": "MEDIUM",
        "runtime_status": RUNTIME_STATUS,
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
    },
    {
        "scenario_id": "SCN_SOCIAL_LIFE_NOISE_SOURCE",
        "scenario_name": "社会生活噪声与经营活动噪声源",
        "aliases": ["社会生活噪声", "商业经营噪声", "餐饮娱乐噪声", "空调外机", "扩声设备"],
        "tags_24": ["social_life_noise", "noise_source", "boundary_noise", "sensitive_receptor", "complaint_trace"],
        "media_type": "noise",
        "facility_or_risk_unit": "商业经营场所、餐饮娱乐扩声设备、空调/冷却塔外机、装卸区、周边敏感点",
        "triggers": [
            "存在商业经营、餐饮娱乐、扩声、装卸、冷却塔/空调外机等社会生活噪声源",
            "周边存在居民、学校、医院等声环境敏感目标或投诉记录",
        ],
        "not_applicable_conditions": [
            "非经营活动场所且无固定社会生活噪声源",
            "设备停用或拆除并有现场和台账证据",
        ],
        "confirmation_questions": [
            "是否存在扩声、装卸、空调外机、冷却塔或夜间经营活动？",
            "周边最近敏感点距离和方向是什么？",
            "是否有投诉、整改、限时经营或降噪措施？",
        ],
        "evidence_requirements": [
            "经营场所平面布置和设备清单",
            "噪声投诉或整改记录",
            "社会生活噪声监测记录",
            "降噪设施和运行时段证明",
        ],
        "photo_points": [
            "扩声设备、外机、冷却塔或装卸区",
            "降噪屏障、隔声门窗或消声设施",
            "场界与周边敏感点方向",
            "投诉整改台账关键页",
        ],
        "related_regulations": [
            "中华人民共和国噪声污染防治法",
            "GB 22337-2008 社会生活环境噪声排放标准",
        ],
        "domain": "noise",
        "extension_version": VERSION,
        "confidence": "MEDIUM",
        "runtime_status": RUNTIME_STATUS,
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
    },
]


RADIATION_SCENARIOS = [
    {
        "scenario_id": "SCN_RADIATION_DEVICE_SOURCE_SAFETY",
        "scenario_name": "射线装置与核技术利用辐射安全",
        "aliases": ["射线装置", "放射诊疗", "工业探伤", "核技术利用", "辐射安全许可"],
        "tags_24": ["radiation", "xray_device", "nuclear_technology_use", "license_management", "warning_signage"],
        "media_type": "radiation",
        "facility_or_risk_unit": "DR/CT/牙片机、工业探伤机、辐照/检测装置、机房屏蔽、防护门、控制区/监督区",
        "triggers": [
            "存在射线装置、放射诊疗、工业探伤、辐照、核技术利用项目或辐射安全许可证",
            "环评、许可、设备清单或现场标识中出现射线装置、放射源、辐射安全、防护检测等信息",
        ],
        "not_applicable_conditions": [
            "无射线装置、无放射源、无核技术利用活动且有设备清单或现场证明",
            "相关检测/诊疗/探伤全部外协且本场所不贮存设备或源项",
        ],
        "confirmation_questions": [
            "是否持有辐射安全许可证或放射诊疗许可，许可范围与设备清单是否一致？",
            "射线装置类别、数量、安装位置和使用状态是什么？",
            "机房屏蔽、防护检测、警示标识、个人剂量和培训记录是否齐全？",
        ],
        "evidence_requirements": [
            "辐射安全许可证或放射诊疗许可证",
            "射线装置/核技术利用设备台账",
            "年度评估、防护检测或验收监测报告",
            "人员培训、个人剂量、职业健康记录",
            "机房屏蔽、防护门、警示标识和控制区划分资料",
        ],
        "photo_points": [
            "射线装置或机房入口警示标识",
            "设备铭牌和控制台",
            "防护门、联锁、警示灯和控制区/监督区标识",
            "个人剂量计、培训或检测报告关键页",
        ],
        "related_regulations": [
            "中华人民共和国放射性污染防治法",
            "放射性同位素与射线装置安全和防护条例",
            "放射性同位素与射线装置安全许可管理办法",
            "放射性同位素与射线装置安全和防护管理办法",
        ],
        "domain": "radiation",
        "extension_version": VERSION,
        "confidence": "HIGH",
        "runtime_status": RUNTIME_STATUS,
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
    },
    {
        "scenario_id": "SCN_RAD_WASTE_PACKAGE_SOLIDIFICATION_CONTAINER",
        "scenario_name": "放射性废物包、固化体与高完整性容器",
        "aliases": ["废物包", "固化体", "高完整性容器", "水泥固化", "包装鉴定"],
        "tags_24": ["radioactive_waste_package", "solidification", "container", "radioactive_waste", "quality_record"],
        "media_type": "radiation_waste",
        "facility_or_risk_unit": "低中水平放射性废物固化体、废物包、高完整性容器、包装记录、核素/活度记录",
        "triggers": [
            "存在低中水平放射性废物固化、包装、容器使用、废物包鉴定或交接",
            "资料中出现水泥固化体、废物包、球墨铸铁/混凝土/交联高密度聚乙烯高完整性容器",
        ],
        "not_applicable_conditions": [
            "普通危废包装桶、医废周转箱、一般固废压缩打包不得触发",
            "无放射性废物包装、固化、鉴定或容器使用活动",
        ],
        "confirmation_questions": [
            "废物包编号、核素、活度、形态、包装日期和去向是否闭环？",
            "固化体性能检测、容器合格证明和包装记录是否齐全？",
            "废物包暂存分区和标签是否与台账一致？",
        ],
        "evidence_requirements": [
            "废物包编号和包装记录",
            "固化体性能检测/鉴定资料",
            "容器合格证明",
            "核素/活度记录",
            "交接单和暂存分区台账",
        ],
        "photo_points": [
            "废物包外观与标签",
            "容器铭牌或合格证关键页",
            "包装作业记录关键页",
            "检测报告关键页",
            "暂存分区标识",
        ],
        "related_regulations": [
            "GB 12711-2018 低、中水平放射性固体废物包安全标准",
            "GB 14569.1-2011 低、中水平放射性废物固化体性能要求 水泥固化体",
            "GB 36900.1-2018 低、中水平放射性废物高完整性容器 球墨铸铁容器",
            "GB 36900.2-2018 低、中水平放射性废物高完整性容器 混凝土容器",
            "GB 36900.3-2018 低、中水平放射性废物高完整性容器 交联高密度聚乙烯容器",
        ],
        "domain": "radiation",
        "extension_version": VERSION,
        "confidence": "HIGH",
        "runtime_status": RUNTIME_STATUS,
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
    },
    {
        "scenario_id": "SCN_RAD_WASTE_DISPOSAL_FACILITY",
        "scenario_name": "放射性废物处置设施与场址管理",
        "aliases": ["近地表处置", "岩洞处置", "废放射源处置", "处置设施", "处置场址"],
        "tags_24": ["radioactive_waste_disposal", "disposal_facility", "site_monitoring", "license_management", "emergency_management"],
        "media_type": "radiation_waste",
        "facility_or_risk_unit": "近地表处置设施、岩洞处置设施、废放射源处置设施、监测井、封场或运行区域",
        "triggers": [
            "存在近地表处置、岩洞处置、废放射源近地表处置或处置设施选址/建造/运行证据",
            "资料中出现处置许可证、环境影响报告书、接收台账、监测井或封场运行记录",
        ],
        "not_applicable_conditions": [
            "普通填埋场、危废填埋、生活垃圾填埋不得因固废处置默认触发",
            "无放射性废物处置设施、无接收或处置活动",
        ],
        "confirmation_questions": [
            "处置设施许可、选址、设计、建造和运行文件是否齐全？",
            "接收、暂存、处置、环境监测和封场记录是否闭环？",
            "监测井、排水/渗漏控制和周边环境监测是否符合要求？",
        ],
        "evidence_requirements": [
            "处置许可证",
            "选址/设计/建造文件",
            "环境影响报告书",
            "接收和处置台账",
            "监测井/环境监测记录",
            "封场或运行记录",
        ],
        "photo_points": [
            "处置设施边界标识",
            "接收或暂存区",
            "监测井或监测点",
            "排水/渗漏控制设施",
            "运行台账关键页",
        ],
        "related_regulations": [
            "GB 9132-2018 低、中水平放射性固体废物近地表处置安全规定",
            "GB 13600-2024 放射性固体废物岩洞处置安全规定",
            "HJ 1336-2023 废放射源近地表处置安全要求",
        ],
        "domain": "radiation",
        "extension_version": VERSION,
        "confidence": "HIGH",
        "runtime_status": RUNTIME_STATUS,
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
    },
    {
        "scenario_id": "SCN_RADIOACTIVE_SOURCE_SECURITY",
        "scenario_name": "放射源安全保卫、台账与退役去向",
        "aliases": ["密封放射源", "废放射源", "源库", "放射源台账", "退役源"],
        "tags_24": ["radioactive_source", "radiation", "security_control", "source_inventory", "emergency_management"],
        "media_type": "radiation",
        "facility_or_risk_unit": "密封放射源、源库、暂存柜、安防设施、领用归还台账、退役或送贮记录",
        "triggers": [
            "存在密封放射源、废放射源、源库、含源仪表、料位计、测厚仪等源项",
            "许可或台账中出现放射源编码、核素、活度、贮存、送贮、退役等信息",
        ],
        "not_applicable_conditions": [
            "无放射源且仅使用非含源射线装置",
            "历史放射源已依法退役/送贮并有闭环证明",
        ],
        "confirmation_questions": [
            "放射源核素、活度、编码、类别和账物是否一致？",
            "源库或暂存柜是否具备防盗、防丢失、防误照射措施？",
            "废旧源、退役源是否有送贮、转让或处置闭环？",
        ],
        "evidence_requirements": [
            "辐射安全许可证及放射源明细",
            "放射源台账、盘点记录和领用归还记录",
            "安防设施、应急预案和演练记录",
            "废放射源送贮/转让/退役证明",
        ],
        "photo_points": [
            "源库或含源设备警示标识",
            "源库门禁、监控、双人双锁或防盗设施",
            "放射源台账关键页",
            "废旧源送贮或退役证明关键页",
        ],
        "related_regulations": [
            "中华人民共和国放射性污染防治法",
            "放射性同位素与射线装置安全和防护条例",
            "废放射源近地表处置安全要求 HJ 1336-2023",
        ],
        "domain": "radiation",
        "extension_version": VERSION,
        "confidence": "HIGH",
        "runtime_status": RUNTIME_STATUS,
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
    },
    {
        "scenario_id": "SCN_RADIOACTIVE_WASTE_STORAGE_TRANSFER_DISPOSAL",
        "scenario_name": "放射性废物贮存、转移与处置",
        "aliases": ["放射性废物", "低中水平放射性废物", "放射性固体废物", "废物库", "废物包"],
        "tags_24": ["radioactive_waste", "radiation", "storage_transfer", "waste_package", "disposal"],
        "media_type": "radiation_waste",
        "facility_or_risk_unit": "放射性废物库、废物包、暂存容器、固化体、近地表/岩洞处置设施、退役场址",
        "triggers": [
            "存在放射性废物产生、贮存、固化、包装、运输、处置或废物库运行管理活动",
            "资料中出现低中水平放射性废物、废物包、固化体、废物库、处置设施等词汇",
        ],
        "not_applicable_conditions": [
            "无放射性废物产生、无源项且无放射性废物贮存/转移/处置活动",
            "仅一般危废或医废，不涉及放射性核素或放射性污染控制要求",
        ],
        "confirmation_questions": [
            "放射性废物类别、核素、活度、形态、数量和贮存状态是什么？",
            "废物包、容器、固化体和库房是否满足相应标准和许可要求？",
            "转移、送贮、处置、退役或场址土壤残留控制是否有闭环证据？",
        ],
        "evidence_requirements": [
            "放射性废物台账和分类记录",
            "废物包/容器/固化体检测或鉴定资料",
            "废物库许可、运行管理记录和监测记录",
            "转移、送贮、处置或退役证明",
            "场址或库区辐射监测资料",
        ],
        "photo_points": [
            "放射性废物库外部和警示标识",
            "废物包/容器标签和暂存区域",
            "监测设备或监测记录关键页",
            "转移/送贮/处置证明关键页",
        ],
        "related_regulations": [
            "放射性废物安全管理条例",
            "放射性废物安全监督管理规定",
            "放射性固体废物贮存和处置许可管理办法",
            "GB 14500-93 放射性废物管理规定",
            "HJ 1258-2022 核技术利用放射性废物库选址、设计与建造技术规范",
            "HJ 1417-2025 核技术利用放射性废物库运行管理技术规范",
        ],
        "domain": "radiation",
        "extension_version": VERSION,
        "confidence": "HIGH",
        "runtime_status": RUNTIME_STATUS,
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
    },
    {
        "scenario_id": "SCN_RADIOACTIVE_MATERIAL_TRANSPORT",
        "scenario_name": "放射性物品运输与运输容器安全",
        "aliases": ["放射性物品运输", "运输容器", "运输许可", "栓系装置", "提升装置"],
        "tags_24": ["radioactive_material_transport", "radiation", "transport_package", "license_management", "emergency_management"],
        "media_type": "radiation_transport",
        "facility_or_risk_unit": "放射性物品运输包装、运输容器、提升/栓系装置、车辆、运输许可和应急资料",
        "triggers": [
            "存在放射性物品运输、托运、承运、运输容器设计/使用或运输许可活动",
            "资料中出现放射性物品运输、运输容器、包装等级、栓系、提升、运输许可等信息",
        ],
        "not_applicable_conditions": [
            "不从事放射性物品运输、托运、承运或运输容器相关活动",
            "仅普通危化品或一般货物运输，不涉及放射性物品",
        ],
        "confirmation_questions": [
            "运输物品类别、包装类型、运输容器和许可资质是否匹配？",
            "运输容器提升装置、栓系装置、防脆性断裂设计或检验证据是否齐全？",
            "运输应急方案、车辆、人员培训和交接记录是否闭环？",
        ],
        "evidence_requirements": [
            "放射性物品运输许可或备案资料",
            "运输容器合格证明、设计/检验资料",
            "运输交接、托运、承运记录",
            "车辆、人员培训和应急资料",
        ],
        "photo_points": [
            "运输容器外观、标识和编号",
            "车辆、栓系/提升装置和警示标识",
            "运输许可或交接记录关键页",
            "应急物资和运输方案关键页",
        ],
        "related_regulations": [
            "放射性物品运输安全管理条例",
            "放射性物品运输安全监督管理办法",
            "放射性物品运输安全许可管理办法",
            "GB 11806-2019 放射性物品安全运输规程",
            "HJ 1201-2021 放射性物品运输容器防脆性断裂的安全设计指南",
            "HJ 1385-2024 放射性物品运输容器提升装置和栓系装置安全要求",
        ],
        "domain": "radiation",
        "extension_version": VERSION,
        "confidence": "MEDIUM",
        "runtime_status": RUNTIME_STATUS,
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
    },
    {
        "scenario_id": "SCN_NORM_RADIOACTIVITY_IN_INDUSTRIAL_RESIDUE",
        "scenario_name": "含天然放射性工业废渣与建材放射性控制",
        "aliases": ["天然放射性物质", "工业废渣放射性", "建材放射性", "铀钍矿冶", "NORM"],
        "tags_24": ["norm_radioactivity", "industrial_residue", "building_material", "radiation", "solid_waste"],
        "media_type": "radiation_solid_waste",
        "facility_or_risk_unit": "铀钍矿冶废物、工业废渣、建材原料、退役场址土壤、废渣堆场和产品放射性检测",
        "triggers": [
            "涉及铀钍矿冶、含天然放射性物料、工业废渣用于建材或退役场址土壤残留控制",
            "资料中出现铀、钍、天然放射性核素、工业废渣放射性、建材放射性限制等信息",
        ],
        "not_applicable_conditions": [
            "无含天然放射性物料、无相关工业废渣利用或矿冶活动",
            "仅普通一般固废且无放射性检测或监管要求",
        ],
        "confirmation_questions": [
            "是否使用或产生含天然放射性物料、矿冶废物或工业废渣？",
            "工业废渣用于建材或外售时是否有放射性检测和去向证明？",
            "退役场址或堆场土壤残留放射性是否有调查和控制要求？",
        ],
        "evidence_requirements": [
            "原料/废渣成分和放射性检测报告",
            "工业废渣利用、外售或处置去向证明",
            "矿冶废物管理资料和场址监测记录",
            "建材产品放射性控制资料",
        ],
        "photo_points": [
            "工业废渣堆场、贮存点或建材原料区",
            "放射性检测报告关键页",
            "废渣外售/利用合同或台账关键页",
            "场址土壤调查或监测点位",
        ],
        "related_regulations": [
            "中华人民共和国放射性污染防治法",
            "GB 6763-86 建筑材料用工业废渣放射性物质限制标准",
            "GB 14585-93 铀、钍矿冶放射性废物安全管理技术规定",
            "GB 45437-2025 核设施退役场址土壤中残留放射性可接受水平",
        ],
        "domain": "radiation",
        "extension_version": VERSION,
        "confidence": "MEDIUM",
        "runtime_status": RUNTIME_STATUS,
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
    },
    {
        "scenario_id": "SCN_URANIUM_THORIUM_MINING_RAD_WASTE",
        "scenario_name": "铀钍矿冶放射性废物与尾矿风险",
        "aliases": ["铀矿冶", "钍矿冶", "放射性金属矿", "矿冶废物", "尾矿放射性"],
        "tags_24": ["uranium_thorium_mining", "radioactive_waste", "tailings", "radiation_monitoring", "site_environment"],
        "media_type": "radiation_mining",
        "facility_or_risk_unit": "铀钍矿冶废物、尾矿库、废石场、渗滤液处理、辐射环境监测点",
        "triggers": [
            "行业或资料明确为放射性金属矿采选、铀钍矿冶或矿冶放射性废物管理",
            "出现铀、钍、矿冶废物、尾矿、废石、辐射环境监测等直接证据",
        ],
        "not_applicable_conditions": [
            "普通有色矿采选、稀土矿采选只能作为UNKNOWN候选，不能默认触发",
            "无铀钍或放射性金属矿冶事实、无相关废物管理要求",
        ],
        "confirmation_questions": [
            "矿种、工艺和废物是否涉及铀、钍或放射性金属？",
            "尾矿库、废石场、渗滤液和辐射监测是否纳入管理？",
            "矿冶放射性废物去向、监测和应急措施是否闭环？",
        ],
        "evidence_requirements": [
            "采选/矿冶环评和批复",
            "放射性废物管理方案",
            "尾矿库/废石场资料",
            "辐射环境监测报告",
            "废物去向和应急资料",
        ],
        "photo_points": [
            "矿冶废物暂存或尾矿设施",
            "监测点位和警示标识",
            "渗滤液或废水处理设施",
            "监测报告关键页",
        ],
        "related_regulations": [
            "GB 14585-93 铀、钍矿冶放射性废物安全管理技术规定",
            "中华人民共和国放射性污染防治法",
        ],
        "domain": "radiation",
        "extension_version": VERSION,
        "confidence": "HIGH",
        "runtime_status": RUNTIME_STATUS,
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
    },
    {
        "scenario_id": "SCN_NUCLEAR_FUEL_EFFLUENT_DECOMMISSIONING",
        "scenario_name": "核燃料循环流出物与核设施退役场址",
        "aliases": ["核燃料加工", "放射性流出物", "核设施退役", "场址土壤残留", "退役场址"],
        "tags_24": ["nuclear_fuel_cycle", "radioactive_effluent", "decommissioning", "soil_residual_radioactivity", "site_monitoring"],
        "media_type": "radiation_nuclear",
        "facility_or_risk_unit": "核燃料循环设施、放射性流出物排放/监测点、退役区域、土壤采样点",
        "triggers": [
            "行业或资料明确为核燃料加工、核燃料循环放射性流出物或核设施退役",
            "出现退役方案、场址调查、土壤残留放射性、监管批复或放射性流出物监测资料",
        ],
        "not_applicable_conditions": [
            "普通燃料加工、普通化工退役场地不得触发",
            "无核燃料循环、无核设施退役、无放射性流出物管理事实",
        ],
        "confirmation_questions": [
            "核燃料循环设施、流出物排放和监测点是否明确？",
            "退役方案、场址调查和土壤残留放射性控制是否有监管批复？",
            "流出物监测、归一化排放量和年度报告是否完整？",
        ],
        "evidence_requirements": [
            "核设施/核燃料加工许可或环评",
            "放射性流出物监测报告",
            "退役方案和监管批复",
            "场址调查/土壤检测资料",
            "排放和监测台账",
        ],
        "photo_points": [
            "排放/监测点标识",
            "监测报告关键页",
            "退役区域边界",
            "土壤采样或监测布点图",
            "台账关键页",
        ],
        "related_regulations": [
            "GB 13695-92 核燃料循环放射性流出物归一化排放量管理限值",
            "GB 45437-2025 核设施退役场址土壤中残留放射性可接受水平",
        ],
        "domain": "radiation",
        "extension_version": VERSION,
        "confidence": "HIGH",
        "runtime_status": RUNTIME_STATUS,
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
    },
    {
        "scenario_id": "SCN_BUILDING_MATERIAL_SLAG_RADIONUCLIDE",
        "scenario_name": "建材工业废渣放射性物质限制",
        "aliases": ["建材放射性", "工业废渣原料", "磷石膏", "粉煤灰", "冶炼渣"],
        "tags_24": ["building_material", "industrial_residue", "radionuclide_limit", "solid_waste", "product_testing"],
        "media_type": "radiation_solid_waste",
        "facility_or_risk_unit": "工业废渣原料堆场、配料系统、建材产品批次、放射性检测报告",
        "triggers": [
            "建材生产使用工业废渣、磷石膏、粉煤灰、冶炼渣、稀土/铀钍相关渣等原料",
            "资料出现建筑材料用工业废渣放射性物质限制、产品放射性检测或批次台账",
        ],
        "not_applicable_conditions": [
            "普通水泥、砖瓦、石材、陶瓷企业不得全行业默认触发",
            "无工业废渣原料证据、无放射性检测或监管要求",
        ],
        "confirmation_questions": [
            "是否使用工业废渣作为建材原料，来源和批次是什么？",
            "原料和产品是否有放射性物质检测报告？",
            "不合格批次、去向和整改是否有记录？",
        ],
        "evidence_requirements": [
            "原料来源和工业废渣成分证明",
            "原料/产品放射性检测报告",
            "配料和批次台账",
            "供应商证明和产品去向",
        ],
        "photo_points": [
            "工业废渣原料堆场",
            "原料标签或来源单据",
            "检测报告关键页",
            "配料记录",
            "成品批次标识",
        ],
        "related_regulations": [
            "GB 6763-86 建筑材料用工业废渣放射性物质限制标准",
        ],
        "domain": "radiation",
        "extension_version": VERSION,
        "confidence": "MEDIUM",
        "runtime_status": RUNTIME_STATUS,
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
    },
]


PROCESS_TRIGGERS = [
    {
        "process_id": "industrial_noise_source",
        "process_name": "工业噪声源/厂界噪声",
        "aliases": "工业噪声;厂界噪声;高噪声设备;隔声减振;噪声监测",
        "positive_keywords": "噪声源;厂界噪声;空压机;风机;泵;破碎;粉磨;冲压;切割;冷却塔;隔声;减振;消声",
        "negative_keywords": "无噪声源;仅办公;无生产设备;设备停用;无夜间生产",
        "source_document_types": "EIA;APPROVAL;PERMIT;LEDGER;SITE;MONITORING",
        "linked_scenario_ids": "SCN_NOISE_SOURCE_BOUNDARY_CONTROL",
        "linked_permit_entry_nos": "109;110;112",
        "evidence_requirements": "环评噪声章节；工业噪声许可要求；设备清单；厂界噪声监测报告；隔声减振维护记录",
        "photo_points": "高噪声设备及铭牌；隔声减振措施；厂界监测点；周边敏感点方向；监测报告关键页",
        "site_verification_required": "true",
        "confidence": "HIGH",
    },
    {
        "process_id": "boundary_noise_monitoring",
        "process_name": "厂界噪声监测/执行标准",
        "aliases": "厂界噪声监测;自行监测;噪声执行标准;监测点位;昼夜监测",
        "positive_keywords": "厂界噪声;自行监测;监测点位;昼间;夜间;GB 12348;功能区;监测频次",
        "negative_keywords": "无监测要求;无需厂界监测;仅现场初筛;社会生活噪声",
        "source_document_types": "PERMIT;EIA;MONITORING;LEDGER",
        "linked_scenario_ids": "SCN_NOISE_BOUNDARY_MONITORING_LEDGER",
        "linked_permit_entry_nos": "",
        "evidence_requirements": "自行监测方案；厂界噪声监测报告；监测点位图；执行标准说明；超标整改记录",
        "photo_points": "厂界监测点位；监测点位示意图；监测报告关键页；厂界四至",
        "site_verification_required": "true",
        "confidence": "HIGH",
    },
    {
        "process_id": "night_operation_sensitive_receptor",
        "process_name": "夜间生产/敏感点噪声风险",
        "aliases": "夜间生产;敏感点;噪声投诉;扰民;连续生产",
        "positive_keywords": "夜间生产;连续生产;居民区;学校;医院;养老机构;投诉;扰民;夜间监测;超标整改",
        "negative_keywords": "无夜间生产;远离敏感点;无投诉;昼间单班",
        "source_document_types": "EIA;SITE;LEDGER;MONITORING;COMPLAINT",
        "linked_scenario_ids": "SCN_NOISE_SENSITIVE_RECEPTOR_NIGHT_OPERATION",
        "linked_permit_entry_nos": "",
        "evidence_requirements": "生产班次记录；敏感点位置图；投诉/整改记录；夜间监测报告；限时运行证明",
        "photo_points": "厂界到敏感点方向；夜间运行设备；隔声屏障；投诉整改记录关键页",
        "site_verification_required": "true",
        "confidence": "MEDIUM",
    },
    {
        "process_id": "social_life_noise_source",
        "process_name": "社会生活噪声源",
        "aliases": "社会生活噪声;商业噪声;餐饮娱乐噪声;扩声设备;空调外机",
        "positive_keywords": "扩声;音响;空调外机;冷却塔;装卸;夜间经营;投诉;社会生活噪声",
        "negative_keywords": "无扩声;无外机;无夜间经营;设备拆除;非经营场所",
        "source_document_types": "SITE;LEDGER;MONITORING;COMPLAINT",
        "linked_scenario_ids": "SCN_SOCIAL_LIFE_NOISE_SOURCE",
        "linked_permit_entry_nos": "",
        "evidence_requirements": "经营设备清单；噪声投诉或整改记录；监测记录；降噪措施证明",
        "photo_points": "扩声设备/外机/冷却塔；降噪设施；场界与敏感点方向；投诉整改台账",
        "site_verification_required": "true",
        "confidence": "MEDIUM",
    },
    {
        "process_id": "radiation_device_source",
        "process_name": "射线装置/核技术利用",
        "aliases": "射线装置;DR;CT;工业探伤;核技术利用;辐射安全许可",
        "positive_keywords": "射线装置;DR;CT;牙片机;工业探伤;辐照;核技术利用;辐射安全许可证;放射诊疗",
        "negative_keywords": "无射线装置;无放射源;全部外协;设备已拆除;许可注销",
        "source_document_types": "PERMIT;EIA;APPROVAL;LEDGER;SITE",
        "linked_scenario_ids": "SCN_RADIATION_DEVICE_SOURCE_SAFETY",
        "linked_permit_entry_nos": "",
        "evidence_requirements": "辐射安全许可证；射线装置台账；防护检测报告；人员培训和个人剂量记录",
        "photo_points": "机房入口警示标识；设备铭牌；防护门/联锁/警示灯；个人剂量计或检测报告关键页",
        "site_verification_required": "true",
        "confidence": "HIGH",
    },
    {
        "process_id": "sealed_radioactive_source",
        "process_name": "密封放射源/废放射源",
        "aliases": "放射源;密封源;废放射源;源库;含源仪表",
        "positive_keywords": "放射源;密封源;废放射源;源库;核素;活度;含源仪表;料位计;测厚仪",
        "negative_keywords": "无放射源;非含源设备;已送贮;已退役;已转让",
        "source_document_types": "PERMIT;LEDGER;SITE;TRANSFER",
        "linked_scenario_ids": "SCN_RADIOACTIVE_SOURCE_SECURITY;SCN_RADIOACTIVE_WASTE_STORAGE_TRANSFER_DISPOSAL",
        "linked_permit_entry_nos": "",
        "evidence_requirements": "辐射安全许可证；放射源台账；盘点记录；安防设施；送贮/退役证明",
        "photo_points": "源库警示标识；门禁监控；放射源台账；送贮或退役证明关键页",
        "site_verification_required": "true",
        "confidence": "HIGH",
    },
    {
        "process_id": "radioactive_waste_storage",
        "process_name": "放射性废物贮存/转移/处置",
        "aliases": "放射性废物;废物库;废物包;固化体;低中水平放射性废物",
        "positive_keywords": "放射性废物;废物库;废物包;固化体;低中水平;送贮;处置;退役场址",
        "negative_keywords": "无放射性废物;仅一般危废;仅医废;无源项",
        "source_document_types": "PERMIT;LEDGER;SITE;MONITORING;TRANSFER",
        "linked_scenario_ids": "SCN_RADIOACTIVE_WASTE_STORAGE_TRANSFER_DISPOSAL",
        "linked_permit_entry_nos": "",
        "evidence_requirements": "放射性废物台账；废物包/容器资料；废物库运行记录；转移/处置证明；监测记录",
        "photo_points": "废物库警示标识；废物包标签；监测记录；转移/处置证明关键页",
        "site_verification_required": "true",
        "confidence": "HIGH",
    },
    {
        "process_id": "radioactive_waste_package_container",
        "process_name": "放射性废物包/固化体/高完整性容器",
        "aliases": "废物包;固化体;高完整性容器;水泥固化;包装鉴定",
        "positive_keywords": "废物包;固化体;高完整性容器;水泥固化;球墨铸铁容器;混凝土容器;聚乙烯容器;包装鉴定",
        "negative_keywords": "普通危废包装;医废周转箱;一般固废打包;无放射性废物包装",
        "source_document_types": "PERMIT;LEDGER;SITE;MONITORING;TRANSFER",
        "linked_scenario_ids": "SCN_RAD_WASTE_PACKAGE_SOLIDIFICATION_CONTAINER",
        "linked_permit_entry_nos": "",
        "evidence_requirements": "废物包编号；固化体检测；容器合格证明；核素/活度记录；交接单",
        "photo_points": "废物包标签；容器铭牌；检测报告关键页；暂存分区标识",
        "site_verification_required": "true",
        "confidence": "HIGH",
    },
    {
        "process_id": "radioactive_waste_disposal_facility",
        "process_name": "放射性废物处置设施/场址",
        "aliases": "近地表处置;岩洞处置;废放射源处置;处置设施;处置场址",
        "positive_keywords": "近地表处置;岩洞处置;废放射源处置;处置设施;处置许可证;监测井;封场",
        "negative_keywords": "普通填埋场;危废填埋;生活垃圾填埋;无放射性处置",
        "source_document_types": "PERMIT;EIA;APPROVAL;LEDGER;SITE;MONITORING",
        "linked_scenario_ids": "SCN_RAD_WASTE_DISPOSAL_FACILITY",
        "linked_permit_entry_nos": "",
        "evidence_requirements": "处置许可证；选址/设计/建造文件；环境影响报告书；接收台账；监测井记录",
        "photo_points": "处置设施边界标识；接收/暂存区；监测井；渗漏控制设施",
        "site_verification_required": "true",
        "confidence": "HIGH",
    },
    {
        "process_id": "radioactive_material_transport",
        "process_name": "放射性物品运输",
        "aliases": "放射性物品运输;运输容器;运输许可;托运;承运",
        "positive_keywords": "放射性物品运输;运输容器;运输许可;托运;承运;包装等级;栓系;提升装置",
        "negative_keywords": "不运输放射性物品;普通货物运输;仅危化品;无运输容器",
        "source_document_types": "PERMIT;LEDGER;SITE;TRANSPORT",
        "linked_scenario_ids": "SCN_RADIOACTIVE_MATERIAL_TRANSPORT",
        "linked_permit_entry_nos": "",
        "evidence_requirements": "运输许可；运输容器合格证明；托运/承运记录；车辆和人员培训；应急方案",
        "photo_points": "运输容器标识；车辆和栓系装置；运输许可；应急物资",
        "site_verification_required": "true",
        "confidence": "MEDIUM",
    },
    {
        "process_id": "norm_industrial_residue_radioactivity",
        "process_name": "含天然放射性工业废渣/建材放射性",
        "aliases": "NORM;天然放射性;工业废渣放射性;建材放射性;铀钍矿冶",
        "positive_keywords": "铀;钍;天然放射性;工业废渣;建材放射性;矿冶废物;退役场址;残留放射性",
        "negative_keywords": "无含天然放射性物料;普通一般固废;无矿冶活动;无废渣利用",
        "source_document_types": "EIA;APPROVAL;LEDGER;SITE;MONITORING",
        "linked_scenario_ids": "SCN_NORM_RADIOACTIVITY_IN_INDUSTRIAL_RESIDUE",
        "linked_permit_entry_nos": "",
        "evidence_requirements": "原料/废渣检测报告；废渣利用/外售台账；矿冶废物管理资料；场址监测记录",
        "photo_points": "废渣堆场；检测报告关键页；废渣外售台账；场址监测点位",
        "site_verification_required": "true",
        "confidence": "MEDIUM",
    },
    {
        "process_id": "uranium_thorium_mining_rad_waste",
        "process_name": "铀钍矿冶放射性废物",
        "aliases": "铀矿冶;钍矿冶;放射性金属矿;矿冶废物;尾矿放射性",
        "positive_keywords": "铀矿;钍矿;放射性金属矿;矿冶废物;尾矿;废石;辐射环境监测",
        "negative_keywords": "普通有色矿;普通稀土矿;无铀钍;无放射性金属",
        "source_document_types": "EIA;APPROVAL;PERMIT;LEDGER;SITE;MONITORING",
        "linked_scenario_ids": "SCN_URANIUM_THORIUM_MINING_RAD_WASTE",
        "linked_permit_entry_nos": "",
        "evidence_requirements": "矿冶环评；废物管理方案；尾矿库资料；辐射环境监测报告；废物去向",
        "photo_points": "尾矿设施；废石场；监测点位；渗滤液处理设施；监测报告关键页",
        "site_verification_required": "true",
        "confidence": "HIGH",
    },
    {
        "process_id": "nuclear_fuel_effluent_decommissioning",
        "process_name": "核燃料循环流出物/核设施退役",
        "aliases": "核燃料加工;放射性流出物;核设施退役;场址土壤残留;归一化排放量",
        "positive_keywords": "核燃料;放射性流出物;归一化排放量;核设施退役;场址土壤;残留放射性",
        "negative_keywords": "普通燃料加工;普通化工退役;无核设施;无放射性流出物",
        "source_document_types": "EIA;APPROVAL;PERMIT;LEDGER;SITE;MONITORING",
        "linked_scenario_ids": "SCN_NUCLEAR_FUEL_EFFLUENT_DECOMMISSIONING",
        "linked_permit_entry_nos": "",
        "evidence_requirements": "核设施许可或环评；流出物监测报告；退役方案；场址调查；监管批复",
        "photo_points": "排放/监测点标识；退役区域边界；土壤采样布点图；监测报告关键页",
        "site_verification_required": "true",
        "confidence": "HIGH",
    },
    {
        "process_id": "building_material_slag_radionuclide",
        "process_name": "建材工业废渣放射性物质限制",
        "aliases": "建材放射性;工业废渣原料;磷石膏;粉煤灰;冶炼渣",
        "positive_keywords": "工业废渣;磷石膏;粉煤灰;冶炼渣;建材放射性;放射性检测;产品批次",
        "negative_keywords": "无工业废渣;普通原料;无放射性检测要求;不使用废渣",
        "source_document_types": "EIA;APPROVAL;LEDGER;SITE;MONITORING",
        "linked_scenario_ids": "SCN_BUILDING_MATERIAL_SLAG_RADIONUCLIDE",
        "linked_permit_entry_nos": "",
        "evidence_requirements": "原料来源；放射性检测报告；配料批次台账；供应商证明；产品去向",
        "photo_points": "工业废渣原料堆场；检测报告关键页；配料记录；成品批次标识",
        "site_verification_required": "true",
        "confidence": "MEDIUM",
    },
]


ACTIVATION_RULES = [
    ("RULE18_NOISE_INDUSTRIAL_BOUNDARY", "industrial_noise_source", "SCN_NOISE_SOURCE_BOUNDARY_CONTROL", "生产设备、动力设备或环评/许可噪声要求命中", "仅办公;无固定噪声源;设备停用", "设备清单;噪声章节;厂界监测报告;隔声减振记录", "高噪声设备;隔声减振设施;厂界监测点;敏感点方向", "S10;S04;S02", "HIGH"),
    ("RULE18_NOISE_BOUNDARY_MONITORING", "boundary_noise_monitoring", "SCN_NOISE_BOUNDARY_MONITORING_LEDGER", "排污许可、环评或自行监测方案要求厂界噪声监测", "无厂界监测要求;社会生活噪声另行判断", "自行监测方案;监测报告;点位图;执行标准", "厂界监测点;点位图;监测报告关键页", "S10;S02", "HIGH"),
    ("RULE18_NOISE_NIGHT_SENSITIVE", "night_operation_sensitive_receptor", "SCN_NOISE_SENSITIVE_RECEPTOR_NIGHT_OPERATION", "夜间生产、敏感点、投诉或夜间监测记录命中", "无夜间生产;远离敏感点;无投诉", "班次记录;敏感点位置图;投诉整改;夜间监测", "敏感点方向;夜间设备;隔声屏障;整改记录", "S10;S04;S11", "MEDIUM"),
    ("RULE18_NOISE_SOCIAL_LIFE", "social_life_noise_source", "SCN_SOCIAL_LIFE_NOISE_SOURCE", "经营活动、扩声、外机、装卸或投诉记录命中", "无经营噪声源;设备拆除;无夜间经营", "设备清单;投诉整改;社会生活噪声监测;降噪措施", "扩声设备;外机/冷却塔;降噪设施;敏感点方向", "S10;S04;S11", "MEDIUM"),
    ("RULE18_RADIATION_DEVICE", "radiation_device_source", "SCN_RADIATION_DEVICE_SOURCE_SAFETY", "辐射安全许可证、射线装置或核技术利用事实命中", "无射线装置;全部外协;设备拆除或许可注销", "辐射安全许可证;设备台账;防护检测;个人剂量;培训记录", "机房入口;设备铭牌;防护门联锁;警示标识", "S12;S09;S02", "HIGH"),
    ("RULE18_RADIOACTIVE_SOURCE", "sealed_radioactive_source", "SCN_RADIOACTIVE_SOURCE_SECURITY", "放射源、源库、含源仪表或废放射源事实命中", "无放射源;历史源已送贮/退役并闭环", "许可明细;源台账;盘点记录;安防设施;送贮证明", "源库警示标识;门禁监控;源台账;送贮证明", "S12;S13;S02", "HIGH"),
    ("RULE18_RADIOACTIVE_WASTE", "radioactive_waste_storage", "SCN_RADIOACTIVE_WASTE_STORAGE_TRANSFER_DISPOSAL", "放射性废物、废物库、废物包、固化体或处置活动命中", "无放射性废物;仅一般危废或医废", "废物台账;废物包资料;库房运行记录;转移/处置证明;监测记录", "废物库;废物包标签;监测记录;处置证明", "S12;S07;S02;S13", "HIGH"),
    ("RULE18_RAD_WASTE_PACKAGE", "radioactive_waste_package_container", "SCN_RAD_WASTE_PACKAGE_SOLIDIFICATION_CONTAINER", "废物包、固化体、高完整性容器或包装鉴定资料命中", "普通危废包装;医废周转箱;无放射性包装", "废物包编号;固化体检测;容器合格证明;交接单", "废物包标签;容器铭牌;检测报告;暂存分区", "S12;S07;S02", "HIGH"),
    ("RULE18_RAD_WASTE_DISPOSAL", "radioactive_waste_disposal_facility", "SCN_RAD_WASTE_DISPOSAL_FACILITY", "近地表处置、岩洞处置、废放射源处置设施资料命中", "普通填埋场;危废填埋;无放射性处置", "处置许可证;环评;接收台账;监测井记录", "处置边界;接收区;监测井;运行台账", "S12;S13;S02", "HIGH"),
    ("RULE18_RADIOACTIVE_TRANSPORT", "radioactive_material_transport", "SCN_RADIOACTIVE_MATERIAL_TRANSPORT", "放射性物品运输、运输容器或运输许可事实命中", "不运输放射性物品;仅普通货物或危化品", "运输许可;容器合格证明;托运/承运记录;车辆人员培训;应急方案", "运输容器;车辆标识;栓系装置;许可关键页", "S12;S13;S02", "MEDIUM"),
    ("RULE18_NORM_RESIDUE", "norm_industrial_residue_radioactivity", "SCN_NORM_RADIOACTIVITY_IN_INDUSTRIAL_RESIDUE", "铀钍矿冶、含天然放射性物料、工业废渣建材利用或场址残留命中", "无相关物料;普通一般固废;无废渣利用", "放射性检测;废渣台账;外售利用证明;场址监测", "废渣堆场;检测报告;外售台账;监测点位", "S12;S07;S10;S04", "MEDIUM"),
    ("RULE18_URANIUM_THORIUM_WASTE", "uranium_thorium_mining_rad_waste", "SCN_URANIUM_THORIUM_MINING_RAD_WASTE", "铀钍矿冶、放射性金属矿或矿冶放射性废物资料命中", "普通有色矿;普通稀土矿;无铀钍事实", "矿冶环评;尾矿库资料;辐射环境监测;废物去向", "尾矿设施;监测点;渗滤液处理;监测报告", "S12;S10;S04;S13", "HIGH"),
    ("RULE18_NUCLEAR_FUEL_DECOM", "nuclear_fuel_effluent_decommissioning", "SCN_NUCLEAR_FUEL_EFFLUENT_DECOMMISSIONING", "核燃料循环、放射性流出物或核设施退役资料命中", "普通燃料加工;普通化工退役;无核设施", "核设施许可;流出物监测;退役方案;场址调查", "监测点标识;退役边界;采样布点图;监测报告", "S12;S10;S04;S02", "HIGH"),
    ("RULE18_BUILDING_SLAG_RAD", "building_material_slag_radionuclide", "SCN_BUILDING_MATERIAL_SLAG_RADIONUCLIDE", "建材使用工业废渣且存在放射性检测或限制要求", "普通建材行业无废渣原料证据;无检测要求", "原料来源;放射性检测报告;配料台账;产品批次", "废渣堆场;检测报告;配料记录;成品批次", "S12;S07;S02", "MEDIUM"),
]


INSPECTION_SECTIONS = {
    "SCN_NOISE_SOURCE_BOUNDARY_CONTROL": ("KNOWLEDGE_NOISE", "工业企业噪声源与厂界噪声控制"),
    "SCN_NOISE_BOUNDARY_MONITORING_LEDGER": ("KNOWLEDGE_NOISE", "厂界噪声监测、执行标准与台账"),
    "SCN_NOISE_SENSITIVE_RECEPTOR_NIGHT_OPERATION": ("KNOWLEDGE_NOISE", "夜间生产、敏感点与噪声投诉风险"),
    "SCN_SOCIAL_LIFE_NOISE_SOURCE": ("KNOWLEDGE_NOISE", "社会生活噪声与经营活动噪声源"),
    "SCN_RADIATION_DEVICE_SOURCE_SAFETY": ("KNOWLEDGE_RADIATION", "射线装置与核技术利用辐射安全"),
    "SCN_RADIOACTIVE_SOURCE_SECURITY": ("KNOWLEDGE_RADIATION", "放射源安全保卫、台账与退役去向"),
    "SCN_RADIOACTIVE_WASTE_STORAGE_TRANSFER_DISPOSAL": ("KNOWLEDGE_RADIATION", "放射性废物贮存、转移与处置"),
    "SCN_RAD_WASTE_PACKAGE_SOLIDIFICATION_CONTAINER": ("KNOWLEDGE_RADIATION", "放射性废物包、固化体与高完整性容器"),
    "SCN_RAD_WASTE_DISPOSAL_FACILITY": ("KNOWLEDGE_RADIATION", "放射性废物处置设施与场址管理"),
    "SCN_RADIOACTIVE_MATERIAL_TRANSPORT": ("KNOWLEDGE_RADIATION", "放射性物品运输与运输容器安全"),
    "SCN_NORM_RADIOACTIVITY_IN_INDUSTRIAL_RESIDUE": ("KNOWLEDGE_RADIATION", "含天然放射性工业废渣与建材放射性控制"),
    "SCN_URANIUM_THORIUM_MINING_RAD_WASTE": ("KNOWLEDGE_RADIATION", "铀钍矿冶放射性废物与尾矿风险"),
    "SCN_NUCLEAR_FUEL_EFFLUENT_DECOMMISSIONING": ("KNOWLEDGE_RADIATION", "核燃料循环流出物与核设施退役场址"),
    "SCN_BUILDING_MATERIAL_SLAG_RADIONUCLIDE": ("KNOWLEDGE_RADIATION", "建材工业废渣放射性物质限制"),
}


def upsert_by(rows, key, new_rows):
    by_key = {row[key]: row for row in rows}
    for row in new_rows:
        if row[key] in by_key:
            by_key[row[key]].update(row)
        else:
            rows.append(row)
            by_key[row[key]] = row
    return rows


def upsert_composite(rows, keys, new_rows):
    by_key = {tuple(row.get(k, "") for k in keys): row for row in rows}
    for row in new_rows:
        row_key = tuple(row.get(k, "") for k in keys)
        if row_key in by_key:
            by_key[row_key].update(row)
        else:
            rows.append(row)
            by_key[row_key] = row
    return rows


def update_scenario_templates():
    path = artifact_path("scenario_templates.json")
    rows = read_json(path)
    for row in rows:
        if row.get("scenario_id") == "SCN_BASE_PRODUCTION_SOLID_NOISE_LEDGER":
            row.setdefault("domain_extension_notes", [])
            note = "v1.8起噪声源独立由SCN_NOISE_SOURCE_BOUNDARY_CONTROL/SCN_SOCIAL_LIFE_NOISE_SOURCE承接；本模板保留为基础生产、一般固废和旧规则兼容召回。"
            if note not in row["domain_extension_notes"]:
                row["domain_extension_notes"].append(note)
            successors = row.setdefault("successor_scenario_ids", [])
            for sid in ["SCN_NOISE_SOURCE_BOUNDARY_CONTROL", "SCN_SOCIAL_LIFE_NOISE_SOURCE"]:
                if sid not in successors:
                    successors.append(sid)
        if row.get("scenario_id") == "SCN_MEDICAL_WASTE_RADIATION":
            row.setdefault("domain_extension_notes", [])
            note = "v1.8起辐射/放射独立由SCN_RADIATION_DEVICE_SOURCE_SAFETY等模板承接；医疗场景保留医废、医疗废水与放射诊疗组合召回。"
            if note not in row["domain_extension_notes"]:
                row["domain_extension_notes"].append(note)
            successors = row.setdefault("successor_scenario_ids", [])
            if "SCN_RADIATION_DEVICE_SOURCE_SAFETY" not in successors:
                successors.append("SCN_RADIATION_DEVICE_SOURCE_SAFETY")
    upsert_by(rows, "scenario_id", NOISE_SCENARIOS + RADIATION_SCENARIOS)
    write_json(path, rows)


def score_rows_for(fields):
    rows = []
    specs = {
        "SCN_NOISE_SOURCE_BOUNDARY_CONTROL": ("工业企业噪声源与厂界噪声控制", "S10", "S04;S02;S06", "噪声排放和厂界达标归S10，现场噪声源和敏感点影响归S04，监测/整改台账归S02，隔声减振设施可辅S06。", "S10需要在知识层拆出 noise_boundary/noise_source/noise_monitoring。"),
        "SCN_NOISE_BOUNDARY_MONITORING_LEDGER": ("厂界噪声监测、执行标准与台账", "S10", "S02;S01", "厂界噪声监测与执行标准归S10，监测方案、报告和整改台账归S02，许可或环评要求可辅S01。", "S10需细分 noise_monitoring、boundary_point、day_night_limit。"),
        "SCN_NOISE_SENSITIVE_RECEPTOR_NIGHT_OPERATION": ("夜间生产、敏感点与噪声投诉风险", "S10", "S04;S11;S13", "夜间噪声和敏感点影响归S10/S04，投诉整改闭环归S11，群体投诉或突发扰民可辅S13。", "现有13维缺少敏感点/投诉/夜间噪声二级语义。"),
        "SCN_SOCIAL_LIFE_NOISE_SOURCE": ("社会生活噪声与经营活动噪声源", "S10", "S04;S11", "社会生活噪声排放归S10，周边敏感点和现场扰民风险归S04，投诉整改闭环可辅S11。", "S10需区分工业噪声与社会生活噪声，避免同一证据链混用。"),
        "SCN_RADIATION_DEVICE_SOURCE_SAFETY": ("射线装置与核技术利用辐射安全", "S12", "S01;S02;S09;S13", "射线装置、核技术利用和辐射安全许可归S12，许可手续归S01，台账/剂量/检测归S02，警示标识归S09，应急归S13。", "S12需要二级语义 radiation_device/source/security_training/dose_monitoring。"),
        "SCN_RADIOACTIVE_SOURCE_SECURITY": ("放射源安全保卫、台账与退役去向", "S12", "S02;S09;S13", "放射源安全保卫和账物一致归S12，盘点和领用记录归S02，警示标识归S09，丢失/事故应急归S13。", "S12需要区分密封源、废旧源、源库安防和退役送贮。"),
        "SCN_RADIOACTIVE_WASTE_STORAGE_TRANSFER_DISPOSAL": ("放射性废物贮存、转移与处置", "S12", "S07;S02;S13", "放射性废物本体按辐射安全归S12，同时具有固废贮存/转移属性辅S07，台账归S02，应急归S13。", "S07不能替代放射性废物知识层，需保留 radioactive_waste 二级标签。"),
        "SCN_RAD_WASTE_PACKAGE_SOLIDIFICATION_CONTAINER": ("放射性废物包、固化体与高完整性容器", "S12", "S07;S02", "废物包、固化体和容器安全归S12，包装贮存属性辅S07，检测/交接记录归S02。", "S12需补 waste_package、solidification、container_acceptance。"),
        "SCN_RAD_WASTE_DISPOSAL_FACILITY": ("放射性废物处置设施与场址管理", "S12", "S13;S02;S04", "处置设施安全归S12，事故/渗漏/封场应急归S13，运行和监测台账归S02，场址边界和周边环境辅S04。", "S12需补 disposal_facility、site_monitoring、closure_management。"),
        "SCN_RADIOACTIVE_MATERIAL_TRANSPORT": ("放射性物品运输与运输容器安全", "S12", "S02;S13;S09", "放射性物品运输和运输容器安全归S12，运输记录归S02，应急方案归S13，运输标识归S09。", "S12需补 transport_package/transport_license/transport_emergency。"),
        "SCN_NORM_RADIOACTIVITY_IN_INDUSTRIAL_RESIDUE": ("含天然放射性工业废渣与建材放射性控制", "S12", "S07;S10;S04;S02", "含天然放射性物料和工业废渣放射性控制归S12，废渣贮存归S07，释放/外排风险辅S10，场址和堆场辅S04，检测台账归S02。", "需把NORM/工业废渣放射性作为辐射与固废交叉二级语义。"),
        "SCN_URANIUM_THORIUM_MINING_RAD_WASTE": ("铀钍矿冶放射性废物与尾矿风险", "S12", "S10;S04;S13;S02", "铀钍矿冶放射性安全归S12，尾矿/渗滤液/流出物影响辅S10，场址环境辅S04，应急和台账辅S13/S02。", "需区分普通矿山与放射性金属矿冶。"),
        "SCN_NUCLEAR_FUEL_EFFLUENT_DECOMMISSIONING": ("核燃料循环流出物与核设施退役场址", "S12", "S10;S04;S02", "核燃料循环和退役场址辐射安全归S12，流出物和土壤残留风险辅S10/S04，监测台账归S02。", "S12需补 nuclear_fuel_cycle、effluent、decommissioning_site。"),
        "SCN_BUILDING_MATERIAL_SLAG_RADIONUCLIDE": ("建材工业废渣放射性物质限制", "S12", "S07;S02", "工业废渣放射性控制归S12，废渣原料管理辅S07，检测和批次台账归S02。", "建材行业不得默认触发，应由工业废渣原料和检测证据触发。"),
    }
    for sid, (name, primary, secondary, reason, gap) in specs.items():
        row = {field: "" for field in fields}
        row.update({
            "scenario_id": sid,
            "scenario_name": name,
            "primary_score_item_id": primary,
            "secondary_score_item_ids": secondary,
            "mapping_reason": reason,
            "possible_report_sections": ";".join([primary, secondary]),
            "human_confirm_required": "需由ESO/ETO结合环评、批复、许可、台账和现场事实确认是否适用。",
            "current_13_dimension_gap": gap,
            "suggested_improvement": "保持S01-S13一级口径不变，在知识图谱层补noise/radiation二级语义。",
            "runtime_status": RUNTIME_CANDIDATE,
        })
        rows.append(row)
    return rows


def update_score_mapping():
    for name in ["scenario_to_score13_mapping_v0_3.csv", "scenario_to_score13_mapping.csv"]:
        path = artifact_path(name)
        rows = read_csv(path)
        fields = list(rows[0].keys())
        upsert_composite(rows, ["scenario_id"], score_rows_for(fields))
        write_csv(path, rows, fields)


def update_inspection_candidates():
    path = artifact_path("inspection_candidate_recommendations_v0_3.csv")
    rows = read_csv(path)
    fields = list(rows[0].keys())
    templates = {row["scenario_id"]: row for row in NOISE_SCENARIOS + RADIATION_SCENARIOS}
    additions = []
    for sid, tpl in templates.items():
        section, subsection = INSPECTION_SECTIONS[sid]
        for inspection_type in ["FIRST", "MONTHLY"]:
            row = {field: "" for field in fields}
            row.update({
                "scenario_id": sid,
                "scenario_name": tpl["scenario_name"],
                "inspection_type": inspection_type,
                "candidate_section": section,
                "candidate_subsection": subsection,
                "risk_or_hidden_danger_point": "；".join(tpl["confirmation_questions"][:2]),
                "evidence_chain": "；".join(tpl["evidence_requirements"]),
                "photo_points": "；".join(tpl["photo_points"]),
                "applicable_when": "；".join(tpl["triggers"]),
                "not_applicable_when": "；".join(tpl["not_applicable_conditions"]),
                "confirmation_questions": "；".join(tpl["confirmation_questions"]),
                "answer_policy": "[\"PASS\",\"FAIL\",\"NA\",\"NEED_CONFIRM\"]",
                "default_severity": "NEED_CONFIRM",
                "default_deduct": "",
                "runtime_status": RUNTIME_CANDIDATE,
            })
            additions.append(row)
    upsert_composite(rows, ["scenario_id", "inspection_type"], additions)
    write_csv(path, rows, fields)


def update_process_triggers():
    path = artifact_path("process_trigger_dictionary_v1_1.csv")
    rows = read_csv(path)
    fields = list(rows[0].keys())
    additions = [with_boundary(row) for row in PROCESS_TRIGGERS]
    upsert_by(rows, "process_id", additions)
    write_csv(path, rows, fields)
    write_json(artifact_path("process_trigger_dictionary_v1_1.json"), rows)


def update_activation_rules():
    path = artifact_path("process_scenario_activation_rules_v1_3.csv")
    rows = read_csv(path)
    fields = list(rows[0].keys())
    additions = []
    for rule_id, process_id, scenario_id, activation, negative, evidence, photo, score13, confidence in ACTIVATION_RULES:
        additions.append(with_boundary({
            "rule_id": rule_id,
            "process_id": process_id,
            "scenario_id": scenario_id,
            "activation_condition": activation,
            "negative_condition": negative,
            "evidence_strength_required": "DIRECT_OR_PERMIT_DOCUMENTED",
            "evidence_chain": evidence,
            "photo_points": photo,
            "score13_hint": score13,
            "open_question_refs": "OQ-RADIATION-NOISE-V1-8" if "RADIATION" in rule_id or "RADIOACTIVE" in rule_id or "NORM" in rule_id else "",
            "rule_effect": "CANDIDATE_SCENARIO_ACTIVATION_ONLY",
            "confidence": confidence,
        }))
    upsert_by(rows, "rule_id", additions)
    write_csv(path, rows, fields)
    write_json(artifact_path("process_scenario_activation_rules_v1_3.json"), rows)


def source_domain_for(path):
    name = path.name
    if "噪声" in name:
        return "noise"
    if any(token in name for token in ["运输", "容器", "栓系", "提升"]):
        return "radiation_transport"
    if any(token in name for token in ["废物", "废放射源", "固化体", "处置", "废物库", "退役", "铀", "钍", "工业废渣"]):
        return "radioactive_waste"
    if any(token in name for token in ["同位素", "射线装置", "放射性污染"]):
        return "radiation_device_source"
    return "radiation"


def scenario_refs_for(domain):
    mapping = {
        "noise": "SCN_NOISE_SOURCE_BOUNDARY_CONTROL;SCN_SOCIAL_LIFE_NOISE_SOURCE",
        "radiation_transport": "SCN_RADIOACTIVE_MATERIAL_TRANSPORT",
        "radioactive_waste": "SCN_RADIOACTIVE_WASTE_STORAGE_TRANSFER_DISPOSAL;SCN_RADIOACTIVE_SOURCE_SECURITY;SCN_NORM_RADIOACTIVITY_IN_INDUSTRIAL_RESIDUE",
        "radiation_device_source": "SCN_RADIATION_DEVICE_SOURCE_SAFETY;SCN_RADIOACTIVE_SOURCE_SECURITY",
        "radiation": "SCN_RADIATION_DEVICE_SOURCE_SAFETY;SCN_RADIOACTIVE_WASTE_STORAGE_TRANSFER_DISPOSAL",
    }
    return mapping[domain]


def build_reference_index():
    rows = []
    for folder in [ROOT / "reference_sources" / "noise", ROOT / "reference_sources" / "radiation"]:
        for path in sorted(folder.glob("*.pdf")):
            domain = source_domain_for(path)
            rows.append({
                "source_id": f"SRC18_{len(rows)+1:03d}",
                "domain": domain,
                "source_type": "PDF_REGULATION_OR_STANDARD",
                "file_path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "file_name": path.name,
                "applicable_scenario_ids": scenario_refs_for(domain),
                "extraction_status": "INDEXED_NOT_EXTRACTED",
                "source_basis": "用户新增噪声和辐射/放射法规标准资料目录，v1.8先做可审计索引和场景承接，不做条文级自动确认。",
                "confidence": "MEDIUM",
                "runtime_status": RUNTIME_STATUS,
                "final_state": FINAL_STATE,
                "runtime_integration": RUNTIME_INTEGRATION,
            })
    fields = [
        "source_id",
        "domain",
        "source_type",
        "file_path",
        "file_name",
        "applicable_scenario_ids",
        "extraction_status",
        "source_basis",
        "confidence",
        "runtime_status",
        "final_state",
        "runtime_integration",
    ]
    write_csv(artifact_path("noise_radiation_reference_sources_v1_8.csv"), rows, fields)
    write_json(artifact_path("noise_radiation_reference_sources_v1_8.json"), rows)
    return rows


def update_artifact_manifest():
    path = ROOT / "artifact_manifest.json"
    data = read_json(path)
    artifacts = data.setdefault("artifacts", {})
    updates = {
        "build_noise_radiation_domain_extension_v1_8.py": "build_noise_radiation_domain_extension_v1_8.py",
        "validate_noise_radiation_domain_extension_v1_8.py": "validate_noise_radiation_domain_extension_v1_8.py",
        "noise_radiation_reference_sources_v1_8.csv": "reference_sources/noise_radiation_reference_sources_v1_8.csv",
        "noise_radiation_reference_sources_v1_8.json": "reference_sources/noise_radiation_reference_sources_v1_8.json",
        "knowledge_base_manifest_v1_8_noise_radiation_extension.json": "manifests/knowledge_base_manifest_v1_8_noise_radiation_extension.json",
        "noise_radiation_domain_extension_gate_report_v1_8.json": "reports/noise_radiation_domain_extension_gate_report_v1_8.json",
        "noise_radiation_domain_extension_gate_report_v1_8.md": "reports/noise_radiation_domain_extension_gate_report_v1_8.md",
        "FINAL_COMPLETION_REPORT_v1_8_noise_radiation_extension.md": "reports/FINAL_COMPLETION_REPORT_v1_8_noise_radiation_extension.md",
    }
    artifacts.update(updates)
    write_json(path, data)


def write_manifest_and_reports(source_rows):
    new_scenario_ids = [row["scenario_id"] for row in NOISE_SCENARIOS + RADIATION_SCENARIOS]
    manifest = {
        "knowledge_base_version": VERSION,
        "base": "existing governed candidate KB",
        "scope": "noise_radiation_domain_extension_only",
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
        "runtime_effect": "NONE",
        "outputs": [
            "scenario_templates.json",
            "scenario_to_score13_mapping_v0_3.csv",
            "inspection_candidate_recommendations_v0_3.csv",
            "process_trigger_dictionary_v1_1.csv/json",
            "process_scenario_activation_rules_v1_3.csv/json",
            "noise_radiation_reference_sources_v1_8.csv/json",
        ],
        "new_scenario_ids": new_scenario_ids,
        "source_counts": {
            "noise_pdf_count": sum(1 for row in source_rows if row["domain"] == "noise"),
            "radiation_pdf_count": sum(1 for row in source_rows if row["domain"] != "noise"),
        },
        "hard_boundaries": [
            "noise may be broad candidate recall but remains NEED_CONFIRM/CANDIDATE_ONLY",
            "radiation must not be all-industry default",
            "no_ecocheck_runtime_integration",
            "no_formal_permit_type",
            "no_formal_inspection_template",
            "no_auto_deduct",
        ],
    }
    write_json(artifact_path("knowledge_base_manifest_v1_8_noise_radiation_extension.json"), manifest)

    gate = {
        "validation_status": "PENDING_RUN_VALIDATE",
        "knowledge_base_version": VERSION,
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
        "new_scenario_count": len(new_scenario_ids),
        "new_process_trigger_count": len(PROCESS_TRIGGERS),
        "new_activation_rule_count": len(ACTIVATION_RULES),
        "reference_source_count": len(source_rows),
    }
    write_json(artifact_path("noise_radiation_domain_extension_gate_report_v1_8.json"), gate)
    gate_md = f"""# v1.8 噪声与辐射/放射知识域增量门禁报告

final_state: `{FINAL_STATE}`

本轮在现有规则库上增量补齐 `noise` 与 `radiation` 知识域，不另造规则库，不接运行时。

## 新增场景

{chr(10).join(f"- `{sid}`" for sid in new_scenario_ids)}

## 边界

- 噪声可作为生产经营通用候选召回，但必须现场确认主要噪声源、厂界监测和适用边界。
- 辐射/放射只能由射线装置、放射源、放射性废物、运输、NORM/工业废渣等明确证据触发，禁止全行业默认适用。
- 所有新增内容保持 `DRAFT_NOT_FOR_RUNTIME` / `CANDIDATE_ONLY` / `NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY`。

请运行：

```powershell
python build_noise_radiation_domain_extension_v1_8.py
python validate_noise_radiation_domain_extension_v1_8.py
```
"""
    artifact_path("noise_radiation_domain_extension_gate_report_v1_8.md").write_text(gate_md, encoding="utf-8")

    final = f"""# FINAL_COMPLETION_REPORT_v1_8_noise_radiation_extension

final_state: `{FINAL_STATE}`

本轮没有新建独立规则库，而是在现有环保语义规则库上增量补齐噪声和辐射/放射两个知识域。

## 完成内容

- 将新增法规标准资料纳入 `reference_sources/noise` 与 `reference_sources/radiation`。
- 新增 {len(NOISE_SCENARIOS)} 个噪声场景模板和 {len(RADIATION_SCENARIOS)} 个辐射/放射场景模板。
- 保留旧模板兼容关系，并标注噪声、辐射应由新细分模板承接。
- 更新 13维映射候选、现场排查候选、工序触发字典和工序-场景激活规则。
- 生成 `noise_radiation_reference_sources_v1_8.csv/json` 作为 PDF 资料可审计索引。

## 禁止事项

- 不接 EcoCheck runtime。
- 不生成正式 permit_type。
- 不生成正式检查模板。
- 不自动扣分。
- 辐射/放射不做全行业默认适用。

## 验证

```powershell
python build_noise_radiation_domain_extension_v1_8.py
python validate_noise_radiation_domain_extension_v1_8.py
```
"""
    artifact_path("FINAL_COMPLETION_REPORT_v1_8_noise_radiation_extension.md").write_text(final, encoding="utf-8")


def update_readme():
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")
    line = "- `reports/FINAL_COMPLETION_REPORT_v1_8_noise_radiation_extension.md`: v1.8 噪声与辐射/放射知识域增量完成报告。"
    if line not in text:
        marker = "- `reports/FINAL_COMPLETION_REPORT_v1_2_to_v1_7.md`: v1.2-v1.7 候选治理链完成报告，覆盖环评/许可抽取、激活规则、open questions、审阅切片、RAG eval 和接入差距。"
        text = text.replace(marker, marker + "\n" + line)
    path.write_text(text, encoding="utf-8")


def main():
    update_artifact_manifest()
    update_scenario_templates()
    update_score_mapping()
    update_inspection_candidates()
    update_process_triggers()
    update_activation_rules()
    source_rows = build_reference_index()
    write_manifest_and_reports(source_rows)
    update_readme()
    print(json.dumps({
        "build_status": "PASS",
        "knowledge_base_version": VERSION,
        "new_scenarios": len(NOISE_SCENARIOS) + len(RADIATION_SCENARIOS),
        "reference_sources": len(source_rows),
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
