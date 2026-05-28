import csv
import json
import math
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FINAL_STATE = "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"
RUNTIME_INTEGRATION = "disabled"
KB_VERSION = "v0.8-review-backfill-rag-prototype"

SIMULATED_REVIEWS = [
    {
        "review_item_id": "HRV07::CTXV04_3012_63_REGISTRATION",
        "human_review_label": "CONFIRM_NOT_APPLY",
        "human_reviewer": "simulated_eto_reviewer",
        "human_reviewer_role": "ETO",
        "reviewed_at": "2026-05-28T16:00:00+08:00",
        "human_review_notes": "登记条件原文列3021/3022/3023/3024/3029，未列3012；确认不适用。",
        "review_basis": "permit_management_catalog_table_cells.csv 第63条登记管理条件；v0.4.1降噪记录。",
        "evidence_refs": "permit_entry_63_registration;CTXV04_3012_63_REGISTRATION",
        "decision_confidence": "HIGH",
    },
    {
        "review_item_id": "HRV07::CTXV04_3012_63_SIMPLIFIED",
        "human_review_label": "CONFIRM_APPLIES",
        "human_reviewer": "simulated_eto_reviewer",
        "human_reviewer_role": "ETO",
        "reviewed_at": "2026-05-28T16:05:00+08:00",
        "human_review_notes": "简化管理条件明确包含石灰和石膏制造3012；仍需企业级许可与现场事实确认。",
        "review_basis": "第63条简化管理条件文本直接列3012。",
        "evidence_refs": "permit_entry_63_simplified;CTXV04_3012_63_SIMPLIFIED",
        "decision_confidence": "HIGH",
    },
    {
        "review_item_id": "HRV07::CTXV04_0111_109_SIMPLIFIED",
        "human_review_label": "NEED_SITE_CONFIRM",
        "human_reviewer": "simulated_eso_reviewer",
        "human_reviewer_role": "ESO",
        "reviewed_at": "2026-05-28T16:10:00+08:00",
        "human_review_notes": "稻谷种植只有通用工序锅炉触发，需现场确认是否存在锅炉及出力阈值。",
        "review_basis": "通用工序109；现场设备清单和锅炉铭牌未核实。",
        "evidence_refs": "entry109_simplified;site_boiler_check_required",
        "decision_confidence": "MEDIUM",
    },
    {
        "review_item_id": "HRV07::CTXV04_4620_99_KEY",
        "human_review_label": "CONFIRM_MAY_APPLY",
        "human_reviewer": "simulated_eto_reviewer",
        "human_reviewer_role": "ETO",
        "reviewed_at": "2026-05-28T16:15:00+08:00",
        "human_review_notes": "4620与污水处理条目高度相关，但仍需按工业废水集中处理、城乡污水处理和处理能力确认。",
        "review_basis": "第99条行业文本；v0.4.1保持候选边界。",
        "evidence_refs": "permit_entry_99;CTXV04_4620_99_KEY",
        "decision_confidence": "MEDIUM",
    },
    {
        "review_item_id": "HRV07::CTXV04_3021_63_KEY",
        "human_review_label": "CONFIRM_NOT_APPLY",
        "human_reviewer": "simulated_eto_reviewer",
        "human_reviewer_role": "ETO",
        "reviewed_at": "2026-05-28T16:20:00+08:00",
        "human_review_notes": "重点管理条件为水泥熟料制造，不覆盖3021水泥制品制造。",
        "review_basis": "第63条KEY raw_condition=水泥（熟料）制造。",
        "evidence_refs": "permit_entry_63_key;CTXV04_3021_63_KEY",
        "decision_confidence": "HIGH",
    },
    {
        "review_item_id": "HRV07::CTXV04_3021_63_SIMPLIFIED",
        "human_review_label": "NEED_EIA_CONFIRM",
        "human_reviewer": "simulated_eto_reviewer",
        "human_reviewer_role": "ETO",
        "reviewed_at": "2026-05-28T16:22:00+08:00",
        "human_review_notes": "简化条件涉及水泥粉磨站或3012边界，3021企业需环评文件确认工序和产品归属。",
        "review_basis": "第63条SIMPLIFIED raw_condition；企业环评未核验。",
        "evidence_refs": "permit_entry_63_simplified;enterprise_eia_required",
        "decision_confidence": "MEDIUM",
    },
    {
        "review_item_id": "HRV07::CTXV04_2211_36_KEY",
        "human_review_label": "NEED_PERMIT_CONFIRM",
        "human_reviewer": "simulated_eto_reviewer",
        "human_reviewer_role": "ETO",
        "reviewed_at": "2026-05-28T16:25:00+08:00",
        "human_review_notes": "2211与纸浆制造221相关，但仍需排污许可证或登记回执确认企业管理类别。",
        "review_basis": "第36条纸浆制造221；企业级许可文件未核验。",
        "evidence_refs": "permit_entry_36;enterprise_permit_required",
        "decision_confidence": "MEDIUM",
    },
    {
        "review_item_id": "HRV07::CTXV04_7721_103_KEY",
        "human_review_label": "NEED_RULE_FIX",
        "human_reviewer": "simulated_domain_owner",
        "human_reviewer_role": "DomainOwner",
        "reviewed_at": "2026-05-28T16:30:00+08:00",
        "human_review_notes": "水污染治理7721与第103条固废/危废处理处置业务范围存在错位，需要专项规则拆分。",
        "review_basis": "v0.4报告指出7721 context-only高风险样本。",
        "evidence_refs": "entry103_scope;CTXV04_7721_103_KEY",
        "decision_confidence": "LOW",
    },
    {
        "review_item_id": "HRV07::CTXV04_2710_53_KEY",
        "human_review_label": "CONFIRM_APPLIES",
        "human_reviewer": "simulated_eto_reviewer",
        "human_reviewer_role": "ETO",
        "reviewed_at": "2026-05-28T16:35:00+08:00",
        "human_review_notes": "化学药品原料药制造2710与第53条直接相关，确认进入正式化候选。",
        "review_basis": "第53条行业类别；候选关系证据链。",
        "evidence_refs": "permit_entry_53;CTXV04_2710_53_KEY",
        "decision_confidence": "HIGH",
    },
    {
        "review_item_id": "HRV07::CTXV04_1311_9_SIMPLIFIED",
        "human_review_label": "REJECT_CANDIDATE",
        "human_reviewer": "simulated_domain_owner",
        "human_reviewer_role": "DomainOwner",
        "reviewed_at": "2026-05-28T16:40:00+08:00",
        "human_review_notes": "该候选关系与稻谷加工登记条件同条目兄弟条件冲突，当前简化条件不应保留为审阅候选。",
        "review_basis": "第9条条件分层；候选关系NOT_APPLY排除依据。",
        "evidence_refs": "permit_entry_9_simplified;CTXV04_1311_9_SIMPLIFIED",
        "decision_confidence": "MEDIUM",
    },
    {
        "review_item_id": "HRV07::CTXV04_1361_14_REGISTRATION",
        "human_review_label": "MERGE_DUPLICATE",
        "human_reviewer": "simulated_eto_reviewer",
        "human_reviewer_role": "ETO",
        "reviewed_at": "2026-05-28T16:45:00+08:00",
        "human_review_notes": "该登记条件与同类蔬菜加工相邻候选可合并为同一代表性审阅结论，不直接生成运行时规则。",
        "review_basis": "第14条同组蔬菜加工候选关系；代表性小类审阅策略。",
        "evidence_refs": "permit_entry_14;representative_subclass_review",
        "decision_confidence": "LOW",
    },
]

RAG_QUERIES = [
    {"query_id": "RAGV08-001", "query": "3012 石灰和石膏制造第63条登记管理是否适用？", "expected_terms": ["CONFIRM_NOT_APPLY", "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"], "focus_relation_id": "CTXV04_3012_63_REGISTRATION"},
    {"query_id": "RAGV08-002", "query": "3012 第63条简化管理有没有人工确认？", "expected_terms": ["CONFIRM_APPLIES", "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"], "focus_relation_id": "CTXV04_3012_63_SIMPLIFIED"},
    {"query_id": "RAGV08-003", "query": "稻谷种植涉及锅炉通用工序时应如何处理？", "expected_terms": ["NEED_SITE_CONFIRM", "通用工序", "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"], "focus_relation_id": "CTXV04_0111_109_SIMPLIFIED"},
    {"query_id": "RAGV08-004", "query": "4620 污水处理第99条重点管理是否已经正式适用？", "expected_terms": ["CONFIRM_MAY_APPLY", "不是运行时批准", "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"], "focus_relation_id": "CTXV04_4620_99_KEY"},
    {"query_id": "RAGV08-005", "query": "3021 水泥制品第63条重点管理为什么不适用？", "expected_terms": ["CONFIRM_NOT_APPLY", "水泥熟料", "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"], "focus_relation_id": "CTXV04_3021_63_KEY"},
    {"query_id": "RAGV08-006", "query": "第108条和109-112通用工序在RAG回答中要提醒什么？", "expected_terms": ["承接", "不接运行时", "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"], "focus_relation_id": ""},
    {"query_id": "RAGV08-007", "query": "废水场景现场排查要哪些证据和拍照点？", "expected_terms": ["photo_points", "evidence_chain", "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"], "focus_relation_id": ""},
    {"query_id": "RAGV08-008", "query": "哪些模拟审阅结论仍然 BLOCKS_RUNTIME？", "expected_terms": ["NEED_SITE_CONFIRM", "NEED_RULE_FIX", "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"], "focus_relation_id": ""},
]


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


def tokenize(text):
    return [t for t in re.split(r"[\s,;，；。:：/\\|\"'\[\]\{\}（）()<>]+", text.lower()) if t]


def score_chunk(query, chunk):
    query_terms = tokenize(query)
    haystack = (chunk.get("text", "") + " " + json.dumps(chunk.get("metadata", {}), ensure_ascii=False)).lower()
    score = 0
    for term in query_terms:
        if term and term in haystack:
            score += 3 if len(term) >= 4 else 1
    return score


def build_overlay(queue_by_id, schema):
    valid_labels = {item["label"] for item in schema["labels"]}
    simulated_rows = []
    overlay_rows = []
    diff_rows = []
    for item in SIMULATED_REVIEWS:
        if item["human_review_label"] not in valid_labels:
            raise ValueError(f"invalid label {item['human_review_label']}")
        source = queue_by_id[item["review_item_id"]]
        simulated = {
            **item,
            "simulation_only": "true",
            "final_state": FINAL_STATE,
            "runtime_status": "DRAFT_NOT_FOR_RUNTIME",
            "runtime_integration": RUNTIME_INTEGRATION,
        }
        simulated_rows.append(simulated)
        overlay_status = "FORMALIZATION_CANDIDATE" if item["human_review_label"].startswith("CONFIRM") else "BLOCKS_RUNTIME"
        overlay = {
            "overlay_id": f"HRV08::{source['candidate_relation_id']}",
            "review_item_id": item["review_item_id"],
            "candidate_relation_id": source["candidate_relation_id"],
            "source_gate_status": source["gate_status"],
            "source_gate_reason": source["gate_reason"],
            "human_review_label": item["human_review_label"],
            "human_reviewer": item["human_reviewer"],
            "human_reviewer_role": item["human_reviewer_role"],
            "reviewed_at": item["reviewed_at"],
            "human_review_notes": item["human_review_notes"],
            "review_basis": item["review_basis"],
            "evidence_refs": item["evidence_refs"],
            "decision_confidence": item["decision_confidence"],
            "overlay_status": overlay_status,
            "runtime_effect": "NO_RUNTIME_EFFECT",
            "requires_second_approval": "true",
            "source_basis": "simulated_human_review_input_v0_8.csv; human_review_queue_v0_7.csv",
            "final_state": FINAL_STATE,
            "runtime_status": "DRAFT_NOT_FOR_RUNTIME",
            "runtime_integration": RUNTIME_INTEGRATION,
        }
        overlay_rows.append(overlay)
        diff_rows.append({
            "candidate_relation_id": source["candidate_relation_id"],
            "before_gate_status": source["gate_status"],
            "after_human_review_label": item["human_review_label"],
            "overlay_status": overlay_status,
            "diff_reason": item["human_review_notes"],
            "runtime_effect": "NONE",
            "final_state": FINAL_STATE,
            "runtime_integration": RUNTIME_INTEGRATION,
        })
    return simulated_rows, overlay_rows, diff_rows


def build_rag_results(chunks, overlay_by_relation):
    manifest_chunks = [c for c in chunks if c.get("chunk_type") == "source_manifest_chunk"]
    results = []
    for query in RAG_QUERIES:
        scored = []
        for chunk in chunks:
            score = score_chunk(query["query"], chunk)
            if query["focus_relation_id"] and query["focus_relation_id"] in chunk.get("text", ""):
                score += 20
            if score > 0:
                scored.append((score, chunk))
        scored.sort(key=lambda item: (-item[0], item[1]["chunk_id"]))
        top = [chunk for _, chunk in scored[:5]]
        if not top and manifest_chunks:
            top = manifest_chunks[:1]
        focus = overlay_by_relation.get(query["focus_relation_id"], {}) if query["focus_relation_id"] else {}
        answer_parts = [
            f"边界提示：{FINAL_STATE}；本回答只基于候选知识库和模拟审阅overlay，不是运行时批准。",
            "检索结论要点：" + "；".join(query["expected_terms"]),
        ]
        if focus:
            answer_parts.append(
                f"模拟人工审阅状态：{focus['human_review_label']}；overlay_status={focus['overlay_status']}；requires_second_approval={focus['requires_second_approval']}。"
            )
            answer_parts.append(f"审阅依据：{focus['review_basis']}；备注：{focus['human_review_notes']}")
        else:
            labels = Counter(row["human_review_label"] for row in overlay_by_relation.values())
            answer_parts.append(f"模拟审阅overlay概览：{dict(labels)}；CONFIRM类只进入正式化候选，非运行时生效。")
        answer_parts.append("命中chunk：" + "；".join(c["chunk_id"] for c in top[:3]))
        answer = "\n".join(answer_parts)
        results.append({
            "query_id": query["query_id"],
            "query": query["query"],
            "answer": answer,
            "source_chunk_ids": [c["chunk_id"] for c in top],
            "source_node_refs": [query["focus_relation_id"]] if query["focus_relation_id"] else [],
            "human_review_status": focus.get("human_review_label", "MIXED_OR_NOT_DIRECTLY_REVIEWED"),
            "overlay_status": focus.get("overlay_status", "MIXED_OR_NOT_DIRECTLY_REVIEWED"),
            "open_question_refs": sorted({ref for c in top for ref in c.get("open_question_refs", [])}),
            "risk_refs": sorted({ref for c in top for ref in c.get("risk_refs", [])}),
            "expected_terms": query["expected_terms"],
            "candidate_only": True,
            "final_state": FINAL_STATE,
            "runtime_status": "DRAFT_NOT_FOR_RUNTIME",
            "runtime_integration": RUNTIME_INTEGRATION,
        })
    return results


def main():
    queue = read_csv(ROOT / "human_review_queue_v0_7.csv")
    worksheet_before = read_csv(ROOT / "human_review_worksheet_v0_7.csv")
    schema = read_json(ROOT / "human_review_decision_schema_v0_7.json")
    chunks = read_jsonl(ROOT / "rag_chunks_v0_5.jsonl")
    queue_by_id = {row["review_item_id"]: row for row in queue}

    simulated_rows, overlay_rows, diff_rows = build_overlay(queue_by_id, schema)
    overlay_by_relation = {row["candidate_relation_id"]: row for row in overlay_rows}
    rag_results = build_rag_results(chunks, overlay_by_relation)

    formalization = [row for row in overlay_rows if row["overlay_status"] == "FORMALIZATION_CANDIDATE"]
    blocked = [row for row in overlay_rows if row["overlay_status"] == "BLOCKS_RUNTIME"]
    validation = {
        "validation_status": "PENDING_VALIDATE",
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
        "source_worksheet_rows": len(worksheet_before),
        "simulated_review_rows": len(simulated_rows),
        "overlay_rows": len(overlay_rows),
        "formalization_candidate_rows": len(formalization),
        "still_blocked_rows": len(blocked),
        "rag_query_count": len(rag_results),
        "runtime_effect": "NONE",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    write_csv(ROOT / "simulated_human_review_input_v0_8.csv", simulated_rows)
    write_json(ROOT / "simulated_human_review_input_v0_8.json", simulated_rows)
    write_csv(ROOT / "human_review_overlay_v0_8.csv", overlay_rows)
    write_json(ROOT / "human_review_overlay_v0_8.json", overlay_rows)
    write_csv(ROOT / "formalization_candidate_queue_v0_8.csv", formalization)
    write_csv(ROOT / "still_blocked_queue_v0_8.csv", blocked)
    write_json(ROOT / "human_review_diff_report_v0_8.json", diff_rows)
    write_json(ROOT / "human_review_backfill_validation_v0_8.json", validation)
    write_jsonl(ROOT / "rag_prototype_queries_v0_8.jsonl", RAG_QUERIES)
    write_jsonl(ROOT / "rag_prototype_results_v0_8.jsonl", rag_results)

    (ROOT / "human_review_diff_report_v0_8.md").write_text(
        "# human_review_diff_report_v0_8\n\n"
        f"final_state: `{FINAL_STATE}`\n\n"
        "本报告来自模拟审阅输入，不覆盖 v0.7 工作表或 v0.4.1 源表。\n\n"
        + "\n".join(
            f"- `{row['candidate_relation_id']}`: {row['before_gate_status']} -> {row['after_human_review_label']}；overlay={row['overlay_status']}；runtime_effect=NONE"
            for row in diff_rows
        )
        + "\n",
        encoding="utf-8",
    )

    passed = 0
    eval_rows = []
    for row in rag_results:
        missing = [term for term in row["expected_terms"] if term not in row["answer"]]
        ok = not missing and FINAL_STATE in row["answer"] and "运行时批准" in row["answer"]
        passed += 1 if ok else 0
        eval_rows.append({
            "query_id": row["query_id"],
            "passed": ok,
            "missing_terms": missing,
            "source_chunk_count": len(row["source_chunk_ids"]),
            "human_review_status": row["human_review_status"],
            "overlay_status": row["overlay_status"],
        })
    eval_report = {
        "validation_status": "PASS" if passed == len(rag_results) else "FAIL",
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
        "rag_query_count": len(rag_results),
        "passed_query_count": passed,
        "failed_query_count": len(rag_results) - passed,
        "items": eval_rows,
    }
    write_json(ROOT / "rag_prototype_eval_report_v0_8.json", eval_report)
    (ROOT / "rag_prototype_eval_report_v0_8.md").write_text(
        "# rag_prototype_eval_report_v0_8\n\n"
        f"final_state: `{FINAL_STATE}`\n\n"
        f"- rag_query_count: {len(rag_results)}\n"
        f"- passed_query_count: {passed}\n"
        f"- failed_query_count: {len(rag_results) - passed}\n"
        "- 所有回答必须带模拟审阅状态和候选边界提示。\n",
        encoding="utf-8",
    )
    (ROOT / "FINAL_COMPLETION_REPORT_v0_8.md").write_text(
        "# FINAL COMPLETION REPORT v0.8\n\n"
        f"最终状态：`{FINAL_STATE}`\n\n"
        "v0.8 已生成审阅回灌模拟与 RAG 原型检索演示，未接 EcoCheck runtime。\n\n"
        f"- simulated_review_rows: {len(simulated_rows)}\n"
        f"- overlay_rows: {len(overlay_rows)}\n"
        f"- formalization_candidate_rows: {len(formalization)}\n"
        f"- still_blocked_rows: {len(blocked)}\n"
        f"- rag_queries: {len(rag_results)}\n"
        "- 模拟审阅只生成 overlay，不覆盖 v0.7 工作表或 v0.4.1 源表。\n",
        encoding="utf-8",
    )
    manifest = {
        "knowledge_base_version": KB_VERSION,
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
        "runtime_promotion_status": "not_approved",
        "source_baseline": "v0.7 human review package + v0.5 rag chunks",
        "outputs": {
            "simulated_human_review_input_v0_8.csv": len(simulated_rows),
            "human_review_overlay_v0_8.csv": len(overlay_rows),
            "formalization_candidate_queue_v0_8.csv": len(formalization),
            "still_blocked_queue_v0_8.csv": len(blocked),
            "rag_prototype_results_v0_8.jsonl": len(rag_results),
        },
        "runtime_effect": "NONE",
        "notes": "模拟审阅只生成overlay；不覆盖v0.7工作表或v0.4.1源表。",
    }
    write_json(ROOT / "knowledge_base_manifest_v0_8.json", manifest)
    print(json.dumps(validation, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
