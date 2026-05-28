import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FINAL_STATE = "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"
KB_VERSION = "v0.6-rag-graph-eval-candidate-layer"


def read_jsonl(path):
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path, rows):
    tmp = path.with_name(f".{path.name}.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    tmp.replace(path)


def write_json(path, data):
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def eval_item(eval_id, category, query, expected_node_ids, expected_chunk_types, expected_answer_contains, open_refs=None, risk_refs=None):
    return {
        "eval_id": eval_id,
        "eval_category": category,
        "query": query,
        "expected_node_ids": expected_node_ids,
        "expected_chunk_types": expected_chunk_types,
        "expected_answer_contains": expected_answer_contains + [FINAL_STATE],
        "must_include_boundary_notice": True,
        "must_not_claim_runtime_ready": True,
        "open_question_refs": open_refs or [],
        "risk_refs": risk_refs or [],
        "runtime_status": "DRAFT_NOT_FOR_RUNTIME",
        "final_state": FINAL_STATE,
    }


def query_sample(sample_id, category, description, start_node_ids, edge_types, expected_result_node_types, open_refs=None, risk_refs=None):
    return {
        "sample_id": sample_id,
        "query_category": category,
        "description": description,
        "start_node_ids": start_node_ids,
        "edge_types": edge_types,
        "expected_result_node_types": expected_result_node_types,
        "query_intent": "candidate_knowledge_exploration_not_runtime_decision",
        "open_question_refs": open_refs or [],
        "risk_refs": risk_refs or [],
        "runtime_status": "DRAFT_NOT_FOR_RUNTIME",
        "final_state": FINAL_STATE,
    }


def main():
    nodes = read_jsonl(ROOT / "graph_nodes_v0_5.jsonl")
    edges = read_jsonl(ROOT / "graph_edges_v0_5.jsonl")
    chunks = read_jsonl(ROOT / "rag_chunks_v0_5.jsonl")
    node_ids = {n["node_id"] for n in nodes}
    chunk_types = {c["chunk_type"] for c in chunks}

    evals = [
        eval_item("EVAL-V06-001", "industry_code", "3012 石灰和石膏制造第63条登记管理是否适用？", ["applicability:CTXV04_3012_63_REGISTRATION"], ["context_relation_chunk"], ["NOT_APPLY", "3021", "3029"], ["OQ-002"], ["RISK-V041-009"]),
        eval_item("EVAL-V06-002", "industry_code", "3021 水泥制品制造第63条重点管理为什么不是默认适用？", ["applicability:CTXV04_3021_63_KEY"], ["context_relation_chunk"], ["NOT_APPLY", "水泥熟料", "3021"], ["OQ-002"], ["RISK-V041-009"]),
        eval_item("EVAL-V06-003", "permit_catalog", "第108条在图谱中如何处理？", ["open_question:V04_ENTRY_108_CONTEXT_001", "risk:RISK-V041-001"], ["open_question_chunk", "risk_acceptance_chunk", "denoise_decision_chunk"], ["1-112", "109-112", "承接"], ["V04_ENTRY_108_CONTEXT_001"], ["RISK-V041-001"]),
        eval_item("EVAL-V06-004", "negative_condition", "锅炉简化管理里“除纳入重点排污单位名录”应如何理解？", ["permit_condition:109:SIMPLIFIED"], ["permit_condition_chunk"], ["not_present", "未被纳入", "若已纳入则不适用"], ["V04_NEGATION_POLARITY_001"], ["RISK-V041-008"]),
        eval_item("EVAL-V06-005", "negative_condition", "水处理登记管理中未纳入重点排污单位名录和处理能力阈值如何同时确认？", ["permit_condition:112:REGISTRATION"], ["permit_condition_chunk"], ["not_present", "500", "2万吨"], ["V04_NEGATION_POLARITY_001"], ["RISK-V041-008"]),
        eval_item("EVAL-V06-006", "general_process", "109-112 通用工序是否可以直接生成企业许可类型？", ["risk:RISK-V041-002", "open_question:V03_GENERAL_PROCESS_001"], ["risk_acceptance_chunk", "open_question_chunk"], ["不得", "NEED_CONFIRM", "通用工序"], ["V03_GENERAL_PROCESS_001"], ["RISK-V041-002"]),
        eval_item("EVAL-V06-007", "score13", "废水场景映射到 EcoCheck 哪些13维？", ["scenario:SCN_WW_PROCESS_AND_TREATMENT", "score13:S06", "score13:S10"], ["scenario_template_chunk", "score13_mapping_chunk"], ["S06", "S10", "S02"], ["V04_SCORE13_PROMOTION_001"], ["RISK-V041-004"]),
        eval_item("EVAL-V06-008", "score13", "VOCs 场景为什么需要 S10 二级语义？", ["scenario:SCN_VOCS_SOLVENT_AND_TREATMENT", "score13:S10"], ["scenario_template_chunk", "score13_mapping_chunk"], ["VOCs", "S10", "organized_exhaust"], ["V04_SCORE13_PROMOTION_001"], ["RISK-V041-004"]),
        eval_item("EVAL-V06-009", "inspection_evidence", "废水场景首次排查需要哪些证据链和拍照点？", ["inspection:SCN_WW_PROCESS_AND_TREATMENT:FIRST"], ["inspection_candidate_chunk"], ["evidence_chain", "photo_points", "污水站"], ["OQ-007"], ["RISK-V041-007"]),
        eval_item("EVAL-V06-010", "inspection_evidence", "危废场景月度排查要看哪些证据？", ["inspection:SCN_HAZWASTE_STORAGE_TRANSFER:MONTHLY"], ["inspection_candidate_chunk"], ["危废", "photo_points", "evidence_chain"], ["OQ-007"], ["RISK-V041-007"]),
        eval_item("EVAL-V06-011", "open_question_trace", "为什么 human_review_label 为空不能视为已审？", ["open_question:V04_HUMAN_REVIEW_EMPTY_001", "risk:RISK-V041-003"], ["open_question_chunk", "risk_acceptance_chunk"], ["待人工审阅", "不得伪造", "human_review"], ["V04_HUMAN_REVIEW_EMPTY_001"], ["RISK-V041-003"]),
        eval_item("EVAL-V06-012", "runtime_boundary", "这个知识库能否直接接入 EcoCheck 小程序？", ["risk:RISK-V041-005", "open_question:V04_RUNTIME_APPROVAL_GATE_001"], ["risk_acceptance_chunk", "open_question_chunk", "source_manifest_chunk"], ["不能", "runtime", "审批"], ["V04_RUNTIME_APPROVAL_GATE_001"], ["RISK-V041-005"]),
        eval_item("EVAL-V06-013", "permit_type_boundary", "target_management_condition 能不能当企业正式 permit_type？", ["risk:RISK-V041-006", "open_question:V03_PERMIT_TYPE_001"], ["risk_acceptance_chunk", "open_question_chunk"], ["不得", "NEED_CONFIRM", "正式"], ["V03_PERMIT_TYPE_001"], ["RISK-V041-006"]),
        eval_item("EVAL-V06-014", "division_context", "纯 DIVISION_CONTEXT 为什么不能直接 APPLIES？", ["open_question:V04_DIVISION_CONTEXT_APPLIES_001", "risk:RISK-V041-009"], ["open_question_chunk", "risk_acceptance_chunk"], ["召回信号", "不得", "直接证据"], ["V04_DIVISION_CONTEXT_APPLIES_001"], ["RISK-V041-009"]),
        eval_item("EVAL-V06-015", "not_apply_evidence", "NOT_APPLY 为什么必须有 blocking_flags？", ["open_question:V04_NOT_APPLY_BLOCKING_FLAGS_001"], ["open_question_chunk"], ["排除依据", "blocking_flags", "NOT_APPLY"], ["V04_NOT_APPLY_BLOCKING_FLAGS_001"], []),
        eval_item("EVAL-V06-016", "scenario_template", "在线监测场景有哪些触发条件和证据？", ["scenario:SCN_ONLINE_MONITORING_KEY_UNIT"], ["scenario_template_chunk"], ["在线监测", "evidence_requirements", "photo_points"], ["V03_SCENARIO_TEMPLATE_001"], []),
        eval_item("EVAL-V06-017", "scenario_template", "加油站油气回收和地下储罐场景怎么确认？", ["scenario:SCN_GAS_STATION_VAPOR_UST"], ["scenario_template_chunk"], ["油气回收", "地下储罐", "confirmation_questions"], ["V03_SCENARIO_TEMPLATE_001"], []),
        eval_item("EVAL-V06-018", "risk_trace", "risk_acceptance_queue 和 open_questions 是什么关系？", ["risk:RISK-V041-005", "open_question:V04_RUNTIME_APPROVAL_GATE_001"], ["risk_acceptance_chunk", "open_question_chunk"], ["风险承接", "开放问题", "运行时"], ["V04_RUNTIME_APPROVAL_GATE_001"], ["RISK-V041-005"]),
        eval_item("EVAL-V06-019", "permit_catalog", "第63条里3012为什么简化管理有直接证据而登记管理没有？", ["applicability:CTXV04_3012_63_SIMPLIFIED", "applicability:CTXV04_3012_63_REGISTRATION"], ["context_relation_chunk", "permit_condition_chunk"], ["3012", "SIMPLIFIED", "REGISTRATION"], ["OQ-002"], ["RISK-V041-009"]),
        eval_item("EVAL-V06-020", "rag_boundary", "RAG回答候选知识时必须提醒什么边界？", ["kb:v0_5:manifest"], ["source_manifest_chunk"], ["候选", "不接", "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"], ["V04_RUNTIME_APPROVAL_GATE_001"], ["RISK-V041-005"]),
        eval_item("EVAL-V06-021", "industry_code", "4620 污水处理及其再生利用与第99条关系如何检索？", ["applicability:CTXV04_4620_99_KEY", "applicability:CTXV04_4620_99_SIMPLIFIED"], ["context_relation_chunk"], ["MAY_APPLY", "污水处理", "现场事实"], ["V04_DIVISION_CONTEXT_APPLIES_001"], ["RISK-V041-009"]),
        eval_item("EVAL-V06-022", "medical_special", "医疗废物和放射诊疗场景应检索哪些节点？", ["scenario:SCN_MEDICAL_WASTE_RADIATION", "score13:S12"], ["scenario_template_chunk", "score13_mapping_chunk"], ["医废", "辐射", "S12"], ["V03_SCENARIO_TEMPLATE_001"], []),
        eval_item("EVAL-V06-023", "solid_waste", "一般固废、危废、医废是否都只归 S07 报告层？", ["score13:S07", "scenario:SCN_HAZWASTE_STORAGE_TRANSFER", "scenario:SCN_MEDICAL_WASTE_RADIATION"], ["score13_mapping_chunk", "scenario_template_chunk"], ["S07", "二级语义", "候选"], ["V04_SCORE13_PROMOTION_001"], ["RISK-V041-004"]),
        eval_item("EVAL-V06-024", "emergency", "雨污和事故水场景与 S13 如何关联？", ["scenario:SCN_RAINWATER_ACCIDENT_EMERGENCY", "score13:S13"], ["scenario_template_chunk", "score13_mapping_chunk"], ["事故水", "S13", "应急"], ["V04_SCORE13_PROMOTION_001"], ["RISK-V041-004"]),
    ]

    query_samples = [
        query_sample("QUERY-V06-001", "industry_to_condition_to_scenario", "从行业3012出发，查询第63条条件、候选关系和相关场景。", ["industry:3012"], ["CANDIDATE_APPLICABILITY", "RELATED_TO_SCENARIO"], ["PermitCondition", "ApplicabilityRelation", "ScenarioTemplate"], ["OQ-002"], ["RISK-V041-009"]),
        query_sample("QUERY-V06-002", "entry_to_conditions", "从许可名录第63条查询三类管理条件及其行业代码边界。", ["permit_entry:63"], ["HAS_CONDITION"], ["PermitCondition"], ["OQ-002"], []),
        query_sample("QUERY-V06-003", "entry108_strategy_trace", "从entry108开放问题追溯到109-112通用工序风险。", ["open_question:V04_ENTRY_108_CONTEXT_001"], ["RISK_LINKED_TO_OPEN_QUESTION"], ["RiskAcceptance"], ["V04_ENTRY_108_CONTEXT_001"], ["RISK-V041-001"]),
        query_sample("QUERY-V06-004", "scenario_to_score13", "从废水场景查询EcoCheck 13维映射。", ["scenario:SCN_WW_PROCESS_AND_TREATMENT"], ["MAPS_TO_SCORE13"], ["Score13Dimension"], ["V04_SCORE13_PROMOTION_001"], ["RISK-V041-004"]),
        query_sample("QUERY-V06-005", "scenario_to_inspection", "从危废场景查询首次/月度候选排查项。", ["scenario:SCN_HAZWASTE_STORAGE_TRANSFER"], ["HAS_INSPECTION_CANDIDATE"], ["InspectionCandidate"], ["OQ-007"], ["RISK-V041-007"]),
        query_sample("QUERY-V06-006", "risk_to_open_question", "从runtime approval风险查询对应开放问题。", ["risk:RISK-V041-005"], ["RISK_LINKED_TO_OPEN_QUESTION"], ["OpenQuestion"], ["V04_RUNTIME_APPROVAL_GATE_001"], ["RISK-V041-005"]),
        query_sample("QUERY-V06-007", "condition_negative_semantics", "从锅炉简化条件查询否定语义和风险引用。", ["permit_condition:109:SIMPLIFIED"], [], ["PermitCondition"], ["V04_NEGATION_POLARITY_001"], ["RISK-V041-008"]),
        query_sample("QUERY-V06-008", "runtime_boundary_manifest", "查询候选知识库不能接运行时的manifest和风险。", ["kb:v0_5:manifest"], [], ["KnowledgeBaseManifest", "RiskAcceptance"], ["V04_RUNTIME_APPROVAL_GATE_001"], ["RISK-V041-005"]),
    ]

    coverage = {
        "eval_count": len(evals),
        "query_sample_count": len(query_samples),
        "eval_category_counts": dict(sorted(Counter(e["eval_category"] for e in evals).items())),
        "final_state": FINAL_STATE,
        "runtime_integration": "disabled",
    }

    missing_nodes = sorted({nid for e in evals for nid in e["expected_node_ids"] if nid not in node_ids})
    missing_chunk_types = sorted({ct for e in evals for ct in e["expected_chunk_types"] if ct not in chunk_types})
    coverage["precheck_missing_nodes"] = missing_nodes
    coverage["precheck_missing_chunk_types"] = missing_chunk_types

    write_jsonl(ROOT / "retrieval_eval_set_v0_6.jsonl", evals)
    write_jsonl(ROOT / "graph_query_samples_v0_6.jsonl", query_samples)
    write_json(ROOT / "rag_graph_eval_coverage_v0_6.json", coverage)
    (ROOT / "rag_graph_eval_spec_v0_6.md").write_text(
        "# rag_graph_eval_spec_v0_6\n\n"
        f"final_state: `{FINAL_STATE}`\n\n"
        "v0.6 是 RAG 检索质量评测与图谱查询样例层，不接 EcoCheck runtime。\n\n"
        "## Coverage\n\n"
        "- 行业代码与许可名录条件\n"
        "- 否定条件和第108条承接\n"
        "- EcoCheck 13维映射\n"
        "- 现场排查证据链和 photo_points\n"
        "- open_questions / risk_acceptance 追溯\n"
        "- runtime / permit_type / template 边界\n\n"
        "所有 eval 都必须要求回答包含候选边界提示，不得把候选知识当作正式运行时规则。\n",
        encoding="utf-8",
    )
    (ROOT / "FINAL_COMPLETION_REPORT_v0_6.md").write_text(
        "# FINAL COMPLETION REPORT v0.6\n\n"
        f"最终状态：`{FINAL_STATE}`\n\n"
        "v0.6 已生成 RAG 检索质量评测与图谱查询样例层，未接 EcoCheck runtime。\n\n"
        f"- retrieval_eval_items: {len(evals)}\n"
        f"- graph_query_samples: {len(query_samples)}\n"
        "- 覆盖行业代码、许可名录、否定条件、第108条承接、13维映射、现场证据链、开放问题追溯。\n",
        encoding="utf-8",
    )
    print(json.dumps(coverage, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
