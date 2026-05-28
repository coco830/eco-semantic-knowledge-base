# human_review_backfill_plan_v0_7

final_state: `NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY`

本计划只设计回灌闭环，不覆盖 v0.4.1 源表。

## 回灌原则

- 已填写的人工审阅表作为 overlay 输入，保留 source_row_id 与 candidate_relation_id。
- 回灌脚本应生成 review_delta_report、failure_list、review_version_manifest。
- 原始候选表保持不可变，审阅结论以新版本 overlay 叠加。

## 可进入正式化候选

- `CONFIRM_APPLIES`
- `CONFIRM_MAY_APPLY`
- `CONFIRM_NOT_APPLY`

这些标签只代表进入正式化候选池，仍需二次审批。

## 仍 BLOCKS_RUNTIME

- `NEED_EIA_CONFIRM`
- `NEED_PERMIT_CONFIRM`
- `NEED_SITE_CONFIRM`
- `REJECT_CANDIDATE`
- `MERGE_DUPLICATE`
- `NEED_RULE_FIX`

## 签字留痕

必须保留 human_reviewer、human_reviewer_role、reviewed_at、review_basis、evidence_refs、decision_confidence。任何运行时接入、正式模板生成、自动扣分或报告口径升级均需二次审批。
