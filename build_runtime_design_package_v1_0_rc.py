import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FINAL_STATE = "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"
RUNTIME_INTEGRATION = "disabled"
VERSION = "v1.0-rc-runtime-promotion-design-only"

GATES = [
    {
        "gate_id": "GATE-001",
        "gate_name": "candidate_source_freeze",
        "required_evidence": "v0.4.1/v0.5/v0.7/v0.8/v0.9 manifests and validation reports are PASS and immutable for the release candidate.",
        "blocks_until": "候选源数据版本冻结，且 hash/manifest 记录完整。",
        "owner_role": "TechLead",
    },
    {
        "gate_id": "GATE-002",
        "gate_name": "human_review_completion",
        "required_evidence": "All promoted rows have valid human_review_label, reviewer, reviewer_role, reviewed_at, notes, basis, evidence_refs, decision_confidence.",
        "blocks_until": "人工审阅签字留痕完整。",
        "owner_role": "ESO+ETO",
    },
    {
        "gate_id": "GATE-003",
        "gate_name": "second_approval",
        "required_evidence": "Formalization candidates are approved by Product+ETO+TechLead and have runtime scope explicitly granted.",
        "blocks_until": "二次审批通过，且审批记录不可篡改。",
        "owner_role": "Product+ETO+TechLead",
    },
    {
        "gate_id": "GATE-004",
        "gate_name": "runtime_contract_tests",
        "required_evidence": "Backend import contract, miniprogram display contract, RAG boundary contract, rollback contract all PASS.",
        "blocks_until": "契约测试全部通过。",
        "owner_role": "TechLead",
    },
    {
        "gate_id": "GATE-005",
        "gate_name": "rollback_ready",
        "required_evidence": "A versioned rollback manifest and previous runtime snapshot are available before any import.",
        "blocks_until": "可回滚版本与演练记录齐全。",
        "owner_role": "TechLead",
    },
    {
        "gate_id": "GATE-006",
        "gate_name": "audit_logging_ready",
        "required_evidence": "Every import/reject/promote/read path writes actor, role, source version, before/after hash and reason.",
        "blocks_until": "审计日志设计和测试通过。",
        "owner_role": "Security+TechLead",
    },
]

CONTRACT_FIELDS = [
    "runtime_candidate_id",
    "source_overlay_id",
    "candidate_relation_id",
    "industry_code",
    "entry_no",
    "target_management_condition",
    "human_review_label",
    "second_approval_id",
    "approved_runtime_scope",
    "source_basis",
    "evidence_refs",
    "open_question_refs",
    "risk_refs",
    "version_manifest_id",
    "rollback_manifest_id",
    "runtime_status",
]

FORBIDDEN = [
    "automatic_permit_type_generation",
    "automatic_inspection_template_generation",
    "automatic_deduct_generation",
    "runtime_import_without_second_approval",
    "score13_report_dimension_change_without_product_approval",
]


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


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


def write_md(path, title, lines):
    path.write_text("# " + title + "\n\n" + "\n".join(lines) + "\n", encoding="utf-8")


def build_mapping_rows():
    formalization = read_csv(ROOT / "formalization_candidate_queue_v0_8.csv")
    impact = {r["candidate_relation_id"]: r for r in read_csv(ROOT / "review_impact_analysis_v0_9.csv")}
    rows = []
    for row in formalization:
        relation_id = row["candidate_relation_id"]
        imp = impact.get(relation_id, {})
        rows.append({
            "runtime_candidate_id": f"RTC10RC::{relation_id}",
            "source_overlay_id": row["overlay_id"],
            "candidate_relation_id": relation_id,
            "industry_code": imp.get("industry_code", ""),
            "entry_no": imp.get("entry_no", ""),
            "target_management_condition": imp.get("target_management_condition", ""),
            "human_review_label": row["human_review_label"],
            "overlay_status": row["overlay_status"],
            "eligible_for_runtime_design": "DESIGN_ONLY_REQUIRES_SECOND_APPROVAL",
            "second_approval_required": "true",
            "second_approval_status": "NOT_STARTED",
            "approved_runtime_scope": "",
            "scenario_ids": imp.get("scenario_ids", "[]"),
            "score13_ids": imp.get("score13_ids", "[]"),
            "inspection_candidate_ids": imp.get("inspection_candidate_ids", "[]"),
            "source_basis": row["source_basis"],
            "evidence_refs": row["evidence_refs"],
            "open_question_refs": imp.get("open_question_refs", "[]"),
            "risk_refs": imp.get("risk_refs", "[]"),
            "version_manifest_id": "knowledge_base_manifest_v1_0_rc",
            "rollback_manifest_id": "rollback_manifest_design_v1_0_rc",
            "runtime_status": "NOT_IMPORTED_DESIGN_ONLY",
            "final_state": FINAL_STATE,
            "runtime_integration": RUNTIME_INTEGRATION,
            "runtime_effect": "NONE",
        })
    return rows


def main():
    mapping_rows = build_mapping_rows()
    write_csv(ROOT / "candidate_to_runtime_mapping_v1_0_rc.csv", mapping_rows)

    promotion_design = {
        "version": VERSION,
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
        "design_only": True,
        "gates": GATES,
        "forbidden_actions": FORBIDDEN,
        "minimum_release_rule": "No candidate row may be imported until all gates pass and second approval explicitly grants runtime scope.",
    }
    write_json(ROOT / "runtime_promotion_gate_design_v1_0_rc.json", promotion_design)
    write_md(ROOT / "runtime_promotion_gate_design_v1_0_rc.md", "runtime_promotion_gate_design_v1_0_rc", [
        f"final_state: `{FINAL_STATE}`",
        "",
        "本文件只设计候选知识进入运行时的闸门，不执行接入。",
        "",
        *[f"- `{g['gate_id']}` {g['gate_name']}: {g['blocks_until']}" for g in GATES],
        "",
        "禁止动作：",
        *[f"- `{item}`" for item in FORBIDDEN],
    ])

    data_contract = {
        "version": VERSION,
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
        "design_only": True,
        "required_fields": CONTRACT_FIELDS,
        "status_values": ["NOT_IMPORTED_DESIGN_ONLY", "APPROVED_FOR_IMPORT_PENDING_TESTS", "IMPORTED_WITH_ROLLBACK_READY"],
        "hard_rules": [
            "permit_type remains NEED_CONFIRM until a separate approved runtime mapping exists.",
            "inspection candidates do not become formal templates in this package.",
            "deduct values are not generated by this package.",
        ],
    }
    write_json(ROOT / "runtime_data_contract_v1_0_rc.json", data_contract)
    write_md(ROOT / "runtime_data_contract_v1_0_rc.md", "runtime_data_contract_v1_0_rc", [
        f"final_state: `{FINAL_STATE}`",
        "",
        "运行时数据契约只定义未来导入形态；本包不导入。",
        "",
        "必填字段：",
        *[f"- `{field}`" for field in CONTRACT_FIELDS],
    ])

    import_manifest = {
        "manifest_id": "runtime_import_candidate_manifest_v1_0_rc",
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
        "import_action": "NONE_DESIGN_ONLY",
        "candidate_count": len(mapping_rows),
        "source_files": [
            "formalization_candidate_queue_v0_8.csv",
            "review_impact_analysis_v0_9.csv",
            "candidate_to_runtime_mapping_v1_0_rc.csv",
        ],
        "all_candidates_require_second_approval": True,
        "all_candidates_runtime_status": "NOT_IMPORTED_DESIGN_ONLY",
    }
    write_json(ROOT / "runtime_import_candidate_manifest_v1_0_rc.json", import_manifest)

    write_md(ROOT / "runtime_rollback_plan_v1_0_rc.md", "runtime_rollback_plan_v1_0_rc", [
        f"final_state: `{FINAL_STATE}`",
        "",
        "本计划只描述未来接入时的回滚要求。",
        "",
        "- 导入前保存当前 runtime snapshot、schema version、manifest hash。",
        "- 每次导入必须生成 rollback_manifest_id。",
        "- 回滚必须能恢复上一版本候选映射、RAG索引和小程序展示配置。",
        "- 回滚演练通过前，不得进行任何 runtime import。",
    ])

    write_md(ROOT / "runtime_contract_test_plan_v1_0_rc.md", "runtime_contract_test_plan_v1_0_rc", [
        f"final_state: `{FINAL_STATE}`",
        "",
        "契约测试计划，不执行运行时代码修改。",
        "",
        "- Backend import contract: 拒绝缺少二次审批、缺少证据链、缺少rollback_manifest的导入。",
        "- Mini program presentation contract: 候选知识、人工审阅状态、运行时状态必须清晰区分。",
        "- RAG boundary contract: 回答必须携带候选边界、source chunks、review overlay status。",
        "- Scoring contract: 本包不得生成自动扣分或正式检查模板。",
        "- Rollback contract: 模拟导入后必须可恢复上一 manifest。",
    ])

    write_md(ROOT / "approval_workflow_v1_0_rc.md", "approval_workflow_v1_0_rc", [
        f"final_state: `{FINAL_STATE}`",
        "",
        "审批流设计：",
        "",
        "1. ESO/ETO 完成人工审阅并形成 overlay。",
        "2. Domain owner 关闭 P0/P1 open questions 或接受风险。",
        "3. Product 审批展示范围和报告口径。",
        "4. TechLead 审批数据契约、回滚方案和契约测试。",
        "5. 安全/审计确认日志字段。",
        "6. 另起实现任务，严禁本设计包直接接入 runtime。",
        "本设计包不执行导入、不修改 EcoCheck 小程序、不生成正式模板、不自动扣分。",
    ])

    audit_design = {
        "version": VERSION,
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
        "events": [
            "candidate_selected_for_promotion",
            "second_approval_granted",
            "runtime_import_attempted",
            "runtime_import_rejected",
            "runtime_import_completed",
            "rollback_started",
            "rollback_completed",
            "rag_answer_served_from_promoted_knowledge",
        ],
        "required_audit_fields": [
            "event_id", "actor_id", "actor_role", "timestamp", "source_manifest_id",
            "runtime_candidate_id", "before_hash", "after_hash", "reason", "approval_id",
            "rollback_manifest_id", "request_id",
        ],
    }
    write_json(ROOT / "security_audit_log_design_v1_0_rc.json", audit_design)
    write_md(ROOT / "security_audit_log_design_v1_0_rc.md", "security_audit_log_design_v1_0_rc", [
        f"final_state: `{FINAL_STATE}`",
        "",
        "审计日志设计要求所有未来导入、拒绝、回滚和RAG服务事件可追溯。",
        "",
        "必填审计字段：",
        *[f"- `{field}`" for field in audit_design["required_audit_fields"]],
    ])

    manifest = {
        "knowledge_base_version": VERSION,
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
        "runtime_promotion_status": "DESIGN_ONLY_NOT_APPROVED",
        "runtime_effect": "NONE",
        "candidate_mapping_rows": len(mapping_rows),
        "outputs": [
            "PROJECT_INDEX_v1_0_rc.md",
            "HANDOFF_v1_0_rc.md",
            "DEPRECATED_AND_REMOVED_FILES_v1_0_rc.md",
            "runtime_promotion_gate_design_v1_0_rc.md/json",
            "runtime_data_contract_v1_0_rc.md/json",
            "runtime_import_candidate_manifest_v1_0_rc.json",
            "runtime_rollback_plan_v1_0_rc.md",
            "runtime_contract_test_plan_v1_0_rc.md",
            "approval_workflow_v1_0_rc.md",
            "security_audit_log_design_v1_0_rc.md/json",
            "candidate_to_runtime_mapping_v1_0_rc.csv",
        ],
    }
    write_json(ROOT / "knowledge_base_manifest_v1_0_rc.json", manifest)
    write_md(ROOT / "PROJECT_INDEX_v1_0_rc.md", "PROJECT_INDEX_v1_0_rc", [
        f"final_state: `{FINAL_STATE}`",
        "runtime_integration: `disabled`",
        "",
        "本目录阶段性封版为 `v1.0-rc design-only baseline`，定位是行业私有知识库候选治理底座，不是 EcoCheck 运行时数据包。",
        "",
        "## 当前主入口",
        "",
        "- `FINAL_COMPLETION_REPORT_v1_0_rc.md`: v1.0-rc 总结。",
        "- `knowledge_base_manifest_v1_0_rc.json`: 当前封版 manifest。",
        "- `PROJECT_INDEX_v1_0_rc.md`: 本索引。",
        "- `HANDOFF_v1_0_rc.md`: 后续人审、RAG demo、运行时接入分支交接说明。",
        "- `DEPRECATED_AND_REMOVED_FILES_v1_0_rc.md`: 已移出当前主线的历史入口说明。",
        "",
        "## 核心数据入口",
        "",
        "- `all_context_applicability_review_v0_4_1.csv/json`: 22815 条候选适用关系，全部候选化。",
        "- `all_permit_condition_backfill_v0_4_1.csv/json`: 336 条许可名录条件治理，覆盖 1-112 条 x 三类管理条件。",
        "- `scenario_templates.json`: 产污场景模板，是知识本体核心，不是行业硬编码。",
        "- `scenario_to_score13_mapping_v0_3.csv`: 场景到 EcoCheck S01-S13 的候选语义映射。",
        "- `inspection_candidate_recommendations_v0_3.csv`: 候选排查建议，不能直接生成正式检查模板。",
        "- `open_questions_v0_4_1.csv`: 高风险开放问题。",
        "- `risk_acceptance_queue_v0_4_1.csv`: 运行时阻断风险队列。",
        "",
        "## 审阅与回灌入口",
        "",
        "- `human_review_queue_v0_7.csv/json`: 全量人工审阅队列。",
        "- `human_review_worksheet_v0_7.xlsx`: 可填写审阅工作表，原始表不得预填人工确认。",
        "- `human_review_overlay_v0_8.csv/json`: 模拟审阅回灌 overlay 示例。",
        "- `review_impact_analysis_v0_9.csv/json`: 审阅结论影响传播分析。",
        "- `review_impact_graph_edges_v0_9.jsonl`: 审阅影响图谱边。",
        "",
        "## RAG 与图谱入口",
        "",
        "- `kb_graph_schema_v0_5.md`: 图谱 schema。",
        "- `graph_nodes_v0_5.jsonl`: 候选图谱节点。",
        "- `graph_edges_v0_5.jsonl`: 候选图谱边。",
        "- `rag_chunks_v0_5.jsonl`: RAG chunk。",
        "- `retrieval_eval_set_v0_6.jsonl`: RAG/图谱检索评测集。",
        "- `graph_query_samples_v0_6.jsonl`: 图谱查询样例。",
        "- `rag_prototype_results_v0_8.jsonl`: 带审阅状态和候选边界的 RAG 原型结果。",
        "",
        "## v1.0-rc 运行时接入设计入口",
        "",
        "- `runtime_promotion_gate_design_v1_0_rc.md/json`: 候选进入运行时前的闸门设计。",
        "- `runtime_data_contract_v1_0_rc.md/json`: 未来运行时数据契约设计。",
        "- `runtime_import_candidate_manifest_v1_0_rc.json`: 设计态导入候选 manifest，import_action 必须为 NONE_DESIGN_ONLY。",
        "- `runtime_rollback_plan_v1_0_rc.md`: 未来接入前回滚要求。",
        "- `runtime_contract_test_plan_v1_0_rc.md`: 后端、前端呈现、RAG 边界、回滚契约测试计划。",
        "- `approval_workflow_v1_0_rc.md`: 二次审批流设计。",
        "- `security_audit_log_design_v1_0_rc.md/json`: 审计日志设计。",
        "- `candidate_to_runtime_mapping_v1_0_rc.csv`: 仅设计态候选映射，不得导入运行时。",
        "",
        "## 验证命令",
        "",
        "按顺序执行：",
        "",
        "```powershell",
        "python build_knowledge_base_v0_4_1.py",
        "python validate_knowledge_base_v0_4_1.py",
        "python build_graph_rag_package_v0_5.py",
        "python validate_graph_rag_package_v0_5.py",
        "python build_rag_graph_eval_v0_6.py",
        "python validate_rag_graph_eval_v0_6.py",
        "python build_human_review_package_v0_7.py",
        "python validate_human_review_package_v0_7.py",
        "python build_review_backfill_rag_prototype_v0_8.py",
        "python validate_review_backfill_rag_prototype_v0_8.py",
        "python build_review_impact_graph_v0_9.py",
        "python validate_review_impact_graph_v0_9.py",
        "python build_runtime_design_package_v1_0_rc.py",
        "python validate_runtime_design_package_v1_0_rc.py",
        "```",
        "",
        "注意：大 JSONL 构建和验证不要并行跑，必须先 build 完成再 validate。",
        "",
        "## 禁止事项",
        "",
        "- 不接 EcoCheck runtime。",
        "- 不改 EcoCheck 小程序。",
        "- 不生成正式 `permit_type`。",
        "- 不生成正式检查模板。",
        "- 不自动扣分。",
        "- 不伪造 `human_review_label`、`human_reviewer`、`reviewed_at`。",
        "- 不把 `DIVISION_CONTEXT` 当作适用证据。",
        "- 不把旧 `12个优先行业规则库_v1.1接入版` 当作当前入口。",
    ])
    write_md(ROOT / "HANDOFF_v1_0_rc.md", "HANDOFF_v1_0_rc", [
        f"final_state: `{FINAL_STATE}`",
        "runtime_integration: `disabled`",
        "",
        "## 封版结论",
        "",
        "本知识库治理线已阶段性封版为 `v1.0-rc design-only baseline`。当前资产可用于人工审阅、RAG demo、图谱样例和未来运行时接入方案评审，但不能直接投产。",
        "",
        "## 下一阶段建议",
        "",
        "1. 人工审阅：从 `human_review_worksheet_v0_7.xlsx` 开始，审阅人员只填写开放字段，不修改候选源表。",
        "2. RAG demo：使用 `rag_chunks_v0_5.jsonl`、`retrieval_eval_set_v0_6.jsonl` 和 `rag_prototype_results_v0_8.jsonl`，回答必须展示候选边界和审阅状态。",
        "3. 图谱 demo：使用 `graph_nodes_v0_5.jsonl`、`graph_edges_v0_5.jsonl`、`review_impact_graph_edges_v0_9.jsonl` 展示行业、许可条件、场景、13维、排查项影响链。",
        "4. EcoCheck 接入：必须另开实现任务或分支，先通过 `runtime_promotion_gate_design_v1_0_rc.md` 中全部闸门。",
        "",
        "## 真正接入前置条件",
        "",
        "- 人工审阅字段完整，且无伪造审阅。",
        "- P0/P1 open questions 关闭或有签字风险接受。",
        "- Product、ETO、TechLead 完成二次审批。",
        "- 后端导入契约、前端呈现契约、RAG 边界契约、回滚契约全部通过。",
        "- 导入前生成版本冻结 manifest、rollback manifest 和审计日志方案。",
        "",
        "## 已清理的历史入口",
        "",
        "旧 `12个优先行业规则库_v1.1接入版` 属于早期试跑的运行时接入口径，和当前候选治理边界冲突，已从当前主线移除。12个优先行业本身已经进入全量新底座，不需要保留旧接入版文件。",
    ])
    write_md(ROOT / "DEPRECATED_AND_REMOVED_FILES_v1_0_rc.md", "DEPRECATED_AND_REMOVED_FILES_v1_0_rc", [
        f"final_state: `{FINAL_STATE}`",
        "runtime_integration: `disabled`",
        "",
        "以下文件属于早期试跑或旧运行时接入口径，已不属于当前 v1.0-rc design-only baseline 主线。",
        "",
        "## 已移除",
        "",
        "- `12个优先行业规则库_v1.1接入版.json`: 早期 12 行业接入版，直接给出 `permit_type` 并声明可接入小程序，和当前候选治理边界冲突。",
        "- `v1.1更新说明.md`: 旧接入版说明，包含“可直接导入小程序使用”等过时口径。",
        "- `generate_rules_v1_1_complete.py`: 旧接入版生成脚本。",
        "- `build_knowledge_base.py`: 依赖旧 v1.1 JSON 的历史构建入口。",
        "",
        "## 保留但不作为当前主入口",
        "",
        "早期 v0.1-v0.3 产物保留为审计链路和可追溯证据；当前主入口以 `PROJECT_INDEX_v1_0_rc.md`、`knowledge_base_manifest_v1_0_rc.json` 和 `FINAL_COMPLETION_REPORT_v1_0_rc.md` 为准。",
        "",
        "## 迁移说明",
        "",
        "12个优先行业已经纳入 1382 个四位小类候选底座，不再需要旧接入版文件。后续若要做运行时接入，必须从 v1.0-rc 闸门设计另起实现，不得恢复旧接入版直接导入路径。",
    ])
    write_md(ROOT / "FINAL_COMPLETION_REPORT_v1_0_rc.md", "FINAL_COMPLETION_REPORT_v1_0_rc", [
        f"最终状态：`{FINAL_STATE}`",
        "",
        "v1.0-rc 已生成运行时接入方案设计包，未接 EcoCheck runtime。",
        "",
        f"- candidate_mapping_rows: {len(mapping_rows)}",
        "- runtime_integration: disabled",
        "- runtime_effect: NONE",
        "- 不生成正式 permit_type、正式检查模板或自动扣分。",
        "- 新增 `PROJECT_INDEX_v1_0_rc.md` 和 `HANDOFF_v1_0_rc.md`，作为封版总入口和后续交接入口。",
        "- 旧 v1.1 接入版入口已从当前主线移除，详见 `DEPRECATED_AND_REMOVED_FILES_v1_0_rc.md`。",
    ])
    print(json.dumps({"final_state": FINAL_STATE, "candidate_mapping_rows": len(mapping_rows)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
