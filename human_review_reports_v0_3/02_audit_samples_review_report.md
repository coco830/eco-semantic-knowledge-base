# 02 audit samples review report

生成时间：2026-05-28  
审阅对象：`context_applicability_review_audit_samples.csv`  
审阅边界：只读源 CSV/JSON；本报告不填写 `human_review_label`，只给推荐审阅口径和人工确认问题。  
运行时边界：样本表 408 行均为 `runtime_status=DRAFT_NOT_FOR_RUNTIME`，不得接入 EcoCheck 运行时。

## 结论

本轮样本表整体符合“候选治理底稿”边界：`human_review_label`、`human_review_notes` 均为空，`runtime_status` 全部为 `DRAFT_NOT_FOR_RUNTIME`；`raw_condition=/` 的 76 行全部正确落到 `NOT_APPLY`，且带 `catalog_cell_slash_not_applicable`。

四个强制重点小类的主口径基本一致：

- `4620 污水处理及其再生利用`：第 98 条不含 4620，建议维持 `NOT_APPLY`；第 99 条明确覆盖 462，建议维持条目-小类层面的 `APPLIES`，但企业级许可类型必须按工业废水、城乡污水和日处理能力人工确认。
- `7721 水污染治理`：第 103 条行业类别覆盖 772，但条件指向危废/一般工业固废贮存、利用、处理、处置；建议维持 `NEED_EIA_OR_PERMIT_CONFIRM`，不能默认 `APPLIES`。
- `2211 木竹浆制造`：第 36 条纸浆制造 221 覆盖 2211，建议 KEY 行维持 `APPLIES`；第 37、38 条分别为造纸 222、纸制品 223，建议维持 `NOT_APPLY`，避免从 22 大类继承。
- `2530 核燃料加工`：第 42-44 条分别指向 251、252、254，不覆盖 2530；建议维持全量 `NOT_APPLY`，但需人工确认是否存在本样本未覆盖的核燃料加工专项监管路径。

主要风险不在这四个强制码，而在“条目大类/中类覆盖”被少量升级为 `APPLIES` 时，`raw_condition` 可能实际限定相邻小类或特定工艺。第 63 条的 `3011/3012/3021` 是优先复核点。

## 样本统计

### 文件与字段

- 总行数：408
- 样本小类数：35
- `catalog_entry_no` 存在，`entry_no` 不存在。
- `division_context_gate_status` 存在，`gate_status` 不存在。
- `division_context_gate_reason` 存在，`gate_reason` 不存在。
- `division_context_blocking_flags` 存在，`blocking_flags` 不存在。
- `human_review_label`：408 行为空。
- `human_review_notes`：408 行为空。
- `runtime_status`：408 行全部 `DRAFT_NOT_FOR_RUNTIME`。

### 门禁标签分布

| gate status | 行数 | 审阅含义 |
|---|---:|---|
| `NOT_APPLY` | 176 | 明确不适用，或该条件单元格为 `/` |
| `NEED_EIA_OR_PERMIT_CONFIRM` | 165 | 只有行业上下文或企业事实依赖，需环评/许可/现场确认 |
| `APPLIES` | 49 | 条目/小类文本有明确覆盖证据，但仍不是企业最终许可类型 |
| `MAY_APPLY` | 18 | 有弱命中或互斥条件，需人工确认后再判断 |

### 35 个样本小类覆盖

| industry_code | industry_name | 行数 | catalog_entry_no | gate 摘要 |
|---|---:|---:|---|---|
| 1311 | 稻谷加工 | 24 | 9-16 | NOT_APPLY 6, APPLIES 1, NEED 17 |
| 1312 | 小麦加工 | 24 | 9-16 | NOT_APPLY 6, APPLIES 1, NEED 17 |
| 1331 | 食用植物油加工 | 24 | 9-16 | NOT_APPLY 22, APPLIES 2 |
| 2211 | 木竹浆制造 | 9 | 36-38 | APPLIES 1, NOT_APPLY 8 |
| 2221 | 机制纸及纸板制造 | 9 | 36-38 | NEED 3, NOT_APPLY 3, APPLIES 3 |
| 2222 | 手工纸制造 | 9 | 36-38 | NEED 3, NOT_APPLY 3, APPLIES 3 |
| 2511 | 原油加工及石油制品制造 | 9 | 42-44 | MAY 1, APPLIES 1, NOT_APPLY 2, NEED 5 |
| 2519 | 其他原油制造 | 9 | 42-44 | MAY 1, APPLIES 1, NOT_APPLY 2, NEED 5 |
| 2530 | 核燃料加工 | 9 | 42-44 | NOT_APPLY 9 |
| 2611 | 无机酸制造 | 24 | 45-52 | MAY 3, NEED 19, NOT_APPLY 2 |
| 2612 | 无机碱制造 | 24 | 45-52 | MAY 3, NEED 19, NOT_APPLY 2 |
| 2671 | 炸药及火工产品制造 | 24 | 45-52 | NOT_APPLY 21, APPLIES 3 |
| 2710 | 化学药品原料药制造 | 21 | 53-59 | APPLIES 1, NOT_APPLY 20 |
| 2720 | 化学药品制剂制造 | 21 | 53-59 | NEED 11, NOT_APPLY 8, APPLIES 2 |
| 2750 | 兽用药品制造 | 21 | 53-59 | NEED 11, NOT_APPLY 8, APPLIES 2 |
| 2811 | 化纤浆粕制造 | 3 | 60 | MAY 1, APPLIES 1, NOT_APPLY 1 |
| 2812 | 人造纤维（纤维素纤维）制造 | 3 | 60 | MAY 1, APPLIES 1, NOT_APPLY 1 |
| 2911 | 轮胎制造 | 6 | 61-62 | MAY 3, NEED 3 |
| 2912 | 橡胶板、管、带制造 | 6 | 61-62 | MAY 3, NEED 3 |
| 3011 | 水泥制造 | 24 | 63-70 | APPLIES 3, NOT_APPLY 21 |
| 3012 | 石灰和石膏制造 | 24 | 63-70 | APPLIES 2, MAY 1, NEED 21 |
| 3021 | 水泥制品制造 | 24 | 63-70 | APPLIES 2, MAY 1, NEED 21 |
| 4411 | 火力发电 | 6 | 95-96 | APPLIES 2, NOT_APPLY 1, NEED 3 |
| 4412 | 热电联产 | 6 | 95-96 | APPLIES 2, NOT_APPLY 1, NEED 3 |
| 4413 | 水力发电 | 6 | 95-96 | NOT_APPLY 6 |
| 4610 | 自来水生产和供应 | 6 | 98-99 | APPLIES 3, NOT_APPLY 3 |
| 4620 | 污水处理及其再生利用 | 6 | 98-99 | NOT_APPLY 3, APPLIES 3 |
| 4630 | 海水淡化处理 | 6 | 98-99 | APPLIES 3, NOT_APPLY 3 |
| 7711 | 自然生态系统保护管理 | 3 | 103 | NOT_APPLY 3 |
| 7712 | 自然遗迹保护管理 | 3 | 103 | NOT_APPLY 3 |
| 7713 | 野生动物保护 | 3 | 103 | NOT_APPLY 3 |
| 7721 | 水污染治理 | 3 | 103 | NEED 1, NOT_APPLY 2 |
| 8411 | 综合医院 | 3 | 107 | APPLIES 3 |
| 8412 | 中医医院 | 3 | 107 | APPLIES 3 |
| 8421 | 社区卫生服务中心（站） | 3 | 107 | NOT_APPLY 3 |

## 强制样本逐项评估

### 4620 污水处理及其再生利用，第 98-99 条

| entry | condition | raw_condition 摘要 | 当前 gate | 推荐审阅口径 | 人工确认问题 |
|---|---|---|---|---|---|
| 98 | KEY | 涉及通用工序重点管理的 | NOT_APPLY | 维持 `NOT_APPLY` | 条目 98 指向 461、463、469，不含 4620；不要因同属 46 大类继承。 |
| 98 | REGISTRATION | 其他 | NOT_APPLY | 维持 `NOT_APPLY` | 同上。 |
| 98 | SIMPLIFIED | 涉及通用工序简化管理的 | NOT_APPLY | 维持 `NOT_APPLY` | 同上。 |
| 99 | KEY | 工业废水集中处理场所，日处理能力 2 万吨及以上的城乡污水集中处理场所 | APPLIES | 条目-小类层面可维持 `APPLIES` | 企业是否为工业废水集中处理场所，或城乡污水集中处理且日处理能力达到 2 万吨及以上。 |
| 99 | REGISTRATION | 日处理能力 500 吨以下的城乡污水集中处理场所 | APPLIES | 条目-小类层面可维持 `APPLIES` | 企业是否为城乡污水集中处理，且日处理能力低于 500 吨。 |
| 99 | SIMPLIFIED | 日处理能力 500 吨及以上 2 万吨以下的城乡污水集中处理场所 | APPLIES | 条目-小类层面可维持 `APPLIES` | 企业是否为城乡污水集中处理，且日处理能力处于 500 吨至 2 万吨区间。 |

### 7721 水污染治理，第 103 条

| entry | condition | raw_condition 摘要 | 当前 gate | 推荐审阅口径 | 人工确认问题 |
|---|---|---|---|---|---|
| 103 | KEY | 专业从事危险废物贮存、利用、处理、处置；专业从事一般工业固体废物贮存、处置 | NEED_EIA_OR_PERMIT_CONFIRM | 维持 `NEED_EIA_OR_PERMIT_CONFIRM` | 7721 是水污染治理，不能因 772 环境治理业整体覆盖就默认适用固废/危废条件；需确认企业是否实际从事危废或一般工业固废业务。 |
| 103 | REGISTRATION | / | NOT_APPLY | 维持 `NOT_APPLY` | 单元格为 `/`。 |
| 103 | SIMPLIFIED | / | NOT_APPLY | 维持 `NOT_APPLY` | 单元格为 `/`。 |

### 2211 木竹浆制造，第 36-38 条

| entry | condition | raw_condition 摘要 | 当前 gate | 推荐审阅口径 | 人工确认问题 |
|---|---|---|---|---|---|
| 36 | KEY | 全部 | APPLIES | 维持 `APPLIES` | 条目 36 为纸浆制造 221，覆盖 2211；企业仍需核对实际工艺和许可材料。 |
| 36 | REGISTRATION | / | NOT_APPLY | 维持 `NOT_APPLY` | 单元格为 `/`。 |
| 36 | SIMPLIFIED | / | NOT_APPLY | 维持 `NOT_APPLY` | 单元格为 `/`。 |
| 37 | KEY | 机制纸及纸板制造 2221、手工纸制造 2222 | NOT_APPLY | 维持 `NOT_APPLY` | 2211 不应继承造纸 222。 |
| 37 | REGISTRATION | 除简化管理外的加工纸制造 2223 | NOT_APPLY | 维持 `NOT_APPLY` | 2211 不应继承 2223。 |
| 37 | SIMPLIFIED | 有工业废水和废气排放的加工纸制造 2223 | NOT_APPLY | 维持 `NOT_APPLY` | 2211 不应继承 2223。 |
| 38 | KEY | / | NOT_APPLY | 维持 `NOT_APPLY` | 单元格为 `/`。 |
| 38 | REGISTRATION | 其他 | NOT_APPLY | 维持 `NOT_APPLY` | 条目 38 为纸制品制造 223，不覆盖 2211。 |
| 38 | SIMPLIFIED | 有工业废水或者废气排放的 | NOT_APPLY | 维持 `NOT_APPLY` | 条目 38 为纸制品制造 223，不覆盖 2211。 |

### 2530 核燃料加工，第 42-44 条

| entry | condition | raw_condition 摘要 | 当前 gate | 推荐审阅口径 | 人工确认问题 |
|---|---|---|---|---|---|
| 42 | KEY | 原油加工及石油制品制造 2511，其他原油制造 2519 | NOT_APPLY | 维持 `NOT_APPLY` | 2530 不应继承精炼石油产品制造 251。 |
| 42 | REGISTRATION | 单纯混合或者分装的 | NOT_APPLY | 维持 `NOT_APPLY` | 2530 不应继承 251。 |
| 42 | SIMPLIFIED | / | NOT_APPLY | 维持 `NOT_APPLY` | 单元格为 `/`。 |
| 43 | KEY | 炼焦 2521，煤制合成气 2522，煤制液体燃料 2523 | NOT_APPLY | 维持 `NOT_APPLY` | 2530 不应继承煤炭加工 252。 |
| 43 | REGISTRATION | 煤制品制造 2524，其他煤炭加工 2529 | NOT_APPLY | 维持 `NOT_APPLY` | 2530 不应继承 252。 |
| 43 | SIMPLIFIED | / | NOT_APPLY | 维持 `NOT_APPLY` | 单元格为 `/`。 |
| 44 | KEY | 涉及通用工序重点管理的 | NOT_APPLY | 维持 `NOT_APPLY` | 条目 44 为生物质燃料加工 254，不覆盖 2530。 |
| 44 | REGISTRATION | 其他 | NOT_APPLY | 维持 `NOT_APPLY` | 2530 不应继承 254。 |
| 44 | SIMPLIFIED | 涉及通用工序简化管理的 | NOT_APPLY | 维持 `NOT_APPLY` | 2530 不应继承 254。 |

## 标签口径建议

- `APPLIES`：只能表示“条目-小类关系文本明确覆盖，且该 target condition 是该条目的一个候选管理条件”。它不能表示企业最终适用该许可类型，更不能生成正式 `permit_type`。
- `MAY_APPLY`：用于文本有小类/中类命中，但 `raw_condition` 带“其他”“除重点/简化外”“通用工序”“重点排污单位名单”等互斥或外部依赖条件。此类不得直接升级为 `APPLIES`。
- `NEED_EIA_OR_PERMIT_CONFIRM`：用于只有大类/中类上下文、业务范围不稳定、需环评/批复/排污许可/登记回执/现场工序确认的关系。`7721-103-KEY` 应作为此口径样例。
- `NOT_APPLY`：用于 `raw_condition=/`，或条目类别明确指向相邻小类/中类，不覆盖当前小类。`4620-98`、`2211-37/38`、`2530-42/43/44` 应作为此口径样例。
- 建议人工审阅时先填写“推荐口径是否接受”和“证据来源”，再填写最终 `human_review_label`；不要由脚本自动回填。

## 发现问题（P0/P1/P2）

### P0

未发现 P0。当前样本表没有源数据被写回、没有 `human_review_label` 被预填、没有运行时启用迹象。

### P1

1. 第 63 条存在“宽行业类别导致 APPLIES 偏宽”的高风险样本。
   - `3011 水泥制造 - entry 63 - REGISTRATION` 当前为 `APPLIES`，但 `raw_condition` 明确列出 `水泥制品制造3021、砼结构构件制造3022、石棉水泥制品制造3023、轻质建筑材料制造3024、其他水泥类似制品制造3029`，不直接覆盖 3011。
   - `3012 石灰和石膏制造 - entry 63 - KEY` 当前为 `APPLIES`，但 `raw_condition` 为 `水泥（熟料）制造`，不应仅凭 `industry_category_text` 中的 301 大类直接升级。
   - `3021 水泥制品制造 - entry 63 - KEY/SIMPLIFIED` 当前为 `APPLIES`，但 KEY 指向水泥熟料，SIMPLIFIED 指向水泥粉磨站、石灰和石膏制造 3012；建议至少降为人工确认口径。

2. 现有说明文件 `context_applicability_review_audit.md` 写“34 条 audit samples”，但本 CSV 和校验文件显示为 408 行、35 个样本小类。建议后续统一为 35 个样本小类，避免人工审阅漏掉一个小类。

3. 字段命名存在接口口径不一致风险。审阅要求里提到 `entry_no/gate_status/gate_reason/blocking_flags`，CSV 实际字段为 `catalog_entry_no/division_context_gate_status/division_context_gate_reason/division_context_blocking_flags`。建议人工审阅模板和脚本统一字段别名。

### P2

1. `FORCED_SAMPLE_REVIEW_MATCH` 的 `APPLIES` 行需要保留人工证据注释，特别是 raw condition 只是“其他”或“涉及通用工序”的行，避免后续被误读为无条件适用。
2. `DIVISION_ONLY_NO_DIRECT_EVIDENCE` 共 164 行，均为 `NEED_EIA_OR_PERMIT_CONFIRM`，口径方向正确；建议人工审阅时优先挑出带 `requires_general_process_cross_reference_109_112`、`requires_external_key_pollutant_unit_list` 的行，补外部证据路径。
3. `human_review_notes` 全空符合“不替 Candy 填标签”的要求，但后续正式人工审阅时建议强制备注证据来源，否则标签难以追溯。

## 建议先审的样本清单

第一优先级：

| industry_code | industry_name | entry | condition | 当前 gate | 建议动作 |
|---|---|---:|---|---|---|
| 3011 | 水泥制造 | 63 | REGISTRATION | APPLIES | 核对是否应降为 `NOT_APPLY` 或 `MAY_APPLY`，因为 raw condition 指向 3021-3029。 |
| 3012 | 石灰和石膏制造 | 63 | KEY | APPLIES | 核对是否应降为 `MAY_APPLY` 或 `NOT_APPLY`，因为 raw condition 是水泥熟料制造。 |
| 3021 | 水泥制品制造 | 63 | KEY | APPLIES | 核对是否应降为 `NOT_APPLY`，因为 raw condition 是水泥熟料制造。 |
| 3021 | 水泥制品制造 | 63 | SIMPLIFIED | APPLIES | 核对是否应降为 `NOT_APPLY` 或 `MAY_APPLY`，因为 raw condition 指向水泥粉磨站、3012。 |
| 7721 | 水污染治理 | 103 | KEY | NEED_EIA_OR_PERMIT_CONFIRM | 作为“类别覆盖但业务条件不默认适用”的标杆样本确认。 |

第二优先级：

| industry_code | industry_name | entry | condition | 当前 gate | 建议动作 |
|---|---|---:|---|---|---|
| 4620 | 污水处理及其再生利用 | 99 | KEY/SIMPLIFIED/REGISTRATION | APPLIES | 确认 APPLIES 只表示条目-小类覆盖，企业最终类型按处理对象和日处理能力确认。 |
| 2211 | 木竹浆制造 | 36-38 | 全部 | APPLIES/NOT_APPLY | 作为“相邻 221/222/223 不继承”的标杆样本确认。 |
| 2530 | 核燃料加工 | 42-44 | 全部 | NOT_APPLY | 确认 2530 不继承 251/252/254，并登记是否存在样本外专项监管问题。 |
| 2911/2912 | 轮胎制造、橡胶板管带制造 | 61 | KEY | MAY_APPLY | 需外部“重点排污单位名录”证据，不能直接 APPLIES。 |
| 2611/2612 | 无机酸/无机碱制造 | 45 | KEY/SIMPLIFIED/REGISTRATION | MAY_APPLY | 需核对“单纯混合或者分装”“其他/除外”的互斥条件。 |

## 审阅证据摘录

- CSV 读取结果：408 行，35 个 `industry_code`。
- 门禁计数：`NOT_APPLY=176`，`NEED_EIA_OR_PERMIT_CONFIRM=165`，`APPLIES=49`，`MAY_APPLY=18`。
- 一致性检查：
  - `raw_condition=/` 但非 `NOT_APPLY`：0 行。
  - `/` 单元格缺少 `catalog_cell_slash_not_applicable`：0 行。
  - `APPLIES` 同时带 blocking flag：0 行。
  - 非 `/` 的 `NOT_APPLY` 缺少 blocking flag：0 行。
  - `runtime_status` 非 `DRAFT_NOT_FOR_RUNTIME`：0 行。
  - `human_review_label` 已填写：0 行。

