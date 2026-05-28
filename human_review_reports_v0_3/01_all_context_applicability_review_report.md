# 01 全量行业-排污许可适用关系主表人工审阅报告

生成时间：2026-05-28  
审阅对象：`all_context_applicability_review_v0_3.csv`  
审阅范围：全量 22815 行，只读源 CSV/JSON；本报告不回填 `human_review_label`。

## 结论

- 主表结构完整，重点字段均存在；`industry_code` 覆盖 GB/T 四位小类 1382/1382，无缺失、无额外行业代码。
- 主表候选关系未发现重复：`candidate_relation_id`、`industry_code+entry_no+target_management_condition`、以及含 source/status/raw_condition 的复合键重复数均为 0。
- 机器校验边界保持住了：`permit_type=NEED_CONFIRM` 22815 行，`runtime_status=DRAFT_NOT_FOR_RUNTIME` 22815 行，`source_basis/confidence/confirmation_questions` 均无缺失。
- 仍不能视为人工审阅完成：`human_review_label` 和 `human_review_notes` 全部为空（22815 / 22815 行），当前状态应解释为全量待人工审阅。
- 未发现 P0 结构性阻断；发现 P1 高优先业务疑点：19 条纯 `DIVISION_CONTEXT` 被标为 `APPLIES`，entry 108 在主表缺席但 109-112 被全行业展开，100 条 `NOT_APPLY` 没有 slash/flag 依据，1 条 `NEED_EIA_OR_PERMIT_CONFIRM` 缺少阻断 flag。

## 核验方法

- 使用 Python `csv.DictReader` 全量读取 22815 行，保留 CSV 物理行号作为示例定位。
- 对照 `industry_catalog_base.csv` 中 `level=class` 的 1382 个四位小类检查行业覆盖。
- 对照 `permit_management_catalog_table_cells.csv` 的 `catalog_entry_no=1-112` 检查 entry 覆盖，并单独核查 108-112 通用/其他行业条目。
- 对 `blocking_flags`、`confirmation_questions`、`related_scenario_ids` 执行 JSON list 解析校验。
- 按 `gate_status`、`relation_source`、`target_management_condition`、`confidence`、`permit_type`、`runtime_status`、`human_review_label` 汇总分布。
- 以候选治理边界检查：`DIVISION_CONTEXT` 只能作为召回信号；`GENERAL_PROCESS_TRIGGER` 只能触发确认；`APPLIES` 需要直接代码/名称/条件证据；`NOT_APPLY` 需要 slash 或明确排除依据。

## 通过项

### 结构和覆盖

- 字段数：28；重点字段缺失：无；必查状态字段缺失：无。
- 重点字段空值：`industry_code/name/entry_no/target_management_condition/relation_source/gate_status/raw_condition/blocking_flags/source_basis/confidence/confirmation_questions/runtime_status/permit_type` 均为 0。
- 行业覆盖：1382/1382；缺失行业代码 0，额外行业代码 0。
- entry 覆盖：111/112；缺失：`108`；额外：0。
- JSON list 字段：`blocking_flags`、`confirmation_questions`、`related_scenario_ids` 均无解析错误、无非 list 值、无空值。

### 分布

`target_management_condition`：
- `KEY`: 7605
- `SIMPLIFIED`: 7605
- `REGISTRATION`: 7605

`gate_status`：
- `NEED_EIA_OR_PERMIT_CONFIRM`: 19894
- `MAY_APPLY`: 1756
- `NOT_APPLY`: 941
- `APPLIES`: 224

`relation_source`：
- `GENERAL_PROCESS_TRIGGER`: 16584
- `DIVISION_CONTEXT`: 5751
- `DIRECT_CODE_MATCH+DIVISION_CONTEXT`: 480

`confidence`：
- `LOW`: 19994
- `MEDIUM`: 1895
- `HIGH`: 926

### 证据与边界

- `APPLIES` 总数 224；其中证据字段空、证据文本空或 confidence 非 HIGH/MEDIUM 的弱证据行数为 0。
- `GENERAL_PROCESS_TRIGGER` 没有被直接升级为 `APPLIES`：0 行。
- `NEED_EIA_OR_PERMIT_CONFIRM` 总数 19894；其中 `DIRECT_CODE_MATCH` 来源 0 行，说明未把直接匹配但待确认的关系混入该状态。
- `source_basis` 缺失 0；`confirmation_questions` 空 list 0；`confidence` 非 LOW/MEDIUM/HIGH 0；`permit_type/runtime_status` 违规 0/0。
- `human_review_label` 已填写 0 行；不存在不合规标签，也不存在 notes 有值但 label 为空的情况。

## 发现问题

### P0

无 P0。未发现会导致主表不可读取、字段缺失、重复候选主键、runtime 状态越界、permit_type 越界或 JSON 解析失败的问题。

### P1

#### P1-1 纯 DIVISION_CONTEXT 被升级为 APPLIES

- 影响：19 行。记忆/本地生成口径均强调 `DIVISION_CONTEXT` 只是候选召回信号；没有 `DIRECT_CODE_MATCH` 时不应直接成为 `APPLIES`。
- 这些行多带 `evidence_field=manual_seed`，`evidence_text` 只是 entry 编号，证据不足以替代行业代码/名称/条件文本命中。

| 行标识 | relation_source | evidence_field | evidence_text | confidence |
| --- | --- | --- | --- | --- |
| L1785 `CTXV03_1331_11_SIMPLIFIED` 1331 食用植物油加工 / entry 11 / SIMPLIFIED | DIVISION_CONTEXT | manual_seed | 11 | MEDIUM |
| L1786 `CTXV03_1331_11_REGISTRATION` 1331 食用植物油加工 / entry 11 / REGISTRATION | DIVISION_CONTEXT | manual_seed | 11 | MEDIUM |
| L4601 `CTXV03_2211_36_KEY` 2211 木竹浆制造 / entry 36 / KEY | DIVISION_CONTEXT | manual_seed | 36 | MEDIUM |
| L6677 `CTXV03_2671_51_KEY` 2671 炸药及火工产品制造 / entry 51 / KEY | DIVISION_CONTEXT | manual_seed | 51 | MEDIUM |
| L6678 `CTXV03_2671_51_SIMPLIFIED` 2671 炸药及火工产品制造 / entry 51 / SIMPLIFIED | DIVISION_CONTEXT | manual_seed | 51 | MEDIUM |
| L6679 `CTXV03_2671_51_REGISTRATION` 2671 炸药及火工产品制造 / entry 51 / REGISTRATION | DIVISION_CONTEXT | manual_seed | 51 | MEDIUM |
| L6911 `CTXV03_2710_53_KEY` 2710 化学药品原料药制造 / entry 53 / KEY | DIVISION_CONTEXT | manual_seed | 53 | MEDIUM |
| L7661 `CTXV03_3011_63_KEY` 3011 水泥制造 / entry 63 / KEY | DIVISION_CONTEXT | manual_seed | 63 | MEDIUM |


#### P1-2 entry 108 缺失，但 109-112 被全行业通用工序展开

- 名录中 entry 108 存在：`五十、其他行业` / `除1-107 外的其他行业`；备注为 `references_general_process_109_112`。
- 主表 entry 108 行数：0。
- 主表 entry 109-112 均为每个小类每种管理条件全量展开：109=4146、110=4146、111=4146、112=4146；每个 entry 都是 KEY/SIMPLIFIED/REGISTRATION 各 1382 行，且全部为 `GENERAL_PROCESS_TRIGGER -> NEED_EIA_OR_PERMIT_CONFIRM`。
- 这可能是有意把 108 的“其他行业/通用工序”逻辑拆到 109-112，但主表没有 108 的显式承接行或说明字段，后续人工审阅和导入时容易误判为 entry 覆盖缺口。

#### P1-3 NOT_APPLY 中存在无 slash/无 blocking flag 的排除行

- `NOT_APPLY` 总数 941；其中 slash 或 `catalog_cell_slash_not_applicable` 依据 841 行。
- 无 slash/无 flag 依据：100 行，`gate_reason` 多为 `forced_denoise`，但 `blocking_flags=[]`，不利于审阅者判断排除依据。

| 行标识 | raw_condition | gate_reason | blocking_flags |
| --- | --- | --- | --- |
| L1780 `CTXV03_1331_9_REGISTRATION` 1331 食用植物油加工 / entry 9 / REGISTRATION | 谷物磨制131﹡ | forced_denoise | [] |
| L1782 `CTXV03_1331_10_SIMPLIFIED` 1331 食用植物油加工 / entry 10 / SIMPLIFIED | 饲料加工132（有发酵工艺的）﹡ | forced_denoise | [] |
| L1783 `CTXV03_1331_10_REGISTRATION` 1331 食用植物油加工 / entry 10 / REGISTRATION | 饲料加工132（无发酵工艺的）﹡ | forced_denoise | [] |
| L1787 `CTXV03_1331_12_KEY` 1331 食用植物油加工 / entry 12 / KEY | 日加工糖料能力1000 吨及以上的原 糖、成品糖或者精制糖生产 | forced_denoise | [] |
| L1788 `CTXV03_1331_12_SIMPLIFIED` 1331 食用植物油加工 / entry 12 / SIMPLIFIED | 其他﹡ | forced_denoise | [] |
| L1790 `CTXV03_1331_13_KEY` 1331 食用植物油加工 / entry 13 / KEY | 年屠宰生猪10 万头及以上的，年屠 宰肉牛1 万头及以上的，年屠宰肉羊 15 万头及以上的，年屠宰禽类1000 万只及以上的 | forced_denoise | [] |
| L1791 `CTXV03_1331_13_SIMPLIFIED` 1331 食用植物油加工 / entry 13 / SIMPLIFIED | 年屠宰生猪2 万头及以上10 万头以 下的，年屠宰肉牛0.2 万头及以上1 万头以下的，年屠宰肉羊2.5 万头及 以上15 万头以下的，年屠宰禽类100 万只及 | forced_denoise | [] |
| L1792 `CTXV03_1331_13_REGISTRATION` 1331 食用植物油加工 / entry 13 / REGISTRATION | 其他﹡ | forced_denoise | [] |


#### P1-4 NEED_EIA_OR_PERMIT_CONFIRM 存在 1 条无阻断 flag 的人工范围行

- `NEED_EIA_OR_PERMIT_CONFIRM` 中预期应有 `division_context_default_apply_blocked`、`requires_general_process_confirmation` 或 `requires_eia_or_permit_confirmation` 之一。
- 实测缺少上述 flag：1 行。

| 行标识 | relation_source | raw_condition | gate_reason | blocking_flags |
| --- | --- | --- | --- | --- |
| L20429 `CTXV03_7721_103_KEY` 7721 水污染治理 / entry 103 / KEY | DIVISION_CONTEXT | 专业从事危险废物贮存、利用、处理、 处置（含焚烧发电）的，专业从事一 般工业固体废物贮存、处置（含焚烧 发电）的 | forced_business_scope | [] |


### P2

#### P2-1 APPLIES 全部含 DIVISION_CONTEXT 语义，需人工审阅时区分直接证据与上下文召回

- `APPLIES` 共 224 行，其中 `DIRECT_CODE_MATCH+DIVISION_CONTEXT` 205 行，纯 `DIVISION_CONTEXT` 19 行。
- 直接证据行机器层面有 `evidence_text`，但仍只是名录文本/代码片段命中，不代表企业实际许可类型。

#### P2-2 MAY_APPLY / NEED_EIA_OR_PERMIT_CONFIRM 数量偏高行业需要作为抽检入口

- `MAY_APPLY` 每行业最大 6 行，P95=3，P99=3。最高行业：`2311 书、报刊印刷`=6, `2312 本册印制`=6, `2319 包装装潢及其他印刷`=6, `3393 锻件及粉末冶金制品制造`=5, `3394 交通及公共管理用金属标牌制造`=5, `3399 其他未列明金属制品制造`=5。
- `NEED_EIA_OR_PERMIT_CONFIRM` 每行业最大 33 行，P95=31，P99=33。最高行业集中在非金属矿物制品/建材/玻璃等：`3012 石灰和石膏制造`=33, `3021 水泥制品制造`=33, `3022 砼结构构件制造`=33, `3023 石棉水泥制品制造`=33, `3024 轻质建筑材料制造`=33, `3029 其他水泥类似制品制造`=33, `3031 粘土砖瓦及建筑砌块制造`=33, `3032 建筑用石加工`=33。
- 这类数量高不一定是错，但说明召回噪声和通用工序交叉引用较重，人工审阅应先看是否存在“大类召回过宽”。

#### P2-3 强制样本表现

| industry_code | industry_name | 行数 | gate_status 分布 | relation_source 分布 | entry 覆盖 |
| --- | --- | ---: | --- | --- | --- |
| `4620` | 污水处理及其再生利用 | 18 | {'NOT_APPLY': 3, 'APPLIES': 3, 'NEED_EIA_OR_PERMIT_CONFIRM': 12} | {'DIVISION_CONTEXT': 6, 'GENERAL_PROCESS_TRIGGER': 12} | 98, 99, 109, 110, 111, 112 |
| `7721` | 水污染治理 | 15 | {'NEED_EIA_OR_PERMIT_CONFIRM': 13, 'NOT_APPLY': 2} | {'DIVISION_CONTEXT': 3, 'GENERAL_PROCESS_TRIGGER': 12} | 103, 109, 110, 111, 112 |
| `2211` | 木竹浆制造 | 21 | {'APPLIES': 1, 'NOT_APPLY': 8, 'NEED_EIA_OR_PERMIT_CONFIRM': 12} | {'DIVISION_CONTEXT': 9, 'GENERAL_PROCESS_TRIGGER': 12} | 36, 37, 38, 109, 110, 111, 112 |
| `2530` | 核燃料加工 | 21 | {'NOT_APPLY': 9, 'NEED_EIA_OR_PERMIT_CONFIRM': 12} | {'DIVISION_CONTEXT': 9, 'GENERAL_PROCESS_TRIGGER': 12} | 42, 43, 44, 109, 110, 111, 112 |

强制样本示例：

| 行标识 | relation_source | gate_status | evidence_text | blocking_flags |
| --- | --- | --- | --- | --- |
| L14588 `CTXV03_4620_99_KEY` 4620 污水处理及其再生利用 / entry 99 / KEY | DIVISION_CONTEXT | APPLIES | 99 | [] |
| L14589 `CTXV03_4620_99_SIMPLIFIED` 4620 污水处理及其再生利用 / entry 99 / SIMPLIFIED | DIVISION_CONTEXT | APPLIES | 99 | [] |
| L14590 `CTXV03_4620_99_REGISTRATION` 4620 污水处理及其再生利用 / entry 99 / REGISTRATION | DIVISION_CONTEXT | APPLIES | 99 | [] |
| L20432 `CTXV03_7721_109_KEY` 7721 水污染治理 / entry 109 / KEY | GENERAL_PROCESS_TRIGGER | NEED_EIA_OR_PERMIT_CONFIRM |  | ["requires_general_process_confirmation"] |
| L20433 `CTXV03_7721_109_SIMPLIFIED` 7721 水污染治理 / entry 109 / SIMPLIFIED | GENERAL_PROCESS_TRIGGER | NEED_EIA_OR_PERMIT_CONFIRM |  | ["requires_general_process_confirmation"] |
| L20434 `CTXV03_7721_109_REGISTRATION` 7721 水污染治理 / entry 109 / REGISTRATION | GENERAL_PROCESS_TRIGGER | NEED_EIA_OR_PERMIT_CONFIRM |  | ["requires_general_process_confirmation"] |
| L4601 `CTXV03_2211_36_KEY` 2211 木竹浆制造 / entry 36 / KEY | DIVISION_CONTEXT | APPLIES | 36 | [] |
| L4610 `CTXV03_2211_109_KEY` 2211 木竹浆制造 / entry 109 / KEY | GENERAL_PROCESS_TRIGGER | NEED_EIA_OR_PERMIT_CONFIRM |  | ["requires_general_process_confirmation"] |
| L4611 `CTXV03_2211_109_SIMPLIFIED` 2211 木竹浆制造 / entry 109 / SIMPLIFIED | GENERAL_PROCESS_TRIGGER | NEED_EIA_OR_PERMIT_CONFIRM |  | ["requires_general_process_confirmation"] |
| L5489 `CTXV03_2530_109_KEY` 2530 核燃料加工 / entry 109 / KEY | GENERAL_PROCESS_TRIGGER | NEED_EIA_OR_PERMIT_CONFIRM |  | ["requires_general_process_confirmation"] |
| L5490 `CTXV03_2530_109_SIMPLIFIED` 2530 核燃料加工 / entry 109 / SIMPLIFIED | GENERAL_PROCESS_TRIGGER | NEED_EIA_OR_PERMIT_CONFIRM |  | ["requires_general_process_confirmation"] |
| L5491 `CTXV03_2530_109_REGISTRATION` 2530 核燃料加工 / entry 109 / REGISTRATION | GENERAL_PROCESS_TRIGGER | NEED_EIA_OR_PERMIT_CONFIRM |  | ["requires_general_process_confirmation"] |

## 建议人工审阅优先队列

1. 先审 19 条纯 `DIVISION_CONTEXT -> APPLIES`：优先确认是否应降为 `MAY_APPLY` 或 `NEED_EIA_OR_PERMIT_CONFIRM`，除非能补充直接代码/名称/条件证据。
2. 再审 entry 108 缺失策略：确认主表是否需要显式保留 108，或在报告/manifest 中声明 108 已由 109-112 通用工序承接。
3. 再审 100 条 `NOT_APPLY` 但无 slash/flag 的 `forced_denoise` 行：要求补充明确排除依据、阻断 flag 或保持待审。
4. 单独审 `7721 水污染治理` 的 entry 103 KEY 行：当前为 `NEED_EIA_OR_PERMIT_CONFIRM` 但 `blocking_flags=[]`，且属于强制高风险样本。
5. 抽检 MAY/NEED 数量异常行业：先看 `2311/2312/2319` 的 MAY 高值，再看 `3012-3056` 等 NEED 高值行业是否由通用工序和大类召回过宽造成。
6. 强制样本顺序建议：`4620`、`7721`、`2211`、`2530`。其中 `4620` 有 3 条纯 DIVISION_CONTEXT APPLIES；`7721` 无 APPLIES 但有 P1-4；`2211` 有 1 条纯 DIVISION_CONTEXT APPLIES；`2530` 目前全部为 NEED/NOT_APPLY。

## 可接受边界

- 本表可作为候选治理底稿和人工审阅队列，不可直接接入 EcoCheck 运行时。
- `human_review_label` 为空是可接受状态，含义是待人工审阅；不要由脚本或 Agent 代填。
- `permit_type=NEED_CONFIRM` 与 `runtime_status=DRAFT_NOT_FOR_RUNTIME` 是当前可接受的安全边界；不得因为机器校验 PASS 而提升为正式许可类型。
- `GENERAL_PROCESS_TRIGGER -> NEED_EIA_OR_PERMIT_CONFIRM` 的全行业展开可接受，但必须被解释为“需要确认是否存在锅炉、炉窑、表面处理、水处理等通用工序”，不是行业天然适用。
- `DIVISION_CONTEXT` 可接受为召回和审阅入口；只有存在直接代码/名称/条件证据，并经人工确认后，才可进入更强适用关系。
- `NOT_APPLY` 最好有 `/`、明确排除文本或 blocking flag；只有 `forced_denoise` 且 flags 为空的行应列入人工复核，不应作为最终排除结论。
