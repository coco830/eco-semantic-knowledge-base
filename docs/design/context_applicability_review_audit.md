# 条目-小类适用关系审阅表

## 定位

本表用于对 34 条 audit samples 的许可名录条目-四位小类适用关系做人工审阅降噪。它不是正式许可结论，不接运行时。

## 标签

- `APPLIES`：文本明确命中小类/中类/名称，且无兜底/重点名单/通用工序等降级条件；仍需按条件和现场事实确认。
- `MAY_APPLY`：存在直接复核来源或文本弱命中，需人工确认。
- `NOT_APPLY`：当前条目明显不适用于该小类或该条件单元格为 `/`。
- `NEED_EIA_OR_PERMIT_CONFIRM`：仅大类上下文候选，必须回到环评/许可/现场确认。

## 门禁

- `DIVISION_CONTEXT` 默认不得直接升级为 `APPLIES`。
- `target_management_condition` 不得当成企业正式许可类型。
- 人工复核应填写 `human_review_label`、`human_reviewer`、`human_review_notes`。

校验状态：`PASS`
