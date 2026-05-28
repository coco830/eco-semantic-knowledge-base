# runtime_promotion_gate_design_v1_0_rc

final_state: `NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY`

本文件只设计候选知识进入运行时的闸门，不执行接入。

- `GATE-001` candidate_source_freeze: 候选源数据版本冻结，且 hash/manifest 记录完整。
- `GATE-002` human_review_completion: 人工审阅签字留痕完整。
- `GATE-003` second_approval: 二次审批通过，且审批记录不可篡改。
- `GATE-004` runtime_contract_tests: 契约测试全部通过。
- `GATE-005` rollback_ready: 可回滚版本与演练记录齐全。
- `GATE-006` audit_logging_ready: 审计日志设计和测试通过。

禁止动作：
- `automatic_permit_type_generation`
- `automatic_inspection_template_generation`
- `automatic_deduct_generation`
- `runtime_import_without_second_approval`
- `score13_report_dimension_change_without_product_approval`
