# open_questions_review_guide_v1_0_rc

final_state: `NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY`
runtime_integration: `disabled`

这份文件把 `open_questions_v0_4_1.csv` 整理成可以分派给人审的具体问题。它不是人工审阅结论，不填写 `human_review_label`，也不解除任何运行时阻断。

## 怎么用

1. 先按 `ask_who` 找到责任角色。
2. 把 `concrete_question` 直接发给对应负责人。
3. 按 `check_materials` 查证据。
4. 只能从 `decision_options` 中选择初步结论，或补充说明为什么不能选择。
5. 关闭问题时必须留下 `evidence_to_record`，并满足 `close_condition`。
6. 关闭前一律保持 `BLOCKS_RUNTIME`，不得接 EcoCheck runtime。

## 按角色分派

- ETO: OQ-002, OQ-003, OQ-004, OQ-005, OQ-006, V03_CONTEXT_SCOPE_001, V03_PERMIT_TYPE_001, V03_GENERAL_PROCESS_001, V03_SCENARIO_TEMPLATE_001, V04_ENTRY_108_CONTEXT_001, V04_NEGATION_POLARITY_001, V04_DIVISION_CONTEXT_APPLIES_001, V04_NOT_APPLY_BLOCKING_FLAGS_001
- ETO+ESO: V04_HUMAN_REVIEW_EMPTY_001
- ETO；必要时由资料负责人提供GB/T 4754原表截图: OQ-001
- Product+ETO: OQ-007, V04_SCORE13_PROMOTION_001
- Product+ETO+Tech Lead: V03_ECOCHECK_RUNTIME_001
- Product+Tech Lead: V04_RUNTIME_APPROVAL_GATE_001

## 具体问题

### OQ-001

- 找谁问：ETO；必要时由资料负责人提供GB/T 4754原表截图
- 具体要问：请确认GB/T 4754-2017中1512是否为白酒制造、1513是否为啤酒制造；早期规则中是否仍有把1512当作啤酒制造的残留。
- 怎么查：2017国民经济行业分类注释.xlsx；industry_catalog_base.csv；all_industry_scenario_candidates_v0_2.csv；旧12行业试跑资料如仍有留档也要核对。
- 可选结论：CONFIRM_FIXED；NEED_MORE_SOURCE；NEED_RULE_FIX
- 要留什么证据：GB/T 4754原表行号/截图；修正前后代码名称对照；受影响candidate_rule_id清单。
- 关闭条件：1512=白酒制造、1513=啤酒制造的口径已写入候选底座，且无旧错配入口残留。
- 运行时影响：关闭前不得把1512/1513相关候选升级为运行时正式规则。

### OQ-002

- 找谁问：ETO
- 具体要问：名录条目只写代表性小类或行业短语时，是否允许外推到同组、同中类或同大类其他四位小类？哪些情况下必须禁止外推？
- 怎么查：固定污染源排污许可分类管理名录原文；GB/T 4754小类解释；all_context_applicability_review_v0_4_1.csv中relation_source和matched_code_or_text。
- 可选结论：ALLOW_GROUP_INHERIT；ALLOW_CLASS_ONLY；NEED_EIA_CONFIRM；REJECT_INHERIT
- 要留什么证据：外推规则说明；可外推/不可外推示例；受影响entry_no和industry_code。
- 关闭条件：形成代表性小类外推规则，并标明默认不得从DIVISION_CONTEXT直接升级APPLIES。
- 运行时影响：关闭前所有代表性小类外推关系保持候选或待确认。

### OQ-003

- 找谁问：ETO
- 具体要问：第36条纸浆制造221与2211、222、223之间的继承边界是什么？是否仅限221相关小类，不得继承到造纸222或纸制品223？
- 怎么查：名录第36条；GB/T 4754中221/222/223定义；相关候选关系表。
- 可选结论：LIMIT_TO_221；EXTEND_WITH_EVIDENCE；NEED_EIA_CONFIRM；REJECT_CANDIDATE
- 要留什么证据：221/222/223边界说明；名录原文截图；被调整关系清单。
- 关闭条件：纸浆、造纸、纸制品相邻中类边界形成书面口径。
- 运行时影响：关闭前不得把221、222、223相邻关系作为正式适用依据。

### OQ-004

- 找谁问：ETO
- 具体要问：第38条纸制品制造223是否不得继承到2211/222类？工业废水、废气条件分别由什么现场事实触发？
- 怎么查：名录第38条；纸制品相关环评/许可样例；all_context_applicability_review_v0_4_1.csv。
- 可选结论：LIMIT_TO_223；TRIGGER_BY_WASTEWATER；TRIGGER_BY_EXHAUST；NEED_SITE_CONFIRM
- 要留什么证据：223适用边界；废水/废气触发条件；确认问题模板。
- 关闭条件：形成纸制品条目-小类适用规则和现场确认问题。
- 运行时影响：关闭前纸制品跨中类关系保持NEED_EIA_OR_PERMIT_CONFIRM。

### OQ-005

- 找谁问：ETO
- 具体要问：食品/农副食品条目中的通用工序触发，是否只能作为召回线索，不能直接推导企业许可管理类型？
- 怎么查：名录第15条及相关食品条目；企业环评/许可样例；109-112通用工序条目。
- 可选结论：RECALL_ONLY；MAY_APPLY_WITH_EVIDENCE；NEED_EIA_CONFIRM
- 要留什么证据：通用工序清单；对应证据要求；不得直接生成permit_type的说明。
- 关闭条件：通用工序触发统一限定为MAY_APPLY或NEED_EIA_OR_PERMIT_CONFIRM，除非有直接证据。
- 运行时影响：关闭前不得由通用工序候选自动生成正式permit_type。

### OQ-006

- 找谁问：ETO
- 具体要问：装备、金属制品相关条目中，3311等相邻小类如何根据表面处理、喷涂、热处理、工业炉窑等工序确认适用？
- 怎么查：名录第80条；GB/T 4754中3311及相邻小类；企业工艺流程、环评、许可。
- 可选结论：DIRECT_CODE_ONLY；PROCESS_TRIGGER_MAY_APPLY；NEED_SITE_CONFIRM；REJECT_ADJACENT_CLASS
- 要留什么证据：3311及相关小类边界；工序触发证据链；受影响候选关系。
- 关闭条件：形成3311及相关小类的工序触发边界和确认证据要求。
- 运行时影响：关闭前相邻小类不得仅凭大类上下文升级APPLIES。

### OQ-007

- 找谁问：Product+ETO
- 具体要问：候选排查章节和S18/S19等知识库章节编号，是否只作为未来候选子章，不映射为当前EcoCheck正式模板章节？
- 怎么查：inspection_candidate_recommendations_v0_3.csv；当前EcoCheck首次/月度模板；产品报告章节口径。
- 可选结论：CANDIDATE_ONLY；MAP_TO_EXISTING_SECTION；NEED_PRODUCT_APPROVAL
- 要留什么证据：章节映射表；不接运行时声明；如映射需产品审批记录。
- 关闭条件：产品和ETO确认正式模板章节映射方案；未经审批不得接运行时。
- 运行时影响：关闭前不得生成正式检查模板或自动扣分。

### V03_CONTEXT_SCOPE_001

- 找谁问：ETO
- 具体要问：DIVISION_CONTEXT是否只能作为召回线索？什么证据足以把MAY_APPLY/NEED_EIA升级为APPLIES？
- 怎么查：all_context_applicability_review_v0_4_1.csv；relation_source；matched_code_or_text；名录原文。
- 可选结论：RECALL_ONLY；APPLIES_WITH_DIRECT_CODE；APPLIES_WITH_NAME_TEXT；NEED_HUMAN_REVIEW
- 要留什么证据：升级证据字段要求；人工审阅字段要求；示例关系ID。
- 关闭条件：形成DIVISION_CONTEXT升级规则，且保留人工审阅要求。
- 运行时影响：关闭前DIVISION_CONTEXT不能直接进入运行时正式适用关系。

### V03_PERMIT_TYPE_001

- 找谁问：ETO
- 具体要问：target_management_condition是否只表示名录条件列，不等于企业正式permit_type？正式permit_type需哪些材料确认？
- 怎么查：all_permit_condition_backfill_v0_4_1.csv；企业排污许可证/登记回执；环评批复。
- 可选结论：COLUMN_ONLY；CAN_PROMOTE_WITH_PERMIT_EVIDENCE；NEED_PERMIT_CONFIRM
- 要留什么证据：字段定义；正式permit_type确认材料清单；禁止自动生成说明。
- 关闭条件：形成target_management_condition和permit_type字段边界说明。
- 运行时影响：关闭前不得由候选条件列生成企业正式permit_type。

### V03_GENERAL_PROCESS_001

- 找谁问：ETO
- 具体要问：109-112通用工序如何依据锅炉、工业炉窑、表面处理、水处理事实确认？每类工序需要什么证据？
- 怎么查：名录109-112条；工艺流程图；设备清单；环评/许可；现场照片。
- 可选结论：CONFIRM_BY_EIA；CONFIRM_BY_PERMIT；CONFIRM_BY_SITE；NOT_APPLY
- 要留什么证据：四类通用工序证据清单；确认问题；适用/不适用样例。
- 关闭条件：形成109-112通用工序证据要求和适用关系规则。
- 运行时影响：关闭前通用工序只能作为候选触发。

### V03_SCENARIO_TEMPLATE_001

- 找谁问：ETO
- 具体要问：是否需要新增尾矿库、餐饮油烟、实验室废液、垃圾焚烧/填埋等场景模板？哪些已有模板可覆盖，哪些必须新增？
- 怎么查：scenario_templates.json；行业样例；环保设施/风险单元清单；法规技术规范。
- 可选结论：COVERED_BY_EXISTING；ADD_NEW_SCENARIO；KEEP_OPEN
- 要留什么证据：新增/不新增理由；触发条件；证据要求；photo_points。
- 关闭条件：完成场景模板缺口评审，新增模板或明确延后。
- 运行时影响：关闭前不影响候选库，但会影响RAG/图谱覆盖度。

### V03_ECOCHECK_RUNTIME_001

- 找谁问：Product+ETO+Tech Lead
- 具体要问：候选排查项在什么审批和测试条件下，才允许进入EcoCheck运行时？
- 怎么查：runtime_promotion_gate_design_v1_0_rc.md；runtime_contract_test_plan_v1_0_rc.md；approval_workflow_v1_0_rc.md。
- 可选结论：BLOCK_RUNTIME；APPROVE_DESIGN_ONLY；APPROVE_IMPLEMENTATION_BRANCH
- 要留什么证据：审批记录；契约测试结果；回滚方案；版本manifest。
- 关闭条件：形成运行时接入审批、回滚和契约测试方案。
- 运行时影响：关闭前不得接小程序或后端运行时。

### V04_ENTRY_108_CONTEXT_001

- 找谁问：ETO
- 具体要问：第108条是否只作为“除1-107外其他行业+通用工序”的兜底引用？是否仍由109-112通用工序承接，而不生成独立全行业关系？
- 怎么查：名录第108-112条；knowledge_base_v0_4_1_gate_report.md；all_context_applicability_review_v0_4_1.csv。
- 可选结论：CROSS_REFERENCE_ONLY；ADD_EXPLICIT_RELATIONS；KEEP_OPEN
- 要留什么证据：第108条承接策略；不生成全行业笛卡尔关系的理由；如新增需关系表设计。
- 关闭条件：确认第108条承接策略，并写入manifest/gate report。
- 运行时影响：关闭前第108条不得被误读为覆盖缺失或独立行业规则。

### V04_HUMAN_REVIEW_EMPTY_001

- 找谁问：ETO+ESO
- 具体要问：人工审阅工作表由谁审？抽样还是全量？每个标签需要哪些必填字段和签字留痕？
- 怎么查：human_review_worksheet_v0_7.xlsx；human_review_decision_schema_v0_7.md；human_review_guidance_v0_7.md。
- 可选结论：DEFINE_FULL_REVIEW；DEFINE_SAMPLING_REVIEW；KEEP_ALL_EMPTY
- 要留什么证据：审阅责任人；标签枚举；review_basis/evidence_refs填写规则；签字留痕。
- 关闭条件：完成审阅标签枚举、审阅责任和签字留痕制度。
- 运行时影响：关闭前不得把空人工审阅字段解释为已确认。

### V04_SCORE13_PROMOTION_001

- 找谁问：Product+ETO
- 具体要问：S01-S13报告口径保持不变时，S07/S08/S10/S13二级语义如何进入RAG、图谱和报告段落提示？
- 怎么查：scenario_to_score13_mapping_v0_3.csv；score13_review.md；EcoCheck报告模板。
- 可选结论：GRAPH_ONLY；RAG_AND_REPORT_HINT；CHANGE_REQUIRES_APPROVAL
- 要留什么证据：二级语义字段表；报告展示策略；不改13维名称说明。
- 关闭条件：形成二级语义层字段与报告展示策略，不直接改名或拆分S01-S13。
- 运行时影响：关闭前不得改变EcoCheck报告13维口径。

### V04_RUNTIME_APPROVAL_GATE_001

- 找谁问：Product+Tech Lead
- 具体要问：候选知识库何时、由谁、凭什么验证证据批准进入EcoCheck运行时？失败后如何回滚？
- 怎么查：runtime_promotion_gate_design_v1_0_rc.md；runtime_rollback_plan_v1_0_rc.md；security_audit_log_design_v1_0_rc.md。
- 可选结论：DESIGN_ONLY；APPROVE_BRANCH_WORK；APPROVE_RUNTIME_IMPORT
- 要留什么证据：二次审批记录；测试报告；rollback manifest；审计日志字段。
- 关闭条件：形成运行时接入审批门禁、回滚方案和小程序契约测试方案。
- 运行时影响：关闭前所有候选资产保持NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY。

### V04_NEGATION_POLARITY_001

- 找谁问：ETO
- 具体要问：含“除/不含/以外/无/未”的条件是否全部保留排除语义？特别是“除纳入重点排污单位名录”是否表达为not_present而不是正向命中？
- 怎么查：all_permit_condition_backfill_v0_4_1.csv；normalized_predicates；raw_condition；抽检样本。
- 可选结论：POLARITY_OK；NEED_RULE_FIX；NEED_MANUAL_REVIEW
- 要留什么证据：否定词扫描结果；修复前后样例；单测或抽检记录。
- 关闭条件：否定语义谓词经抽检无正向化，必要时补充规则库单测。
- 运行时影响：关闭前否定条件不得用于自动正式化。

### V04_DIVISION_CONTEXT_APPLIES_001

- 找谁问：ETO
- 具体要问：是否仍存在纯DIVISION_CONTEXT自动升级为APPLIES？未来升级APPLIES时必须有哪些直接代码/名称/条件文本证据和人工审阅记录？
- 怎么查：all_context_applicability_review_v0_4_1.csv；automated_denoise_diff_report_v0_4.md；relation_source。
- 可选结论：NO_DIRECT_APPLIES；ALLOW_WITH_DIRECT_EVIDENCE；NEED_REVIEW
- 要留什么证据：0条纯DIVISION_CONTEXT->APPLIES检查结果；升级规则；审阅字段要求。
- 关闭条件：0条纯DIVISION_CONTEXT->APPLIES，升级路径有人工审阅字段和证据链。
- 运行时影响：关闭前DIVISION_CONTEXT关系不得作为运行时APPLIES。

### V04_NOT_APPLY_BLOCKING_FLAGS_001

- 找谁问：ETO
- 具体要问：NOT_APPLY是否都有/、明确排除文本、相邻条目/小类排除或forced_denoise依据？无法解释的是否应降为NEED_EIA_OR_PERMIT_CONFIRM？
- 怎么查：all_context_applicability_review_v0_4_1.csv；blocking_flags；gate_reason；raw_condition。
- 可选结论：NOT_APPLY_OK；DOWNGRADE_TO_NEED_CONFIRM；NEED_RULE_FIX
- 要留什么证据：NOT_APPLY抽检结果；缺失blocking_flags清单；降级diff。
- 关闭条件：0条NOT_APPLY缺少blocking_flags或明确排除依据。
- 运行时影响：关闭前缺证据NOT_APPLY不得进入运行时。
