# 排污许可名录条件二次规则化草案

本产物把 `permit_management_catalog_table_cells.csv` 的三类管理条件从 raw text 转成 `normalized_predicates` 草案。它是治理中间层，不是运行时规则库。

## 设计原则

- `raw_condition` 永远保留原文。
- 能稳定识别的阈值、区间、通用工序、重点排污单位、星号、其他兜底、常见工序会进入 `normalized_predicates` 或 `audit_flags`。
- 无法稳定识别的内容标 `need_human_normalization`，不做猜测式解释。
- 数字 token 统一进入 `numeric_condition_token`，并拆成 `threshold_or_capacity_number`、`capacity_or_threshold_number`、`industry_code_reference_candidate`、`unclassified_numeric_token`，避免把规模阈值误当行业代码。
- `condition_code_fragments` 只保留在条目级原始审计信息中，不再直接灌入每个管理条件的谓词。

## 禁止用途

- 不得直接生成正式 `permit_type`。
- 不得接入 EcoCheck 小程序或正式检查模板。
- 带 `requires_general_process_cross_reference_109_112`、`requires_external_key_pollutant_unit_list`、`else_condition_requires_peer_condition_exclusion` 的条件必须人工复核。
