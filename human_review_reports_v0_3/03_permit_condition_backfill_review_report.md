# 03 排污许可名录条件治理表审阅报告

生成时间：2026-05-28  
审阅对象：`C:\Users\candy\Desktop\国民经济行业代码 + 排污许可类型 - 默认产污场景画像的规则库\all_permit_condition_backfill_v0_3.csv`  
输出报告：`C:\Users\candy\Desktop\国民经济行业代码 + 排污许可类型 - 默认产污场景画像的规则库\human_review_reports_v0_3\03_permit_condition_backfill_review_report.md`  
源文件 SHA256：`9710c97fc3a8084d8d05bd4b41ba081853658fef2e05fb36cc0a3de05a32294a`

## 结论

本轮核对了 `all_permit_condition_backfill_v0_3.csv` 的 336 条逻辑记录。整体结论：候选治理表的结构完整，1-112 条连续，每条均有 `KEY` / `SIMPLIFIED` / `REGISTRATION` 三类条件；来源页码、来源单元格、`/` 单元格状态、候选运行态边界均通过检查。当前没有发现 P0 级问题。

但该表还不能直接进入运行时正式化。主要 P1 风险有三类：

1. `除纳入重点排污单位名录` 的 7 行在归一化 JSON 和确认问题中丢失否定/排除语义，未来如果按结构化条件自动判定，可能把“不在重点排污单位名录”误读成“在重点排污单位名录”。
2. 109-112 通用工序共 12 行 `gb_code_fragments` 为空；候选阶段可解释为通用工序非 GB/T 行业代码条目，但正式化前必须显式建模为空值豁免或通用工序编码。
3. 22 行非 `/` 条件的 `normalized_condition=[]`，均已被 `need_human_normalization` 标记，候选阶段可接受；正式化前仍会阻塞结构化判定。

## 核验方法

- 使用 Python `csv.DictReader` 按 CSV 逻辑记录读取，避免被单元格内换行误导。
- 对 `normalized_condition`、`blocking_flags`、`confirmation_questions` 逐行执行 JSON 解析。
- 按以下规则核验：`entry_no` 连续性、每条三类条件完整性、字段缺失、`source_page/source_row_index/source_cell_name` 可追溯性、`source_cell_name` 与条件类型映射、`/` 条件状态、空归一化与 blocking flags 对应关系、重点排污单位/通用工序/阈值条件的 flags 与确认问题、`permit_type` 与 `runtime_status` 候选边界。
- 未修改任何源 CSV/JSON；仅写入本报告。

## 通过项

| 项目 | 核验结果 |
|---|---:|
| 逻辑记录数 | 336 |
| `entry_no` 连续性 | 1-112 完整，无缺号、无越界 |
| 每条三类条件 | `KEY=112`、`SIMPLIFIED=112`、`REGISTRATION=112` |
| 重复 `(entry_no, target_management_condition)` | 0 |
| `source_pdf/source_page/source_row_index/source_cell_name` 缺失 | 0 |
| `source_cell_name` 与三类条件映射错误 | 0 |
| `source_page/source_row_index` 非数字 | 0 |
| JSON 解析错误 | 0 |
| `permit_type` | 336/336 为 `NEED_CONFIRM` |
| `runtime_status` | 336/336 为 `DRAFT_NOT_FOR_RUNTIME` |
| `/` 条件 | 53/53 为 `NOT_APPLICABLE_IN_CATALOG` 且含 `catalog_cell_slash_not_applicable` |
| 非 `/` 空归一化未标记 | 0 |

补充分布：

- `applies_status`：`APPLIES_IF_CONDITION_MET=187`，`ELSE_CONDITION=96`，`NOT_APPLICABLE_IN_CATALOG=53`。
- `confidence`：`HIGH=96`，`MEDIUM=168`，`LOW=72`。
- `normalized_condition`：261 行为非空 JSON list，75 行为空 list；其中 53 行为 `/`，22 行为 `need_human_normalization`。
- `blocking_flags` 计数：`catalog_cell_slash_not_applicable=53`，`requires_general_process_cross_reference_109_112=61`，`else_condition_requires_peer_condition_exclusion=96`，`asterisk_footnote_requires_industrial_building_condition=43`，`condition_contains_industry_code_candidate_review_needed=72`，`requires_external_key_pollutant_unit_list=20`，`need_human_normalization=22`。
- 阈值结构：46 行含 `threshold` 或 `threshold_range` 结构化谓词，且均有“请确认实际规模/用量/产能，并提供证据”类确认问题。另有 2 行含“规模”字样但未结构化，均已进入 `need_human_normalization`。

## 问题清单

### P0：未发现

未发现会立即破坏候选包边界或导致源数据无法追溯的 P0 问题。所有记录仍为 `NEED_CONFIRM` / `DRAFT_NOT_FOR_RUNTIME`，没有被误升为运行时可用状态。

### P1-1：`除纳入重点排污单位名录` 的否定语义丢失

影响范围：7 行。

109 SIMPLIFIED: 除纳入重点排污单位名录的，单台或 者合计出力20 吨/小时（14 兆瓦）及 以上的锅炉（不含电热锅炉）; 109 REGISTRATION: 除纳入重点排污单位名录的，单台且合 计出力20 吨/小时（14 兆瓦）以下的锅 炉（不含电热锅炉）; 110 SIMPLIFIED: 除纳入重点排污单位名录的，除以 天然气或者电为能源的加热炉、热 处理炉、干燥炉（窑）以外的其他 工业炉窑; 110 REGISTRATION: 除纳入重点排污单位名录的，以天然气 或者电为能源的加热炉、热处理炉或者 干燥炉（窑）; 111 SIMPLIFIED: 除纳入重点排污单位名录的，有电镀 工序、酸洗、抛光（电解抛光和化学 抛光）、热浸镀（溶剂法）、淬火或 者钝化等工序的、年使用10 吨及以 上有机溶剂的; 112 SIMPLIFIED: 除纳入重点排污单位名录的，日处理 能力2 万吨及以上的水处理设施; 112 REGISTRATION: 除纳入重点排污单位名录的，日处理 能力 500 吨及以上 2 万吨以下的水处 理设施

证据：这些行的 `raw_condition` 表达的是“除纳入重点排污单位名录的……”，但 `normalized_condition` 中结构化为 `dynamic_key_pollutant_unit_list` + `operator=present`，`raw_fragment` 仅保留“纳入重点排污单位名录”；`confirmation_questions` 也使用“是否被纳入重点排污单位名录？”而非“是否未被纳入/不在重点排污单位名录？”。

风险：候选阶段因 `NEED_CONFIRM` 可挡住自动决策；正式化阶段若下游直接消费结构化条件，可能把排除条件反向解释，属于运行时正式化阻塞项。

建议：为重点排污单位名录谓词增加极性字段，例如 `polarity: included/excluded` 或 `operator: not_present`；确认问题同步改为“是否未被纳入重点排污单位名录？”或拆成“是否被纳入；若是则不得进入本条件”。

### P1-2：109-112 通用工序 `gb_code_fragments` 为空

影响范围：12 行。

109-KEY(锅炉), 109-SIMPLIFIED(锅炉), 109-REGISTRATION(锅炉), 110-KEY(工业炉窑), 110-SIMPLIFIED(工业炉窑), 110-REGISTRATION(工业炉窑), 111-KEY(表面处理), 111-SIMPLIFIED(表面处理), 111-REGISTRATION(表面处理), 112-KEY(水处理), 112-SIMPLIFIED(水处理), 112-REGISTRATION(水处理)

证据：其他字段有来源页码、行号、单元格、行业文本，缺失集中在“五十一、通用工序”的锅炉、工业炉窑、表面处理、水处理。

风险：候选阶段可接受，因为通用工序不是普通 GB/T 四位行业代码；但若未来 runtime、索引或 join 逻辑假定 `gb_code_fragments` 必填，会产生匹配失败或被误当成脏数据。

建议：正式化前二选一：一是给通用工序建立稳定伪编码，如 `GENERAL_PROCESS_109`；二是在 schema 中声明 `major_category_text=五十一、通用工序` 时 `gb_code_fragments` 可空，并要求下游按 `entry_no` 或通用工序 ID 关联。

### P1-3：22 行非 `/` 条件仍为空归一化

影响范围：22 行，均已含 `need_human_normalization`。

1-KEY, 1-REGISTRATION, 2-REGISTRATION, 25-SIMPLIFIED, 36-KEY, 53-KEY, 56-SIMPLIFIED, 63-KEY, 64-REGISTRATION, 66-KEY, 66-SIMPLIFIED, 67-KEY, 67-SIMPLIFIED, 71-KEY, 72-KEY, 75-KEY, 79-SIMPLIFIED, 93-KEY, 100-SIMPLIFIED, 103-KEY, 104-KEY, 105-SIMPLIFIED

证据：这些行 `raw_condition` 不是 `/`，但 `normalized_condition=[]`。好消息是没有发现未标记的非 `/` 空归一化，且确认问题均非空。

风险：候选阶段可接受；正式化前这些行必须人工归一化或保留为明确的人工判定项，否则不能自动决策。

### P2-1：通用工序 flags 语义需要继续区分“跨表引用”和“直接工序条件”

证据：61 行明确含 `requires_general_process_cross_reference_109_112`，形如“涉及通用工序重点管理/简化管理的”，这类 flag 合理。另有若干行含锅炉、电镀、酸洗、染色、工业废水等工序关键词但无该 cross-reference flag，多数已经被直接归一化为 `process_or_flag` 或 `threshold`。

判断：这不是当前候选表错误；但正式化前建议把 flag 命名区分为 `cross_reference_general_process_109_112` 与 `direct_process_condition`，避免审阅者把所有工序关键词都误认为跨表引用。

### P2-2：阈值条件整体可用，但门禁应校验单位、上下界和排除语义

证据：46 行已有结构化阈值谓词并配有规模/用量/产能确认问题；2 行含“规模”但未结构化，分别为 `1-KEY` 与 `1-REGISTRATION`，已被 `need_human_normalization` 标记。

待关注样例：1 KEY: 设有污水排放口的规模化畜禽养殖 场、养殖小区（具体规模化标准按《畜 禽规模养殖污染防治条例》执行）; 1 REGISTRATION: 无污水排放口的规模化畜禽养殖场、养 殖小区，设有污水排放口的规模以下畜 禽养殖场、养殖小区

判断：当前 flags 合理，未见未标记的空阈值归一化；但运行时正式化前要对 `unit`、`inclusive`、`gte_and_lt` 上下界、等价值单位进行独立 validator 校验。

### P2-3：例外/排除短语还没有统一负向谓词模型

证据：除 P1 的“除纳入重点排污单位名录”外，表内还存在“除重点管理以外”“不含”“除以……以外”等短语。多数因原文保留和候选确认问题可人工判断，但结构化 JSON 未统一表达 `not/except/excluded`。

判断：候选阶段可接受；正式化前应作为统一建模问题处理，避免单点修补。

## 建议人工审阅优先条目

1. 第一优先：`109-SIMPLIFIED`、`109-REGISTRATION`、`110-SIMPLIFIED`、`110-REGISTRATION`、`111-SIMPLIFIED`、`112-SIMPLIFIED`、`112-REGISTRATION`。重点核对“除纳入重点排污单位名录”的否定语义、确认问题措辞和结构化谓词极性。
2. 第二优先：109-112 全部 12 行。决定通用工序是否使用伪编码、专用 ID，或 schema 级空值豁免。
3. 第三优先：22 行 `need_human_normalization`。这些是正式化前的人工归一化工作队列。
4. 第四优先：含“除重点管理以外”“不含”“除以……以外”的条目，尤其与阈值或工序同时出现的条目，如 16、19、20、81、96、102、107、109-112。

## 未来正式化门禁建议

- 运行态门禁：只有当 `permit_type != NEED_CONFIRM` 且 `runtime_status` 从 `DRAFT_NOT_FOR_RUNTIME` 经人工批准提升后，才允许被运行时读取。
- 结构化完整性门禁：非 `/` 条件不得存在 `normalized_condition=[]`，除非显式声明为“人工判定型条件”并有可执行确认问题。
- 极性门禁：所有 `除/不含/无/未/以外` 等否定或排除短语必须在结构化谓词中有 `polarity` 或 `operator=not_present/excluded`，并且确认问题必须与极性一致。
- 重点排污单位门禁：凡出现“纳入/除纳入重点排污单位名录”，必须引用外部重点排污单位名录证据源，并记录名单版本、查询时间、行政区和企业名称匹配证据。
- 通用工序门禁：109-112 必须有稳定关联键；行业条目引用通用工序时，必须区分“跨表引用”与“直接工序条件”。
- 阈值门禁：所有 `threshold/threshold_range` 必须校验 `metric`、`operator`、`value/lower_value/upper_value`、`unit`、`inclusive`、等价值单位，以及证据材料来源。
- 来源追溯门禁：`source_pdf/source_page/source_row_index/source_cell_name/raw_condition` 必须全部保留，且正式化后的归一化片段需要能回指原文片段。
- 候选包边界门禁：验证器通过不等于运行时批准；正式化必须另有人工审阅签字、版本冻结、差异报告和回滚策略。
