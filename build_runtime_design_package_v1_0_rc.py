import csv
import json
from pathlib import Path
from kb_paths import artifact_path


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

OPEN_QUESTION_REVIEW_ROWS = [
    {
        "question_id": "OQ-001",
        "ask_who": "ETO；必要时由资料负责人提供GB/T 4754原表截图",
        "concrete_question": "请确认GB/T 4754-2017中1512是否为白酒制造、1513是否为啤酒制造；早期规则中是否仍有把1512当作啤酒制造的残留。",
        "check_materials": "2017国民经济行业分类注释.xlsx；industry_catalog_base.csv；all_industry_scenario_candidates_v0_2.csv；旧12行业试跑资料如仍有留档也要核对。",
        "decision_options": "CONFIRM_FIXED；NEED_MORE_SOURCE；NEED_RULE_FIX",
        "evidence_to_record": "GB/T 4754原表行号/截图；修正前后代码名称对照；受影响candidate_rule_id清单。",
        "close_condition": "1512=白酒制造、1513=啤酒制造的口径已写入候选底座，且无旧错配入口残留。",
        "runtime_effect": "关闭前不得把1512/1513相关候选升级为运行时正式规则。",
    },
    {
        "question_id": "OQ-002",
        "ask_who": "ETO",
        "concrete_question": "名录条目只写代表性小类或行业短语时，是否允许外推到同组、同中类或同大类其他四位小类？哪些情况下必须禁止外推？",
        "check_materials": "固定污染源排污许可分类管理名录原文；GB/T 4754小类解释；all_context_applicability_review_v0_4_1.csv中relation_source和matched_code_or_text。",
        "decision_options": "ALLOW_GROUP_INHERIT；ALLOW_CLASS_ONLY；NEED_EIA_CONFIRM；REJECT_INHERIT",
        "evidence_to_record": "外推规则说明；可外推/不可外推示例；受影响entry_no和industry_code。",
        "close_condition": "形成代表性小类外推规则，并标明默认不得从DIVISION_CONTEXT直接升级APPLIES。",
        "runtime_effect": "关闭前所有代表性小类外推关系保持候选或待确认。",
    },
    {
        "question_id": "OQ-003",
        "ask_who": "ETO",
        "concrete_question": "第36条纸浆制造221与2211、222、223之间的继承边界是什么？是否仅限221相关小类，不得继承到造纸222或纸制品223？",
        "check_materials": "名录第36条；GB/T 4754中221/222/223定义；相关候选关系表。",
        "decision_options": "LIMIT_TO_221；EXTEND_WITH_EVIDENCE；NEED_EIA_CONFIRM；REJECT_CANDIDATE",
        "evidence_to_record": "221/222/223边界说明；名录原文截图；被调整关系清单。",
        "close_condition": "纸浆、造纸、纸制品相邻中类边界形成书面口径。",
        "runtime_effect": "关闭前不得把221、222、223相邻关系作为正式适用依据。",
    },
    {
        "question_id": "OQ-004",
        "ask_who": "ETO",
        "concrete_question": "第38条纸制品制造223是否不得继承到2211/222类？工业废水、废气条件分别由什么现场事实触发？",
        "check_materials": "名录第38条；纸制品相关环评/许可样例；all_context_applicability_review_v0_4_1.csv。",
        "decision_options": "LIMIT_TO_223；TRIGGER_BY_WASTEWATER；TRIGGER_BY_EXHAUST；NEED_SITE_CONFIRM",
        "evidence_to_record": "223适用边界；废水/废气触发条件；确认问题模板。",
        "close_condition": "形成纸制品条目-小类适用规则和现场确认问题。",
        "runtime_effect": "关闭前纸制品跨中类关系保持NEED_EIA_OR_PERMIT_CONFIRM。",
    },
    {
        "question_id": "OQ-005",
        "ask_who": "ETO",
        "concrete_question": "食品/农副食品条目中的通用工序触发，是否只能作为召回线索，不能直接推导企业许可管理类型？",
        "check_materials": "名录第15条及相关食品条目；企业环评/许可样例；109-112通用工序条目。",
        "decision_options": "RECALL_ONLY；MAY_APPLY_WITH_EVIDENCE；NEED_EIA_CONFIRM",
        "evidence_to_record": "通用工序清单；对应证据要求；不得直接生成permit_type的说明。",
        "close_condition": "通用工序触发统一限定为MAY_APPLY或NEED_EIA_OR_PERMIT_CONFIRM，除非有直接证据。",
        "runtime_effect": "关闭前不得由通用工序候选自动生成正式permit_type。",
    },
    {
        "question_id": "OQ-006",
        "ask_who": "ETO",
        "concrete_question": "装备、金属制品相关条目中，3311等相邻小类如何根据表面处理、喷涂、热处理、工业炉窑等工序确认适用？",
        "check_materials": "名录第80条；GB/T 4754中3311及相邻小类；企业工艺流程、环评、许可。",
        "decision_options": "DIRECT_CODE_ONLY；PROCESS_TRIGGER_MAY_APPLY；NEED_SITE_CONFIRM；REJECT_ADJACENT_CLASS",
        "evidence_to_record": "3311及相关小类边界；工序触发证据链；受影响候选关系。",
        "close_condition": "形成3311及相关小类的工序触发边界和确认证据要求。",
        "runtime_effect": "关闭前相邻小类不得仅凭大类上下文升级APPLIES。",
    },
    {
        "question_id": "OQ-007",
        "ask_who": "Product+ETO",
        "concrete_question": "候选排查章节和S18/S19等知识库章节编号，是否只作为未来候选子章，不映射为当前EcoCheck正式模板章节？",
        "check_materials": "inspection_candidate_recommendations_v0_3.csv；当前EcoCheck首次/月度模板；产品报告章节口径。",
        "decision_options": "CANDIDATE_ONLY；MAP_TO_EXISTING_SECTION；NEED_PRODUCT_APPROVAL",
        "evidence_to_record": "章节映射表；不接运行时声明；如映射需产品审批记录。",
        "close_condition": "产品和ETO确认正式模板章节映射方案；未经审批不得接运行时。",
        "runtime_effect": "关闭前不得生成正式检查模板或自动扣分。",
    },
    {
        "question_id": "V03_CONTEXT_SCOPE_001",
        "ask_who": "ETO",
        "concrete_question": "DIVISION_CONTEXT是否只能作为召回线索？什么证据足以把MAY_APPLY/NEED_EIA升级为APPLIES？",
        "check_materials": "all_context_applicability_review_v0_4_1.csv；relation_source；matched_code_or_text；名录原文。",
        "decision_options": "RECALL_ONLY；APPLIES_WITH_DIRECT_CODE；APPLIES_WITH_NAME_TEXT；NEED_HUMAN_REVIEW",
        "evidence_to_record": "升级证据字段要求；人工审阅字段要求；示例关系ID。",
        "close_condition": "形成DIVISION_CONTEXT升级规则，且保留人工审阅要求。",
        "runtime_effect": "关闭前DIVISION_CONTEXT不能直接进入运行时正式适用关系。",
    },
    {
        "question_id": "V03_PERMIT_TYPE_001",
        "ask_who": "ETO",
        "concrete_question": "target_management_condition是否只表示名录条件列，不等于企业正式permit_type？正式permit_type需哪些材料确认？",
        "check_materials": "all_permit_condition_backfill_v0_4_1.csv；企业排污许可证/登记回执；环评批复。",
        "decision_options": "COLUMN_ONLY；CAN_PROMOTE_WITH_PERMIT_EVIDENCE；NEED_PERMIT_CONFIRM",
        "evidence_to_record": "字段定义；正式permit_type确认材料清单；禁止自动生成说明。",
        "close_condition": "形成target_management_condition和permit_type字段边界说明。",
        "runtime_effect": "关闭前不得由候选条件列生成企业正式permit_type。",
    },
    {
        "question_id": "V03_GENERAL_PROCESS_001",
        "ask_who": "ETO",
        "concrete_question": "109-112通用工序如何依据锅炉、工业炉窑、表面处理、水处理事实确认？每类工序需要什么证据？",
        "check_materials": "名录109-112条；工艺流程图；设备清单；环评/许可；现场照片。",
        "decision_options": "CONFIRM_BY_EIA；CONFIRM_BY_PERMIT；CONFIRM_BY_SITE；NOT_APPLY",
        "evidence_to_record": "四类通用工序证据清单；确认问题；适用/不适用样例。",
        "close_condition": "形成109-112通用工序证据要求和适用关系规则。",
        "runtime_effect": "关闭前通用工序只能作为候选触发。",
    },
    {
        "question_id": "V03_SCENARIO_TEMPLATE_001",
        "ask_who": "ETO",
        "concrete_question": "是否需要新增尾矿库、餐饮油烟、实验室废液、垃圾焚烧/填埋等场景模板？哪些已有模板可覆盖，哪些必须新增？",
        "check_materials": "scenario_templates.json；行业样例；环保设施/风险单元清单；法规技术规范。",
        "decision_options": "COVERED_BY_EXISTING；ADD_NEW_SCENARIO；KEEP_OPEN",
        "evidence_to_record": "新增/不新增理由；触发条件；证据要求；photo_points。",
        "close_condition": "完成场景模板缺口评审，新增模板或明确延后。",
        "runtime_effect": "关闭前不影响候选库，但会影响RAG/图谱覆盖度。",
    },
    {
        "question_id": "V03_ECOCHECK_RUNTIME_001",
        "ask_who": "Product+ETO+Tech Lead",
        "concrete_question": "候选排查项在什么审批和测试条件下，才允许进入EcoCheck运行时？",
        "check_materials": "runtime_promotion_gate_design_v1_0_rc.md；runtime_contract_test_plan_v1_0_rc.md；approval_workflow_v1_0_rc.md。",
        "decision_options": "BLOCK_RUNTIME；APPROVE_DESIGN_ONLY；APPROVE_IMPLEMENTATION_BRANCH",
        "evidence_to_record": "审批记录；契约测试结果；回滚方案；版本manifest。",
        "close_condition": "形成运行时接入审批、回滚和契约测试方案。",
        "runtime_effect": "关闭前不得接小程序或后端运行时。",
    },
    {
        "question_id": "V04_ENTRY_108_CONTEXT_001",
        "ask_who": "ETO",
        "concrete_question": "第108条是否只作为“除1-107外其他行业+通用工序”的兜底引用？是否仍由109-112通用工序承接，而不生成独立全行业关系？",
        "check_materials": "名录第108-112条；knowledge_base_v0_4_1_gate_report.md；all_context_applicability_review_v0_4_1.csv。",
        "decision_options": "CROSS_REFERENCE_ONLY；ADD_EXPLICIT_RELATIONS；KEEP_OPEN",
        "evidence_to_record": "第108条承接策略；不生成全行业笛卡尔关系的理由；如新增需关系表设计。",
        "close_condition": "确认第108条承接策略，并写入manifest/gate report。",
        "runtime_effect": "关闭前第108条不得被误读为覆盖缺失或独立行业规则。",
    },
    {
        "question_id": "V04_HUMAN_REVIEW_EMPTY_001",
        "ask_who": "ETO+ESO",
        "concrete_question": "人工审阅工作表由谁审？抽样还是全量？每个标签需要哪些必填字段和签字留痕？",
        "check_materials": "human_review_worksheet_v0_7.xlsx；human_review_decision_schema_v0_7.md；human_review_guidance_v0_7.md。",
        "decision_options": "DEFINE_FULL_REVIEW；DEFINE_SAMPLING_REVIEW；KEEP_ALL_EMPTY",
        "evidence_to_record": "审阅责任人；标签枚举；review_basis/evidence_refs填写规则；签字留痕。",
        "close_condition": "完成审阅标签枚举、审阅责任和签字留痕制度。",
        "runtime_effect": "关闭前不得把空人工审阅字段解释为已确认。",
    },
    {
        "question_id": "V04_SCORE13_PROMOTION_001",
        "ask_who": "Product+ETO",
        "concrete_question": "S01-S13报告口径保持不变时，S07/S08/S10/S13二级语义如何进入RAG、图谱和报告段落提示？",
        "check_materials": "scenario_to_score13_mapping_v0_3.csv；score13_review.md；EcoCheck报告模板。",
        "decision_options": "GRAPH_ONLY；RAG_AND_REPORT_HINT；CHANGE_REQUIRES_APPROVAL",
        "evidence_to_record": "二级语义字段表；报告展示策略；不改13维名称说明。",
        "close_condition": "形成二级语义层字段与报告展示策略，不直接改名或拆分S01-S13。",
        "runtime_effect": "关闭前不得改变EcoCheck报告13维口径。",
    },
    {
        "question_id": "V04_RUNTIME_APPROVAL_GATE_001",
        "ask_who": "Product+Tech Lead",
        "concrete_question": "候选知识库何时、由谁、凭什么验证证据批准进入EcoCheck运行时？失败后如何回滚？",
        "check_materials": "runtime_promotion_gate_design_v1_0_rc.md；runtime_rollback_plan_v1_0_rc.md；security_audit_log_design_v1_0_rc.md。",
        "decision_options": "DESIGN_ONLY；APPROVE_BRANCH_WORK；APPROVE_RUNTIME_IMPORT",
        "evidence_to_record": "二次审批记录；测试报告；rollback manifest；审计日志字段。",
        "close_condition": "形成运行时接入审批门禁、回滚方案和小程序契约测试方案。",
        "runtime_effect": "关闭前所有候选资产保持NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY。",
    },
    {
        "question_id": "V04_NEGATION_POLARITY_001",
        "ask_who": "ETO",
        "concrete_question": "含“除/不含/以外/无/未”的条件是否全部保留排除语义？特别是“除纳入重点排污单位名录”是否表达为not_present而不是正向命中？",
        "check_materials": "all_permit_condition_backfill_v0_4_1.csv；normalized_predicates；raw_condition；抽检样本。",
        "decision_options": "POLARITY_OK；NEED_RULE_FIX；NEED_MANUAL_REVIEW",
        "evidence_to_record": "否定词扫描结果；修复前后样例；单测或抽检记录。",
        "close_condition": "否定语义谓词经抽检无正向化，必要时补充规则库单测。",
        "runtime_effect": "关闭前否定条件不得用于自动正式化。",
    },
    {
        "question_id": "V04_DIVISION_CONTEXT_APPLIES_001",
        "ask_who": "ETO",
        "concrete_question": "是否仍存在纯DIVISION_CONTEXT自动升级为APPLIES？未来升级APPLIES时必须有哪些直接代码/名称/条件文本证据和人工审阅记录？",
        "check_materials": "all_context_applicability_review_v0_4_1.csv；automated_denoise_diff_report_v0_4.md；relation_source。",
        "decision_options": "NO_DIRECT_APPLIES；ALLOW_WITH_DIRECT_EVIDENCE；NEED_REVIEW",
        "evidence_to_record": "0条纯DIVISION_CONTEXT->APPLIES检查结果；升级规则；审阅字段要求。",
        "close_condition": "0条纯DIVISION_CONTEXT->APPLIES，升级路径有人工审阅字段和证据链。",
        "runtime_effect": "关闭前DIVISION_CONTEXT关系不得作为运行时APPLIES。",
    },
    {
        "question_id": "V04_NOT_APPLY_BLOCKING_FLAGS_001",
        "ask_who": "ETO",
        "concrete_question": "NOT_APPLY是否都有/、明确排除文本、相邻条目/小类排除或forced_denoise依据？无法解释的是否应降为NEED_EIA_OR_PERMIT_CONFIRM？",
        "check_materials": "all_context_applicability_review_v0_4_1.csv；blocking_flags；gate_reason；raw_condition。",
        "decision_options": "NOT_APPLY_OK；DOWNGRADE_TO_NEED_CONFIRM；NEED_RULE_FIX",
        "evidence_to_record": "NOT_APPLY抽检结果；缺失blocking_flags清单；降级diff。",
        "close_condition": "0条NOT_APPLY缺少blocking_flags或明确排除依据。",
        "runtime_effect": "关闭前缺证据NOT_APPLY不得进入运行时。",
    },
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
    formalization = read_csv(artifact_path("formalization_candidate_queue_v0_8.csv"))
    impact = {r["candidate_relation_id"]: r for r in read_csv(artifact_path("review_impact_analysis_v0_9.csv"))}
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


def write_open_question_review_guide():
    fields = [
        "question_id",
        "ask_who",
        "concrete_question",
        "check_materials",
        "decision_options",
        "evidence_to_record",
        "close_condition",
        "runtime_effect",
    ]
    write_csv(artifact_path("open_questions_review_matrix_v1_0_rc.csv"), OPEN_QUESTION_REVIEW_ROWS, fields)

    by_owner = {}
    for row in OPEN_QUESTION_REVIEW_ROWS:
        by_owner.setdefault(row["ask_who"], []).append(row["question_id"])

    lines = [
        f"final_state: `{FINAL_STATE}`",
        "runtime_integration: `disabled`",
        "",
        "这份文件把 `open_questions_v0_4_1.csv` 整理成可以分派给人审的具体问题。它不是人工审阅结论，不填写 `human_review_label`，也不解除任何运行时阻断。",
        "",
        "## 怎么用",
        "",
        "1. 先按 `ask_who` 找到责任角色。",
        "2. 把 `concrete_question` 直接发给对应负责人。",
        "3. 按 `check_materials` 查证据。",
        "4. 只能从 `decision_options` 中选择初步结论，或补充说明为什么不能选择。",
        "5. 关闭问题时必须留下 `evidence_to_record`，并满足 `close_condition`。",
        "6. 关闭前一律保持 `BLOCKS_RUNTIME`，不得接 EcoCheck runtime。",
        "",
        "## 按角色分派",
        "",
    ]
    for owner, ids in sorted(by_owner.items()):
        lines.append(f"- {owner}: {', '.join(ids)}")

    lines.extend(["", "## 具体问题", ""])
    for row in OPEN_QUESTION_REVIEW_ROWS:
        lines.extend([
            f"### {row['question_id']}",
            "",
            f"- 找谁问：{row['ask_who']}",
            f"- 具体要问：{row['concrete_question']}",
            f"- 怎么查：{row['check_materials']}",
            f"- 可选结论：{row['decision_options']}",
            f"- 要留什么证据：{row['evidence_to_record']}",
            f"- 关闭条件：{row['close_condition']}",
            f"- 运行时影响：{row['runtime_effect']}",
            "",
        ])

    (artifact_path("open_questions_review_guide_v1_0_rc.md")).write_text(
        "# open_questions_review_guide_v1_0_rc\n\n" + "\n".join(lines),
        encoding="utf-8",
    )


def main():
    mapping_rows = build_mapping_rows()
    write_open_question_review_guide()
    write_csv(artifact_path("candidate_to_runtime_mapping_v1_0_rc.csv"), mapping_rows)

    promotion_design = {
        "version": VERSION,
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
        "design_only": True,
        "gates": GATES,
        "forbidden_actions": FORBIDDEN,
        "minimum_release_rule": "No candidate row may be imported until all gates pass and second approval explicitly grants runtime scope.",
    }
    write_json(artifact_path("runtime_promotion_gate_design_v1_0_rc.json"), promotion_design)
    write_md(artifact_path("runtime_promotion_gate_design_v1_0_rc.md"), "runtime_promotion_gate_design_v1_0_rc", [
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
    write_json(artifact_path("runtime_data_contract_v1_0_rc.json"), data_contract)
    write_md(artifact_path("runtime_data_contract_v1_0_rc.md"), "runtime_data_contract_v1_0_rc", [
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
    write_json(artifact_path("runtime_import_candidate_manifest_v1_0_rc.json"), import_manifest)

    write_md(artifact_path("runtime_rollback_plan_v1_0_rc.md"), "runtime_rollback_plan_v1_0_rc", [
        f"final_state: `{FINAL_STATE}`",
        "",
        "本计划只描述未来接入时的回滚要求。",
        "",
        "- 导入前保存当前 runtime snapshot、schema version、manifest hash。",
        "- 每次导入必须生成 rollback_manifest_id。",
        "- 回滚必须能恢复上一版本候选映射、RAG索引和小程序展示配置。",
        "- 回滚演练通过前，不得进行任何 runtime import。",
    ])

    write_md(artifact_path("runtime_contract_test_plan_v1_0_rc.md"), "runtime_contract_test_plan_v1_0_rc", [
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

    write_md(artifact_path("approval_workflow_v1_0_rc.md"), "approval_workflow_v1_0_rc", [
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
    write_json(artifact_path("security_audit_log_design_v1_0_rc.json"), audit_design)
    write_md(artifact_path("security_audit_log_design_v1_0_rc.md"), "security_audit_log_design_v1_0_rc", [
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
            "open_questions_review_guide_v1_0_rc.md",
            "open_questions_review_matrix_v1_0_rc.csv",
            "eto_eso_open_question_decisions_v1_0_rc.md",
            "eto_eso_open_question_decisions_v1_0_rc.csv",
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
    write_json(artifact_path("knowledge_base_manifest_v1_0_rc.json"), manifest)
    write_md(artifact_path("PROJECT_INDEX_v1_0_rc.md"), "PROJECT_INDEX_v1_0_rc", [
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
        "- `open_questions_review_guide_v1_0_rc.md`: 19个开放问题的可分派审阅指南。",
        "- `open_questions_review_matrix_v1_0_rc.csv`: 19个开放问题的分派矩阵。",
        "- `eto_eso_open_question_decisions_v1_0_rc.md/csv`: ETO/ESO初步审阅决策记录，仍不解除运行时阻断。",
        "",
        "## 核心数据入口",
        "",
        "- `all_context_applicability_review_v0_4_1.csv/json`: 22815 条候选适用关系，全部候选化。",
        "- `all_permit_condition_backfill_v0_4_1.csv/json`: 336 条许可名录条件治理，覆盖 1-112 条 x 三类管理条件。",
        "- `scenario_templates.json`: 产污场景模板，是知识本体核心，不是行业硬编码。",
        "- `scenario_to_score13_mapping_v0_3.csv`: 场景到 EcoCheck S01-S13 的候选语义映射。",
        "- `inspection_candidate_recommendations_v0_3.csv`: 候选排查建议，不能直接生成正式检查模板。",
        "- `open_questions_v0_4_1.csv`: 高风险开放问题。",
        "- `open_questions_review_guide_v1_0_rc.md`: 把开放问题拆成“问谁、问什么、查什么、怎么关闭”。",
        "- `eto_eso_open_question_decisions_v1_0_rc.md/csv`: 已收到的ETO/ESO初步判定，作为后续v1.1治理修复输入。",
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
    write_md(artifact_path("HANDOFF_v1_0_rc.md"), "HANDOFF_v1_0_rc", [
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
    write_md(artifact_path("DEPRECATED_AND_REMOVED_FILES_v1_0_rc.md"), "DEPRECATED_AND_REMOVED_FILES_v1_0_rc", [
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
    write_md(artifact_path("FINAL_COMPLETION_REPORT_v1_0_rc.md"), "FINAL_COMPLETION_REPORT_v1_0_rc", [
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
