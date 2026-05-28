# security_audit_log_design_v1_0_rc

final_state: `NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY`

审计日志设计要求所有未来导入、拒绝、回滚和RAG服务事件可追溯。

必填审计字段：
- `event_id`
- `actor_id`
- `actor_role`
- `timestamp`
- `source_manifest_id`
- `runtime_candidate_id`
- `before_hash`
- `after_hash`
- `reason`
- `approval_id`
- `rollback_manifest_id`
- `request_id`
