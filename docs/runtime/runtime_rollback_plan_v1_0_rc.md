# runtime_rollback_plan_v1_0_rc

final_state: `NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY`

本计划只描述未来接入时的回滚要求。

- 导入前保存当前 runtime snapshot、schema version、manifest hash。
- 每次导入必须生成 rollback_manifest_id。
- 回滚必须能恢复上一版本候选映射、RAG索引和小程序展示配置。
- 回滚演练通过前，不得进行任何 runtime import。
