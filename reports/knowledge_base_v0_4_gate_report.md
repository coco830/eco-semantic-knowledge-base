# knowledge_base_v0_4 门禁报告

- final_state: `NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY`
- validation_status: `PASS`
- context_relation_count: 22815
- industry_count: 1382
- entry_count: 111
- gate_status_counts: `{"APPLIES": 202, "MAY_APPLY": 1774, "NEED_EIA_OR_PERMIT_CONFIRM": 19895, "NOT_APPLY": 944}`
- pure_DIVISION_CONTEXT_APPLIES: 0
- NOT_APPLY_missing_blocking_flags: 0
- negative_semantics_positivized: 0

## entry 108 承接策略

第108条是“除1-107外的其他行业，涉及通用工序”的兜底交叉引用条目；v0.4不直接展开为条目-小类适用关系，避免被误读为独立行业覆盖。其治理口径由109-112通用工序候选关系承接，并在正式化前作为开放问题确认。

## 运行时边界

- 未接 EcoCheck 小程序运行时。
- 未生成正式 permit_type。
- 未生成正式检查模板。
- 未自动扣分。
- 未伪造 human_review_label / human_reviewer。
