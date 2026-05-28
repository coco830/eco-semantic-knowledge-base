# 排污许可条件治理台账摘要

本摘要对应以下派生产物：

- `permit_industry_code_reference_review.csv/json`
- `permit_threshold_predicate_governance.csv/json`
- `permit_parallel_material_threshold_inheritance_review.csv/json`
- `permit_condition_governance_validation.json`

所有产物均为 `DRAFT_NOT_FOR_RUNTIME`，不得生成正式 `permit_type`，不得接入 EcoCheck 小程序或正式检查模板。

## 行业代码引用复核清单

- 共 193 条候选引用。
- 181 条匹配 GB/T 4754 四位小类。
- 12 条匹配 GB/T 4754 三位中类。
- 0 条未匹配 GB/T 4754 底表。

复核目的不是确认企业最终行业，而是确认名录条件文本中的数字是否表示行业代码范围、例外项或条件性行业引用。

## 阈值谓词治理表

- 共 66 条阈值谓词。
- 54 条为单阈值草案，需回看名录原文确认来源。
- 8 条为范围阈值草案，需确认上下界开闭口。
- 4 条为同句并列物料阈值继承草案，需确认是否继承左侧指标词。

已明确沉淀的代表性指标包括：

- `annual_material_use`
- `annual_output`
- `annual_processing_capacity`
- `bed_count`
- `boiler_capacity_single_or_total`
- `boiler_capacity_single_and_total`
- `business_area`
- `daily_sugar_processing_capacity`
- `daily_transfer_capacity`
- `daily_treatment_capacity`
- `single_berth_tonnage`
- `storage_total_capacity`

## 当前剩余人工确认点

`threshold_metric` 已清零。原 4 条已进入 `permit_parallel_material_threshold_inheritance_review.csv/json`，作为“同句并列物料阈值继承规则”专项：

- 第 16 条简化管理：`0.1万吨及以上`，草案继承 `年加工能力`
- 第 16 条简化管理：`4.5万吨及以上`，草案继承 `年加工能力`
- 第 32 条简化管理：`溶剂型胶粘剂或者3吨及以上`，草案继承 `年使用`
- 第 39 条简化管理：`涂料或者10吨及以上`，草案继承 `年使用`

这些继承结果不直接正式化，必须人工确认“指标词是否适用于后续并列物料/处理剂/稀释剂”。
