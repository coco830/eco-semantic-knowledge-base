# PROJECT_INDEX_v1_0_rc

final_state: `NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY`
runtime_integration: `disabled`

本目录阶段性封版为 `v1.0-rc design-only baseline`，定位是行业私有知识库候选治理底座，不是 EcoCheck 运行时数据包。

## 当前主入口

- `FINAL_COMPLETION_REPORT_v1_0_rc.md`: v1.0-rc 总结。
- `knowledge_base_manifest_v1_0_rc.json`: 当前封版 manifest。
- `PROJECT_INDEX_v1_0_rc.md`: 本索引。
- `HANDOFF_v1_0_rc.md`: 后续人审、RAG demo、运行时接入分支交接说明。
- `DEPRECATED_AND_REMOVED_FILES_v1_0_rc.md`: 已移出当前主线的历史入口说明。
- `open_questions_review_guide_v1_0_rc.md`: 19个开放问题的可分派审阅指南。
- `open_questions_review_matrix_v1_0_rc.csv`: 19个开放问题的分派矩阵。
- `eto_eso_open_question_decisions_v1_0_rc.md/csv`: ETO/ESO初步审阅决策记录，仍不解除运行时阻断。
- `process_evidence_schema_v1_1.md`: v1.1 工序/工艺证据层候选 schema，把环评、批复、许可、台账和现场事实转成企业画像 overlay。

## 核心数据入口

- `all_context_applicability_review_v0_4_1.csv/json`: 22815 条候选适用关系，全部候选化。
- `all_permit_condition_backfill_v0_4_1.csv/json`: 336 条许可名录条件治理，覆盖 1-112 条 x 三类管理条件。
- `scenario_templates.json`: 产污场景模板，是知识本体核心，不是行业硬编码。
- `scenario_to_score13_mapping_v0_3.csv`: 场景到 EcoCheck S01-S13 的候选语义映射。
- `inspection_candidate_recommendations_v0_3.csv`: 候选排查建议，不能直接生成正式检查模板。
- `open_questions_v0_4_1.csv`: 高风险开放问题。
- `open_questions_review_guide_v1_0_rc.md`: 把开放问题拆成“问谁、问什么、查什么、怎么关闭”。
- `eto_eso_open_question_decisions_v1_0_rc.md/csv`: 已收到的ETO/ESO初步判定，作为后续v1.1治理修复输入。
- `risk_acceptance_queue_v0_4_1.csv`: 运行时阻断风险队列。

## v1.1 工序/工艺证据层入口

v1.1 不是运行时接入包。它用于表达“行业代码/许可名录只是召回入口，企业画像需要由环评、批复、排污许可、台账和现场事实中的工序证据进一步确认”。

- `process_trigger_dictionary_v1_1.csv/json`: 10 类工序触发词典，含正向/否定关键词、证据要求、拍照要点。
- `process_to_scenario_activation_v1_1.csv/json`: 工序到产污场景模板的候选激活关系。
- `process_evidence_predicates_samples_v1_1.csv/json`: 环评/现场证据谓词样例，区分确认、否定、弱证据和新增场景候选。
- `enterprise_profile_overlay_samples_v1_1.csv/json`: 企业画像 overlay 样例，全部要求许可/现场二次确认。
- `process_graph_rag_design_v1_1.md/json`: 工序证据层进入图谱和 RAG 的设计。
- `process_evidence_gate_report_v1_1.md/json`: v1.1 门禁报告。
- `knowledge_base_manifest_v1_1.json`: v1.1 manifest。
- `FINAL_COMPLETION_REPORT_v1_1.md`: v1.1 完成报告。

## v1.2-v1.7 候选治理链入口

这组产物按建议 1-6 继续推进，但仍然只属于候选知识库治理层。

- `eia_permit_extraction_samples_v1_2.csv/json`: 5 个脱敏环评/许可文本抽取样例。
- `eia_permit_extracted_predicates_v1_2.csv/json`: 文本到工序/场景谓词的候选抽取结果。
- `process_scenario_activation_rules_v1_3.csv/json`: 12 条工序证据到产污场景的激活/否定规则。
- `open_question_decision_overlay_v1_4.csv/json`: 19 个 open questions 的 ETO/ESO 初步决策 overlay，不关闭运行时门禁。
- `human_review_slices_v1_5.csv/json`: 7 个 ETO/ESO 审阅专题切片。
- `retrieval_eval_set_v1_6.jsonl`: 12 条 RAG/图谱检索质量评测项，覆盖工序证据、否定作用域、13维、证据链、运行时边界。
- `runtime_readiness_matrix_v1_7.csv/json`: 未来接入前差距矩阵。
- `runtime_readiness_gap_report_v1_7.md/json`: 运行时接入差距报告。
- `knowledge_base_manifest_v1_2_to_v1_7.json`: v1.2-v1.7 manifest。
- `FINAL_COMPLETION_REPORT_v1_2_to_v1_7.md`: v1.2-v1.7 完成报告。

## v1.0 approved 行业专项检查包入口

本入口承接 2026-06-04 ETO 审批通过的行业专项检查包。它和早期候选包不同，已可作为 EcoCheck import 的 approved baseline 输入；但仍不改变评分、扣分、权限、schema 或治理内核。

- `specialized_inspection_items_governance_v1_0.md`: 行业专项检查包治理沉淀，固定“场景/工序/风险单元优先于行业硬挂”、三层结构、ETO 审批准入、维度映射、运行时呈现验收和辐射高风险覆盖层口径。
- `approved_specialized_inspection_items_v1_0.csv`: 49 条已审批专项检查项。
- `approved_specialized_inspection_items_manifest_v1_0.json`: 专项项 manifest，锁定审批状态、计数、CSV hash 和 import 边界。
- `approved_specialized_inspection_items_gate_report_v1_0.json`: 专项项验证报告。
- `ETO_SPECIALIZED_INSPECTION_ITEMS_REVIEW_PLAIN_v1_0.md`: ETO 大白话审核稿、批复结论和修改意见。

## 审阅与回灌入口

- `human_review_queue_v0_7.csv/json`: 全量人工审阅队列。
- `human_review_worksheet_v0_7.xlsx`: 可填写审阅工作表，原始表不得预填人工确认。
- `human_review_overlay_v0_8.csv/json`: 模拟审阅回灌 overlay 示例。
- `review_impact_analysis_v0_9.csv/json`: 审阅结论影响传播分析。
- `review_impact_graph_edges_v0_9.jsonl`: 审阅影响图谱边。

## RAG 与图谱入口

- `kb_graph_schema_v0_5.md`: 图谱 schema。
- `graph_nodes_v0_5.jsonl`: 候选图谱节点。
- `graph_edges_v0_5.jsonl`: 候选图谱边。
- `rag_chunks_v0_5.jsonl`: RAG chunk。
- `retrieval_eval_set_v0_6.jsonl`: RAG/图谱检索评测集。
- `graph_query_samples_v0_6.jsonl`: 图谱查询样例。
- `rag_prototype_results_v0_8.jsonl`: 带审阅状态和候选边界的 RAG 原型结果。

## v1.0-rc 运行时接入设计入口

- `runtime_promotion_gate_design_v1_0_rc.md/json`: 候选进入运行时前的闸门设计。
- `runtime_data_contract_v1_0_rc.md/json`: 未来运行时数据契约设计。
- `runtime_import_candidate_manifest_v1_0_rc.json`: 设计态导入候选 manifest，import_action 必须为 NONE_DESIGN_ONLY。
- `runtime_rollback_plan_v1_0_rc.md`: 未来接入前回滚要求。
- `runtime_contract_test_plan_v1_0_rc.md`: 后端、前端呈现、RAG 边界、回滚契约测试计划。
- `approval_workflow_v1_0_rc.md`: 二次审批流设计。
- `security_audit_log_design_v1_0_rc.md/json`: 审计日志设计。
- `candidate_to_runtime_mapping_v1_0_rc.csv`: 仅设计态候选映射，不得导入运行时。

## 验证命令

按顺序执行：

```powershell
python build_knowledge_base_v0_4_1.py
python validate_knowledge_base_v0_4_1.py
python build_graph_rag_package_v0_5.py
python validate_graph_rag_package_v0_5.py
python build_rag_graph_eval_v0_6.py
python validate_rag_graph_eval_v0_6.py
python build_human_review_package_v0_7.py
python validate_human_review_package_v0_7.py
python build_review_backfill_rag_prototype_v0_8.py
python validate_review_backfill_rag_prototype_v0_8.py
python build_review_impact_graph_v0_9.py
python validate_review_impact_graph_v0_9.py
python build_runtime_design_package_v1_0_rc.py
python validate_runtime_design_package_v1_0_rc.py
python validate_runtime_preintegration_contracts_v1_0_rc.py
python build_process_evidence_package_v1_1.py
python validate_process_evidence_package_v1_1.py
python build_semantic_governance_roadmap_v1_2_to_v1_7.py
python validate_semantic_governance_roadmap_v1_2_to_v1_7.py
```

注意：大 JSONL 构建和验证不要并行跑，必须先 build 完成再 validate。

## 禁止事项

- 不接 EcoCheck runtime。
- 不改 EcoCheck 小程序。
- 不生成正式 `permit_type`。
- 不生成正式检查模板。
- 不自动扣分。
- 不伪造 `human_review_label`、`human_reviewer`、`reviewed_at`。
- 不把 `DIVISION_CONTEXT` 当作适用证据。
- 不把旧 `12个优先行业规则库_v1.1接入版` 当作当前入口。
