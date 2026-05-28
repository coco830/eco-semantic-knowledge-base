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

## 核心数据入口

- `all_context_applicability_review_v0_4_1.csv/json`: 22815 条候选适用关系，全部候选化。
- `all_permit_condition_backfill_v0_4_1.csv/json`: 336 条许可名录条件治理，覆盖 1-112 条 x 三类管理条件。
- `scenario_templates.json`: 产污场景模板，是知识本体核心，不是行业硬编码。
- `scenario_to_score13_mapping_v0_3.csv`: 场景到 EcoCheck S01-S13 的候选语义映射。
- `inspection_candidate_recommendations_v0_3.csv`: 候选排查建议，不能直接生成正式检查模板。
- `open_questions_v0_4_1.csv`: 高风险开放问题。
- `open_questions_review_guide_v1_0_rc.md`: 把开放问题拆成“问谁、问什么、查什么、怎么关闭”。
- `risk_acceptance_queue_v0_4_1.csv`: 运行时阻断风险队列。

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
