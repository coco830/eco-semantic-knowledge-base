# human_review_decision_schema_v0_7

final_state: `NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY`

人工审阅标签只表达候选知识是否可进入下一轮正式化候选，不产生运行时效果。

## Labels

- `CONFIRM_APPLIES`: runtime_effect=`NO_RUNTIME_EFFECT_IN_V0_7`
- `CONFIRM_MAY_APPLY`: runtime_effect=`NO_RUNTIME_EFFECT_IN_V0_7`
- `CONFIRM_NOT_APPLY`: runtime_effect=`NO_RUNTIME_EFFECT_IN_V0_7`
- `NEED_EIA_CONFIRM`: runtime_effect=`NO_RUNTIME_EFFECT_IN_V0_7`
- `NEED_PERMIT_CONFIRM`: runtime_effect=`NO_RUNTIME_EFFECT_IN_V0_7`
- `NEED_SITE_CONFIRM`: runtime_effect=`NO_RUNTIME_EFFECT_IN_V0_7`
- `REJECT_CANDIDATE`: runtime_effect=`NO_RUNTIME_EFFECT_IN_V0_7`
- `MERGE_DUPLICATE`: runtime_effect=`NO_RUNTIME_EFFECT_IN_V0_7`
- `NEED_RULE_FIX`: runtime_effect=`NO_RUNTIME_EFFECT_IN_V0_7`

## Required Evidence

ACCEPT/CONFIRM 类标签必须填写 human_reviewer、human_reviewer_role、reviewed_at、human_review_notes、review_basis、evidence_refs、decision_confidence。
任何正式化、模板化、扣分、报告口径升级动作必须进入二次审批，不在 v0.7 自动生效。
