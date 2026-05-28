# knowledge_base_v0_4_1 门禁报告

- final_state: `NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY`
- validation_status: `PASS`
- catalog_entry_coverage: `1-112 continuous`
- context_relation_entry_count: 111（第108条为特殊承接项，不代表缺失）
- context_relation_count: 22815
- industry_count: 1382
- gate_status_counts: `{"APPLIES": 202, "MAY_APPLY": 1773, "NEED_EIA_OR_PERMIT_CONFIRM": 19895, "NOT_APPLY": 945}`
- pure_DIVISION_CONTEXT_APPLIES: 0
- NOT_APPLY_missing_blocking_flags: 0

## entry 108 承接策略

许可名录原始条目覆盖1-112连续；第108条是“除1-107外的其他行业，涉及通用工序”的兜底承接条，不作为独立条目-小类适用关系展开，因此适用关系表涉及111个条目不是许可名录缺失。第108条由109-112通用工序候选关系承接，正式化前必须通过开放问题确认。

## risk queue 与 open questions 关系

risk_acceptance_queue_v0_4_1.csv是open_questions的风险承接队列；只列运行时正式化或图谱/RAG入库前必须接受/关闭的阻断风险，不替代open_questions全量问题清单。

