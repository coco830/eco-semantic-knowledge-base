import json
from collections import Counter
from pathlib import Path


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


def main():
    failures = []
    required = [
        "rag_graph_eval_spec_v0_6.md",
        "build_rag_graph_eval_v0_6.py",
        "validate_rag_graph_eval_v0_6.py",
        "retrieval_eval_set_v0_6.jsonl",
        "graph_query_samples_v0_6.jsonl",
        "rag_graph_eval_coverage_v0_6.json",
        "FINAL_COMPLETION_REPORT_v0_6.md",
    ]
    for name in required:
        if not (ROOT / name).exists():
            fail(failures, name, "missing_required_output")

    nodes = read_jsonl(ROOT / "graph_nodes_v0_5.jsonl")
    chunks = read_jsonl(ROOT / "rag_chunks_v0_5.jsonl")
    evals = read_jsonl(ROOT / "retrieval_eval_set_v0_6.jsonl")
    samples = read_jsonl(ROOT / "graph_query_samples_v0_6.jsonl")
    coverage = read_json(ROOT / "rag_graph_eval_coverage_v0_6.json")
    node_ids = {n["node_id"] for n in nodes}
    chunk_types = {c["chunk_type"] for c in chunks}

    if len(evals) < 20:
        fail(failures, "retrieval_eval_set_v0_6.jsonl", "eval_count_below_20")
    if len(samples) < 8:
        fail(failures, "graph_query_samples_v0_6.jsonl", "query_sample_count_below_8")

    required_categories = {
        "industry_code", "permit_catalog", "negative_condition", "general_process",
        "score13", "inspection_evidence", "open_question_trace", "runtime_boundary",
        "permit_type_boundary", "division_context", "not_apply_evidence",
        "risk_trace", "rag_boundary", "scenario_template", "solid_waste", "emergency",
    }
    categories = {e.get("eval_category") for e in evals}
    for category in required_categories - categories:
        fail(failures, "retrieval_eval_set_v0_6.jsonl", "missing_eval_category", category)

    for item in evals:
        row_id = item.get("eval_id", "")
        if item.get("final_state") != FINAL_STATE or item.get("runtime_status") != "DRAFT_NOT_FOR_RUNTIME":
            fail(failures, "retrieval_eval_set_v0_6.jsonl", "bad_boundary", row_id)
        if item.get("must_include_boundary_notice") is not True or item.get("must_not_claim_runtime_ready") is not True:
            fail(failures, "retrieval_eval_set_v0_6.jsonl", "missing_boundary_assertion", row_id)
        if FINAL_STATE not in item.get("expected_answer_contains", []):
            fail(failures, "retrieval_eval_set_v0_6.jsonl", "expected_answer_missing_final_state", row_id)
        if not item.get("open_question_refs") and item["eval_category"] in {"runtime_boundary", "permit_type_boundary", "division_context", "negative_condition"}:
            fail(failures, "retrieval_eval_set_v0_6.jsonl", "missing_open_question_refs", row_id)
        for nid in item.get("expected_node_ids", []):
            if nid not in node_ids:
                fail(failures, "retrieval_eval_set_v0_6.jsonl", "missing_expected_node", f"{row_id}:{nid}")
        for chunk_type in item.get("expected_chunk_types", []):
            if chunk_type not in chunk_types:
                fail(failures, "retrieval_eval_set_v0_6.jsonl", "missing_expected_chunk_type", f"{row_id}:{chunk_type}")

    for sample in samples:
        row_id = sample.get("sample_id", "")
        if sample.get("final_state") != FINAL_STATE or sample.get("runtime_status") != "DRAFT_NOT_FOR_RUNTIME":
            fail(failures, "graph_query_samples_v0_6.jsonl", "bad_boundary", row_id)
        if sample.get("query_intent") != "candidate_knowledge_exploration_not_runtime_decision":
            fail(failures, "graph_query_samples_v0_6.jsonl", "bad_query_intent", row_id)
        for nid in sample.get("start_node_ids", []):
            if nid not in node_ids:
                fail(failures, "graph_query_samples_v0_6.jsonl", "missing_start_node", f"{row_id}:{nid}")

    if coverage.get("final_state") != FINAL_STATE or coverage.get("runtime_integration") != "disabled":
        fail(failures, "rag_graph_eval_coverage_v0_6.json", "bad_coverage_boundary")
    if coverage.get("precheck_missing_nodes") or coverage.get("precheck_missing_chunk_types"):
        fail(failures, "rag_graph_eval_coverage_v0_6.json", "precheck_missing_refs")

    report = {
        "validation_status": "PASS" if not failures else "FAIL",
        "final_state": FINAL_STATE,
        "failure_count": len(failures),
        "eval_count": len(evals),
        "query_sample_count": len(samples),
        "eval_category_counts": dict(sorted(Counter(e["eval_category"] for e in evals).items())),
        "failure_samples": failures[:50],
    }
    (ROOT / "rag_graph_eval_v0_6_validation_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (ROOT / "rag_graph_eval_v0_6_failure_list.json").write_text(
        json.dumps(failures, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
