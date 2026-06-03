import csv
import gzip
import hashlib
import json
from collections import Counter

from kb_paths import artifact_path


VERSION = "v8.6-pollutant-standard-link-map-and-graph-v0.6"
FINAL_STATE = "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"
RUNTIME_STATUS = "DRAFT_NOT_FOR_RUNTIME"
RUNTIME_INTEGRATION = "disabled"
EXPECTED_SOURCE_COUNT = 209
EXPECTED_SCENARIO_COUNT = 28

BLOCKING_CONTENT_FLAGS = {
    "OCR_REQUIRED_BEFORE_CLAUSE_OR_NUMERIC_ADOPTION",
    "SMALL_FILE_REVIEW_REQUIRED_POSSIBLE_TRUNCATION_OR_EXCERPT",
}
RECOVERY_UNBLOCK_ACTIONS = {"CONFIRMED_UNBLOCK_CURRENT_STANDARD"}
RECOVERY_EXCLUDED_ACTIONS = {
    "OBSOLETE_EXCLUDE_REPLACEMENT_GOVERNANCE",
    "OBSOLETE_EXCLUDE_NO_ACTIVE_REPLACEMENT",
}
ACTIVE_REPLACEMENT_STATUSES = {"CURRENT", "FUTURE_EFFECTIVE"}
DEEP_TARGET_KINDS = {"SCENARIO", "INDUSTRY", "SCORE13"}
REVIEW_ACCEPT_GATE_STATUS = "HUMAN_REVIEW_ACCEPTED"
REVIEW_REJECT_GATE_STATUS = "HUMAN_REVIEW_REJECTED"
SOURCE_RECOVERY_GATE_STATUS = "SOURCE_RECOVERY_CONFIRMED"
RADIATION_ALLOWED_SCENARIOS = {
    "SCN_RADIATION_DEVICE_SOURCE_SAFETY",
    "SCN_RAD_WASTE_PACKAGE_SOLIDIFICATION_CONTAINER",
    "SCN_RAD_WASTE_DISPOSAL_FACILITY",
    "SCN_RADIOACTIVE_SOURCE_SECURITY",
    "SCN_RADIOACTIVE_WASTE_STORAGE_TRANSFER_DISPOSAL",
    "SCN_RADIOACTIVE_MATERIAL_TRANSPORT",
    "SCN_NORM_RADIOACTIVITY_IN_INDUSTRIAL_RESIDUE",
    "SCN_URANIUM_THORIUM_MINING_RAD_WASTE",
    "SCN_NUCLEAR_FUEL_EFFLUENT_DECOMMISSIONING",
    "SCN_BUILDING_MATERIAL_SLAG_RADIONUCLIDE",
}


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path):
    rows = []
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def sha256_file(path):
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def fail(failures, file, reason, row_id=""):
    failures.append({"file": file, "reason": reason, "row_id": row_id})


def require_lf_only(failures, name, path):
    if b"\r\n" in path.read_bytes():
        fail(failures, name, "crlf_detected")


def check_boundary(failures, item, file, row_id):
    if item.get("runtime_status") != RUNTIME_STATUS:
        fail(failures, file, "bad_runtime_status", row_id)
    if item.get("final_state") != FINAL_STATE:
        fail(failures, file, "bad_final_state", row_id)
    if item.get("runtime_integration") != RUNTIME_INTEGRATION:
        fail(failures, file, "bad_runtime_integration", row_id)
    if item.get("candidate_only") not in {True, "TRUE", "true"}:
        fail(failures, file, "candidate_only_not_true", row_id)
    if "runtime_integration\":\"enabled" in json.dumps(item, ensure_ascii=False):
        fail(failures, file, "forbidden_runtime_token", row_id)


def main():
    failures = []
    paths = {
        "pollutant_standard_link_map_v8_6.csv": artifact_path("pollutant_standard_link_map_v8_6.csv"),
        "pollutant_standard_link_review_overlay_v8_6.csv": artifact_path("pollutant_standard_link_review_overlay_v8_6.csv"),
        "pollutant_standard_link_review_overlay_v8_6.json": artifact_path("pollutant_standard_link_review_overlay_v8_6.json"),
        "pollutant_standard_source_recovery_v8_7.csv": artifact_path("pollutant_standard_source_recovery_v8_7.csv"),
        "graph_nodes_v0_6.jsonl": artifact_path("graph_nodes_v0_6.jsonl"),
        "graph_edges_v0_6.jsonl.gz": artifact_path("graph_edges_v0_6.jsonl.gz"),
        "pollutant_standard_link_map_v8_6.md": artifact_path("pollutant_standard_link_map_v8_6.md"),
        "pollutant_standard_link_graph_manifest_v8_6.json": artifact_path("pollutant_standard_link_graph_manifest_v8_6.json"),
        "pollutant_standard_link_review_overlay_v8_6_report.json": artifact_path("pollutant_standard_link_review_overlay_v8_6_report.json"),
        "FINAL_POLLUTANT_STANDARD_LINK_GRAPH_v8_6.md": artifact_path("FINAL_POLLUTANT_STANDARD_LINK_GRAPH_v8_6.md"),
        "build_pollutant_standard_link_v8_6.py": artifact_path("build_pollutant_standard_link_v8_6.py"),
        "validate_pollutant_standard_link_v8_6.py": artifact_path("validate_pollutant_standard_link_v8_6.py"),
    }
    for name, path in paths.items():
        if not path.exists():
            fail(failures, name, "missing_required_output")

    baseline = read_csv(artifact_path("pollutant_domain_approved_baseline_v8_5.csv"))
    scenarios = read_json(artifact_path("approved_scenario_templates_v1_0.json"))
    industries = [row for row in read_csv(artifact_path("industry_catalog_base.csv")) if row.get("level") == "class"]
    links = read_csv(paths["pollutant_standard_link_map_v8_6.csv"])
    review_overlay = read_csv(paths["pollutant_standard_link_review_overlay_v8_6.csv"])
    review_overlay_json = read_json(paths["pollutant_standard_link_review_overlay_v8_6.json"])
    source_recovery = read_csv(paths["pollutant_standard_source_recovery_v8_7.csv"])
    nodes = read_jsonl(paths["graph_nodes_v0_6.jsonl"])
    edges = read_jsonl(paths["graph_edges_v0_6.jsonl.gz"])
    manifest = read_json(paths["pollutant_standard_link_graph_manifest_v8_6.json"])

    for name, path in paths.items():
        if path.exists() and path.suffix in {".csv", ".json", ".jsonl", ".md"}:
            require_lf_only(failures, name, path)

    source_ids = {row["source_id"] for row in baseline}
    scenario_ids = {row["scenario_id"] for row in scenarios}
    industry_codes = {row["class_code"] for row in industries}
    score_ids = {f"S{i:02d}" for i in range(1, 14)}
    recovery_by_source = {row["source_id"]: row for row in source_recovery}
    unblocked_sources = {row["source_id"] for row in source_recovery if row.get("recovery_action") in RECOVERY_UNBLOCK_ACTIONS}
    obsolete_sources = {row["source_id"] for row in source_recovery if row.get("recovery_action") in RECOVERY_EXCLUDED_ACTIONS}
    active_replacement_standards = {
        row["replacement_standard_no"]
        for row in source_recovery
        if row.get("recovery_action") == "OBSOLETE_EXCLUDE_REPLACEMENT_GOVERNANCE"
        and row.get("replacement_standard_no")
        and row.get("replacement_lifecycle_status") in ACTIVE_REPLACEMENT_STATUSES
    }
    blocked_sources = {
        row["source_id"]
        for row in baseline
        if row.get("content_usability_flag") in BLOCKING_CONTENT_FLAGS
        and row["source_id"] not in unblocked_sources
        and row["source_id"] not in obsolete_sources
    }
    expected_active_standard_count = EXPECTED_SOURCE_COUNT - len(obsolete_sources)

    if len(source_ids) != EXPECTED_SOURCE_COUNT:
        fail(failures, "pollutant_domain_approved_baseline_v8_5.csv", "source_count_mismatch", str(len(source_ids)))
    if len(scenario_ids) != EXPECTED_SCENARIO_COUNT:
        fail(failures, "approved_scenario_templates_v1_0.json", "scenario_count_mismatch", str(len(scenario_ids)))
    if len({row["link_id"] for row in links}) != len(links):
        fail(failures, "pollutant_standard_link_map_v8_6.csv", "duplicate_link_id")
    if {row["source_id"] for row in links} != source_ids:
        fail(failures, "pollutant_standard_link_map_v8_6.csv", "source_coverage_mismatch")
    if set(recovery_by_source) != (unblocked_sources | obsolete_sources):
        fail(failures, "pollutant_standard_source_recovery_v8_7.csv", "bad_recovery_source_partition")

    deep_links = [row for row in links if row["target_kind"] in DEEP_TARGET_KINDS]
    review_required_deep_links = [row for row in deep_links if row["source_id"] not in unblocked_sources]
    source_recovery_deep_links = [row for row in deep_links if row["source_id"] in unblocked_sources]
    overlay_link_ids = [row["link_id"] for row in review_overlay]
    overlay_review_ids = [row["review_item_id"] for row in review_overlay]
    if len(overlay_link_ids) != len(set(overlay_link_ids)):
        fail(failures, "pollutant_standard_link_review_overlay_v8_6.csv", "duplicate_link_id")
    if len(overlay_review_ids) != len(set(overlay_review_ids)):
        fail(failures, "pollutant_standard_link_review_overlay_v8_6.csv", "duplicate_review_item_id")
    if {row["link_id"] for row in review_overlay} != {row["link_id"] for row in review_required_deep_links}:
        fail(failures, "pollutant_standard_link_review_overlay_v8_6.csv", "review_overlay_deep_link_coverage_mismatch")
    if len(review_overlay_json) != len(review_overlay):
        fail(failures, "pollutant_standard_link_review_overlay_v8_6.json", "row_count_mismatch")

    overlay_by_link = {row["link_id"]: row for row in review_overlay}
    for row in review_overlay:
        row_id = row.get("overlay_id", "")
        check_boundary(failures, row, "pollutant_standard_link_review_overlay_v8_6.csv", row_id)
        if row.get("decision") not in {"ACCEPT", "REJECT"}:
            fail(failures, "pollutant_standard_link_review_overlay_v8_6.csv", "bad_decision", row_id)
        if row.get("review_item_id") != f"RVQ86::{row.get('link_id')}":
            fail(failures, "pollutant_standard_link_review_overlay_v8_6.csv", "bad_review_item_id", row_id)
        if row.get("runtime_effect") != "NO_RUNTIME_EFFECT":
            fail(failures, "pollutant_standard_link_review_overlay_v8_6.csv", "bad_runtime_effect", row_id)

    for row in source_recovery:
        row_id = row.get("source_id", "")
        if row.get("recovery_action") not in RECOVERY_UNBLOCK_ACTIONS | RECOVERY_EXCLUDED_ACTIONS:
            fail(failures, "pollutant_standard_source_recovery_v8_7.csv", "bad_recovery_action", row_id)
        if row.get("recovery_action") in RECOVERY_UNBLOCK_ACTIONS and row.get("standard_lifecycle_status") != "CURRENT":
            fail(failures, "pollutant_standard_source_recovery_v8_7.csv", "unblock_not_current", row_id)
        if row.get("recovery_action") in RECOVERY_EXCLUDED_ACTIONS and not row.get("standard_lifecycle_status", "").startswith("OBSOLETE"):
            fail(failures, "pollutant_standard_source_recovery_v8_7.csv", "excluded_not_obsolete", row_id)
        if row.get("recovery_action") in RECOVERY_UNBLOCK_ACTIONS and row.get("graph_policy") != "ALLOW_DEEP_CANDIDATE_LINKS":
            fail(failures, "pollutant_standard_source_recovery_v8_7.csv", "bad_unblock_graph_policy", row_id)

    domain_links = Counter(row["source_id"] for row in links if row["target_kind"] == "DOMAIN")
    for source_id in source_ids:
        expected_domain_count = 0 if source_id in obsolete_sources else 1
        if domain_links[source_id] != expected_domain_count:
            fail(failures, "pollutant_standard_link_map_v8_6.csv", "missing_or_duplicate_domain_link", source_id)

    for row in links:
        row_id = row.get("link_id", "")
        check_boundary(failures, row, "pollutant_standard_link_map_v8_6.csv", row_id)
        if row["source_id"] in obsolete_sources and row["target_kind"] != "STANDARD_LIFECYCLE":
            fail(failures, "pollutant_standard_link_map_v8_6.csv", "obsolete_source_has_non_lifecycle_link", row_id)
        if row["target_kind"] in DEEP_TARGET_KINDS and row["source_id"] in unblocked_sources:
            if row.get("human_review_label") != SOURCE_RECOVERY_GATE_STATUS:
                fail(failures, "pollutant_standard_link_map_v8_6.csv", "source_recovery_label_mismatch", row_id)
            if row.get("gate_status") != SOURCE_RECOVERY_GATE_STATUS:
                fail(failures, "pollutant_standard_link_map_v8_6.csv", "source_recovery_gate_status_mismatch", row_id)
        elif row["target_kind"] in DEEP_TARGET_KINDS:
            review_row = overlay_by_link[row["link_id"]]
            expected_label = "CONFIRM_LINK" if review_row["decision"] == "ACCEPT" else "REJECT_CANDIDATE"
            expected_gate = REVIEW_ACCEPT_GATE_STATUS if review_row["decision"] == "ACCEPT" else REVIEW_REJECT_GATE_STATUS
            if row.get("human_review_label") != expected_label:
                fail(failures, "pollutant_standard_link_map_v8_6.csv", "human_review_label_mismatch", row_id)
            if row.get("gate_status") != expected_gate:
                fail(failures, "pollutant_standard_link_map_v8_6.csv", "human_review_gate_status_mismatch", row_id)
        elif row.get("human_review_label"):
            fail(failures, "pollutant_standard_link_map_v8_6.csv", "unexpected_human_review_label", row_id)
        if row["target_kind"] == "SCENARIO" and row["target_id"] not in scenario_ids:
            fail(failures, "pollutant_standard_link_map_v8_6.csv", "unknown_scenario_id", row_id)
        if row["target_kind"] == "INDUSTRY" and row["target_id"] not in industry_codes:
            fail(failures, "pollutant_standard_link_map_v8_6.csv", "unknown_industry_code", row_id)
        if row["target_kind"] == "SCORE13" and row["target_id"] not in score_ids:
            fail(failures, "pollutant_standard_link_map_v8_6.csv", "unknown_score13_id", row_id)
        if row["source_id"] in blocked_sources and row["target_kind"] in DEEP_TARGET_KINDS:
            fail(failures, "pollutant_standard_link_map_v8_6.csv", "blocked_source_has_deep_link", row_id)
        if row["domain"] == "radiation":
            if row.get("radiation_all_industry_default_blocked") != "TRUE":
                fail(failures, "pollutant_standard_link_map_v8_6.csv", "radiation_not_blocked", row_id)
            if row["target_kind"] == "SCENARIO" and row["target_id"] not in RADIATION_ALLOWED_SCENARIOS:
                fail(failures, "pollutant_standard_link_map_v8_6.csv", "radiation_generic_scenario_link", row_id)

    node_ids = [row["node_id"] for row in nodes]
    edge_ids = [row["edge_id"] for row in edges]
    if len(node_ids) != len(set(node_ids)):
        fail(failures, "graph_nodes_v0_6.jsonl", "duplicate_node_id")
    if len(edge_ids) != len(set(edge_ids)):
        fail(failures, "graph_edges_v0_6.jsonl.gz", "duplicate_edge_id")

    node_set = set(node_ids)
    node_type_counts = Counter(row["node_type"] for row in nodes)
    edge_type_counts = Counter(row["edge_type"] for row in edges)
    if node_type_counts["ScenarioTemplate"] != EXPECTED_SCENARIO_COUNT:
        fail(failures, "graph_nodes_v0_6.jsonl", "scenario_node_count_mismatch", str(node_type_counts["ScenarioTemplate"]))
    if node_type_counts["PollutantStandardSource"] != expected_active_standard_count:
        fail(failures, "graph_nodes_v0_6.jsonl", "standard_node_count_mismatch", str(node_type_counts["PollutantStandardSource"]))
    if node_type_counts["ReplacementStandardCandidate"] != len(active_replacement_standards):
        fail(failures, "graph_nodes_v0_6.jsonl", "replacement_standard_node_count_mismatch", str(node_type_counts["ReplacementStandardCandidate"]))
    for source_id in obsolete_sources:
        if f"standard:{source_id}" in node_set:
            fail(failures, "graph_nodes_v0_6.jsonl", "obsolete_source_has_standard_node", source_id)

    for row in nodes:
        check_boundary(failures, row, "graph_nodes_v0_6.jsonl", row.get("node_id", ""))
    for row in edges:
        check_boundary(failures, row, "graph_edges_v0_6.jsonl.gz", row.get("edge_id", ""))
        if row["from_node_id"] not in node_set or row["to_node_id"] not in node_set:
            fail(failures, "graph_edges_v0_6.jsonl.gz", "orphan_edge_endpoint", row["edge_id"])
        if row["edge_type"] == "STANDARD_GOVERNS_SCENARIO":
            props = row.get("properties", {})
            if props.get("domain") == "radiation" and props.get("target_id") not in RADIATION_ALLOWED_SCENARIOS:
                fail(failures, "graph_edges_v0_6.jsonl.gz", "radiation_generic_graph_edge", row["edge_id"])

    for edge_type in ["STANDARD_IN_DOMAIN", "STANDARD_GOVERNS_SCENARIO", "STANDARD_APPLIES_TO_INDUSTRY", "STANDARD_SUPPORTS_SCORE13"]:
        if edge_type_counts[edge_type] == 0:
            fail(failures, "graph_edges_v0_6.jsonl.gz", "missing_edge_type", edge_type)
    if active_replacement_standards and edge_type_counts["REPLACEMENT_STANDARD_IN_DOMAIN"] != len(active_replacement_standards):
        fail(failures, "graph_edges_v0_6.jsonl.gz", "replacement_standard_edge_count_mismatch", str(edge_type_counts["REPLACEMENT_STANDARD_IN_DOMAIN"]))

    edge_id_set = set(edge_ids)
    for row in links:
        if row["target_kind"] in {"SOURCE_REVIEW", "STANDARD_LIFECYCLE"}:
            continue
        expected_edge_id = f"edge:v8_6:{row['link_id']}"
        if row["target_kind"] in DEEP_TARGET_KINDS and row.get("human_review_label") == "REJECT_CANDIDATE":
            if expected_edge_id in edge_id_set:
                fail(failures, "graph_edges_v0_6.jsonl.gz", "rejected_review_link_has_graph_edge", row["link_id"])
        elif expected_edge_id not in edge_id_set:
            fail(failures, "graph_edges_v0_6.jsonl.gz", "accepted_or_domain_link_missing_graph_edge", row["link_id"])

    if manifest.get("knowledge_base_version") != VERSION:
        fail(failures, "pollutant_standard_link_graph_manifest_v8_6.json", "bad_version")
    if manifest.get("final_state") != FINAL_STATE or manifest.get("runtime_integration") != RUNTIME_INTEGRATION:
        fail(failures, "pollutant_standard_link_graph_manifest_v8_6.json", "bad_boundary")
    for key, path_name in {
        "link_csv": "pollutant_standard_link_map_v8_6.csv",
        "graph_nodes": "graph_nodes_v0_6.jsonl",
        "graph_edges": "graph_edges_v0_6.jsonl.gz",
        "design_md": "pollutant_standard_link_map_v8_6.md",
        "report_md": "FINAL_POLLUTANT_STANDARD_LINK_GRAPH_v8_6.md",
        "review_overlay_csv": "pollutant_standard_link_review_overlay_v8_6.csv",
        "review_overlay_json": "pollutant_standard_link_review_overlay_v8_6.json",
        "source_recovery_csv": "pollutant_standard_source_recovery_v8_7.csv",
    }.items():
        if manifest.get("outputs", {}).get(key, {}).get("sha256") != sha256_file(paths[path_name]):
            fail(failures, "pollutant_standard_link_graph_manifest_v8_6.json", f"{key}_sha256_mismatch")

    report = {
        "validation_status": "PASS" if not failures else "FAIL",
        "failure_count": len(failures),
        "knowledge_base_version": VERSION,
        "final_state": FINAL_STATE,
        "runtime_status": RUNTIME_STATUS,
        "runtime_integration": RUNTIME_INTEGRATION,
        "counts": {
            "source_count": len(source_ids),
            "link_count": len(links),
            "node_type_counts": dict(sorted(node_type_counts.items())),
            "edge_type_counts": dict(sorted(edge_type_counts.items())),
            "link_target_kind_counts": dict(sorted(Counter(row["target_kind"] for row in links).items())),
            "blocked_source_count": len(blocked_sources),
            "source_recovery_count": len(source_recovery),
            "source_recovery_deep_link_count": len(source_recovery_deep_links),
            "obsolete_excluded_source_count": len(obsolete_sources),
            "active_replacement_standard_count": len(active_replacement_standards),
            "review_decision_counts": dict(sorted(Counter(row["decision"] for row in review_overlay).items())),
            "accepted_deep_link_count": sum(1 for row in deep_links if row.get("human_review_label") == "CONFIRM_LINK"),
            "rejected_deep_link_count": sum(1 for row in deep_links if row.get("human_review_label") == "REJECT_CANDIDATE"),
        },
        "failure_samples": failures[:50],
    }
    artifact_path("pollutant_standard_link_graph_gate_report_v8_6.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
