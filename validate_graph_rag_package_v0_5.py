import json
from collections import Counter
from pathlib import Path
from kb_paths import artifact_path


ROOT = Path(__file__).resolve().parent
FINAL_STATE = "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"


def read_jsonl(path):
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def fail(failures, file, reason, row_id=""):
    failures.append({"file": file, "reason": reason, "row_id": row_id})


def check_common(row, id_field, failures, file):
    row_id = row.get(id_field, "")
    for field in ["source_basis", "runtime_status", "final_state", "open_question_refs", "risk_refs"]:
        if field not in row:
            fail(failures, file, f"missing_{field}", row_id)
    if row.get("final_state") != FINAL_STATE:
        fail(failures, file, "bad_final_state", row_id)
    if row.get("candidate_only") is not True:
        fail(failures, file, "candidate_only_not_true", row_id)
    body = json.dumps(row, ensure_ascii=False)
    forbidden = ["runtime_integration\":\"enabled", "AUTO_DEDUCT"]
    for token in forbidden:
        if token in body:
            fail(failures, file, "forbidden_runtime_or_formal_token", row_id)


def main():
    failures = []
    required = [
        "kb_graph_schema_v0_5.md",
        "rag_chunk_spec_v0_5.md",
        "build_graph_rag_package_v0_5.py",
        "validate_graph_rag_package_v0_5.py",
        "graph_nodes_v0_5.jsonl",
        "graph_edges_v0_5.jsonl",
        "rag_chunks_v0_5.jsonl",
        "retrieval_eval_set_v0_5.jsonl",
        "FINAL_COMPLETION_REPORT_v0_5.md",
        "knowledge_base_manifest_v0_5.json",
    ]
    for name in required:
        if not (artifact_path(name)).exists():
            fail(failures, name, "missing_required_output")

    nodes = read_jsonl(artifact_path("graph_nodes_v0_5.jsonl"))
    edges = read_jsonl(artifact_path("graph_edges_v0_5.jsonl"))
    chunks = read_jsonl(artifact_path("rag_chunks_v0_5.jsonl"))
    evals = read_jsonl(artifact_path("retrieval_eval_set_v0_5.jsonl"))
    manifest = read_json(artifact_path("knowledge_base_manifest_v0_5.json"))

    node_ids = [n["node_id"] for n in nodes]
    edge_ids = [e["edge_id"] for e in edges]
    chunk_ids = [c["chunk_id"] for c in chunks]
    if len(node_ids) != len(set(node_ids)):
        fail(failures, "graph_nodes_v0_5.jsonl", "duplicate_node_id")
    if len(edge_ids) != len(set(edge_ids)):
        fail(failures, "graph_edges_v0_5.jsonl", "duplicate_edge_id")
    if len(chunk_ids) != len(set(chunk_ids)):
        fail(failures, "rag_chunks_v0_5.jsonl", "duplicate_chunk_id")

    required_node_types = {
        "Industry", "PermitCatalogEntry", "PermitCondition", "ApplicabilityRelation",
        "ScenarioTemplate", "Score13Dimension", "InspectionCandidate", "OpenQuestion", "RiskAcceptance",
    }
    node_type_counts = Counter(n["node_type"] for n in nodes)
    for node_type in required_node_types:
        if node_type_counts[node_type] == 0:
            fail(failures, "graph_nodes_v0_5.jsonl", "missing_node_type", node_type)

    node_set = set(node_ids)
    for n in nodes:
        check_common(n, "node_id", failures, "graph_nodes_v0_5.jsonl")
        if n["node_type"] == "ApplicabilityRelation":
            props = n.get("properties", {})
            if props.get("permit_type") != "NEED_CONFIRM" or props.get("runtime_status") != "DRAFT_NOT_FOR_RUNTIME":
                fail(failures, "graph_nodes_v0_5.jsonl", "bad_applicability_boundary", n["node_id"])
            if props.get("relation_source") == "DIVISION_CONTEXT" and props.get("gate_status") == "APPLIES":
                fail(failures, "graph_nodes_v0_5.jsonl", "division_context_applies", n["node_id"])
        if n["node_type"] == "InspectionCandidate":
            props = n.get("properties", {})
            if props.get("runtime_status") != "CANDIDATE_ONLY" or not props.get("photo_points") or not props.get("evidence_chain"):
                fail(failures, "graph_nodes_v0_5.jsonl", "bad_inspection_candidate", n["node_id"])

    for e in edges:
        check_common(e, "edge_id", failures, "graph_edges_v0_5.jsonl")
        if e["from_node_id"] not in node_set or e["to_node_id"] not in node_set:
            fail(failures, "graph_edges_v0_5.jsonl", "orphan_edge_endpoint", e["edge_id"])
        if e["edge_type"] == "CANDIDATE_APPLICABILITY" and e.get("runtime_status") != "DRAFT_NOT_FOR_RUNTIME":
            fail(failures, "graph_edges_v0_5.jsonl", "bad_candidate_applicability_runtime", e["edge_id"])

    for c in chunks:
        check_common(c, "chunk_id", failures, "rag_chunks_v0_5.jsonl")
        if not c.get("text") or not c.get("metadata"):
            fail(failures, "rag_chunks_v0_5.jsonl", "missing_text_or_metadata", c["chunk_id"])

    for item in evals:
        if item.get("final_state") != FINAL_STATE:
            fail(failures, "retrieval_eval_set_v0_5.jsonl", "bad_eval_final_state", item.get("eval_id", ""))
        for nid in item.get("expected_node_ids", []):
            if nid not in node_set:
                fail(failures, "retrieval_eval_set_v0_5.jsonl", "eval_expected_node_missing", nid)

    if manifest.get("final_state") != FINAL_STATE or manifest.get("runtime_integration") != "disabled":
        fail(failures, "knowledge_base_manifest_v0_5.json", "bad_manifest_boundary")

    with (artifact_path("graph_rag_package_v0_5_failure_list.json")).open("w", encoding="utf-8") as f:
        json.dump(failures, f, ensure_ascii=False, indent=2)

    report = {
        "validation_status": "PASS" if not failures else "FAIL",
        "final_state": FINAL_STATE,
        "failure_count": len(failures),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "chunk_count": len(chunks),
        "eval_count": len(evals),
        "node_type_counts": dict(sorted(node_type_counts.items())),
        "failure_samples": failures[:50],
    }
    (artifact_path("graph_rag_package_v0_5_validation_report.json")).write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
