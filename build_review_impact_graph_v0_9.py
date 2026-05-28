import csv
import json
from pathlib import Path
from kb_paths import artifact_path


ROOT = Path(__file__).resolve().parent
FINAL_STATE = "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"
RUNTIME_INTEGRATION = "disabled"
KB_VERSION = "v0.9-review-impact-graph"
IMPACT_SCOPE_NOTE = "候选影响范围来自 related_scenario_ids 聚合，用于审阅传播分析；不代表企业现场事实已确认适用。"

SUBSCENARIO_BY_SCENARIO = {
    "SCN_BASE_PRODUCTION_SOLID_NOISE_LEDGER": ["production_activity", "general_solid_waste", "noise_source", "ledger"],
    "SCN_WW_PROCESS_AND_TREATMENT": ["production_wastewater", "medical_wastewater", "cleaning_wastewater", "domestic_sewage", "wastewater_treatment"],
    "SCN_VOCS_SOLVENT_AND_TREATMENT": ["vocs_material", "organized_exhaust", "unorganized_exhaust", "waste_gas_treatment"],
    "SCN_HAZWASTE_STORAGE_TRANSFER": ["hazardous_waste_storage", "transfer_manifest", "waste_identification"],
    "SCN_MEDICAL_WASTE_RADIATION": ["medical_waste", "medical_wastewater", "radiation_diagnosis"],
    "SCN_CHEMICAL_TANK_LDAR_SEEPAGE": ["chemical_tank", "ldar", "soil_groundwater_risk", "seepage_control"],
    "SCN_GAS_STATION_VAPOR_UST": ["vapor_recovery", "underground_storage_tank", "oil_unloading_area"],
    "SCN_DUST_PARTICULATE_CONTROL": ["particulate", "dust_collection", "yard_unorganized_dust"],
    "SCN_ONLINE_MONITORING_KEY_UNIT": ["online_monitoring", "data_transmission", "operation_maintenance"],
    "SCN_RAINWATER_ACCIDENT_EMERGENCY": ["rainwater_outfall", "rain_sewage_mixing", "accident_water", "emergency_pool"],
    "SCN_TRAINING_SIGNAGE_REVIEW_GAP": ["environmental_training", "signage_publicity", "issue_closure", "emergency_training"],
}


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


def write_csv(path, rows, fields=None):
    tmp = path.with_name(f".{path.name}.tmp")
    if fields is None:
        fields = list(rows[0].keys()) if rows else []
    with tmp.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    tmp.replace(path)


def write_json(path, data):
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def write_jsonl(path, rows):
    tmp = path.with_name(f".{path.name}.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    tmp.replace(path)


def parse_json(value):
    if isinstance(value, list):
        return value
    if not value:
        return []
    return json.loads(value)


def common(source_basis, open_refs=None, risk_refs=None):
    return {
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
        "runtime_status": "DRAFT_NOT_FOR_RUNTIME",
        "candidate_only": True,
        "source_basis": source_basis,
        "open_question_refs": open_refs or [],
        "risk_refs": risk_refs or [],
        "runtime_effect": "NO_RUNTIME_EFFECT",
    }


def edge(edge_type, edge_id, from_id, to_id, props, source_basis, open_refs=None, risk_refs=None):
    enriched_props = dict(props)
    enriched_props["impact_scope_note"] = IMPACT_SCOPE_NOTE
    return {
        "edge_id": edge_id,
        "edge_type": edge_type,
        "from_id": from_id,
        "to_id": to_id,
        "properties": enriched_props,
        **common(source_basis, open_refs, risk_refs),
    }


def main():
    overlays = read_json(artifact_path("human_review_overlay_v0_8.json"))
    relations = {r["candidate_relation_id"]: r for r in read_csv(artifact_path("all_context_applicability_review_v0_4_1.csv"))}
    scenarios = {s["scenario_id"]: s for s in read_json(artifact_path("scenario_templates.json"))}
    score_map = {r["scenario_id"]: r for r in read_csv(artifact_path("scenario_to_score13_mapping_v0_3.csv"))}
    inspections = read_csv(artifact_path("inspection_candidate_recommendations_v0_3.csv"))
    inspections_by_scenario = {}
    for row in inspections:
        inspections_by_scenario.setdefault(row["scenario_id"], []).append(row)
    rag_results = read_jsonl(artifact_path("rag_prototype_results_v0_8.jsonl"))
    rag_by_relation = {}
    for row in rag_results:
        for ref in row.get("source_node_refs", []):
            rag_by_relation.setdefault(ref, []).append(row)

    impact_rows = []
    impact_edges = []
    for overlay in overlays:
        rel = relations[overlay["candidate_relation_id"]]
        scenario_ids = parse_json(rel["related_scenario_ids"])
        score13_ids = []
        inspection_ids = []
        media_types = []
        subscenario_tags = []
        facility_or_risk_units = []
        for sid in scenario_ids:
            scenario = scenarios.get(sid, {})
            media_types.append(scenario.get("media_type", ""))
            subscenario_tags.extend(SUBSCENARIO_BY_SCENARIO.get(sid, []))
            if scenario.get("facility_or_risk_unit"):
                facility_or_risk_units.append(scenario["facility_or_risk_unit"])
            mapping = score_map.get(sid)
            if mapping:
                score13_ids.append(mapping["primary_score_item_id"])
                score13_ids.extend([x for x in mapping["secondary_score_item_ids"].split(";") if x])
            for ins in inspections_by_scenario.get(sid, []):
                inspection_ids.append(f"{sid}:{ins['inspection_type']}")
        rag_query_ids = [r["query_id"] for r in rag_by_relation.get(overlay["candidate_relation_id"], [])]
        open_refs = sorted(set(parse_json(rel["confirmation_questions"]) and parse_json(rel["open_question_refs"]) if "open_question_refs" in rel else []))
        risk_refs = parse_json(rel.get("risk_refs", "[]"))
        row = {
            "impact_id": f"IMP09::{overlay['candidate_relation_id']}",
            "overlay_id": overlay["overlay_id"],
            "candidate_relation_id": overlay["candidate_relation_id"],
            "human_review_label": overlay["human_review_label"],
            "overlay_status": overlay["overlay_status"],
            "industry_code": rel["industry_code"],
            "industry_name": rel["industry_name"],
            "entry_no": rel["entry_no"],
            "target_management_condition": rel["target_management_condition"],
            "gate_status": rel["gate_status"],
            "relation_source": rel["relation_source"],
            "scenario_ids": json.dumps(sorted(set(scenario_ids)), ensure_ascii=False),
            "media_types": json.dumps(sorted(set(x for x in media_types if x)), ensure_ascii=False),
            "subscenario_tags": json.dumps(sorted(set(subscenario_tags)), ensure_ascii=False),
            "facility_or_risk_units": json.dumps(sorted(set(facility_or_risk_units)), ensure_ascii=False),
            "score13_ids": json.dumps(sorted(set(score13_ids)), ensure_ascii=False),
            "inspection_candidate_ids": json.dumps(sorted(set(inspection_ids)), ensure_ascii=False),
            "open_question_refs": rel.get("open_question_refs", "[]"),
            "risk_refs": rel.get("risk_refs", "[]"),
            "rag_query_ids": json.dumps(rag_query_ids, ensure_ascii=False),
            "impact_scope_note": IMPACT_SCOPE_NOTE,
            "requires_second_approval": overlay["requires_second_approval"],
            "runtime_effect": "NO_RUNTIME_EFFECT",
            "final_state": FINAL_STATE,
            "runtime_status": "DRAFT_NOT_FOR_RUNTIME",
        }
        impact_rows.append(row)
        refs_open = parse_json(row["open_question_refs"])
        refs_risk = parse_json(row["risk_refs"])
        impact_edges.append(edge("REVIEW_OVERLAY_AFFECTS_RELATION", f"edge09:overlay_relation:{overlay['candidate_relation_id']}", f"review_overlay:{overlay['overlay_id']}", f"applicability:{overlay['candidate_relation_id']}", {"human_review_label": overlay["human_review_label"], "overlay_status": overlay["overlay_status"]}, "human_review_overlay_v0_8.json", refs_open, refs_risk))
        for sid in sorted(set(scenario_ids)):
            impact_edges.append(edge("RELATION_AFFECTS_SCENARIO", f"edge09:relation_scenario:{overlay['candidate_relation_id']}:{sid}", f"applicability:{overlay['candidate_relation_id']}", f"scenario:{sid}", {"media_type": scenarios.get(sid, {}).get("media_type", ""), "subscenario_tags": SUBSCENARIO_BY_SCENARIO.get(sid, [])}, "all_context_applicability_review_v0_4_1.csv; scenario_templates.json", refs_open, refs_risk))
            mapping = score_map.get(sid)
            if mapping:
                for score_id in sorted(set([mapping["primary_score_item_id"]] + [x for x in mapping["secondary_score_item_ids"].split(";") if x])):
                    impact_edges.append(edge("SCENARIO_AFFECTS_SCORE13", f"edge09:scenario_score:{sid}:{score_id}:{overlay['candidate_relation_id']}", f"scenario:{sid}", f"score13:{score_id}", {"candidate_relation_id": overlay["candidate_relation_id"]}, "scenario_to_score13_mapping_v0_3.csv", refs_open, refs_risk))
            for ins in inspections_by_scenario.get(sid, []):
                impact_edges.append(edge("SCENARIO_AFFECTS_INSPECTION", f"edge09:scenario_inspection:{sid}:{ins['inspection_type']}:{overlay['candidate_relation_id']}", f"scenario:{sid}", f"inspection:{sid}:{ins['inspection_type']}", {"candidate_relation_id": overlay["candidate_relation_id"], "candidate_section": ins["candidate_section"], "photo_points": ins["photo_points"], "evidence_chain": ins["evidence_chain"]}, "inspection_candidate_recommendations_v0_3.csv", refs_open, refs_risk))
        for rag in rag_by_relation.get(overlay["candidate_relation_id"], []):
            impact_edges.append(edge("RAG_QUERY_REFERENCES_REVIEW_OVERLAY", f"edge09:rag_overlay:{rag['query_id']}:{overlay['candidate_relation_id']}", f"rag_query:{rag['query_id']}", f"review_overlay:{overlay['overlay_id']}", {"human_review_status": rag["human_review_status"], "source_chunk_ids": rag["source_chunk_ids"]}, "rag_prototype_results_v0_8.jsonl", rag.get("open_question_refs", []), rag.get("risk_refs", [])))

    playbook = {
        "knowledge_base_version": KB_VERSION,
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
        "query_patterns": [
            {
                "query_id": "PLAY09-001",
                "name": "industry_to_inspection_path",
                "path": ["Industry", "PermitCondition", "ApplicabilityRelation", "ScenarioTemplate", "Score13Dimension", "InspectionCandidate"],
                "description": "行业召回后，经许可条件和候选适用关系进入场景本体，再映射13维和候选排查项。",
            },
            {
                "query_id": "PLAY09-002",
                "name": "review_overlay_impact_path",
                "path": ["ReviewOverlay", "ApplicabilityRelation", "ScenarioTemplate", "Score13Dimension", "InspectionCandidate", "RagQuery"],
                "description": "查看一条模拟审阅结论影响哪些场景、13维、排查项和RAG回答。",
            },
            {
                "query_id": "PLAY09-003",
                "name": "entry108_general_process_path",
                "path": ["PermitCatalogEntry108", "PermitCatalogEntry109-112", "OpenQuestion", "RiskAcceptance"],
                "description": "解释第108条承接到109-112通用工序，不代表许可名录缺失。",
            },
        ],
    }

    mermaid = """# graph_visualization_samples_v0_9

final_state: `NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY`

全局提示：以下可视化展示的是候选影响范围传播，不代表企业现场事实已确认适用，不产生运行时效果。

## 3012 登记管理确认不适用

```mermaid
flowchart LR
  A["Industry 3012 石灰和石膏制造"] --> B["Permit Condition Entry 63 REGISTRATION"]
  B --> C["Applicability CTXV04_3012_63_REGISTRATION"]
  C --> D["Review Overlay CONFIRM_NOT_APPLY"]
  C --> E["Scenario: Dust / Wastewater / Solid ledger candidates"]
  E --> F["Score13 S10/S06/S07..."]
  E --> G["Inspection Candidates FIRST/MONTHLY"]
  D --> H["Formalization candidate only, second approval required"]
  H --> I["NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"]
```

## 0111 锅炉通用工序仍需现场确认

```mermaid
flowchart LR
  A["Industry 0111 稻谷种植"] --> B["Entry 109 Boiler SIMPLIFIED"]
  B --> C["GENERAL_PROCESS_TRIGGER"]
  C --> D["Review Overlay NEED_SITE_CONFIRM"]
  D --> E["Still BLOCKS_RUNTIME"]
  C --> F["Open Questions: general process + entry108 strategy"]
  E --> G["NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"]
```

## 4620 第99条确认为候选仍需二次审批

```mermaid
flowchart LR
  A["Industry 4620 污水处理及其再生利用"] --> B["Entry 99 wastewater treatment"]
  B --> C["Applicability CTXV04_4620_99_KEY"]
  C --> D["Review Overlay CONFIRM_MAY_APPLY"]
  D --> E["Formalization candidate"]
  E --> F["Second approval required"]
  F --> G["No runtime effect"]
```

## Entry 108 承接策略

```mermaid
flowchart LR
  A["Entry 108 other industries"] --> B["Bridge / carry-forward strategy"]
  B --> C["Entry 109 Boiler"]
  B --> D["Entry 110 Industrial kiln"]
  B --> E["Entry 111 Surface treatment"]
  B --> F["Entry 112 Water treatment"]
  B --> G["Open Question V04_ENTRY_108_CONTEXT_001"]
  G --> H["Risk RISK-V041-001"]
  H --> I["Not a missing catalog entry"]
```
"""

    write_csv(artifact_path("review_impact_analysis_v0_9.csv"), impact_rows)
    write_json(artifact_path("review_impact_analysis_v0_9.json"), impact_rows)
    write_jsonl(artifact_path("review_impact_graph_edges_v0_9.jsonl"), impact_edges)
    write_json(artifact_path("graph_query_playbook_v0_9.json"), playbook)
    (artifact_path("graph_query_playbook_v0_9.md")).write_text(
        "# graph_query_playbook_v0_9\n\n"
        f"final_state: `{FINAL_STATE}`\n\n"
        + "\n".join(f"- `{q['query_id']}` {q['name']}: {' -> '.join(q['path'])}" for q in playbook["query_patterns"])
        + "\n",
        encoding="utf-8",
    )
    (artifact_path("graph_visualization_samples_v0_9.md")).write_text(mermaid, encoding="utf-8")
    write_json(artifact_path("graph_visualization_samples_v0_9.json"), {
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
        "samples": ["3012_registration_not_apply", "0111_general_process_site_confirm", "4620_may_apply_second_approval", "entry108_strategy"],
    })
    manifest = {
        "knowledge_base_version": KB_VERSION,
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
        "runtime_promotion_status": "not_approved",
        "outputs": {
            "review_impact_analysis_v0_9.csv": len(impact_rows),
            "review_impact_graph_edges_v0_9.jsonl": len(impact_edges),
            "graph_query_playbook_v0_9.md": 1,
            "graph_visualization_samples_v0_9.md": 1,
        },
        "runtime_effect": "NONE",
    }
    write_json(artifact_path("knowledge_base_manifest_v0_9.json"), manifest)
    (artifact_path("FINAL_COMPLETION_REPORT_v0_9.md")).write_text(
        "# FINAL COMPLETION REPORT v0.9\n\n"
        f"最终状态：`{FINAL_STATE}`\n\n"
        "v0.9 已生成图谱查询/可视化样例与审阅影响传播分析，未接 EcoCheck runtime。\n\n"
        f"- review_impact_rows: {len(impact_rows)}\n"
        f"- review_impact_edges: {len(impact_edges)}\n"
        "- 每条模拟审阅overlay均追溯到候选适用关系，并尽可能展开到场景、13维、候选排查项和RAG查询。\n",
        encoding="utf-8",
    )
    print(json.dumps({"final_state": FINAL_STATE, "impact_rows": len(impact_rows), "impact_edges": len(impact_edges)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
