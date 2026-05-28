# runtime_contract_test_plan_v1_0_rc

final_state: `NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY`

契约测试计划，不执行运行时代码修改。

- Backend import contract: 拒绝缺少二次审批、缺少证据链、缺少rollback_manifest的导入。
- Mini program presentation contract: 候选知识、人工审阅状态、运行时状态必须清晰区分。
- RAG boundary contract: 回答必须携带候选边界、source chunks、review overlay status。
- Scoring contract: 本包不得生成自动扣分或正式检查模板。
- Rollback contract: 模拟导入后必须可恢复上一 manifest。
