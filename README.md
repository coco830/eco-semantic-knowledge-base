# 环保语义知识库

本仓库用于沉淀环保管家行业的候选语义知识库，当前封版状态为 `v1.0-rc design-only baseline`。

主入口：

- `PROJECT_INDEX_v1_0_rc.md`: 封版索引、关键文件、验证命令和禁止事项。
- `HANDOFF_v1_0_rc.md`: 后续人工审阅、RAG demo、图谱 demo、运行时接入前置条件。
- `FINAL_COMPLETION_REPORT_v1_0_rc.md`: v1.0-rc 完成报告。

硬边界：

- `final_state=NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY`
- `runtime_integration=disabled`
- 不接 EcoCheck runtime。
- 不生成正式 `permit_type`。
- 不生成正式检查模板。
- 不自动扣分。

