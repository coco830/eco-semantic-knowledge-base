# 行业专项检查包治理沉淀 v1.0

final_state: `SPECIALIZED_INSPECTION_ITEMS_GOVERNANCE_APPROVED`
runtime_status: `APPROVED_BASELINE_GOVERNANCE`
applies_to: `v1.0-approved-specialized-inspection-items`
source_artifacts:
- `data/approved_baseline/approved_specialized_inspection_items_v1_0.csv`
- `manifests/approved_specialized_inspection_items_manifest_v1_0.json`
- `reports/ETO_SPECIALIZED_INSPECTION_ITEMS_REVIEW_PLAIN_v1_0.md`

本文件沉淀 2026-06-04 行业专项检查包从知识库进入 EcoCheck 运行时前置产物的治理口径。它不新增 EcoCheck 评分、权限、schema 或治理内核，只定义专项排查项在知识库侧如何建模、审批、导入、验证和后续扩展。

## 1. 本体边界

专项排查本体按“产污场景 / 工序 / 风险单元”组织，不按行业代码硬挂。

行业代码、排污许可类型和经营范围只能作为召回入口。是否挂出专项项，必须回到企业现场事实：环评、批复、排污许可、台账、设备清单、原辅料、现场工序和风险单元是否指向对应专项包。

落地规则：

- 喷涂、印刷、酸洗、电镀、锅炉、污水站、实验室废液、医疗废水、医废、辐射等专项包，均以现场存在对应工序、设施或风险单元为触发依据。
- 仅凭 GB/T 4754 行业小类或许可名录大类上下文，不得直接推导企业正式专项画像。
- 企业画像最终仍由 ESO/ETO 结合材料和现场证据确认。

## 2. 三层结构

专项包分三层治理：

1. 包级触发项：判断企业是否存在对应工序、设施或风险单元。
2. 细化检查项：在包级触发后，呈现更具体的排查节点、判定口径和现场核查内容。
3. 现场证据点：约束 ESO 应拍什么、查什么、留什么材料。

2026-06-04 ETO 追加的 10 条细化排查项属于第二层和第三层，不另起运行时命名空间，不替代 24 个包级触发项，只作为对应专项包内的细化检查点进入 `HUMAN_APPROVED_BASELINE`。

落地规则：

- 包级项可用 `PROCESS_SPEC_*` 表达知识库来源，但导入 EcoCheck 时必须落入既有 FIRST/MONTHLY item_id 命名空间。
- 细化项应继承父包的触发语义，并补足 `threshold_text`、`source_basis`、拍照点和 ETO 口径。
- 新增细化项不能绕过父包治理，也不能创造新的评分维度或权限边界。

## 3. 触发与判定

专项触发不等于强扣分。

固定口径：

- 存在对应工序、设施、风险单元或材料证据指向：触发专项包。
- 明确不存在，且能给出反向证据：`NA`。
- 材料或现场证据不足：`NEED_CONFIRM`。
- 触发后发现明显违法违规事实：由 EcoCheck 既有检查项和扣分规则处理，本知识库不新增自动扣分。

典型边界：

- 五即一码、扫码入库、地方危废平台：地方暂未强制或企业只有纸质记录时，可降级为普通危废台账核查，不作机械强扣。
- 低 VOCs 原辅料：水性油墨或低 VOCs 原辅料仍可触发无组织管控和危废证据核查；是否豁免末端治理设施须看许可、环评和现场事实。
- 小微企业替代证据：无独立电子称重系统时，可接受现场台秤/地磅照片与纸质手工台账，首筛可判 `NEED_CONFIRM` 交 ETO 复核。
- 医疗余氯：系统提示 `3–10 mg/L`，但排污许可、环评批复、地方标准或监管要求严于该口径时按从严依据覆盖。

## 4. 审批准入

ETO 审批是专项项进入运行时 import 的准入门，不是文案备注。

必须同时满足：

- `approval_status = HUMAN_APPROVED_BASELINE`
- `runtime_status = APPROVED_BASELINE`
- 行级 `source_basis` 非空
- manifest 锁定 CSV `sha256`
- ETO 审核稿保留批复结论和修改意见
- import 脚本校验 manifest hash 与行级审批状态

不得进入 import 的情况：

- `DRAFT_NOT_FOR_RUNTIME`
- `NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY`
- `disabled`
- 缺少 ETO 批复
- 缺少来源依据
- CSV 与 manifest hash 不一致

候选来源边界必须继续保留：候选知识库可以作为起草和审阅底稿，但不得因 validator 通过而自动获得运行时授权。

## 5. 维度映射

知识库可以使用业务友好的复合维度名，EcoCheck 编译器只能接收白名单维度名。二者之间必须显式映射，并由契约测试兜底。

落地规则：

- KB 侧复合维度如 `solid_waste_hazardous_waste` 必须映射到 EcoCheck 编译器白名单维度，如 `hazardous_waste`。
- 新增 KB 维度前，必须同步更新 importer/generator 映射表。
- 编译后每条专项 L2 item 的 `applicability_dimension` 必须在编译器白名单内。
- 不允许出现“KB 有项、画像点亮、但执行页拉不出”的孤立专项项。

推荐测试：

- import 层拒绝未知复合维度。
- generator 层断言所有专项项有有效 `applicability_dimension`。
- compiler 层断言专项项随画像维度触发。
- 前端契约断言执行页按维度分组呈现专项项。

## 6. 运行时验收

专项包验收不能只看生成数量，必须看真实画像能否挂出。

每批新增专项包至少覆盖两类烟测：

- 典型制造/工序画像：如喷涂/涂装/涂布、印刷/粘合/覆膜、酸洗/电镀、锅炉或污水站。
- 医疗或高风险画像：如医院、医疗废水、医疗废物、辐射/放射或实验室废液。

验收必须证明：

- 模板生成数量正确且 item_id 唯一。
- 专项项没有孤立维度。
- 画像点亮后，编译器实际拉出对应专项项。
- 小程序执行页真实呈现 `thresholdText` 和可展开 `sourceBasisText`。
- 页面中文呈现，不暴露英文机器码。
- 可拍照、可引用、可追溯来源依据。

API、生成器、编译器通过不等于闭环。涉及前后端同步修改时，必须有“实际呈现相关”的契约测试、截图或 DevTools 烟测证据。

## 7. 计数守卫

专项包增长是知识库的正常行为。测试不得把总数写成不可解释的裸常量。

推荐计数模型：

- DMC/通用基线计数固定守卫，例如 FIRST 166、MONTHLY 67。
- 已审批专项项数量从 approved specialized CSV 或 generated specialized_source 动态统计。
- 总数断言表达为：`当前总数 = DMC 基线 + 已审批专项项`。

这样可以同时守住两件事：

- DMC 基线没有意外漂移。
- ETO 批准的专项新增不会把发布门禁炸红。

如果下次新增 10 条专项项，测试应显示“专项项有意新增 10 条”，而不是只报 “FIRST 总数不等于旧常量”。

## 8. 辐射专项覆盖层

辐射/放射专项应作为高风险覆盖层，不和通用医疗、危废、废水场景互相吞并。

治理口径：

- 医院画像可能同时触发医疗废水、医疗废物、消毒余氯和医疗放射诊疗，但这些不是同一类检查。
- 普通工业企业也可能因工业探伤、含源仪表、放射源库或放射性废物暂存触发辐射专项。
- 辐射专项只在环评、许可、设备台账、放射源台账、现场标识或监管材料指向时触发。
- 不启用全行业默认辐射检查，不进入一般企业默认首检。
- 医疗放射、工业探伤、含源仪表、放射性废物、放射性处置场等后续可拆为子包，但必须保持高风险覆盖层边界。

辐射专项和医疗专项可以同单呈现，但必须按维度分组，避免把辐射证照、源库台账、剂量监测、放射性废物暂存等证据要求混入普通医疗废水或医疗废物项。

## 后续扩展清单

新增专项包或细化项时，按以下清单过门：

1. ETO 审核稿有大白话说明、适用边界、拍照点、判定口径。
2. CSV 行级状态为 `HUMAN_APPROVED_BASELINE` 和 `APPROVED_BASELINE`。
3. `source_basis` 和 `threshold_text` 非空。
4. manifest 记录 CSV sha256 和条目计数。
5. importer 校验审批状态、hash、命名空间和维度映射。
6. generator 保留 `threshold_text`、`source_basis`、`specialized_source`。
7. compiler 保持确定性、幂等、item_id 唯一、不孤立。
8. 前端执行页实际呈现中文阈值和依据。
9. 契约测试覆盖至少两个真实画像。
10. 不改评分、扣分、权限、schema 或治理内核。
