import csv
import gzip
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from kb_paths import artifact_path


ROOT = Path(__file__).resolve().parent
VERSION = "v8.6-pollutant-standard-link-map-and-graph-v0.6"
FINAL_STATE = "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"
RUNTIME_STATUS = "DRAFT_NOT_FOR_RUNTIME"
RUNTIME_INTEGRATION = "disabled"

BASELINE = artifact_path("pollutant_domain_approved_baseline_v8_5.csv")
SCENARIOS = artifact_path("approved_scenario_templates_v1_0.json")
INDUSTRY_CATALOG = artifact_path("industry_catalog_base.csv")
GRAPH_NODES_V05 = artifact_path("graph_nodes_v0_5.jsonl")
GRAPH_EDGES_V05 = artifact_path("graph_edges_v0_5.jsonl")
GRAPH_EDGES_V05_GZ = artifact_path("graph_edges_v0_5.jsonl.gz")

OUT_LINKS = artifact_path("pollutant_standard_link_map_v8_6.csv")
OUT_NODES = artifact_path("graph_nodes_v0_6.jsonl")
OUT_EDGES = ROOT / "data" / "graph_rag" / "graph_edges_v0_6.jsonl.gz"
OUT_DESIGN = artifact_path("pollutant_standard_link_map_v8_6.md")
OUT_MANIFEST = artifact_path("pollutant_standard_link_graph_manifest_v8_6.json")
OUT_REPORT = artifact_path("FINAL_POLLUTANT_STANDARD_LINK_GRAPH_v8_6.md")

BLOCKING_CONTENT_FLAGS = {
    "OCR_REQUIRED_BEFORE_CLAUSE_OR_NUMERIC_ADOPTION",
    "SMALL_FILE_REVIEW_REQUIRED_POSSIBLE_TRUNCATION_OR_EXCERPT",
}

SCORE13_NAMES = {
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

ROLE_RULES = {
    "EMISSION_STANDARD_SOURCE": ("STANDARD_SETS_EMISSION_LIMIT", ["S10"]),
    "TREATMENT_TECHNICAL_SPEC_SOURCE": ("STANDARD_SPECIFIES_TREATMENT", ["S06"]),
    "HAZARDOUS_WASTE_MANAGEMENT_SOURCE": ("STANDARD_GOVERNS_HAZWASTE", ["S07"]),
    "RADIATION_SAFETY_SOURCE": ("STANDARD_GOVERNS_RADIATION", ["S12"]),
    "MONITORING_REQUIREMENT_SOURCE": ("STANDARD_REQUIRES_MONITORING", ["S10"]),
    "PERMIT_APPLICATION_AND_LEDGER_EVIDENCE_SOURCE": ("STANDARD_SUPPORTS_PERMIT_LEDGER", ["S01", "S02"]),
    "SUPPORTING_REGULATION_SOURCE": ("STANDARD_REFERENCE_CONTEXT", []),
    "POLLUTANT_DOMAIN_REFERENCE_SOURCE": ("STANDARD_REFERENCE_CONTEXT", []),
}

DOMAIN_SCENARIO_SEEDS = {
    "water": ["SCN_WW_PROCESS_AND_TREATMENT", "NEW_SCN_WASTE_DISPOSAL_CANDIDATE", "NEW_SCN_TAILINGS_CANDIDATE"],
    "air": ["SCN_VOCS_SOLVENT_AND_TREATMENT", "SCN_DUST_PARTICULATE_CONTROL", "SCN_GAS_STATION_VAPOR_UST"],
    "noise": [
        "SCN_NOISE_SOURCE_BOUNDARY_CONTROL",
        "SCN_NOISE_BOUNDARY_MONITORING_LEDGER",
        "SCN_NOISE_SENSITIVE_RECEPTOR_NIGHT_OPERATION",
        "SCN_SOCIAL_LIFE_NOISE_SOURCE",
    ],
    "solid_waste": ["NEW_SCN_LAB_WASTE_CANDIDATE", "SCN_BASE_PRODUCTION_SOLID_NOISE_LEDGER"],
    "hazardous_waste": ["SCN_HAZWASTE_STORAGE_TRANSFER"],
    "special_industry": ["SCN_BASE_PRODUCTION_SOLID_NOISE_LEDGER"],
    "general_environmental_engineering": ["SCN_TRAINING_SIGNAGE_REVIEW_GAP"],
}

LINK_FIELDS = [
    "link_id",
    "baseline_entry_id",
    "source_id",
    "source_doc_title",
    "source_standard_no_canonical",
    "domain",
    "source_role",
    "link_type",
    "target_kind",
    "target_id",
    "target_label",
    "mapping_method",
    "mapping_confidence",
    "evidence_text",
    "content_usability_flag",
    "content_gate_status",
    "human_review_label",
    "gate_status",
    "runtime_status",
    "final_state",
    "runtime_integration",
    "candidate_only",
    "radiation_all_industry_default_blocked",
    "source_hash",
]


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path, gz_path=None):
    source = path
    opener = open
    if not source.exists() and gz_path and gz_path.exists():
        source = gz_path
        opener = gzip.open
    rows = []
    with opener(source, "rt", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_json_lf(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    tmp.replace(path)


def write_text_lf(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")
    tmp.replace(path)


def write_csv_lf(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    with tmp.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=LINK_FIELDS, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    tmp.replace(path)


def write_jsonl_lf(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    tmp.replace(path)


def write_jsonl_gz(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    with gzip.open(tmp, "wt", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    tmp.replace(path)


def sha256_file(path):
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def safe_id(value):
    return re.sub(r"[^0-9A-Za-z_\-]+", "_", str(value)).strip("_")


def content_gate(row):
    return "BLOCKED_PENDING_OCR" if row.get("content_usability_flag") in BLOCKING_CONTENT_FLAGS else "TITLE_LEVEL_LINK_ONLY"


def normalize_zh(value):
    value = re.sub(r"（.*?）|\(.*?\)|[\s,，、/—\-一]+", "", value or "")
    for token in ["污染物排放标准", "排放标准", "治理工程技术规范", "工程技术规范", "排污许可证申请与核发技术规范", "技术规范", "行业", "工业", "制造业", "制造", "加工工业", "加工", "产品", "污染控制"]:
        value = value.replace(token, "")
    return value


def industry_index(industries):
    result = []
    for row in industries:
        if row.get("level") != "class":
            continue
        keys = {normalize_zh(row.get("class_name", "")), normalize_zh(row.get("group_name", ""))}
        keys |= {normalize_zh(token) for token in re.split(r"[和及与、，,的]+", row.get("class_name", ""))}
        keys = {key for key in keys if len(key) >= 3}
        result.append((row, keys))
    return result


def match_industries(title, index):
    normalized = normalize_zh(title)
    matches = []
    seen = set()
    for industry, keys in index:
        if any(key in normalized or normalized in key for key in keys):
            code = industry["class_code"]
            if code not in seen:
                matches.append(industry)
                seen.add(code)
    return sorted(matches, key=lambda item: (item["class_code"], item["class_name"]))[:12]


def radiation_scenarios_for(title):
    rules = [
        (r"运输|放射性物品", ["SCN_RADIOACTIVE_MATERIAL_TRANSPORT"]),
        (r"铀|钍|矿冶|铀矿", ["SCN_URANIUM_THORIUM_MINING_RAD_WASTE"]),
        (r"核动力|核设施|核燃料|核热|流出物|退役", ["SCN_NUCLEAR_FUEL_EFFLUENT_DECOMMISSIONING"]),
        (r"建材|炉渣|建筑材料", ["SCN_BUILDING_MATERIAL_SLAG_RADIONUCLIDE"]),
        (r"伴生|NORM|工业残渣|放射性物料", ["SCN_NORM_RADIOACTIVITY_IN_INDUSTRIAL_RESIDUE"]),
        (r"固体废物包|固化体|包装", ["SCN_RAD_WASTE_PACKAGE_SOLIDIFICATION_CONTAINER"]),
        (r"处置|填埋|近地表|岩洞", ["SCN_RAD_WASTE_DISPOSAL_FACILITY"]),
        (r"贮存|转移|放射性固体废物", ["SCN_RADIOACTIVE_WASTE_STORAGE_TRANSFER_DISPOSAL"]),
        (r"放射源", ["SCN_RADIOACTIVE_SOURCE_SECURITY"]),
        (r"射线|加速器|核医学|测井|装置|辐照", ["SCN_RADIATION_DEVICE_SOURCE_SAFETY"]),
    ]
    matched = []
    for pattern, scenario_ids in rules:
        if re.search(pattern, title, re.IGNORECASE):
            matched.extend(scenario_ids)
    return sorted(set(matched or ["SCN_RADIATION_DEVICE_SOURCE_SAFETY"]))


def append_link(rows, source, link_type, target_kind, target_id, target_label, method, confidence, evidence, gate_status):
    row = {
        "link_id": f"PSL-V8_6-{len(rows) + 1:05d}",
        "baseline_entry_id": source.get("baseline_entry_id", ""),
        "source_id": source.get("source_id", ""),
        "source_doc_title": source.get("source_doc_title", ""),
        "source_standard_no_canonical": source.get("source_standard_no_canonical", ""),
        "domain": source.get("domain", ""),
        "source_role": source.get("source_role", ""),
        "link_type": link_type,
        "target_kind": target_kind,
        "target_id": target_id,
        "target_label": target_label,
        "mapping_method": method,
        "mapping_confidence": confidence,
        "evidence_text": evidence,
        "content_usability_flag": source.get("content_usability_flag", ""),
        "content_gate_status": content_gate(source),
        "human_review_label": "",
        "gate_status": gate_status,
        "runtime_status": RUNTIME_STATUS,
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
        "candidate_only": "TRUE",
        "radiation_all_industry_default_blocked": "TRUE" if source.get("domain") == "radiation" else "FALSE",
        "source_hash": source.get("source_hash", ""),
    }
    rows.append(row)


def build_links(baseline_rows, scenarios_by_id, industry_ix):
    rows = []
    for source in sorted(baseline_rows, key=lambda item: item["source_id"]):
        append_link(rows, source, "STANDARD_IN_DOMAIN", "DOMAIN", source["domain"], source["domain"], "DOMAIN_CLASSIFICATION", "HIGH", f"V8.5 domain={source['domain']}", "N/A")
        if content_gate(source) == "BLOCKED_PENDING_OCR":
            append_link(rows, source, "STANDARD_BLOCKED_PENDING_SOURCE_REVIEW", "SOURCE_REVIEW", "BLOCKED_PENDING_OCR", "OCR or small-file source review required before deep linking", "CONTENT_USABILITY_GATE", "HIGH", f"content_usability_flag={source.get('content_usability_flag', '')}", "BLOCKED_PENDING_OCR")
            continue

        link_type, score_ids = ROLE_RULES.get(source["source_role"], ("STANDARD_REFERENCE_CONTEXT", []))
        scenario_ids = radiation_scenarios_for(source["source_doc_title"]) if source["domain"] == "radiation" else DOMAIN_SCENARIO_SEEDS.get(source["domain"], [])
        if source["source_role"] == "MONITORING_REQUIREMENT_SOURCE":
            scenario_ids = sorted(set(scenario_ids + ["SCN_ONLINE_MONITORING_KEY_UNIT"]))
        for scenario_id in scenario_ids:
            append_link(rows, source, link_type, "SCENARIO", scenario_id, scenarios_by_id.get(scenario_id, {}).get("scenario_name", scenario_id), "RADIATION_TITLE_RULE" if source["domain"] == "radiation" else "DOMAIN_MEDIA_SEED", "MEDIUM" if source["domain"] == "radiation" else "LOW", f"domain={source['domain']}; role={source['source_role']}; title={source['source_doc_title']}", "NEED_SCENARIO_CONFIRM")
        for score_id in score_ids:
            append_link(rows, source, link_type, "SCORE13", score_id, SCORE13_NAMES[score_id], "ROLE_RULE", "MEDIUM", f"source_role={source['source_role']} -> {score_id}", "NEED_SCORE_CONFIRM")
        for industry in match_industries(source["source_doc_title"], industry_ix):
            append_link(rows, source, "STANDARD_APPLIES_TO_INDUSTRY", "INDUSTRY", industry["class_code"], industry["class_name"], "TITLE_INDUSTRY_MATCH", "LOW", f"title={source['source_doc_title']}; matched industry={industry['class_code']} {industry['class_name']}", "NEED_INDUSTRY_CONFIRM")
    return rows


def common(source_basis, confidence="MEDIUM", gate_status="NEED_CONFIRM"):
    return {
        "kb_version": VERSION,
        "final_state": FINAL_STATE,
        "runtime_status": RUNTIME_STATUS,
        "runtime_integration": RUNTIME_INTEGRATION,
        "candidate_only": True,
        "source_basis": source_basis,
        "confidence": confidence,
        "gate_status": gate_status,
        "open_question_refs": [],
        "risk_refs": [],
    }


def node(node_type, node_id, natural_key, properties, source_basis, confidence="MEDIUM", gate_status="NEED_CONFIRM"):
    return {"node_id": node_id, "node_type": node_type, "natural_key": natural_key, **common(source_basis, confidence, gate_status), "properties": properties}


def edge(edge_type, edge_id, from_id, to_id, properties, source_basis, confidence="MEDIUM", gate_status="NEED_CONFIRM"):
    return {"edge_id": edge_id, "edge_type": edge_type, "from_node_id": from_id, "to_node_id": to_id, **common(source_basis, confidence, gate_status), "properties": properties}


def normalize_existing_graph_row(row):
    normalized = dict(row)
    normalized["kb_version"] = VERSION
    normalized["final_state"] = FINAL_STATE
    normalized["runtime_status"] = RUNTIME_STATUS
    normalized["runtime_integration"] = RUNTIME_INTEGRATION
    normalized["candidate_only"] = True
    props = dict(normalized.get("properties") or {})
    props.setdefault("v0_6_preserved_from", row.get("kb_version", "v0.5-graph-rag-candidate-package"))
    props.setdefault("runtime_integration", RUNTIME_INTEGRATION)
    normalized["properties"] = props
    return normalized


def build_graph(v05_nodes, v05_edges, baseline_rows, scenarios, links):
    baseline_by_source = {row["source_id"]: row for row in baseline_rows}
    nodes = [normalize_existing_graph_row(row) for row in v05_nodes if row.get("node_type") != "ScenarioTemplate"]
    node_ids = {row["node_id"] for row in nodes}

    for scenario in sorted(scenarios, key=lambda item: item["scenario_id"]):
        nodes.append(node("ScenarioTemplate", f"scenario:{scenario['scenario_id']}", scenario["scenario_id"], scenario, "approved_scenario_templates_v1_0.json", scenario.get("confidence", "MEDIUM"), "APPROVED_BASELINE_REFERENCE_NEED_LINK_CONFIRM"))
        node_ids.add(f"scenario:{scenario['scenario_id']}")
    for domain in sorted({row["domain"] for row in baseline_rows}):
        nodes.append(node("PollutantDomain", f"domain:{domain}", domain, {"domain": domain}, "pollutant_domain_approved_baseline_v8_5.csv", "HIGH", "N/A"))
        node_ids.add(f"domain:{domain}")
    for score_id, name in SCORE13_NAMES.items():
        if f"score13:{score_id}" not in node_ids:
            nodes.append(node("Score13Dimension", f"score13:{score_id}", score_id, {"score_item_id": score_id, "score_item_name": name}, "EcoCheck S01-S13 report dimension baseline", "HIGH", "N/A"))
            node_ids.add(f"score13:{score_id}")
    for row in sorted(baseline_rows, key=lambda item: item["source_id"]):
        props = dict(row)
        props.update({"v8_6_link_status": "BLOCKED_PENDING_OCR" if content_gate(row) == "BLOCKED_PENDING_OCR" else "TITLE_LEVEL_LINKED_NEED_CONFIRM", "radiation_all_industry_default_blocked": row["domain"] == "radiation"})
        nodes.append(node("PollutantStandardSource", f"standard:{row['source_id']}", row["source_id"], props, "pollutant_domain_approved_baseline_v8_5.csv", "HIGH", "NEED_CONFIRM"))
        node_ids.add(f"standard:{row['source_id']}")

    edges = [normalize_existing_graph_row(row) for row in v05_edges]
    edge_ids = {row["edge_id"] for row in edges}
    for link in sorted(links, key=lambda item: item["link_id"]):
        if link["target_kind"] == "DOMAIN":
            edge_type, to_id = "STANDARD_IN_DOMAIN", f"domain:{link['target_id']}"
        elif link["target_kind"] == "SCENARIO":
            edge_type, to_id = "STANDARD_GOVERNS_SCENARIO", f"scenario:{link['target_id']}"
        elif link["target_kind"] == "INDUSTRY":
            edge_type, to_id = "STANDARD_APPLIES_TO_INDUSTRY", f"industry:{link['target_id']}"
        elif link["target_kind"] == "SCORE13":
            edge_type, to_id = "STANDARD_SUPPORTS_SCORE13", f"score13:{link['target_id']}"
        else:
            continue
        edge_id = f"edge:v8_6:{safe_id(link['link_id'])}"
        if edge_id in edge_ids:
            continue
        props = dict(link)
        props["approved_pollutant_baseline_final_state"] = baseline_by_source[link["source_id"]]["final_state"]
        props["source_candidate_boundary_preserved"] = True
        edges.append(edge(edge_type, edge_id, f"standard:{link['source_id']}", to_id, props, "pollutant_standard_link_map_v8_6.csv", link["mapping_confidence"], link["gate_status"]))
        edge_ids.add(edge_id)

    return sorted(nodes, key=lambda item: (item["node_type"], item["node_id"])), sorted(edges, key=lambda item: (item["edge_type"], item["edge_id"]))


def update_artifact_manifest():
    path = ROOT / "artifact_manifest.json"
    data = read_json(path)
    artifacts = data.setdefault("artifacts", {})
    artifacts.pop("graph_edges_v0_6.jsonl", None)
    artifacts.update({
        "pollutant_standard_link_map_v8_6.csv": "data/approved_baseline/pollutant_domain_v8_5/pollutant_standard_link_map_v8_6.csv",
        "graph_nodes_v0_6.jsonl": "data/graph_rag/graph_nodes_v0_6.jsonl",
        "graph_edges_v0_6.jsonl.gz": "data/graph_rag/graph_edges_v0_6.jsonl.gz",
        "pollutant_standard_link_map_v8_6.md": "docs/design/pollutant_standard_link_map_v8_6.md",
        "pollutant_standard_link_graph_manifest_v8_6.json": "manifests/pollutant_standard_link_graph_manifest_v8_6.json",
        "pollutant_standard_link_graph_gate_report_v8_6.json": "reports/pollutant_standard_link_graph_gate_report_v8_6.json",
        "FINAL_POLLUTANT_STANDARD_LINK_GRAPH_v8_6.md": "reports/FINAL_POLLUTANT_STANDARD_LINK_GRAPH_v8_6.md",
        "build_pollutant_standard_link_v8_6.py": "build_pollutant_standard_link_v8_6.py",
        "validate_pollutant_standard_link_v8_6.py": "validate_pollutant_standard_link_v8_6.py",
    })
    write_json_lf(path, data)


def main():
    update_artifact_manifest()
    baseline_rows = read_csv(BASELINE)
    scenarios = read_json(SCENARIOS)
    scenarios_by_id = {row["scenario_id"]: row for row in scenarios}
    links = build_links(baseline_rows, scenarios_by_id, industry_index(read_csv(INDUSTRY_CATALOG)))
    nodes, edges = build_graph(read_jsonl(GRAPH_NODES_V05), read_jsonl(GRAPH_EDGES_V05, GRAPH_EDGES_V05_GZ), baseline_rows, scenarios, links)

    write_csv_lf(OUT_LINKS, links)
    write_jsonl_lf(OUT_NODES, nodes)
    write_jsonl_gz(OUT_EDGES, edges)

    link_counts = Counter(row["target_kind"] for row in links)
    node_counts = Counter(row["node_type"] for row in nodes)
    edge_counts = Counter(row["edge_type"] for row in edges)
    domain_counts = Counter(row["domain"] for row in baseline_rows)
    role_counts = Counter(row["source_role"] for row in baseline_rows)
    usability_counts = Counter(row["content_usability_flag"] for row in baseline_rows)

    design = f"""# pollutant_standard_link_map_v8_6

final_state: `{FINAL_STATE}`
runtime_integration: `{RUNTIME_INTEGRATION}`

v8.6 adds a candidate bridge from V8.5 pollutant-domain approved sources to scenario, industry, Score13, and graph-v0.6 surfaces. It does not mutate the V8.5 approved baseline CSV and does not promote runtime use.

## Truth Snapshot

- V8.5 source rows: {len(baseline_rows)}
- Domain distribution: `{dict(sorted(domain_counts.items()))}`
- Source-role distribution: `{dict(sorted(role_counts.items()))}`
- Content usability distribution: `{dict(sorted(usability_counts.items()))}`

The design draft expected `hazardous_waste=31` and `TITLE_LEVEL_AND_SOURCE_LOCK_READY=200`; the real repository data is `hazardous_waste={domain_counts.get('hazardous_waste', 0)}` and `TITLE_LEVEL_AND_SOURCE_LOCK_READY={usability_counts.get('TITLE_LEVEL_AND_SOURCE_LOCK_READY', 0)}`.

## Output Counts

`{dict(sorted(link_counts.items()))}`
"""
    report = f"""# FINAL POLLUTANT STANDARD LINK GRAPH v8.6

Final state: `{FINAL_STATE}`
Runtime integration: `{RUNTIME_INTEGRATION}`

## Delivered

- Built `pollutant_standard_link_map_v8_6.csv` as the candidate bridge over V8.5.
- Built `graph_nodes_v0_6.jsonl` and `graph_edges_v0_6.jsonl.gz`.
- Preserved candidate-only/runtime-disabled boundaries on every new link and graph edge.
- Kept the original V8.5 baseline CSV unchanged.

## Counts

- Link rows by target kind: `{dict(sorted(link_counts.items()))}`
- Graph nodes by type: `{dict(sorted(node_counts.items()))}`
- Graph edges by type: `{dict(sorted(edge_counts.items()))}`
- V8.5 domains: `{dict(sorted(domain_counts.items()))}`
- V8.5 source roles: `{dict(sorted(role_counts.items()))}`
- V8.5 content usability: `{dict(sorted(usability_counts.items()))}`

## Known Gaps

- Title-to-industry links are low-confidence candidates and still require human review.
- OCR and small-file rows are intentionally blocked from scenario, industry, and Score13 linking.
- This package is graph/RAG candidate scaffolding only; no EcoCheck runtime mutation or formal compliance conclusion is authorized.
"""
    write_text_lf(OUT_DESIGN, design)
    write_text_lf(OUT_REPORT, report)

    manifest = {
        "schema_version": "pollutant-standard-link-graph.v8_6",
        "knowledge_base_version": VERSION,
        "final_state": FINAL_STATE,
        "runtime_status": RUNTIME_STATUS,
        "runtime_integration": RUNTIME_INTEGRATION,
        "source_baseline": "v8.5-pollutant-domain-approved-baseline",
        "approved_pollutant_rows": len(baseline_rows),
        "approved_scenario_rows": len(scenarios),
        "truth_snapshot": {
            "domain_distribution": dict(sorted(domain_counts.items())),
            "source_role_distribution": dict(sorted(role_counts.items())),
            "content_usability_flag_distribution": dict(sorted(usability_counts.items())),
            "industry_linked_source_count": len({row["source_id"] for row in links if row["target_kind"] == "INDUSTRY"}),
        },
        "outputs": {
            "link_csv": {"path": "data/approved_baseline/pollutant_domain_v8_5/pollutant_standard_link_map_v8_6.csv", "rows": len(links), "sha256": sha256_file(OUT_LINKS)},
            "graph_nodes": {"path": "data/graph_rag/graph_nodes_v0_6.jsonl", "rows": len(nodes), "sha256": sha256_file(OUT_NODES)},
            "graph_edges": {"path": "data/graph_rag/graph_edges_v0_6.jsonl.gz", "rows": len(edges), "sha256": sha256_file(OUT_EDGES)},
            "design_md": {"path": "docs/design/pollutant_standard_link_map_v8_6.md", "sha256": sha256_file(OUT_DESIGN)},
            "report_md": {"path": "reports/FINAL_POLLUTANT_STANDARD_LINK_GRAPH_v8_6.md", "sha256": sha256_file(OUT_REPORT)},
        },
        "guards": {
            "v8_5_baseline_mutated": False,
            "radiation_all_industry_default": "blocked",
            "ocr_and_small_file_deep_links": "blocked",
            "runtime_code_mutation": False,
        },
    }
    write_json_lf(OUT_MANIFEST, manifest)
    print(json.dumps({"status": "BUILT", "version": VERSION, "link_rows": len(links), "graph_nodes": len(nodes), "graph_edges": len(edges), "link_counts": dict(sorted(link_counts.items()))}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
