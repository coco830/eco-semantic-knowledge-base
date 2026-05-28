# process_graph_rag_design_v1_1

final_state: `NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY`
runtime_integration: `disabled`

The v1.1 graph/RAG layer adds ProcessTrigger, ProcessEvidence, and EnterpriseProfileOverlay nodes. RAG answers must show source excerpt, evidence strength, candidate boundary, and site verification status. No answer may claim formal runtime approval or final enterprise permit_type.

## Example Query Paths

- Industry 3311 -> process evidence spraying -> VOCs scenario -> S10/S06/S07 -> inspection candidate.
- Industry 1512 -> fermentation/distillation evidence -> wastewater scenario -> site verification.
- Paper product 2231 -> printing/gluing evidence -> VOCs and hazardous waste scenarios.
- Medical 8411 -> medical wastewater/waste/radiation evidence -> S07/S12/S06.
- Laboratory sample -> laboratory waste liquid evidence -> NEW_SCN_LAB_WASTE_CANDIDATE.
