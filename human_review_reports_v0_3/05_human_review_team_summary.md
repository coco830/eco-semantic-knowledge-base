# v0.3 人工审阅 Agent Team 总结报告

生成时间：2026-05-28

审阅对象：

- `all_context_applicability_review_v0_3.csv`
- `context_applicability_review_audit_samples.csv`
- `all_permit_condition_backfill_v0_3.csv`
- `open_questions_v0_3.csv`

本次审阅只读源文件，未回填 `human_review_label`，未修改运行时边界。

## 总体结论

v0.3 可以作为 `NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY` 候选知识库治理闭环包保留。四份文件结构基本完整，核心边界守住：没有接 EcoCheck 小程序运行时，没有生成正式 `permit_type`，没有生成正式检查模板，没有自动扣分。

当前不能视为“人工审阅完成”。主表 `all_context_applicability_review_v0_3.csv` 的 22815 行和样本表 408 行中，`human_review_label / human_reviewer / human_review_notes` 全部为空。它们是待人工审阅队列，不是已审结论。

未发现 P0 级数据结构阻断。P1 主要集中在：纯 `DIVISION_CONTEXT -> APPLIES`、entry 108 与 109-112 通用工序承接关系、否定语义归一化、部分 `NOT_APPLY` 缺少明确 blocking flag、开放问题清单字段不够可执行。

## 已通过的硬边界

- 许可条件表：336 行，1-112 连续，每条均有 KEY / SIMPLIFIED / REGISTRATION。
- 主适用关系表：22815 行，覆盖 1382 个四位小类。
- 候选关系 ID 无重复。
- `permit_type` 全部为 `NEED_CONFIRM`。
- 主表和许可条件表 `runtime_status` 全部为 `DRAFT_NOT_FOR_RUNTIME`。
- 候选排查项 22 行，`photo_points` 与 `evidence_chain` 均不缺，`runtime_status=CANDIDATE_ONLY`。
- 失败清单为空。

## P1 重点问题

1. 19 条纯 `DIVISION_CONTEXT -> APPLIES`

这些行没有 `DIRECT_CODE_MATCH`，主要依赖 `manual_seed` 或上下文召回。建议优先人工确认是否降为 `MAY_APPLY` 或 `NEED_EIA_OR_PERMIT_CONFIRM`。

代表样本：

- `1331` 食用植物油加工 / entry 11
- `2211` 木竹浆制造 / entry 36
- `2671` 炸药及火工产品制造 / entry 51
- `2710` 化学药品原料药制造 / entry 53
- `3011` 水泥制造 / entry 63
- `4620` 污水处理及其再生利用 / entry 99

2. entry 108 没有在主适用关系表直接展开

entry 108 是“除 1-107 外的其他行业，涉及通用工序……”兜底条。主表没有 entry 108 关系，但 109-112 已按通用工序全行业展开。建议形成书面口径：entry 108 是否只作为 109-112 的兜底引用，是否需要保留显式记录。

3. 许可条件表中否定语义存在正向化风险

7 行“除纳入重点排污单位名录……”在 `normalized_condition` 和确认问题中可能被误读成“纳入重点排污单位名录”。正式化前必须补 `polarity` 或 `operator=not_present/excluded`。

4. 109-112 通用工序 `gb_code_fragments` 为空

候选阶段可接受，因为它们不是普通 GB/T 四位行业代码。正式化前需要稳定伪编码或 schema 级空值豁免。

5. 100 条 `NOT_APPLY` 无 slash/无 blocking flag

这些多为 `forced_denoise`。建议补充明确排除依据或阻断 flag，避免人工审阅时不知道为什么排除。

6. open questions 不足以支撑正式化审批

`open_questions_v0_3.csv` 有 13 行，但 `OQ-001` 至 `OQ-007` 的 `question` 为空，且缺少 owner、priority、close criteria。建议补强为可执行审阅任务表。

## 人工审阅优先队列

第一批先审：

- 19 条纯 `DIVISION_CONTEXT -> APPLIES`
- entry 108 与 109-112 承接策略
- 许可条件表中 7 条“除纳入重点排污单位名录”否定语义
- 样本表第 63 条在 `3011 / 3012 / 3021` 上的 APPLIES 偏宽问题
- `7721-103-KEY`，作为“类别覆盖但业务条件不默认适用”的标杆样本

第二批再审：

- 100 条 `forced_denoise` 但 `blocking_flags=[]` 的 NOT_APPLY 行
- 22 条非 `/` 但 `normalized_condition=[]` 的许可条件行
- MAY_APPLY 高值行业：`2311 / 2312 / 2319`
- NEED_EIA 高值行业：`3012-3056` 非金属矿物制品、建材、玻璃相关行业

第三批用于固化口径：

- `4620-99`：污水处理条目按处理对象和日处理能力确认
- `2211-36/37/38`：纸浆 221 与造纸 222、纸制品 223 不互相继承
- `2530-42/43/44`：核燃料加工不继承 251/252/254
- `109-112`：锅炉、工业炉窑、表面处理、水处理作为通用工序触发，而非行业天然适用

## 建议下一步

1. 先修 `open_questions_v0_3.csv`

补齐问题正文、owner_role、priority、affected_artifacts、close_criteria。尤其要把“22815 行 human_review_label 全空”和“13 维映射提升审批”单列为阻断问题。

2. 再启动人工试审

先用样本表统一标签口径，再回到主表。人工只填写 `human_review_label / human_reviewer / human_review_notes`，不要改 `gate_status`。

3. 建立审阅标签规则

建议人工标签至少包括：

- `ACCEPT_GATE_STATUS`
- `DOWNGRADE_TO_NEED_CONFIRM`
- `DOWNGRADE_TO_MAY_APPLY`
- `CONFIRM_NOT_APPLY`
- `NEEDS_MORE_EVIDENCE`
- `QUESTION_TO_DOMAIN_OWNER`

4. 暂不进入运行时接入

当前适合进入 RAG/图谱候选入库设计和人工审阅流程设计。EcoCheck 小程序运行时接入必须等开放问题关闭、人工审阅有签字、模板/扣分/报告口径有独立审批后再做。

## 报告文件

- `00_coordinator_crosscheck.md`
- `01_all_context_applicability_review_report.md`
- `02_audit_samples_review_report.md`
- `03_permit_condition_backfill_review_report.md`
- `04_open_questions_review_report.md`

