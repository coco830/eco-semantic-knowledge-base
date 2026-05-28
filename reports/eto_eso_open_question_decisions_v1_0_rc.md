# eto_eso_open_question_decisions_v1_0_rc

final_state: `NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY`
runtime_integration: `disabled`
decision_status: `PRELIMINARY_ETO_ESO_REVIEW_RECORDED`

本文件记录 ETO/ESO 对 `open_questions_review_guide_v1_0_rc.md` 的初步业务判定。它是技术审阅意见，不是运行时批准，不关闭 `BLOCKS_RUNTIME`，不解除任何运行时阻断，不填写或伪造 `human_review_label` / `human_reviewer` / `reviewed_at`。

## 总原则

- 所有结论在系统修复、证据留档、验证通过前，继续保持 `BLOCKS_RUNTIME`。
- 严格禁止进入 EcoCheck runtime。
- 严格禁止自动生成正式 `permit_type`。
- 严格禁止自动生成正式检查模板或自动扣分。
- `DIVISION_CONTEXT` 只能作为召回线索，不能直接升级为 `APPLIES`。
- `NOT_APPLY` 必须有明确 `blocking_flags` 或排除依据，否则降级为 `NEED_EIA_OR_PERMIT_CONFIRM`。

## P0 立即固化口径

### OQ-001 1512/1513

ETO 确认：GB/T 4754-2017 中 `1512=白酒制造`，`1513=啤酒制造`。早期规则若把 1512 当作啤酒制造，属于明确代码-名称错配，必须修复并清理残留。

需要留档：GB/T 4754-2017 原文截图；修复前后 `candidate_rule_id` 对照；受影响企业清单如有。

### V04_DIVISION_CONTEXT_APPLIES_001

ETO 确认：纯 `DIVISION_CONTEXT` 自动升级 `APPLIES` 零容忍。升级必须具备直接四位代码匹配、直接名称匹配或条件文本命中，并保留人工审阅记录。

需要留档：0 条纯 `DIVISION_CONTEXT -> APPLIES` 检查结果；升级规则；审阅字段要求。

### V03_PERMIT_TYPE_001

ETO 确认：`target_management_condition` 只代表名录条件列，不等于企业法定 `permit_type`。正式 `permit_type` 只能由排污许可证副本、固定污染源排污登记回执或环评批复等材料确认。

需要留档：字段边界说明；正式 `permit_type` 确认材料白名单；禁止自动生成声明。

### V04_NOT_APPLY_BLOCKING_FLAGS_001

ETO 确认：没有明确排除依据的 `NOT_APPLY` 必须降级为 `NEED_EIA_OR_PERMIT_CONFIRM`。排除依据包括名录明确排除文本、相邻条目/小类排除规则、或有签字留痕的 forced_denoise。

需要留档：`NOT_APPLY` 抽检结果；缺失 `blocking_flags` 清单；降级 diff；0 条缺依据 `NOT_APPLY` 查验结果。

## 行业与名录边界

### OQ-002 代表性小类外推

ETO 判定：名录只写代表性小类或行业短语时，默认禁止外推到同组、同中类或同大类其他四位小类。只有名录原文、生态环境部解释或完全一致产排污节点和污染物特征能支持时，才可例外，并默认走 `NEED_EIA_CONFIRM`。

### OQ-003 纸浆 221 与 222/223

ETO 判定：第 36 条纸浆制造 `221` 仅限 221 中类，不得继承至 222 造纸或 223 纸制品制造。

### OQ-004 纸制品 223

ETO 判定：第 38 条纸制品制造 `223` 不得反向继承到 2211/222。触发事实主要是工业废水工序，或涂布、浸渍、印刷、粘结等产生 VOCs 废气的工序。

### OQ-005 通用工序定位

ETO 判定：109-112 通用工序是工序维度，不是行业维度。只能作为召回线索或辅助校验，不能直接推导企业最终 `permit_type`。

### OQ-006 装备/金属制品工序触发

ETO 判定：3311 等装备、金属制品相邻小类必须以表面处理、电镀、酸洗、喷涂、热处理、工业炉窑等现场事实确认；无工序证据不得判定适用。

### V04_ENTRY_108_CONTEXT_001

ETO 判定：第 108 条是“除 1-107 外其他行业涉及通用工序”的兜底交叉引用，只由 109-112 承接；不得生成覆盖全行业的独立关系或笛卡尔积。

## 人工审阅与场景模板

### V04_HUMAN_REVIEW_EMPTY_001

ETO+ESO 判定：空人工审阅字段绝不能视为已确认。初版上线前或关键变更应全量审阅；稳定后可风险抽样，但 `DIVISION_CONTEXT` 升级 `APPLIES`、`NOT_APPLY`、否定语义、重点管理和敏感风险项必须全量审阅。审阅应由 ETO 做技术合规审阅、ESO 做现场事实审阅，并保留签字或系统 UserID。

### V03_SCENARIO_TEMPLATE_001

ETO 判定：需新增尾矿库、实验室废液、垃圾焚烧/填埋等场景模板；餐饮油烟可先延后或作为已有废气场景子项验证。新增模板必须包含触发条件、证据要求和 `photo_points`。

### OQ-007

Product+ETO 口径：候选排查章节和 S18/S19 等扩展编号当前只作为 candidate section，不得直接映射为 EcoCheck 正式模板章节。未来映射需 Product、ETO、Tech Lead 三方审批。

## 运行时与报告口径

### V03_ECOCHECK_RUNTIME_001 / V04_RUNTIME_APPROVAL_GATE_001

当前结论：`BLOCK_RUNTIME`。未来只有在设计审批、契约测试、回滚方案、安全审计全部完成后，才可进入单独实现分支；本知识库包不执行运行时导入。

### V04_SCORE13_PROMOTION_001

Product+ETO 口径：S01-S13 一级报告口径保持不变。二级语义可进入 RAG、图谱和报告段落提示，但不得直接改名或拆分 13 维编码；任何一级口径变更必须另走审批。

### V04_NEGATION_POLARITY_001

ETO 判定：含“除/不含/以外/无/未”的条件必须保留排除语义，解析为 `not_present` 或 `excluded`。需要全量否定词扫描、抽检比对和单测留档。

## 后续技术动作

1. 将本文件与 `eto_eso_open_question_decisions_v1_0_rc.csv` 作为初步审阅决策输入。
2. 针对 `NEED_RULE_FIX`、`ADD_NEW_SCENARIO`、`DOWNGRADE_TO_NEED_CONFIRM` 等项，另开 v1.1 治理修复任务。
3. 修复完成后生成 diff、验证报告和 close evidence，再决定是否关闭对应 open question。
4. 在所有 close evidence 完成前，继续保持 `NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY`。
