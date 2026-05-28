# runtime_contract_test_plan_v1_0_rc

final_state: `NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY`

契约测试计划，不执行运行时代码修改。

- Backend import contract: 拒绝缺少二次审批、缺少证据链、缺少rollback_manifest的导入。
- Backend rejection contract: 不得导入 `NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY` 包；任何候选包必须先被拒绝并返回可审计错误。
- Reviewer signature contract: `simulated_*` 审阅人只能作为模拟数据，不能作为真实 ETO/ESO 签名。
- Mini program presentation contract: 候选知识、人工审阅状态、运行时状态必须清晰区分。
- RAG boundary contract: 回答必须携带候选边界、source chunks、review overlay status。
- Scoring contract: 本包不得生成自动扣分或正式检查模板。
- Runtime generation rejection contract: 候选数据不能生成正式 permit_type，不能生成正式检查模板，不能自动扣分。
- Rollback contract: 模拟导入后必须可恢复上一 manifest。
