# HANDOFF_v1_0_rc

final_state: `NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY`
runtime_integration: `disabled`

## 封版结论

本知识库治理线已阶段性封版为 `v1.0-rc design-only baseline`。当前资产可用于人工审阅、RAG demo、图谱样例和未来运行时接入方案评审，但不能直接投产。

## 下一阶段建议

1. 人工审阅：从 `human_review_worksheet_v0_7.xlsx` 开始，审阅人员只填写开放字段，不修改候选源表。
2. RAG demo：使用 `rag_chunks_v0_5.jsonl`、`retrieval_eval_set_v0_6.jsonl` 和 `rag_prototype_results_v0_8.jsonl`，回答必须展示候选边界和审阅状态。
3. 图谱 demo：使用 `graph_nodes_v0_5.jsonl`、`graph_edges_v0_5.jsonl`、`review_impact_graph_edges_v0_9.jsonl` 展示行业、许可条件、场景、13维、排查项影响链。
4. EcoCheck 接入：必须另开实现任务或分支，先通过 `runtime_promotion_gate_design_v1_0_rc.md` 中全部闸门。

## 真正接入前置条件

- 人工审阅字段完整，且无伪造审阅。
- P0/P1 open questions 关闭或有签字风险接受。
- Product、ETO、TechLead 完成二次审批。
- 后端导入契约、前端呈现契约、RAG 边界契约、回滚契约全部通过。
- 导入前生成版本冻结 manifest、rollback manifest 和审计日志方案。

## 已清理的历史入口

旧 `12个优先行业规则库_v1.1接入版` 属于早期试跑的运行时接入口径，和当前候选治理边界冲突，已从当前主线移除。12个优先行业本身已经进入全量新底座，不需要保留旧接入版文件。
