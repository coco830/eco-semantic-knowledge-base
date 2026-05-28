# human_review_guidance_v0_7

final_state: `NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY`

v0.7 是人工审阅工作台数据包，不接 EcoCheck runtime。

## 可填写字段

- `human_review_label`
- `human_reviewer`
- `human_reviewer_role`
- `reviewed_at`
- `human_review_notes`
- `review_basis`
- `evidence_refs`
- `decision_confidence`

## 不可修改字段

除上述字段外，所有 source/gate/condition/scenario/open question/risk 字段均为只读证据字段，不得在工作表中直接改写。

## 审阅规则

- `DIVISION_CONTEXT` 只能作为召回线索，不能作为适用证据。
- `photo_points` / `evidence_chain` 是一等字段，不能合并进备注后丢失。
- 人工审阅不等于运行时批准；即使填写 `CONFIRM_*`，仍不得自动生成正式 permit_type、正式检查模板或自动扣分。
- 需要改规则时填写 `NEED_RULE_FIX`，不要直接覆盖 v0.4.1 源表。
