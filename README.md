# 环保语义知识库

本仓库用于沉淀环保管家行业的环保语义知识库。当前主线已经在候选治理底座之上生成 `v1.0-approved-baseline-knowledge`，用于 EcoCheck 后续读取 `show_if`、检查项、问题/整改/报告链路。另有 `v8.5-pollutant-domain-approved-baseline`，用于承接 `semantic-profile-lab` 人工 L5 审批通过的水、气、声、渣、辐射/放射污染物域标准源基线。

主入口：

- `docs/index/PROJECT_INDEX_v1_0_rc.md`: 封版索引、关键文件、验证命令和禁止事项。
- `docs/index/HANDOFF_v1_0_rc.md`: 后续人工审阅、RAG demo、图谱 demo、运行时接入前置条件。
- `docs/design/open_questions_review_guide_v1_0_rc.md`: 19 个开放问题的分派审阅指南。
- `reports/eto_eso_open_question_decisions_v1_0_rc.md`: ETO/ESO 初步审阅决策记录，仍保持运行时阻断。
- `docs/design/process_evidence_schema_v1_1.md`: 工序/工艺证据层候选 schema，用于把环评和现场事实转成企业画像 overlay。
- `validate_runtime_preintegration_contracts_v1_0_rc.py`: 运行时接入前拒绝型契约测试，防止候选包误投产。
- `reports/FINAL_COMPLETION_REPORT_v1_1.md`: v1.1 工序/工艺证据层候选包完成报告。
- `reports/FINAL_COMPLETION_REPORT_v1_2_to_v1_7.md`: v1.2-v1.7 候选治理链完成报告，覆盖环评/许可抽取、激活规则、open questions、审阅切片、RAG eval 和接入差距。
- `reports/FINAL_COMPLETION_REPORT_v1_8_noise_radiation_extension.md`: v1.8 噪声与辐射/放射知识域增量完成报告。
- `reports/FINAL_APPROVED_BASELINE_KNOWLEDGE_v1_0.md`: 已人工确认知识库导出的 approved baseline 包说明。
- `manifests/approved_baseline_knowledge_manifest_v1_0.json`: approved baseline manifest，可作为 EcoCheck 导入前的知识层入口。
- `data/approved_baseline/approved_show_if_rules_v1_0.csv`: EcoCheck 模板项可见性 `show_if` 规则导出。
- `reports/FINAL_POLLUTANT_DOMAIN_APPROVED_BASELINE_v8_5.md`: V8.5 污染物域 approved baseline 回灌说明，保留 209 条已审条目与 6 条 P1 排除决断。
- `manifests/pollutant_domain_approved_baseline_manifest_v8_5.json`: V8.5 污染物域 approved baseline manifest，锁定 CSV/package/report 哈希。
- `data/approved_baseline/pollutant_domain_v8_5/pollutant_domain_approved_baseline_v8_5.csv`: V8.5 污染物域 209 条 approved baseline 条目。
- `reports/FINAL_COMPLETION_REPORT_v1_0_rc.md`: v1.0-rc 完成报告。

目录分层：

- `data/`: 候选规则、许可条件、图谱/RAG、人审、运行时设计数据和 approved baseline 导出。
- `docs/`: 索引、设计说明、运行时边界文档。
- `reports/`: 各阶段报告、验证报告、审计报告。
- `manifests/`: 知识库和导入候选 manifest。
- `reference_sources/`: 原始法规/国标参考文件。
- `artifact_manifest.json`: 文件名到分类路径的映射，脚本通过 `kb_paths.py` 解析产物位置。

候选层历史边界：

- `final_state=NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY`
- `runtime_integration=disabled`

approved baseline 边界：

- `final_state=APPROVED_BASELINE_KNOWLEDGE`
- `runtime_status=APPROVED_BASELINE`
- `runtime_integration=approved_baseline_export_ready`
- 可驱动 EcoCheck `show_if`、模板项显示、问题/整改/报告链路。
- 数值扣分仍由 EcoCheck 现有 score item / deduct-rule 映射决定。
- 企业正式 `permit_type` 仍必须结合企业许可证、环评、批复、台账和现场事实确认，不能仅凭行业候选推断。

V8.5 pollutant-domain approved baseline 边界：

- `final_state=APPROVED_POLLUTANT_DOMAIN_BASELINE_KNOWLEDGE`
- `runtime_status=APPROVED_BASELINE`
- `runtime_integration=approved_baseline_export_ready`
- 每行保留来源候选边界：`source_final_state=NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY`、`source_runtime_integration=disabled`
- `ConfirmedDataset` 仍为 `NOT_CREATED`，正式排污权/系数计算仍为 `NOT_AUTHORIZED`
- 辐射/放射不得启用全行业默认：`radiation_all_industry_default` 仍在 blocked actions 中
