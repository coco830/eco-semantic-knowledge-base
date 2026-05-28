# 候选知识库覆盖报告

## 当前定位

本报告汇总 v0.1 候选知识库扩展进展。所有 Batch 规则均为候选召回，不是正式运行时规则。

## 批次覆盖

- Batch1：73 条；`CANDIDATE_ONLY=True`；`NEED_CONFIRM=True`；悬空模板引用 `0`
- Batch2：90 条；`CANDIDATE_ONLY=True`；`NEED_CONFIRM=True`；悬空模板引用 `0`
- Batch3：91 条；`CANDIDATE_ONLY=True`；`NEED_CONFIRM=True`；悬空模板引用 `0`
- 合计候选规则：254 条

## v0.2 全量候选底座

- Batch4：114 条；`CANDIDATE_ONLY=True`；`NEED_CONFIRM=True`
- Batch5：101 条；`CANDIDATE_ONLY=True`；`NEED_CONFIRM=True`
- Batch6：256 条；`CANDIDATE_ONLY=True`；`NEED_CONFIRM=True`
- Batch7：62 条；`CANDIDATE_ONLY=True`；`NEED_CONFIRM=True`
- Batch8：211 条；`CANDIDATE_ONLY=True`；`NEED_CONFIRM=True`
- Batch9：258 条；`CANDIDATE_ONLY=True`；`NEED_CONFIRM=True`
- Batch10：131 条；`CANDIDATE_ONLY=True`；`NEED_CONFIRM=True`
- `all_industry_scenario_candidates_v0_2.csv/json`：1382 条，覆盖 GB/T 4754 四位小类 1382/1382。
- `all_industry_scenario_candidates_v0_2_gate_report.json/md`：独立门禁 PASS，缺失 0、额外 0、重复 0、悬空场景 0、permit/runtime 违规 0、服务业过重 BLOCK 0。
- v0.2 合并时排除了历史 Batch2 中 23 大类跨批重复的 5 条，保留 Batch1 的 23 大类候选作为主记录。

## 高优先许可条件回填

- 覆盖大类：`13/22/25/26/27/28/29/30/44/46/77/84`
- `high_priority_permit_condition_backfill_v0_2.csv/json`：201 条高优先四位小类 overlay。
- `high_priority_permit_condition_backfill_detail_v0_2.csv`：3036 行“行业小类 × 名录条目 × 三类管理条件”明细。
- `high_priority_permit_condition_backfill_audit_samples.csv`：34 条抽检样本。
- `high_priority_permit_condition_backfill_validation.json`：校验 PASS。
- 回填层状态固定为 `DRAFT_CONDITION_BACKFILL_NEED_CONFIRM` / `DRAFT_NOT_FOR_RUNTIME`，不得把 `target_management_condition` 当成企业正式许可类型。

## 条目-小类适用关系降噪

- `context_applicability_review_audit_samples.csv`：408 行审阅明细，覆盖 35 个样本小类，包含强制目标 `4620/7721/2211/2530`。
- 标签分布：`APPLIES=49`、`MAY_APPLY=18`、`NEED_EIA_OR_PERMIT_CONFIRM=165`、`NOT_APPLY=176`。
- `context_applicability_review_validation.json`：校验 PASS，`DIVISION_CONTEXT` 无证据直接升级为 `APPLIES` 的数量为 0。
- 该表是人工审阅降噪表，不是正式许可结论；`human_review_label` 等字段留给 ESO/ETO 后续填写。

## 许可名录审计源

- 表格级抽取条目：112
- 编号范围：1-112
- 缺号：[]
- 重号：[]
- 验证状态：`PASS`
- 运行时状态：`NOT_FOR_RUNTIME_RAW_AUDIT_ONLY`

## 硬边界

- 不改 EcoCheck 小程序。
- 不生成正式检查模板。
- 不从候选规则推断正式 `permit_type`。
- 不新增场景模板；扩展批次只复用 `scenario_templates.json` 里的 `SCN_*`。
- 排污许可名录表格级 raw 条件必须二次规则化和人工抽检后，才能进入正式规则。
