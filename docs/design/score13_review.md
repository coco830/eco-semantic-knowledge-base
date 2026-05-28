# EcoCheck 环保13维评审

## 保持不变的理由

EcoCheck 13 维已经是报告口径和历史数据口径，直接改名或拆分会影响扣分项、导出包、趋势对比和报告解释。本次建议保持 S01-S13 不变，只在知识图谱和 RAG 层增加二级语义。

## 需要二级语义增强的地方

- S08 环保培训情况：当前 24 标签没有承载培训，应新增 `environmental_training`、`hazardous_waste_training`、`emergency_drill_training`、`radiation_staff_training`。
- S13 环保应急管理情况：现有应急预案、物资、事故记录在映射中散落到 S01/S06/S02；知识层应补 `emergency_plan`、`drill`、`materials`、`accident_water`、`incident_record`。
- S10 废水、废气、噪声、废渣排放及处置情况：过宽，应按 `water_discharge`、`organized_exhaust`、`unorganized_exhaust`、`vocs_material`、`particulate_control`、`noise_boundary` 拆二级。
- S07 固体废物贮存规范情况：应区分一般固废、危废、医废；现场贮存归 S07，台账、联单、去向凭证归 S02。
- S09 标识、标牌、制度公示情况：需要和危废、排口、辐射、应急标识建立二级关系。
- S11 历史遗留问题整改情况：默认行业画像不应硬塞 S11，但月度和复查场景必须有整改闭环、复发防控、前后对比证据。

## 不建议直接改名/拆分的风险

直接拆 S10 或改 S07/S13 名称，会导致既有报告、扣分统计、前端选项、导出字段和历史趋势不兼容。更稳的做法是在 `scenario_to_score13_mapping.csv` 里保留主维度，同时用 `current_13_dimension_gap` 和 `suggested_improvement` 标注二级增强。这样报告口径稳定，RAG 和环保语义图谱又能获得足够细的知识节点。
