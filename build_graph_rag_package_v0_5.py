import csv
import hashlib
import json
from pathlib import Path
from kb_paths import artifact_path


ROOT = Path(__file__).resolve().parent
FINAL_STATE = "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"
KB_VERSION = "v0.5-graph-rag-candidate-package"

SCORE13 = {
    "S01": "环保手续完善情况",
    "S02": "环保台账规范情况",
    "S03": "环保相关系统完成情况",
    "S04": "内部现场环境情况",
    "S05": "外部周边环境情况",
    "S06": "环保治理设施运行情况",
    "S07": "固体废物贮存规范情况",
    "S08": "环保培训情况",
    "S09": "标识、标牌、制度公示情况",
    "S10": "废水、废气、噪声、废渣排放及处置情况",
    "S11": "历史遗留问题整改情况",
    "S12": "辐射安全管理",
    "S13": "环保应急管理情况",
}


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


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


def parse_json(value, default=None):
    if default is None:
        default = []
    if isinstance(value, (list, dict)):
        return value
    if not value:
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


def sha8(obj):
    body = json.dumps(obj, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()[:8]


def chunk_id(chunk_type, natural_key, content):
    safe_key = str(natural_key).replace(" ", "_").replace("/", "_")
    return f"kbv0_5::{chunk_type}::{safe_key}::{sha8(content)}"


def common(source_basis, runtime_status, confidence="MEDIUM", gate_status="N/A", open_refs=None, risk_refs=None):
    return {
        "kb_version": KB_VERSION,
        "final_state": FINAL_STATE,
        "runtime_status": runtime_status,
        "candidate_only": True,
        "source_basis": source_basis,
        "confidence": confidence or "MEDIUM",
        "gate_status": gate_status or "N/A",
        "open_question_refs": open_refs or [],
        "risk_refs": risk_refs or [],
    }


def refs_for_context(row):
    oq = ["V04_HUMAN_REVIEW_EMPTY_001"]
    risks = ["RISK-V041-003"]
    entry = row.get("entry_no")
    if entry == "108":
        oq += ["V04_ENTRY_108_CONTEXT_001"]
        risks += ["RISK-V041-001"]
    if entry in {"109", "110", "111", "112"} or "GENERAL_PROCESS_TRIGGER" in row.get("relation_source", ""):
        oq += ["OQ-005", "V03_GENERAL_PROCESS_001", "V04_ENTRY_108_CONTEXT_001"]
        risks += ["RISK-V041-002"]
    if row.get("relation_source") == "DIVISION_CONTEXT":
        oq += ["V03_CONTEXT_SCOPE_001", "V04_DIVISION_CONTEXT_APPLIES_001"]
        risks += ["RISK-V041-009"]
    if row.get("gate_status") == "NOT_APPLY":
        oq += ["V04_NOT_APPLY_BLOCKING_FLAGS_001"]
    if row.get("entry_no") in {"36", "38", "63"}:
        oq += ["OQ-002", "OQ-003", "OQ-004"]
    return sorted(set(oq)), sorted(set(risks))


def refs_for_condition(row):
    oq = []
    risks = []
    if row.get("entry_no") in {"109", "110", "111", "112"}:
        oq += ["OQ-005", "V03_GENERAL_PROCESS_001", "V04_ENTRY_108_CONTEXT_001"]
        risks += ["RISK-V041-002"]
    if row.get("condition_polarity") in {"exclusion", "contains_exclusion_semantics"}:
        oq += ["V04_NEGATION_POLARITY_001"]
        risks += ["RISK-V041-008"]
    return sorted(set(oq)), sorted(set(risks))


def node(node_type, node_id, natural_key, properties, source_basis, runtime_status, confidence="MEDIUM", gate_status="N/A", open_refs=None, risk_refs=None):
    return {
        "node_id": node_id,
        "node_type": node_type,
        "natural_key": natural_key,
        **common(source_basis, runtime_status, confidence, gate_status, open_refs, risk_refs),
        "properties": properties,
    }


def edge(edge_type, edge_id, from_id, to_id, properties, source_basis, runtime_status, confidence="MEDIUM", gate_status="N/A", open_refs=None, risk_refs=None):
    return {
        "edge_id": edge_id,
        "edge_type": edge_type,
        "from_node_id": from_id,
        "to_node_id": to_id,
        **common(source_basis, runtime_status, confidence, gate_status, open_refs, risk_refs),
        "properties": properties,
    }


def build_text(title, fields):
    lines = [title]
    for key, value in fields.items():
        if isinstance(value, (list, dict)):
            value = json.dumps(value, ensure_ascii=False)
        lines.append(f"{key}: {value}")
    return "\n".join(lines)


def chunk(chunk_type, natural_key, text, metadata):
    base = {
        "chunk_type": chunk_type,
        "natural_key": natural_key,
        "text": text,
        "metadata": metadata,
    }
    return {
        "chunk_id": chunk_id(chunk_type, natural_key, base),
        **base,
        "kb_version": KB_VERSION,
        "final_state": FINAL_STATE,
        "runtime_status": metadata.get("runtime_status", "DRAFT_NOT_FOR_RUNTIME"),
        "candidate_only": True,
        "source_basis": metadata.get("source_basis", ""),
        "confidence": metadata.get("confidence", "MEDIUM"),
        "gate_status": metadata.get("gate_status", "N/A"),
        "open_question_refs": metadata.get("open_question_refs", []),
        "risk_refs": metadata.get("risk_refs", []),
    }


def main():
    industries = read_json(artifact_path("all_industry_scenario_candidates_v0_2.json"))
    raw_entries = read_csv(artifact_path("permit_management_catalog_table_cells.csv"))
    permit_conditions = read_csv(artifact_path("all_permit_condition_backfill_v0_4_1.csv"))
    context = read_csv(artifact_path("all_context_applicability_review_v0_4_1.csv"))
    scenarios = read_json(artifact_path("scenario_templates.json"))
    score_map = read_csv(artifact_path("scenario_to_score13_mapping_v0_3.csv"))
    inspections = read_csv(artifact_path("inspection_candidate_recommendations_v0_3.csv"))
    open_questions = read_csv(artifact_path("open_questions_v0_4_1.csv"))
    risks = read_csv(artifact_path("risk_acceptance_queue_v0_4_1.csv"))
    manifest = read_json(artifact_path("knowledge_base_manifest_v0_4_1.json"))

    nodes = []
    edges = []
    chunks = []

    nodes.append(node(
        "KnowledgeBaseManifest", "kb:v0_5:manifest", "manifest:v0_5",
        {"runtime_integration": "disabled", "positioning": "RAG/环保语义图谱候选入库设计包", "source_manifest": "knowledge_base_manifest_v0_4_1.json"},
        "knowledge_base_manifest_v0_4_1.json", "DRAFT_NOT_FOR_RUNTIME", "HIGH", "N/A",
        ["V04_RUNTIME_APPROVAL_GATE_001"], ["RISK-V041-005"],
    ))
    chunks.append(chunk(
        "source_manifest_chunk", "manifest:v0_5",
        build_text("候选知识库 v0.5 边界", {"final_state": FINAL_STATE, "runtime_integration": "disabled", "hard_boundaries": manifest.get("hard_boundaries", [])}),
        common("knowledge_base_manifest_v0_4_1.json", "DRAFT_NOT_FOR_RUNTIME", "HIGH", "N/A", ["V04_RUNTIME_APPROVAL_GATE_001"], ["RISK-V041-005"]),
    ))

    for industry in industries:
        nid = f"industry:{industry['industry_code']}"
        refs, risk_refs = ["V04_HUMAN_REVIEW_EMPTY_001"], ["RISK-V041-003"]
        nodes.append(node("Industry", nid, industry["industry_code"], industry, "all_industry_scenario_candidates_v0_2.json", "CANDIDATE_ONLY", industry.get("confidence", "MEDIUM"), "NEED_CONFIRM", refs, risk_refs))

    for entry in raw_entries:
        nid = f"permit_entry:{entry['catalog_entry_no']}"
        open_refs = ["V04_ENTRY_108_CONTEXT_001"] if entry["catalog_entry_no"] == "108" else []
        risk_refs = ["RISK-V041-001"] if entry["catalog_entry_no"] == "108" else []
        nodes.append(node("PermitCatalogEntry", nid, entry["catalog_entry_no"], entry, "permit_management_catalog_table_cells.csv", "DRAFT_NOT_FOR_RUNTIME", "HIGH", "NEED_CONFIRM", open_refs, risk_refs))

    for row in permit_conditions:
        cid = f"permit_condition:{int(row['entry_no']):03d}:{row['target_management_condition']}"
        open_refs, risk_refs = refs_for_condition(row)
        nodes.append(node("PermitCondition", cid, f"{row['entry_no']}:{row['target_management_condition']}", row, row["source_basis"], "DRAFT_NOT_FOR_RUNTIME", row["confidence"], row["applies_status"], open_refs, risk_refs))
        edges.append(edge("HAS_CONDITION", f"edge:entry:{row['entry_no']}:condition:{row['target_management_condition']}", f"permit_entry:{row['entry_no']}", cid, {"target_management_condition": row["target_management_condition"]}, row["source_basis"], "DRAFT_NOT_FOR_RUNTIME", row["confidence"], row["applies_status"], open_refs, risk_refs))
        chunks.append(chunk("permit_condition_chunk", f"entry{int(row['entry_no']):03d}_{row['target_management_condition']}", build_text("排污许可条件候选", row), common(row["source_basis"], "DRAFT_NOT_FOR_RUNTIME", row["confidence"], row["applies_status"], open_refs, risk_refs)))

    for row in context:
        rel_id = f"applicability:{row['candidate_relation_id']}"
        open_refs, risk_refs = refs_for_context(row)
        nodes.append(node("ApplicabilityRelation", rel_id, row["candidate_relation_id"], row, row["source_basis"], "DRAFT_NOT_FOR_RUNTIME", row["confidence"], row["gate_status"], open_refs, risk_refs))
        condition_id = f"permit_condition:{int(row['entry_no']):03d}:{row['target_management_condition']}"
        edges.append(edge("CANDIDATE_APPLICABILITY", f"edge:app:{row['candidate_relation_id']}", f"industry:{row['industry_code']}", condition_id, {"candidate_relation_id": row["candidate_relation_id"], "relation_source": row["relation_source"], "gate_reason": row["gate_reason"], "blocking_flags": parse_json(row["blocking_flags"])}, row["source_basis"], "DRAFT_NOT_FOR_RUNTIME", row["confidence"], row["gate_status"], open_refs, risk_refs))
        edges.append(edge("HAS_APPLICABILITY_RELATION", f"edge:industry_rel:{row['candidate_relation_id']}", f"industry:{row['industry_code']}", rel_id, {}, row["source_basis"], "DRAFT_NOT_FOR_RUNTIME", row["confidence"], row["gate_status"], open_refs, risk_refs))
        for sid in parse_json(row["related_scenario_ids"]):
            edges.append(edge("RELATED_TO_SCENARIO", f"edge:rel_scenario:{row['candidate_relation_id']}:{sid}", rel_id, f"scenario:{sid}", {"ref_reason": "candidate_relation_related_scenario_ids"}, row["source_basis"], "DRAFT_NOT_FOR_RUNTIME", row["confidence"], row["gate_status"], open_refs, risk_refs))
        chunks.append(chunk("context_relation_chunk", row["candidate_relation_id"], build_text("行业-许可条件候选适用关系", row), common(row["source_basis"], "DRAFT_NOT_FOR_RUNTIME", row["confidence"], row["gate_status"], open_refs, risk_refs)))

    for scenario in scenarios:
        sid = scenario["scenario_id"]
        nodes.append(node("ScenarioTemplate", f"scenario:{sid}", sid, scenario, "scenario_templates.json", "DRAFT_NOT_FOR_RUNTIME", scenario.get("confidence", "MEDIUM"), "NEED_CONFIRM", ["V03_SCENARIO_TEMPLATE_001"], []))
        chunks.append(chunk("scenario_template_chunk", sid, build_text("产污场景模板", scenario), common("scenario_templates.json", "DRAFT_NOT_FOR_RUNTIME", scenario.get("confidence", "MEDIUM"), "NEED_CONFIRM", ["V03_SCENARIO_TEMPLATE_001"], [])))

    for item_id, name in SCORE13.items():
        nodes.append(node("Score13Dimension", f"score13:{item_id}", item_id, {"score_item_id": item_id, "score_item_name": name}, "EcoCheck S01-S13 report dimension baseline", "CANDIDATE_ONLY", "HIGH", "N/A", ["V04_SCORE13_PROMOTION_001"], ["RISK-V041-004"]))

    for row in score_map:
        scenario_id = row["scenario_id"]
        ids = [row["primary_score_item_id"]] + [x for x in row["secondary_score_item_ids"].split(";") if x]
        for score_id in sorted(set(ids)):
            edges.append(edge("MAPS_TO_SCORE13", f"edge:scenario_score13:{scenario_id}:{score_id}", f"scenario:{scenario_id}", f"score13:{score_id}", row, "scenario_to_score13_mapping_v0_3.csv", "CANDIDATE_ONLY", "MEDIUM", "NEED_CONFIRM", ["V04_SCORE13_PROMOTION_001"], ["RISK-V041-004"]))
        chunks.append(chunk("score13_mapping_chunk", scenario_id, build_text("EcoCheck 13维候选语义映射", row), common("scenario_to_score13_mapping_v0_3.csv", "CANDIDATE_ONLY", "MEDIUM", "NEED_CONFIRM", ["V04_SCORE13_PROMOTION_001"], ["RISK-V041-004"])))

    for idx, row in enumerate(inspections, start=1):
        iid = f"inspection:{row['scenario_id']}:{row['inspection_type']}"
        nodes.append(node("InspectionCandidate", iid, f"{row['scenario_id']}:{row['inspection_type']}", row, "inspection_candidate_recommendations_v0_3.csv", "CANDIDATE_ONLY", "MEDIUM", "NEED_CONFIRM", ["OQ-007", "V03_ECOCHECK_RUNTIME_001"], ["RISK-V041-007"]))
        edges.append(edge("HAS_INSPECTION_CANDIDATE", f"edge:scenario_inspection:{row['scenario_id']}:{row['inspection_type']}", f"scenario:{row['scenario_id']}", iid, {"inspection_type": row["inspection_type"]}, "inspection_candidate_recommendations_v0_3.csv", "CANDIDATE_ONLY", "MEDIUM", "NEED_CONFIRM", ["OQ-007", "V03_ECOCHECK_RUNTIME_001"], ["RISK-V041-007"]))
        chunks.append(chunk("inspection_candidate_chunk", f"{row['scenario_id']}:{row['inspection_type']}", build_text("候选现场排查项", row), common("inspection_candidate_recommendations_v0_3.csv", "CANDIDATE_ONLY", "MEDIUM", "NEED_CONFIRM", ["OQ-007", "V03_ECOCHECK_RUNTIME_001"], ["RISK-V041-007"])))

    for row in open_questions:
        qid = row["question_id"]
        nodes.append(node("OpenQuestion", f"open_question:{qid}", qid, row, "open_questions_v0_4_1.csv", "DRAFT_NOT_FOR_RUNTIME", "HIGH" if row.get("priority") == "P0" else "MEDIUM", "BLOCKS_RUNTIME", [qid], []))
        chunks.append(chunk("open_question_chunk", qid, build_text("开放问题", row), common("open_questions_v0_4_1.csv", "DRAFT_NOT_FOR_RUNTIME", "HIGH" if row.get("priority") == "P0" else "MEDIUM", "BLOCKS_RUNTIME", [qid], [])))

    for row in risks:
        rid = row["risk_id"]
        refs = [x for x in row.get("open_question_refs", "").split(";") if x]
        nodes.append(node("RiskAcceptance", f"risk:{rid}", rid, row, "risk_acceptance_queue_v0_4_1.csv", "DRAFT_NOT_FOR_RUNTIME", "HIGH", "BLOCKS_RUNTIME", refs, [rid]))
        for qid in refs:
            edges.append(edge("RISK_LINKED_TO_OPEN_QUESTION", f"edge:risk_oq:{rid}:{qid}", f"risk:{rid}", f"open_question:{qid}", {"ref_reason": row["risk_topic"]}, "risk_acceptance_queue_v0_4_1.csv", "DRAFT_NOT_FOR_RUNTIME", "HIGH", "BLOCKS_RUNTIME", [qid], [rid]))
        chunks.append(chunk("risk_acceptance_chunk", rid, build_text("风险接受队列", row), common("risk_acceptance_queue_v0_4_1.csv", "DRAFT_NOT_FOR_RUNTIME", "HIGH", "BLOCKS_RUNTIME", refs, [rid])))

    strategy_text = (artifact_path("automated_denoise_diff_report_v0_4.md")).read_text(encoding="utf-8") if (artifact_path("automated_denoise_diff_report_v0_4.md")).exists() else ""
    chunks.append(chunk("denoise_decision_chunk", "v0_4_to_v0_4_1_denoise", strategy_text + "\n\nv0.4.1: CTXV04_3012_63_REGISTRATION降为NOT_APPLY；entry108承接策略和risk queue关系已明确。", common("automated_denoise_diff_report_v0_4.md; FINAL_COMPLETION_REPORT_v0_4_1.md", "DRAFT_NOT_FOR_RUNTIME", "HIGH", "BLOCKS_RUNTIME", ["V04_ENTRY_108_CONTEXT_001", "V04_DIVISION_CONTEXT_APPLIES_001"], ["RISK-V041-001", "RISK-V041-009"])))

    eval_set = [
        {"eval_id": "EVAL-V05-001", "query": "3012 石灰和石膏制造第63条登记管理是否默认适用？", "expected_node_ids": ["applicability:CTXV04_3012_63_REGISTRATION"], "expected_answer_contains": ["NOT_APPLY", "3021", "3029", "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"], "final_state": FINAL_STATE, "runtime_status": "DRAFT_NOT_FOR_RUNTIME"},
        {"eval_id": "EVAL-V05-002", "query": "第108条为什么适用关系表只有111个条目？", "expected_node_ids": ["open_question:V04_ENTRY_108_CONTEXT_001", "risk:RISK-V041-001"], "expected_answer_contains": ["1-112连续", "109-112", "承接"], "final_state": FINAL_STATE, "runtime_status": "DRAFT_NOT_FOR_RUNTIME"},
        {"eval_id": "EVAL-V05-003", "query": "锅炉通用工序条件里除纳入重点排污单位名录是什么意思？", "expected_node_ids": ["permit_condition:109:SIMPLIFIED"], "expected_answer_contains": ["not_present", "未被纳入", "若已纳入则不适用"], "final_state": FINAL_STATE, "runtime_status": "DRAFT_NOT_FOR_RUNTIME"},
        {"eval_id": "EVAL-V05-004", "query": "废水场景进入EcoCheck 13维如何映射？", "expected_node_ids": ["scenario:SCN_WW_PROCESS_AND_TREATMENT"], "expected_answer_contains": ["S06", "S10", "候选"], "final_state": FINAL_STATE, "runtime_status": "CANDIDATE_ONLY"},
        {"eval_id": "EVAL-V05-005", "query": "现场排查拍照要点是否保留？", "expected_node_ids": ["inspection:SCN_WW_PROCESS_AND_TREATMENT:FIRST"], "expected_answer_contains": ["photo_points", "候选"], "final_state": FINAL_STATE, "runtime_status": "CANDIDATE_ONLY"},
    ]

    write_jsonl(artifact_path("graph_nodes_v0_5.jsonl"), nodes)
    write_jsonl(artifact_path("graph_edges_v0_5.jsonl"), edges)
    write_jsonl(artifact_path("rag_chunks_v0_5.jsonl"), chunks)
    write_jsonl(artifact_path("retrieval_eval_set_v0_5.jsonl"), eval_set)

    schema_md = [
        "# kb_graph_schema_v0_5",
        "",
        f"final_state: `{FINAL_STATE}`",
        "",
        "v0.5 是 RAG/环保语义图谱候选入库设计包，不接 EcoCheck runtime。",
        "",
        "## Node Types",
        "",
        "- Industry: GB/T 4754 四位小类候选召回入口。",
        "- PermitCatalogEntry: 排污许可名录1-112原始条目。",
        "- PermitCondition: KEY/SIMPLIFIED/REGISTRATION三类条件单元。",
        "- ApplicabilityRelation: 行业小类与许可条件的候选适用关系。",
        "- ScenarioTemplate: 产污场景本体。",
        "- Score13Dimension: EcoCheck S01-S13报告维度。",
        "- InspectionCandidate: 候选现场排查项，不是正式模板。",
        "- OpenQuestion: 运行时/正式化前必须关闭或接受的问题。",
        "- RiskAcceptance: open questions的风险承接队列。",
        "",
        "## Required Common Fields",
        "",
        "`source_basis`, `confidence`, `gate_status`, `runtime_status`, `final_state`, `open_question_refs`, `risk_refs`, `candidate_only`。",
        "",
        "## Edge Types",
        "",
        "`HAS_CONDITION`, `CANDIDATE_APPLICABILITY`, `HAS_APPLICABILITY_RELATION`, `RELATED_TO_SCENARIO`, `MAPS_TO_SCORE13`, `HAS_INSPECTION_CANDIDATE`, `RISK_LINKED_TO_OPEN_QUESTION`。",
    ]
    (artifact_path("kb_graph_schema_v0_5.md")).write_text("\n".join(schema_md) + "\n", encoding="utf-8")

    rag_md = [
        "# rag_chunk_spec_v0_5",
        "",
        f"final_state: `{FINAL_STATE}`",
        "",
        "chunk_id策略：`kbv0_5::{chunk_type}::{natural_key}::{content_sha8}`。",
        "",
        "## Chunk Types",
        "",
        "- source_manifest_chunk",
        "- permit_condition_chunk",
        "- context_relation_chunk",
        "- scenario_template_chunk",
        "- inspection_candidate_chunk",
        "- score13_mapping_chunk",
        "- open_question_chunk",
        "- risk_acceptance_chunk",
        "- denoise_decision_chunk",
        "",
        "所有chunk必须显式携带候选边界字段，RAG回答不得把候选关系当成正式permit_type或正式检查模板。",
    ]
    (artifact_path("rag_chunk_spec_v0_5.md")).write_text("\n".join(rag_md) + "\n", encoding="utf-8")

    manifest_v05 = {
        "knowledge_base_version": KB_VERSION,
        "final_state": FINAL_STATE,
        "runtime_integration": "disabled",
        "runtime_promotion_status": "not_approved",
        "source_baseline": "v0.4.1-candidate-governance-denoise-patch",
        "outputs": {
            "kb_graph_schema_v0_5.md": 1,
            "rag_chunk_spec_v0_5.md": 1,
            "graph_nodes_v0_5.jsonl": len(nodes),
            "graph_edges_v0_5.jsonl": len(edges),
            "rag_chunks_v0_5.jsonl": len(chunks),
            "retrieval_eval_set_v0_5.jsonl": len(eval_set),
            "build_graph_rag_package_v0_5.py": 1,
            "validate_graph_rag_package_v0_5.py": 1,
            "FINAL_COMPLETION_REPORT_v0_5.md": 1,
        },
    }
    write_json(artifact_path("knowledge_base_manifest_v0_5.json"), manifest_v05)
    (artifact_path("FINAL_COMPLETION_REPORT_v0_5.md")).write_text(
        "# FINAL COMPLETION REPORT v0.5\n\n"
        f"最终状态：`{FINAL_STATE}`\n\n"
        "v0.5 已生成 RAG/环保语义图谱候选入库设计包，未接 EcoCheck runtime。\n\n"
        f"- graph_nodes: {len(nodes)}\n"
        f"- graph_edges: {len(edges)}\n"
        f"- rag_chunks: {len(chunks)}\n"
        f"- retrieval_eval_items: {len(eval_set)}\n\n"
        "硬边界：不生成正式 permit_type，不生成正式检查模板，不自动扣分，不接小程序运行时。\n",
        encoding="utf-8",
    )
    print(json.dumps({"final_state": FINAL_STATE, "nodes": len(nodes), "edges": len(edges), "chunks": len(chunks), "eval_items": len(eval_set)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
