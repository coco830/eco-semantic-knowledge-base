# open_questions_v0_3 审阅报告

## 结论

当前 `open_questions_v0_3.csv` 可以证明 v0.3 包仍处于 `DRAFT_NOT_FOR_RUNTIME` / `NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY` 边界内，但还不能作为“正式化前开放问题清单”的唯一审批底稿。

质量判断：方向正确、阻断边界基本在场，但字段完整性不足。13 条问题全部标记为 `BLOCKS_RUNTIME`、`OPEN`、`DRAFT_NOT_FOR_RUNTIME`，与 `knowledge_base_manifest_v0_3.json` 和 `FINAL_COMPLETION_REPORT.md` 的运行时禁入边界一致；但是前 7 条问题正文为空，CSV 不含 `owner` / `owner_role` / `priority` / `object_id` / `impact` / `recommended_action` 等字段，导致人工分派、闭环验收和正式化审批无法直接执行。

审阅结论：维持“不得接 EcoCheck 运行时、不得生成企业正式 permit_type、不得生成正式检查模板、不得自动扣分”的硬边界。v0.3 校验 `PASS` 只能说明候选包结构和边界字段通过，不能视为运行时接入批准。

## 现有问题统计

| 项目 | 审阅结果 |
| --- | --- |
| `open_questions_v0_3.csv` 行数 | 13 |
| 字段 | `question_id`, `topic`, `question`, `blocking_level`, `status`, `source_basis`, `runtime_status` |
| 空 `question` | 7 / 13，集中在 `OQ-001` 至 `OQ-007` |
| `blocking_level` | 13 / 13 为 `BLOCKS_RUNTIME` |
| `status` | 13 / 13 为 `OPEN` |
| `runtime_status` | 13 / 13 为 `DRAFT_NOT_FOR_RUNTIME` |
| owner / owner_role | 缺失字段 |
| priority | 缺失字段；仅能从 `BLOCKS_RUNTIME` 推断为运行时阻断 |
| v0.3 校验报告 | `validation_status=PASS`，`failure_count=0` |
| 上下文适用关系 | 22,815 行，`human_review_label` / `human_reviewer` / `human_review_notes` 全部为空 |
| 上下文门禁分布 | `APPLIES=224`, `MAY_APPLY=1756`, `NEED_EIA_OR_PERMIT_CONFIRM=19894`, `NOT_APPLY=941` |
| 第 108 条 | gate report 覆盖 111 个条目，未直接展开第 108 条；已由 `V03_ENTRY_108_CONTEXT_001` 记录 |
| 13 维映射 | 11 行，全为 `CANDIDATE_ONLY`，但开放问题清单未单列“映射提升/报告维度变更”审批问题 |

已覆盖的关键边界：

- entry 108 通用工序交叉引用：已覆盖。
- `DIVISION_CONTEXT` 不得自动升级：部分覆盖，已有人工审阅后才可升级的表述，但建议补强为显式禁止自动升级到 `APPLIES`。
- 许可类型不得自动生成：已覆盖，`permit_type=NEED_CONFIRM` 与 manifest 一致。
- 运行时接入禁止：已覆盖。
- 109-112 通用工序需现场事实确认：已覆盖。

覆盖不足或表达不够可执行的边界：

- `OQ-001` 至 `OQ-007` 在 v0.3 CSV/MD 中只剩标题和阻断等级，问题正文丢失。
- 候选章节不得等同现行模板：v0.3 里只通过 `OQ-007` 空问题和 `V03_ECOCHECK_RUNTIME_001` 间接表达，缺少可执行问题正文。
- 行业代码与现场事实冲突：旧版 `open_questions.csv` 有具体代码冲突和代表性小类范围问题，v0.3 问题正文为空，现清单无法支撑正式审阅。
- 人工审阅字段为空：数据事实存在，但 open questions 未单列“22,815 行 human review 全空如何闭环”的问题。
- 13 维映射提升问题：`scenario_to_score13_mapping_v0_3.csv` 有候选映射和改进建议，但 open questions 未设置审批问题。

## 缺口/新增建议（P0/P1/P2）

### P0：正式化前必须补充

1. 恢复或重写 `OQ-001` 至 `OQ-007` 的问题正文。
   - 证据：v0.3 CSV 中 7 条 `question` 为空；旧版 `open_questions.csv` 仍保留 1512/1513、1521、2211、2231、1371、3311、候选章节等具体问题。
   - 建议：将旧版的 `object_type`、`object_id`、`issue`、`impact`、`owner_role`、`recommended_action` 恢复到 v0.3 结构，或在 v0.3 中拆成等价字段。

2. 增加人工审阅字段全空的阻断问题。
   - 建议新增：`V03_HUMAN_REVIEW_EMPTY_001`。
   - 问题：`all_context_applicability_review_v0_3.csv` 的 22,815 行 `human_review_label`、`human_reviewer`、`human_review_notes` 全为空；正式化前必须定义标签枚举、抽样/全量策略、责任人和签字闭环。

3. 增加 13 维映射提升审批问题。
   - 建议新增：`V03_SCORE13_PROMOTION_001`。
   - 问题：11 个场景已映射到 13 维评分/报告章节并提出二级语义改进，但全部仍为 `CANDIDATE_ONLY`；不得自动改动现行评分、报告章节、扣分口径或统计口径。

4. 为所有问题增加 owner 和优先级字段。
   - 建议字段：`priority`, `owner_role`, `decision_owner`, `review_status`, `due_stage`, `close_criteria`。
   - 原因：当前只有 `OPEN`，无法区分“待 ESO 事实确认”“待 ETO 技术口径”“待 Product 模板审批”“待 runtime owner 放行”。

5. 将运行时接入禁入从“说明”升级为审批清单。
   - 建议新增：`V03_RUNTIME_APPROVAL_GATE_001`。
   - 要求：只有 `final_state` 从 `NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY` 经人工审批变更，且模板、扣分、权限、数据迁移、回滚、灰度方案全部通过后，才允许设计运行时接入。

### P1：建议补强

1. 补强 `DIVISION_CONTEXT` 问题措辞。
   - 当前写法是“需要人工审阅后才能升级”，建议明确“不得自动升级为 `APPLIES`；`APPLIES` 必须有代码、名称、名录条件或现场事实证据”。
   - 同时要求审阅 224 条 `APPLIES` 的证据字段，避免把候选召回信号误当适用结论。

2. 补强 entry 108 与 109-112 的关系口径。
   - 当前已有问题，但建议增加关闭条件：确认第 108 条是否只作为兜底交叉引用，是否允许通过 109-112 通用工序承载，是否需要独立条目-小类关系记录。

3. 补强许可类型不得自动生成。
   - 当前 `V03_PERMIT_TYPE_001` 覆盖了 `target_management_condition` 不是正式 `permit_type`，建议增加关闭条件：企业画像必须由环评、批复、排污许可、登记回执、台账和现场事实共同确认。

4. 补强“候选章节不得等同现行模板”。
   - 建议把 `candidate_section`、`candidate_subsection`、`default_severity=NEED_CONFIRM`、`default_deduct` 全空等事实写入问题。
   - 关闭条件应包括 Product/ETO 明确哪些候选章节可转正式模板，哪些只能留在知识库建议。

5. 补强行业代码与现场事实冲突。
   - 建议将“行业代码只是召回入口，场景和现场事实才是适用依据”设为独立问题，不只散落在场景治理说明中。

### P2：结构化改进

1. 为 `source_basis` 增加机器可追溯字段。
   - 建议拆分为 `source_file`, `source_row_or_entry`, `source_quote_or_summary`，避免证据只能人工阅读。

2. 为问题增加 `affected_artifacts`。
   - 示例：`all_context_applicability_review_v0_3.csv`、`scenario_to_score13_mapping_v0_3.csv`、`inspection_candidate_recommendations_v0_3.csv`。

3. 为 `status` 增加状态机。
   - 建议枚举：`OPEN`, `IN_REVIEW`, `NEEDS_MORE_EVIDENCE`, `APPROVED_FOR_CANDIDATE_ONLY`, `APPROVED_FOR_RUNTIME_DESIGN`, `CLOSED_REJECTED`, `CLOSED_SUPERSEDED`。

4. 为开放问题生成审阅视图。
   - 建议按 owner_role 输出 Product、ESO、ETO、Runtime Owner、Data Governance 五类视图，避免一张 CSV 同时承担事实确认、产品模板审批和运行时发布审批。

## 建议下一步工作流

1. 先修复开放问题清单结构。
   - 不改变候选知识库结论，只补足 v0.3 open questions 的问题正文、owner、优先级、影响范围、关闭条件。
   - 将旧版 `open_questions.csv` 的 `OQ-001` 至 `OQ-007` 信息迁回 v0.3，避免 v0.3 把历史关键问题变成空壳。

2. 建立人工审阅流程。
   - Data Governance 先确认字段枚举和状态机。
   - ETO 审阅 `DIVISION_CONTEXT`、entry 108/109-112、许可名录条目与小类关系。
   - ESO 根据企业环评、批复、排污许可、登记回执、台账、监测报告和现场事实填充 `human_review_label`。
   - Product/ETO 审批候选章节是否可转正式模板。
   - 每条问题必须有 `close_criteria` 和审阅人，不允许仅用 `PASS` 或空备注关闭。

3. 运行时接入前审批清单。
   - `knowledge_base_manifest_v0_3.json` 的 `runtime_integration` 从 `disabled` 变更前，必须有人类审批记录。
   - 所有 `BLOCKS_RUNTIME` 问题关闭或明确转为非阻断。
   - 22,815 条上下文适用关系的人工审阅策略完成，并保留审阅标签、审阅人、审阅说明。
   - `permit_type` 仍不得由候选包自动生成；企业正式许可类型只能来自正式证照、登记回执、监管口径和现场事实确认。
   - `scenario_to_score13_mapping_v0_3.csv` 的 13 维映射不得直接改动评分、扣分、报告章节或统计口径；如需提升，必须有独立 PRD/BDD/审批。
   - `inspection_candidate_recommendations_v0_3.csv` 的候选章节不得直接生成正式检查模板；`default_deduct` 为空和 `default_severity=NEED_CONFIRM` 应保持为禁入信号。
   - entry 108 与 109-112 通用工序关系口径必须形成书面决定。
   - CloudRun/小程序接入设计必须包含权限、灰度、回滚、审计日志、数据迁移和禁用开关。

4. 验收口径。
   - v0.3 仍可作为候选治理闭环包保留。
   - 运行时正式化的最小前置条件不是“校验 PASS”，而是“开放问题有 owner、有关闭条件、有人工证据、有审批记录，并且 manifest 边界被显式批准变更”。
