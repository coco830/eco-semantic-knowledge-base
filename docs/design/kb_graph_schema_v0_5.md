# kb_graph_schema_v0_5

final_state: `NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY`

v0.5 是 RAG/环保语义图谱候选入库设计包，不接 EcoCheck runtime。

## Node Types

- Industry: GB/T 4754 四位小类候选召回入口。
- PermitCatalogEntry: 排污许可名录1-112原始条目。
- PermitCondition: KEY/SIMPLIFIED/REGISTRATION三类条件单元。
- ApplicabilityRelation: 行业小类与许可条件的候选适用关系。
- ScenarioTemplate: 产污场景本体。
- Score13Dimension: EcoCheck S01-S13报告维度。
- InspectionCandidate: 候选现场排查项，不是正式模板。
- OpenQuestion: 运行时/正式化前必须关闭或接受的问题。
- RiskAcceptance: open questions的风险承接队列。

## Required Common Fields

`source_basis`, `confidence`, `gate_status`, `runtime_status`, `final_state`, `open_question_refs`, `risk_refs`, `candidate_only`。

## Edge Types

`HAS_CONDITION`, `CANDIDATE_APPLICABILITY`, `HAS_APPLICABILITY_RELATION`, `RELATED_TO_SCENARIO`, `MAPS_TO_SCORE13`, `HAS_INSPECTION_CANDIDATE`, `RISK_LINKED_TO_OPEN_QUESTION`。
