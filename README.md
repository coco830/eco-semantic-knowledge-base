# 环保语义知识库

本仓库用于沉淀环保管家行业的候选语义知识库，当前封版状态为 `v1.0-rc design-only baseline`。

主入口：

- `PROJECT_INDEX_v1_0_rc.md`: 封版索引、关键文件、验证命令和禁止事项。
- `HANDOFF_v1_0_rc.md`: 后续人工审阅、RAG demo、图谱 demo、运行时接入前置条件。
- `open_questions_review_guide_v1_0_rc.md`: 19 个开放问题的分派审阅指南。
- `eto_eso_open_question_decisions_v1_0_rc.md`: ETO/ESO 初步审阅决策记录，仍保持运行时阻断。
- `process_evidence_schema_v1_1.md`: 工序/工艺证据层候选 schema，用于把环评和现场事实转成企业画像 overlay。
- `FINAL_COMPLETION_REPORT_v1_1.md`: v1.1 工序/工艺证据层候选包完成报告。
- `FINAL_COMPLETION_REPORT_v1_0_rc.md`: v1.0-rc 完成报告。

硬边界：

- `final_state=NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY`
- `runtime_integration=disabled`
- 不接 EcoCheck runtime。
- 不生成正式 `permit_type`。
- 不生成正式检查模板。
- 不自动扣分。
