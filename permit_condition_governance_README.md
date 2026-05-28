# 排污许可条件治理台账

本批文件从 `permit_condition_normalization_draft.csv` 派生，用于把二次规则化结果拆成两类可审计台账。

## 文件

- `permit_industry_code_reference_review.csv/json`：只收 `industry_code_reference_candidate`，用于复核名录条件中的行业代码引用、例外和范围。
- `permit_threshold_predicate_governance.csv/json`：只收 `threshold` / `threshold_range`，用于治理阈值指标、单位、上下界和证据口径。
- `permit_parallel_material_threshold_inheritance_review.csv/json`：只收同句并列物料阈值继承草案，必须人工确认。
- `permit_condition_governance_validation.json`：生成与计数校验。

## 边界

- 所有行均为 `DRAFT_NOT_FOR_RUNTIME`。
- 这些文件不生成正式 `permit_type`，不接入 EcoCheck 小程序，不生成正式检查模板。
- `review_status` / `governance_status` 是人工复核路由，不是法规结论。
