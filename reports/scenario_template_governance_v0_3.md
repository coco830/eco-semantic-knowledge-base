# 场景模板治理 v0.3

本文件对应 `scenario_template_governance_v0_3.json`。场景是产污场景，不是行业硬编码；行业只作为召回入口，最终以环评、批复、排污许可、台账和现场事实确认。

- `SCN_BASE_PRODUCTION_SOLID_NOISE_LEDGER`：通用生产经营、一般固废、噪声与基础台账；风险点：生产活动与手续不一致；一般固废/噪声/台账证据不足；现场事实需确认
- `SCN_WW_PROCESS_AND_TREATMENT`：生产/医疗/清洗废水与污水处理设施；风险点：废水来源不清；污水站停运或绕排；排口/接管证据缺失
- `SCN_VOCS_SOLVENT_AND_TREATMENT`：VOCs溶剂使用、无组织排放与废气治理；风险点：VOCs无组织逸散；废气治理设施低效；废活性炭更换证据缺失
- `SCN_HAZWASTE_STORAGE_TRANSFER`：危险废物识别、暂存与转移；风险点：危废识别不全；暂存间不规范；联单/台账缺失
- `SCN_MEDICAL_WASTE_RADIATION`：医疗废物、医疗废水与放射诊疗确认；风险点：医废混入生活垃圾；医疗废水/放射诊疗边界不清；暂存和转运证据缺失
- `SCN_CHEMICAL_TANK_LDAR_SEEPAGE`：液态化学品储罐、LDAR与防渗风险；风险点：储罐围堰/防渗不足；LDAR缺失；泄漏与土壤地下水风险
- `SCN_GAS_STATION_VAPOR_UST`：加油站油气回收、地下储罐与土壤地下水风险；风险点：油气回收异常；地下储罐防渗监测缺失；卸油区应急措施不足
- `SCN_DUST_PARTICULATE_CONTROL`：粉尘颗粒物产生与除尘设施；风险点：粉尘无组织排放；除尘设施失效；料场/装卸扬尘
- `SCN_ONLINE_MONITORING_KEY_UNIT`：重点管理/重点排污单位在线监测；风险点：在线监测未联网；运维记录缺失；数据异常未闭环
- `SCN_RAINWATER_ACCIDENT_EMERGENCY`：雨污分流、事故水与环境应急；风险点：雨污混接；事故水收集不足；应急物资/演练缺失
- `SCN_TRAINING_SIGNAGE_REVIEW_GAP`：环保培训、标识公示与历史问题闭环补强；风险点：培训缺失；标识公示不足；整改闭环证据不足
