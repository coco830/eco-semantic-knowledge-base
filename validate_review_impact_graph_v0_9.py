import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FINAL_STATE = "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"
RUNTIME_INTEGRATION = "disabled"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path):
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def parse_json(value):
    if not value:
        return []
    return json.loads(value)


def fail(failures, file, reason, row_id=""):
    failures.append({"file": file, "reason": reason, "row_id": row_id})


def main():
    failures = []
    required = [
        "graph_query_playbook_v0_9.md",
        "graph_query_playbook_v0_9.json",
        "review_impact_analysis_v0_9.csv",
        "review_impact_analysis_v0_9.json",
        "review_impact_graph_edges_v0_9.jsonl",
        "graph_visualization_samples_v0_9.md",
        "graph_visualization_samples_v0_9.json",
        "build_review_impact_graph_v0_9.py",
        "validate_review_impact_graph_v0_9.py",
        "FINAL_COMPLETION_REPORT_v0_9.md",
        "knowledge_base_manifest_v0_9.json",
    ]
    for name in required:
        if not (ROOT / name).exists():
            fail(failures, name, "missing_required_output")

    overlays = read_json(ROOT / "human_review_overlay_v0_8.json")
    impact = read_csv(ROOT / "review_impact_analysis_v0_9.csv")
    impact_json = read_json(ROOT / "review_impact_analysis_v0_9.json")
    edges = read_jsonl(ROOT / "review_impact_graph_edges_v0_9.jsonl")
    playbook = read_json(ROOT / "graph_query_playbook_v0_9.json")
    manifest = read_json(ROOT / "knowledge_base_manifest_v0_9.json")
    overlay_relations = {o["candidate_relation_id"] for o in overlays}
    impact_relations = {r["candidate_relation_id"] for r in impact}
    if overlay_relations != impact_relations or len(impact_json) != len(impact):
        fail(failures, "review_impact_analysis_v0_9.csv", "overlay_impact_mismatch")

    required_edge_types = {
        "REVIEW_OVERLAY_AFFECTS_RELATION",
        "RELATION_AFFECTS_SCENARIO",
        "SCENARIO_AFFECTS_SCORE13",
        "SCENARIO_AFFECTS_INSPECTION",
    }
    edge_types = {e["edge_type"] for e in edges}
    for edge_type in required_edge_types:
        if edge_type not in edge_types:
            fail(failures, "review_impact_graph_edges_v0_9.jsonl", "missing_edge_type", edge_type)

    for row in impact:
        row_id = row["impact_id"]
        if row.get("final_state") != FINAL_STATE or row.get("runtime_status") != "DRAFT_NOT_FOR_RUNTIME":
            fail(failures, "review_impact_analysis_v0_9.csv", "bad_boundary", row_id)
        if not parse_json(row["scenario_ids"]):
            fail(failures, "review_impact_analysis_v0_9.csv", "missing_scenario_ids", row_id)
        if not parse_json(row["media_types"]):
            fail(failures, "review_impact_analysis_v0_9.csv", "missing_media_types", row_id)
        if not parse_json(row["subscenario_tags"]):
            fail(failures, "review_impact_analysis_v0_9.csv", "missing_subscenario_tags", row_id)
        if row["requires_second_approval"] != "true" or row["runtime_effect"] != "NO_RUNTIME_EFFECT":
            fail(failures, "review_impact_analysis_v0_9.csv", "bad_runtime_effect", row_id)
        if "不代表企业现场事实已确认适用" not in row.get("impact_scope_note", ""):
            fail(failures, "review_impact_analysis_v0_9.csv", "missing_impact_scope_note", row_id)

    for edge in edges:
        if edge.get("final_state") != FINAL_STATE or edge.get("runtime_integration") != RUNTIME_INTEGRATION:
            fail(failures, "review_impact_graph_edges_v0_9.jsonl", "bad_edge_boundary", edge.get("edge_id", ""))
        if edge.get("runtime_effect") != "NO_RUNTIME_EFFECT":
            fail(failures, "review_impact_graph_edges_v0_9.jsonl", "bad_edge_runtime_effect", edge.get("edge_id", ""))
        if "不代表企业现场事实已确认适用" not in edge.get("properties", {}).get("impact_scope_note", ""):
            fail(failures, "review_impact_graph_edges_v0_9.jsonl", "missing_edge_impact_scope_note", edge.get("edge_id", ""))

    visual_md = (ROOT / "graph_visualization_samples_v0_9.md").read_text(encoding="utf-8")
    for phrase in ["mermaid", FINAL_STATE, "Entry 108", "CONFIRM_NOT_APPLY", "NEED_SITE_CONFIRM", "不代表企业现场事实已确认适用"]:
        if phrase not in visual_md:
            fail(failures, "graph_visualization_samples_v0_9.md", "missing_visual_phrase", phrase)

    if manifest.get("final_state") != FINAL_STATE or manifest.get("runtime_integration") != RUNTIME_INTEGRATION:
        fail(failures, "knowledge_base_manifest_v0_9.json", "bad_manifest_boundary")
    if len(playbook.get("query_patterns", [])) < 3:
        fail(failures, "graph_query_playbook_v0_9.json", "too_few_query_patterns")

    report = {
        "validation_status": "PASS" if not failures else "FAIL",
        "final_state": FINAL_STATE,
        "failure_count": len(failures),
        "impact_rows": len(impact),
        "impact_edges": len(edges),
        "edge_type_counts": {edge_type: sum(1 for e in edges if e["edge_type"] == edge_type) for edge_type in sorted(edge_types)},
        "failure_samples": failures[:50],
    }
    (ROOT / "review_impact_graph_v0_9_validation_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (ROOT / "review_impact_graph_v0_9_failure_list.json").write_text(
        json.dumps(failures, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
