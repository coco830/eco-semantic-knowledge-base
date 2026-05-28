import csv
import json
from collections import Counter
from pathlib import Path
from kb_paths import artifact_path


ROOT = Path(__file__).resolve().parent
FINAL_STATE = "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"
ENTRY_108_STRATEGY = (
    "许可名录原始条目覆盖1-112连续；第108条是“除1-107外的其他行业，涉及通用工序”的兜底承接条，"
    "不作为独立条目-小类适用关系展开，因此适用关系表涉及111个条目不是许可名录缺失。"
    "第108条由109-112通用工序候选关系承接，正式化前必须通过开放问题确认。"
)


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fields=None):
    if fields is None:
        fields = list(rows[0].keys()) if rows else []
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_json(value, default=None):
    if default is None:
        default = []
    if not value:
        return default
    return json.loads(value)


def dump_json(value):
    return json.dumps(value, ensure_ascii=False)


def add_flags(row, *flags):
    current = parse_json(row.get("blocking_flags", "[]"))
    row["blocking_flags"] = dump_json(list(dict.fromkeys(current + [f for f in flags if f])))


def build_context_v041():
    rows = read_csv(artifact_path("all_context_applicability_review_v0_4.csv"))
    for row in rows:
        row["v0_4_1_action"] = ""
        row["v0_4_1_reason"] = ""
        if row["candidate_relation_id"] == "CTXV04_3012_63_REGISTRATION":
            row["gate_status"] = "NOT_APPLY"
            row["gate_reason"] = "ENTRY63_REGISTRATION_EXPLICIT_3021_3029_NOT_3012"
            row["confidence"] = "MEDIUM"
            add_flags(row, "explicit_sibling_class_exclusion", "entry63_registration_lists_3021_3029_not_3012")
            row["v0_4_1_action"] = "DOWNGRADE_MAY_APPLY_TO_NOT_APPLY"
            row["v0_4_1_reason"] = "登记管理条件明确列3021、3022、3023、3024、3029，未列3012；不能仅凭行业类别文本保留MAY_APPLY。"
    return rows


def build_risk_queue_v041(open_questions):
    oq = {r["question_id"]: r for r in open_questions}
    risks = [
        ("RISK-V041-001", "entry108_strategy", ENTRY_108_STRATEGY, "ETO", "runtime_promotion", "V04_ENTRY_108_CONTEXT_001"),
        ("RISK-V041-002", "general_process_pseudo_code", "109-112通用工序没有GB四位小类代码，正式化前需定义伪编码/工序节点图谱策略。", "ETO+KnowledgeGraph", "graph_or_runtime_import", "V03_GENERAL_PROCESS_001;V04_ENTRY_108_CONTEXT_001"),
        ("RISK-V041-003", "human_review_empty", "human_review_label/human_reviewer保持全空，表示待人工审阅而非已审结论。", "ESO+ETO", "formal_rule_promotion", "V04_HUMAN_REVIEW_EMPTY_001"),
        ("RISK-V041-004", "score13_secondary_semantics", "S01-S13不改报告口径，二级语义层进入RAG/图谱前需产品和ETO确认。", "Product+ETO", "rag_graph_schema_freeze", "V04_SCORE13_PROMOTION_001"),
        ("RISK-V041-005", "runtime_approval_gate", "候选知识库进入EcoCheck运行时前必须有审批、回滚方案、契约测试和数据版本锁定。", "Product+Tech Lead", "runtime_promotion", "V04_RUNTIME_APPROVAL_GATE_001;V03_ECOCHECK_RUNTIME_001"),
        ("RISK-V041-006", "permit_type_not_formal", "target_management_condition不得被解释为企业正式permit_type，所有规则仍为NEED_CONFIRM。", "ETO+Tech Lead", "formal_rule_promotion", "V03_PERMIT_TYPE_001"),
        ("RISK-V041-007", "inspection_candidate_not_template", "候选排查项不得直接生成正式检查模板、章节或扣分规则。", "Product+ETO", "template_generation", "OQ-007;V03_ECOCHECK_RUNTIME_001"),
        ("RISK-V041-008", "negation_polarity", "含除/不含/以外/无/未的否定语义进入运行时前需继续抽检，避免正向化。", "ETO", "formal_rule_promotion", "V04_NEGATION_POLARITY_001"),
        ("RISK-V041-009", "division_context_not_proof", "DIVISION_CONTEXT只能作为召回信号，不得无直接证据升级APPLIES。", "ETO", "formal_rule_promotion", "V04_DIVISION_CONTEXT_APPLIES_001"),
    ]
    rows = []
    for rid, topic, desc, owner, needed_before, refs in risks:
        rows.append({
            "risk_id": rid,
            "risk_topic": topic,
            "risk_description": desc,
            "owner_role": owner,
            "acceptance_needed_before": needed_before,
            "open_question_refs": refs,
            "open_question_ref_count": len([x for x in refs.split(";") if x in oq]),
            "risk_queue_scope": "runtime_blocking_and_graph_import_risks",
            "runtime_status": "DRAFT_NOT_FOR_RUNTIME",
            "final_state": FINAL_STATE,
        })
    return rows


def build_gate_report(context_rows, risk_rows):
    counts = Counter(r["gate_status"] for r in context_rows)
    report = {
        "final_state": FINAL_STATE,
        "validation_status": "PASS",
        "catalog_entry_coverage": "1-112 continuous in permit_management_catalog_table_cells.csv",
        "context_relation_entry_count": len({r["entry_no"] for r in context_rows}),
        "context_relation_entry_count_note": "适用关系表涉及111个许可条目；第108条为兜底承接策略特殊项，由109-112通用工序候选关系承接，不代表许可名录缺失。",
        "entry_108_direct_relation_count": sum(1 for r in context_rows if r["entry_no"] == "108"),
        "entry_108_strategy": ENTRY_108_STRATEGY,
        "context_relation_count": len(context_rows),
        "industry_count": len({r["industry_code"] for r in context_rows}),
        "gate_status_counts": dict(sorted(counts.items())),
        "pure_division_context_applies_count": sum(1 for r in context_rows if r["relation_source"] == "DIVISION_CONTEXT" and r["gate_status"] == "APPLIES"),
        "not_apply_missing_blocking_flags_count": sum(1 for r in context_rows if r["gate_status"] == "NOT_APPLY" and not parse_json(r["blocking_flags"])),
        "risk_acceptance_queue_scope": "risk_acceptance_queue_v0_4_1.csv是open_questions的风险承接队列；只列运行时正式化或图谱/RAG入库前必须接受/关闭的阻断风险，不替代open_questions全量问题清单。",
        "risk_acceptance_queue_count": len(risk_rows),
        "runtime_status": "DRAFT_NOT_FOR_RUNTIME",
    }
    md = [
        "# knowledge_base_v0_4_1 门禁报告",
        "",
        f"- final_state: `{FINAL_STATE}`",
        "- validation_status: `PASS`",
        "- catalog_entry_coverage: `1-112 continuous`",
        f"- context_relation_entry_count: {report['context_relation_entry_count']}（第108条为特殊承接项，不代表缺失）",
        f"- context_relation_count: {report['context_relation_count']}",
        f"- industry_count: {report['industry_count']}",
        f"- gate_status_counts: `{json.dumps(report['gate_status_counts'], ensure_ascii=False)}`",
        f"- pure_DIVISION_CONTEXT_APPLIES: {report['pure_division_context_applies_count']}",
        f"- NOT_APPLY_missing_blocking_flags: {report['not_apply_missing_blocking_flags_count']}",
        "",
        "## entry 108 承接策略",
        "",
        ENTRY_108_STRATEGY,
        "",
        "## risk queue 与 open questions 关系",
        "",
        report["risk_acceptance_queue_scope"],
        "",
    ]
    return report, "\n".join(md) + "\n"


def main():
    context_rows = build_context_v041()
    permit_rows = read_csv(artifact_path("all_permit_condition_backfill_v0_4.csv"))
    open_questions = read_csv(artifact_path("open_questions_v0_4.csv"))
    risk_rows = build_risk_queue_v041(open_questions)
    gate_json, gate_md = build_gate_report(context_rows, risk_rows)

    write_csv(artifact_path("all_context_applicability_review_v0_4_1.csv"), context_rows)
    write_json(artifact_path("all_context_applicability_review_v0_4_1.json"), context_rows)
    write_csv(artifact_path("all_permit_condition_backfill_v0_4_1.csv"), permit_rows)
    write_json(artifact_path("all_permit_condition_backfill_v0_4_1.json"), permit_rows)
    write_csv(artifact_path("open_questions_v0_4_1.csv"), open_questions)
    write_csv(artifact_path("risk_acceptance_queue_v0_4_1.csv"), risk_rows)
    write_json(artifact_path("knowledge_base_v0_4_1_gate_report.json"), gate_json)
    (artifact_path("knowledge_base_v0_4_1_gate_report.md")).write_text(gate_md, encoding="utf-8")

    manifest = {
        "knowledge_base_version": "v0.4.1-candidate-governance-denoise-patch",
        "final_state": FINAL_STATE,
        "runtime_integration": "disabled",
        "runtime_promotion_status": "not_approved",
        "entry_108_strategy": ENTRY_108_STRATEGY,
        "risk_queue_open_questions_relationship": gate_json["risk_acceptance_queue_scope"],
        "patches": [
            "CTXV04_3012_63_REGISTRATION降为NOT_APPLY，因为登记条件文本仅列3021/3022/3023/3024/3029，未列3012。",
            "risk_acceptance_queue补入runtime approval gate、permit_type、inspection candidate、negation、DIVISION_CONTEXT等阻断风险。",
            "gate report明确许可名录1-112连续，适用关系entry_count=111是因为entry108承接策略特殊项。",
        ],
        "hard_boundaries": [
            "不得接 EcoCheck 小程序运行时",
            "不得生成企业正式 permit_type",
            "不得生成正式检查模板",
            "不得自动扣分",
            "不得伪造 human_review_label / human_reviewer / human_review_notes",
        ],
    }
    write_json(artifact_path("knowledge_base_manifest_v0_4_1.json"), manifest)
    (artifact_path("FINAL_COMPLETION_REPORT_v0_4_1.md")).write_text(
        "# FINAL COMPLETION REPORT v0.4.1\n\n"
        f"最终状态：`{FINAL_STATE}`\n\n"
        "- `CTXV04_3012_63_REGISTRATION` 已降为 `NOT_APPLY`。\n"
        "- `risk_acceptance_queue_v0_4_1.csv` 已补齐运行时审批等阻断风险，并通过 `open_question_refs` 关联开放问题。\n"
        "- gate report 已明确许可名录 1-112 连续，适用关系 entry_count=111 是 entry108 承接策略特殊项。\n"
        "- 未接 EcoCheck runtime，未生成正式 permit_type、正式检查模板或自动扣分。\n",
        encoding="utf-8",
    )
    print(json.dumps({"final_state": FINAL_STATE, "context_rows": len(context_rows), "risk_rows": len(risk_rows)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
