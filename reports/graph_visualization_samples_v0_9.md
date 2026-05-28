# graph_visualization_samples_v0_9

final_state: `NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY`

全局提示：以下可视化展示的是候选影响范围传播，不代表企业现场事实已确认适用，不产生运行时效果。

## 3012 登记管理确认不适用

```mermaid
flowchart LR
  A["Industry 3012 石灰和石膏制造"] --> B["Permit Condition Entry 63 REGISTRATION"]
  B --> C["Applicability CTXV04_3012_63_REGISTRATION"]
  C --> D["Review Overlay CONFIRM_NOT_APPLY"]
  C --> E["Scenario: Dust / Wastewater / Solid ledger candidates"]
  E --> F["Score13 S10/S06/S07..."]
  E --> G["Inspection Candidates FIRST/MONTHLY"]
  D --> H["Formalization candidate only, second approval required"]
  H --> I["NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"]
```

## 0111 锅炉通用工序仍需现场确认

```mermaid
flowchart LR
  A["Industry 0111 稻谷种植"] --> B["Entry 109 Boiler SIMPLIFIED"]
  B --> C["GENERAL_PROCESS_TRIGGER"]
  C --> D["Review Overlay NEED_SITE_CONFIRM"]
  D --> E["Still BLOCKS_RUNTIME"]
  C --> F["Open Questions: general process + entry108 strategy"]
  E --> G["NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"]
```

## 4620 第99条确认为候选仍需二次审批

```mermaid
flowchart LR
  A["Industry 4620 污水处理及其再生利用"] --> B["Entry 99 wastewater treatment"]
  B --> C["Applicability CTXV04_4620_99_KEY"]
  C --> D["Review Overlay CONFIRM_MAY_APPLY"]
  D --> E["Formalization candidate"]
  E --> F["Second approval required"]
  F --> G["No runtime effect"]
```

## Entry 108 承接策略

```mermaid
flowchart LR
  A["Entry 108 other industries"] --> B["Bridge / carry-forward strategy"]
  B --> C["Entry 109 Boiler"]
  B --> D["Entry 110 Industrial kiln"]
  B --> E["Entry 111 Surface treatment"]
  B --> F["Entry 112 Water treatment"]
  B --> G["Open Question V04_ENTRY_108_CONTEXT_001"]
  G --> H["Risk RISK-V041-001"]
  H --> I["Not a missing catalog entry"]
```
