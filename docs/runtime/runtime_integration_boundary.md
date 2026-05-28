# Runtime Integration Boundary

本批产物定位为 `knowledge_base_version = v0.2-candidate-base+v0.2-high-priority-overlay`。`knowledge_base_v0_1_manifest.json` 文件名为历史入口名；本批产物不直接接入小程序或 EcoCheck 运行时。

## 可以使用

- 作为图谱/RAG 的样板语料和字段设计参考。
- 作为 ESO/ETO 人工确认问题和现场拍照提示的候选来源。
- 作为后续行业批量扩展、去重和质量抽检的底座。

## 不可以使用

- 不得把 `industry_scenario_rules.json` 直接写入企业最终画像。
- 不得把 `inspection_item_recommendations.csv` 中的 `KNOWLEDGE_CANDIDATE_SECTION` 直接生成检查模板。
- 优先把 `inspection_candidate_recommendations_v0_1.csv` 当作 v0.1 候选检查项视图；其中 `candidate_*`、`activation_condition`、`runtime_status=CANDIDATE_ONLY` 都是防误接语义。
- 不得因行业代码和许可类型命中，就跳过环评、批复、排污许可、台账和现场事实确认。

## 候选章节口径

`S18/S19/S20/S21/S22/S23/S24/M18/M19` 等章节为知识库候选章节。它们表达的是未来可能增强的场景子章，不代表当前 EcoCheck 模板已经存在这些章节。
