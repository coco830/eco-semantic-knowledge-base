# 行业产污场景候选知识库 v0.2 治理包

## 定位

本目录当前产物是候选知识库治理包：包含 v0.1 场景模板样板、v0.2 全量行业候选底座，以及 v0.2 高优先行业许可条件 overlay。它不是运行时规则库。

`knowledge_base_v0_1_manifest.json` 文件名为历史入口名，当前内容版本以其中的 `knowledge_base_version = v0.2-candidate-base+v0.2-high-priority-overlay` 为准。

行业代码和排污许可类型只作为默认召回入口；最终企业画像必须由 ESO/ETO 根据环评、批复、排污许可证、台账和现场事实确认。

## 核心文件

- `scenario_templates.json`：可复用产污场景模板。
- `industry_scenario_rules.json`：31 条样板行业规则到场景模板的候选召回。
- `industry_catalog_base.csv`：GB/T 4754-2017 全量层级底座。
- `all_industry_scenario_candidates_v0_2.csv/json`：覆盖 1382 个四位小类的全量候选召回底座。
- `high_priority_permit_condition_backfill_v0_2.csv/json`：高优先行业许可名录条件回填 overlay。
- `context_applicability_review_audit_samples.csv`：条目-小类适用关系人工审阅降噪表。
- `permit_management_catalog_draft.csv`：2019 排污许可名录原文草表，需人工拆分三类管理条件。
- `permit_management_catalog_table_cells.csv`：2019 排污许可名录表格级审计中间表，已验证 1-112 连续时可作为 raw audit source。
- `permit_management_catalog_table_cells_validation.json`：表格级抽取验证结果。
- `scenario_to_score13_mapping.csv`：场景到 EcoCheck S01-S13 的语义映射。
- `inspection_candidate_recommendations_v0_1.csv`：候选检查项、证据和拍照点，不直接接模板。
- `open_questions.csv` / `open_questions.md`：阻塞运行时或需治理确认的问题。
- `runtime_integration_boundary.md`：运行时禁用边界。

## 当前硬边界

- 不自动扣分。
- 不自动创建正式检查项或报告章节。
- 不把 `UNKNOWN` 当成 `YES` 或 `NO`。
- 不直接改 EcoCheck S01-S13 报告口径。
- 不把候选章节 `S18/S19/S20/S21/S22/S23/S24/M18/M19` 当作现行模板章节。

## 已知限制

`permit_management_catalog_draft.csv` 由 PDF 文本保守抽取生成，只用于定位原文和字段设计草稿。`permit_management_catalog_table_cells.csv` 是更可靠的表格级 raw audit source，已完成 1-112 连续抽取、条件规则化草案和高优先 overlay，但仍不能直接生成正式 `permit_type`。

## 下一步

下一阶段重点不是继续扩量，而是对 `DIVISION_CONTEXT` 条目-小类候选做人工审阅降噪，形成可解释、可追溯、可人工确认的适用关系。
