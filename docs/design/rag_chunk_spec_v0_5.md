# rag_chunk_spec_v0_5

final_state: `NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY`

chunk_id策略：`kbv0_5::{chunk_type}::{natural_key}::{content_sha8}`。

## Chunk Types

- source_manifest_chunk
- permit_condition_chunk
- context_relation_chunk
- scenario_template_chunk
- inspection_candidate_chunk
- score13_mapping_chunk
- open_question_chunk
- risk_acceptance_chunk
- denoise_decision_chunk

所有chunk必须显式携带候选边界字段，RAG回答不得把候选关系当成正式permit_type或正式检查模板。
