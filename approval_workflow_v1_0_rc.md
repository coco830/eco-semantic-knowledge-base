# approval_workflow_v1_0_rc

final_state: `NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY`

审批流设计：

1. ESO/ETO 完成人工审阅并形成 human_review overlay。
2. Domain owner 关闭 P0/P1 open questions 或接受风险。
3. Product 审批展示范围和报告口径。
4. TechLead 完成 second_approval，审批数据契约、回滚方案和契约测试。
5. 安全/审计确认日志字段。
6. 另起实现任务，严禁本设计包直接接入 runtime。
本设计包不执行导入、不修改 EcoCheck 小程序、不生成正式模板、不自动扣分。
