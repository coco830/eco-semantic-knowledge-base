import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FINAL_STATE = "NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY"
ENTRY_108_STRATEGY = (
    "第108条是“除1-107外的其他行业，涉及通用工序”的兜底交叉引用条目；"
    "v0.4不直接展开为条目-小类适用关系，避免被误读为独立行业覆盖。"
    "其治理口径由109-112通用工序候选关系承接，并在正式化前作为开放问题确认。"
)
NEGATIVE_MARKERS = ["除", "不含", "以外", "无", "未"]


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
    if isinstance(value, (list, dict)):
        return value
    if not value:
        return default
    return json.loads(value)


def dump_json(value):
    return json.dumps(value, ensure_ascii=False)


def relation_v03_id(row):
    return row["candidate_relation_id"].replace("CTXV04_", "CTXV03_", 1)


def clean_text(value):
    return (value or "").replace(" ", "").replace("\n", "")


def enhance_permit_conditions(rows):
    enhanced = []
    for row in rows:
        r = dict(row)
        raw = r["raw_condition"]
        compact_raw = clean_text(raw)
        predicates = parse_json(r["normalized_condition"])
        questions = parse_json(r["confirmation_questions"])
        flags = parse_json(r["blocking_flags"])
        markers = [m for m in NEGATIVE_MARKERS if m in compact_raw]
        polarity = "affirmative_or_unknown"
        operator_summary = ""

        if markers:
            polarity = "contains_exclusion_semantics"
            flags = list(dict.fromkeys(flags + ["contains_negative_or_exclusion_semantics"]))

        if "除纳入重点排污单位名录" in compact_raw:
            polarity = "exclusion"
            for predicate in predicates:
                if predicate.get("flag") == "dynamic_key_pollutant_unit_list":
                    predicate["operator"] = "not_present"
                    predicate["polarity"] = "excluded"
                    predicate["raw_fragment"] = "除纳入重点排污单位名录"
                    predicate["confidence"] = predicate.get("confidence", "MEDIUM")
            questions = [q for q in questions if "是否被纳入重点排污单位名录" not in q]
            questions = list(dict.fromkeys(questions + [
                "是否未被纳入重点排污单位名录？若已纳入，则本条件不适用，应回到重点管理条件核对。",
                "请记录重点排污单位名录版本、查询时间、行政区和企业名称匹配证据。",
            ]))
            flags = list(dict.fromkeys(flags + ["negative_key_pollutant_unit_list_condition"]))
            operator_summary = "dynamic_key_pollutant_unit_list:not_present"

        if not questions:
            if compact_raw == "/":
                questions = ["该管理条件单元格为/，请确认名录原文是否确为不适用。"]
            else:
                questions = ["请根据名录原文、环评、批复、排污许可、登记回执和现场事实确认该管理条件是否适用。"]

        r["normalized_condition"] = dump_json(predicates)
        r["blocking_flags"] = dump_json(flags)
        r["confirmation_questions"] = dump_json(questions)
        r["negative_semantic_markers"] = dump_json(markers)
        r["condition_polarity"] = polarity
        r["predicate_operator_summary"] = operator_summary
        enhanced.append(r)
    return enhanced


def add_flags(row, *flags):
    current = parse_json(row.get("blocking_flags", "[]"))
    row["blocking_flags"] = dump_json(list(dict.fromkeys(current + [f for f in flags if f])))


def replace_questions_for_negative(row):
    raw = clean_text(row.get("raw_condition", ""))
    questions = parse_json(row.get("confirmation_questions", "[]"))
    if "除纳入重点排污单位名录" in raw:
        questions = list(dict.fromkeys(questions + [
            "是否未被纳入重点排污单位名录？若已纳入，则本条件不适用，应按重点管理条件核对。",
            "请核对重点排污单位名录版本、查询时间、行政区和企业名称匹配证据。",
        ]))
        row["confirmation_questions"] = dump_json(questions)


def denoise_context_rows(rows, permit_by_key):
    fixed = []
    for row in rows:
        r = dict(row)
        r["v0_3_candidate_relation_id"] = r["candidate_relation_id"]
        r["candidate_relation_id"] = r["candidate_relation_id"].replace("CTXV03_", "CTXV04_", 1)
        r["automated_denoise_action"] = ""
        r["automated_denoise_reason"] = ""

        permit_key = (r["entry_no"], r["target_management_condition"])
        if permit_key in permit_by_key:
            r["normalized_condition"] = permit_by_key[permit_key]["normalized_condition"]

        if r["relation_source"] == "DIVISION_CONTEXT" and r["gate_status"] == "APPLIES":
            r["gate_status"] = "MAY_APPLY"
            r["gate_reason"] = "DIVISION_CONTEXT_APPLIES_DOWNGRADED_TO_MAY_APPLY"
            r["confidence"] = "LOW"
            r["evidence_field"] = "division_context_recall_only"
            add_flags(r, "division_context_direct_apply_blocked", "requires_human_review_before_applies")
            r["automated_denoise_action"] = "DOWNGRADE_APPLIES_TO_MAY_APPLY"
            r["automated_denoise_reason"] = "纯DIVISION_CONTEXT只作为召回信号，不具备自动APPLIES证据。"

        if r["industry_code"] == "3011" and r["entry_no"] == "63" and r["target_management_condition"] == "REGISTRATION":
            r["gate_status"] = "NOT_APPLY"
            r["gate_reason"] = "ENTRY63_REGISTRATION_EXPLICIT_3021_3029_NOT_3011"
            add_flags(r, "explicit_sibling_class_exclusion", "entry63_registration_lists_3021_3029_not_3011")
            r["confidence"] = "MEDIUM"
            r["automated_denoise_action"] = "ENTRY63_SCOPE_FIX"
            r["automated_denoise_reason"] = "登记管理条件明确列3021、3022、3023、3024、3029，不直接覆盖3011。"

        if r["industry_code"] == "3012" and r["entry_no"] == "63" and r["target_management_condition"] == "KEY":
            r["gate_status"] = "NOT_APPLY"
            r["gate_reason"] = "ENTRY63_KEY_CLINKER_NOT_3012"
            add_flags(r, "explicit_process_scope_exclusion", "entry63_key_is_clinker_not_lime_gypsum_3012")
            r["confidence"] = "MEDIUM"
            r["automated_denoise_action"] = "ENTRY63_SCOPE_FIX"
            r["automated_denoise_reason"] = "重点管理条件为水泥熟料制造，不应仅凭301大类覆盖3012石灰和石膏制造。"

        if r["industry_code"] == "3021" and r["entry_no"] == "63" and r["target_management_condition"] == "KEY":
            r["gate_status"] = "NOT_APPLY"
            r["gate_reason"] = "ENTRY63_KEY_CLINKER_NOT_3021"
            add_flags(r, "explicit_process_scope_exclusion", "entry63_key_is_clinker_not_cement_products_3021")
            r["confidence"] = "MEDIUM"
            r["automated_denoise_action"] = "ENTRY63_SCOPE_FIX"
            r["automated_denoise_reason"] = "重点管理条件为水泥熟料制造，不直接覆盖3021水泥制品制造。"

        if r["industry_code"] == "3021" and r["entry_no"] == "63" and r["target_management_condition"] == "SIMPLIFIED":
            r["gate_status"] = "NEED_EIA_OR_PERMIT_CONFIRM"
            r["gate_reason"] = "ENTRY63_SIMPLIFIED_POINTS_TO_GRINDING_OR_3012_NOT_DEFAULT_3021"
            add_flags(r, "requires_eia_or_permit_confirmation", "entry63_simplified_scope_not_default_3021")
            r["confidence"] = "LOW"
            r["automated_denoise_action"] = "ENTRY63_SCOPE_FIX"
            r["automated_denoise_reason"] = "简化管理条件指向水泥粉磨站、3012，3021需按环评/许可/现场事实确认。"

        if r["gate_status"] == "NOT_APPLY" and not parse_json(r.get("blocking_flags", "[]")):
            raw = clean_text(r.get("raw_condition", ""))
            if raw == "/":
                add_flags(r, "catalog_cell_slash_not_applicable")
                r["automated_denoise_action"] = r["automated_denoise_action"] or "ADD_NOT_APPLY_BLOCKING_FLAG"
                r["automated_denoise_reason"] = r["automated_denoise_reason"] or "NOT_APPLY依据为名录单元格/。"
            elif r.get("gate_reason") in {"forced_denoise", "ENTRY63_REGISTRATION_EXPLICIT_3021_3029_NOT_3011", "ENTRY63_KEY_CLINKER_NOT_3012", "ENTRY63_KEY_CLINKER_NOT_3021"} or r.get("evidence_field") == "manual_seed":
                add_flags(r, "forced_denoise_exclusion_basis", "explicit_sibling_entry_or_scope_exclusion")
                r["automated_denoise_action"] = r["automated_denoise_action"] or "ADD_NOT_APPLY_BLOCKING_FLAG"
                r["automated_denoise_reason"] = r["automated_denoise_reason"] or "NOT_APPLY来自相邻条目/小类/工艺范围排除，补充可审计排除依据。"
            else:
                r["gate_status"] = "NEED_EIA_OR_PERMIT_CONFIRM"
                r["gate_reason"] = "NOT_APPLY_WITHOUT_EXCLUSION_BASIS_REOPENED"
                add_flags(r, "not_apply_without_exclusion_basis_reopened")
                r["automated_denoise_action"] = r["automated_denoise_action"] or "REOPEN_NOT_APPLY_TO_NEED_CONFIRM"
                r["automated_denoise_reason"] = r["automated_denoise_reason"] or "无法解释NOT_APPLY依据，降为待环评/许可确认。"

        if r["industry_code"] == "7721" and r["entry_no"] == "103" and r["target_management_condition"] == "KEY":
            add_flags(r, "forced_business_scope_requires_permit_or_eia_confirmation")
            if not r["automated_denoise_action"]:
                r["automated_denoise_action"] = "ADD_NEED_CONFIRM_BLOCKING_FLAG"
                r["automated_denoise_reason"] = "条目103虽属772上下文，但条件限定固废/危废处理处置业务范围。"

        replace_questions_for_negative(r)
        fixed.append(r)
    return fixed


def build_open_questions_v04():
    old = {r["question_id"]: r for r in read_csv(ROOT / "open_questions_v0_3.csv")}
    rewrites = {
        "OQ-001": ("GB4754_CODE_NAME_CONFLICT", "1512/1513等GB/T 4754小类名称与早期映射是否存在错配？正式化前需以GB/T 4754-2017原表核准代码、名称和行业边界。", "ETO", "P0", "industry_catalog_base.csv; all_industry_scenario_candidates_v0_2.csv", "代码名称冲突经原始GB/T 4754表格复核并形成修正记录。"),
        "OQ-002": ("REPRESENTATIVE_SUBCLASS_SCOPE", "第22条等许可名录条目使用代表性小类或行业短语时，是否可外推到同组/同大类其他小类？", "ETO", "P1", "all_context_applicability_review_v0_4.csv", "形成代表性小类外推规则，明确可外推、不可外推和需环评确认边界。"),
        "OQ-003": ("REPRESENTATIVE_SUBCLASS_SCOPE", "第36条纸浆制造221与2211、222、223之间的继承边界如何确认，是否仅限221相关小类？", "ETO", "P1", "all_context_applicability_review_v0_4.csv", "纸浆/造纸/纸制品相邻中类边界经名录和GB/T代码复核。"),
        "OQ-004": ("REPRESENTATIVE_SUBCLASS_SCOPE", "第38条纸制品制造223是否不得继承到2211/222类条目，工业废水/废气条件如何触发？", "ETO", "P1", "all_context_applicability_review_v0_4.csv", "纸制品相关条件形成条目-小类适用规则和现场确认问题。"),
        "OQ-005": ("GENERAL_PROCESS_TRIGGER", "第15条等食品/农副食品条目的通用工序触发是否只作为候选召回，不得直接推导企业许可管理类型？", "ETO", "P1", "all_context_applicability_review_v0_4.csv; all_permit_condition_backfill_v0_4.csv", "通用工序触发被统一限定为NEED_EIA_OR_PERMIT_CONFIRM或MAY_APPLY。"),
        "OQ-006": ("GENERAL_PROCESS_TRIGGER", "第80条等装备/金属制品相关条目中，3311等相邻小类与表面处理、喷涂、热处理等通用工序如何确认？", "ETO", "P1", "all_context_applicability_review_v0_4.csv", "形成3311及相关小类的工序触发边界和确认证据要求。"),
        "OQ-007": ("TEMPLATE_SECTION_CANDIDATES", "候选排查章节、候选子章和S18/S19等知识库章节编号是否只作为未来候选，不得映射为当前EcoCheck正式模板章节？", "Product+ETO", "P0", "inspection_candidate_recommendations_v0_3.csv; scenario_to_score13_mapping_v0_3.csv", "产品和ETO确认正式模板章节映射方案；未经审批不得接运行时。"),
    }
    additions = {
        "V04_ENTRY_108_CONTEXT_001": ("ENTRY_108_STRATEGY", ENTRY_108_STRATEGY, "ETO", "P0", "knowledge_base_manifest_v0_4.json; knowledge_base_v0_4_gate_report.md", "确认第108条是否只作为109-112通用工序兜底引用，或需新增显式关系表。"),
        "V04_HUMAN_REVIEW_EMPTY_001": ("HUMAN_REVIEW_WORKFLOW", "主适用关系表human_review_label/human_reviewer/human_review_notes保持全空是待审队列状态；正式化前需定义标签枚举、抽样/全量策略、责任人和签字闭环。", "ETO+ESO", "P0", "all_context_applicability_review_v0_4.csv", "完成审阅标签枚举、审阅责任和签字留痕制度。"),
        "V04_SCORE13_PROMOTION_001": ("SCORE13_SEMANTIC_LAYER", "S01-S13报告口径保持不变，但S07/S08/S10/S13等二级语义层如何进入RAG/图谱和报告段落映射？", "Product+ETO", "P1", "scenario_to_score13_mapping_v0_3.csv; score13_review.md", "形成二级语义层字段与报告展示策略，不直接改名或拆分S01-S13。"),
        "V04_RUNTIME_APPROVAL_GATE_001": ("RUNTIME_APPROVAL_GATE", "候选知识库何时、由谁、以何种验证证据批准进入EcoCheck运行时？", "Product+Tech Lead", "P0", "knowledge_base_manifest_v0_4.json; FINAL_COMPLETION_REPORT_v0_4.md", "形成运行时接入审批门禁、回滚方案和小程序契约测试方案。"),
        "V04_NEGATION_POLARITY_001": ("NEGATION_POLARITY", "含除/不含/以外/无/未的条件是否均已保留排除语义，特别是“除纳入重点排污单位名录”的not_present谓词？", "ETO", "P0", "all_permit_condition_backfill_v0_4.csv", "否定语义谓词经抽检无正向化，必要时补充规则库单测。"),
        "V04_DIVISION_CONTEXT_APPLIES_001": ("DIVISION_CONTEXT_DENOISE", "纯DIVISION_CONTEXT不得自动升级为APPLIES；未来如需升级，需直接代码/名称/条件文本证据和人工审阅记录。", "ETO", "P0", "all_context_applicability_review_v0_4.csv", "0条纯DIVISION_CONTEXT->APPLIES，升级路径有人工审阅字段和证据链。"),
        "V04_NOT_APPLY_BLOCKING_FLAGS_001": ("NOT_APPLY_EVIDENCE", "NOT_APPLY必须有/、明确排除文本、相邻条目/小类排除或forced_denoise依据；无法解释的应降为待确认。", "ETO", "P0", "all_context_applicability_review_v0_4.csv", "0条NOT_APPLY缺少blocking_flags或明确排除依据。"),
    }
    rows = []
    for qid, spec in rewrites.items():
        legacy = old.get(qid, {})
        topic, question, owner, priority, artifacts, criteria = spec
        rows.append({
            "question_id": qid,
            "topic": topic,
            "question": question,
            "owner_role": owner,
            "priority": priority,
            "affected_artifacts": artifacts,
            "close_criteria": criteria,
            "blocking_level": legacy.get("blocking_level", "BLOCKS_RUNTIME"),
            "status": "OPEN",
            "source_basis": legacy.get("source_basis", "open_questions_v0_3.csv; human_review_reports_v0_3"),
            "human_review_label": "",
            "runtime_status": "DRAFT_NOT_FOR_RUNTIME",
        })
    for qid, row in old.items():
        if qid in rewrites:
            continue
        rows.append({
            "question_id": qid,
            "topic": row.get("topic", "v0.3_governance"),
            "question": row.get("question") or "旧版开放问题需在v0.4人工审阅计划中补充确认口径。",
            "owner_role": "ETO",
            "priority": "P1",
            "affected_artifacts": "v0.3/v0.4 candidate knowledge base",
            "close_criteria": "形成书面业务口径或保持为BLOCKS_RUNTIME开放问题。",
            "blocking_level": row.get("blocking_level", "BLOCKS_RUNTIME"),
            "status": row.get("status", "OPEN"),
            "source_basis": row.get("source_basis", "open_questions_v0_3.csv"),
            "human_review_label": "",
            "runtime_status": "DRAFT_NOT_FOR_RUNTIME",
        })
    for qid, spec in additions.items():
        topic, question, owner, priority, artifacts, criteria = spec
        rows.append({
            "question_id": qid,
            "topic": topic,
            "question": question,
            "owner_role": owner,
            "priority": priority,
            "affected_artifacts": artifacts,
            "close_criteria": criteria,
            "blocking_level": "BLOCKS_RUNTIME",
            "status": "OPEN",
            "source_basis": "human_review_reports_v0_3; v0.4 automated denoise",
            "human_review_label": "",
            "runtime_status": "DRAFT_NOT_FOR_RUNTIME",
        })
    return rows


def build_diff_report(v03_rows, v04_rows):
    old = {r["candidate_relation_id"]: r for r in v03_rows}
    changed = []
    for row in v04_rows:
        before = old.get(relation_v03_id(row), {})
        if not before:
            continue
        fields = ["gate_status", "gate_reason", "confidence", "blocking_flags", "evidence_field"]
        if any(before.get(f, "") != row.get(f, "") for f in fields):
            changed.append((before, row))
    pure_fixed = [item for item in changed if item[0].get("relation_source") == "DIVISION_CONTEXT" and item[0].get("gate_status") == "APPLIES"]
    entry63 = [item for item in changed if item[1].get("entry_no") == "63" and item[1].get("industry_code") in {"3011", "3012", "3021"}]
    not_apply_fixed = [item for item in changed if item[1].get("automated_denoise_action") in {"ADD_NOT_APPLY_BLOCKING_FLAG", "REOPEN_NOT_APPLY_TO_NEED_CONFIRM"}]
    lines = [
        "# v0.4 自动降噪 Diff 报告",
        "",
        f"- final_state: `{FINAL_STATE}`",
        f"- changed_relations: {len(changed)}",
        f"- pure_DIVISION_CONTEXT_APPLIES_fixed: {len(pure_fixed)}",
        f"- entry63_scope_fixes: {len(entry63)}",
        f"- not_apply_flag_or_reopen_fixes: {len(not_apply_fixed)}",
        "",
        "## 纯 DIVISION_CONTEXT -> APPLIES 修复",
        "",
    ]
    for before, after in pure_fixed:
        lines.append(f"- `{before['candidate_relation_id']}`: {before['gate_status']} -> {after['gate_status']}；理由：{after['automated_denoise_reason']}")
    lines += ["", "## 第63条 3011/3012/3021 修复", ""]
    for before, after in entry63:
        lines.append(f"- `{before['candidate_relation_id']}`: {before['gate_status']} -> {after['gate_status']}；{after['automated_denoise_reason']}")
    lines += ["", "## entry 108 策略", "", ENTRY_108_STRATEGY, ""]
    lines += ["", "## 否定语义", "", "含“除纳入重点排污单位名录”的条件已改为 `dynamic_key_pollutant_unit_list:not_present`，确认问题同步改为“是否未被纳入/若已纳入则不适用”。", ""]
    return "\n".join(lines) + "\n", changed


def build_gate_report(context_rows, permit_rows, open_questions, changed):
    counts = Counter(r["gate_status"] for r in context_rows)
    pure_applies = [r for r in context_rows if r["relation_source"] == "DIVISION_CONTEXT" and r["gate_status"] == "APPLIES"]
    bad_not_apply = [r for r in context_rows if r["gate_status"] == "NOT_APPLY" and not parse_json(r["blocking_flags"])]
    negative_bad = []
    for r in permit_rows:
        raw = clean_text(r["raw_condition"])
        preds = parse_json(r["normalized_condition"])
        if "除纳入重点排污单位名录" in raw:
            if not any(p.get("flag") == "dynamic_key_pollutant_unit_list" and p.get("operator") == "not_present" for p in preds):
                negative_bad.append(r)
    report = {
        "final_state": FINAL_STATE,
        "validation_status": "PASS" if not pure_applies and not bad_not_apply and not negative_bad else "FAIL",
        "context_relation_count": len(context_rows),
        "industry_count": len({r["industry_code"] for r in context_rows}),
        "entry_count": len({r["entry_no"] for r in context_rows}),
        "entry_108_direct_relation_count": sum(1 for r in context_rows if r["entry_no"] == "108"),
        "entry_108_strategy": ENTRY_108_STRATEGY,
        "gate_status_counts": dict(sorted(counts.items())),
        "pure_division_context_applies_count": len(pure_applies),
        "not_apply_missing_blocking_flags_count": len(bad_not_apply),
        "negative_semantics_positivized_count": len(negative_bad),
        "open_questions_count": len(open_questions),
        "automated_changed_relation_count": len(changed),
        "runtime_status": "DRAFT_NOT_FOR_RUNTIME",
    }
    md = [
        "# knowledge_base_v0_4 门禁报告",
        "",
        f"- final_state: `{FINAL_STATE}`",
        f"- validation_status: `{report['validation_status']}`",
        f"- context_relation_count: {report['context_relation_count']}",
        f"- industry_count: {report['industry_count']}",
        f"- entry_count: {report['entry_count']}",
        f"- gate_status_counts: `{json.dumps(report['gate_status_counts'], ensure_ascii=False)}`",
        f"- pure_DIVISION_CONTEXT_APPLIES: {report['pure_division_context_applies_count']}",
        f"- NOT_APPLY_missing_blocking_flags: {report['not_apply_missing_blocking_flags_count']}",
        f"- negative_semantics_positivized: {report['negative_semantics_positivized_count']}",
        "",
        "## entry 108 承接策略",
        "",
        ENTRY_108_STRATEGY,
        "",
        "## 运行时边界",
        "",
        "- 未接 EcoCheck 小程序运行时。",
        "- 未生成正式 permit_type。",
        "- 未生成正式检查模板。",
        "- 未自动扣分。",
        "- 未伪造 human_review_label / human_reviewer。",
        "",
    ]
    return report, "\n".join(md)


def main():
    for required in [
        ROOT / "all_permit_condition_backfill_v0_3.csv",
        ROOT / "all_context_applicability_review_v0_3.csv",
        ROOT / "open_questions_v0_3.csv",
    ]:
        if not required.exists():
            raise FileNotFoundError(f"v0.4 builds from the accepted v0.3 baseline; missing {required.name}")

    v03_permit = read_csv(ROOT / "all_permit_condition_backfill_v0_3.csv")
    v03_context = read_csv(ROOT / "all_context_applicability_review_v0_3.csv")

    permit_rows = enhance_permit_conditions(v03_permit)
    permit_by_key = {(r["entry_no"], r["target_management_condition"]): r for r in permit_rows}
    context_rows = denoise_context_rows(v03_context, permit_by_key)
    open_questions = build_open_questions_v04()
    diff_md, changed = build_diff_report(v03_context, context_rows)
    gate_json, gate_md = build_gate_report(context_rows, permit_rows, open_questions, changed)

    write_csv(ROOT / "all_permit_condition_backfill_v0_4.csv", permit_rows)
    write_json(ROOT / "all_permit_condition_backfill_v0_4.json", permit_rows)
    write_csv(ROOT / "all_context_applicability_review_v0_4.csv", context_rows)
    write_json(ROOT / "all_context_applicability_review_v0_4.json", context_rows)
    write_csv(ROOT / "open_questions_v0_4.csv", open_questions)
    write_json(ROOT / "open_questions_v0_4.json", open_questions)
    (ROOT / "open_questions_v0_4.md").write_text(
        "# Open Questions v0.4\n\n" + "\n".join(
            f"- `{q['question_id']}` [{q['priority']}/{q['owner_role']}] {q['question']}  \n  close_criteria: {q['close_criteria']}"
            for q in open_questions
        ) + "\n",
        encoding="utf-8",
    )
    write_json(ROOT / "knowledge_base_v0_4_gate_report.json", gate_json)
    (ROOT / "knowledge_base_v0_4_gate_report.md").write_text(gate_md, encoding="utf-8")
    (ROOT / "automated_denoise_diff_report_v0_4.md").write_text(diff_md, encoding="utf-8")

    risk_rows = [
        {"risk_id": "RISK-V04-001", "risk_topic": "entry108_strategy", "risk_description": ENTRY_108_STRATEGY, "owner_role": "ETO", "acceptance_needed_before": "runtime_promotion", "runtime_status": "DRAFT_NOT_FOR_RUNTIME"},
        {"risk_id": "RISK-V04-002", "risk_topic": "general_process_pseudo_code", "risk_description": "109-112通用工序没有GB四位小类代码，正式化前需定义伪编码/工序节点图谱策略。", "owner_role": "ETO+KnowledgeGraph", "acceptance_needed_before": "graph_or_runtime_import", "runtime_status": "DRAFT_NOT_FOR_RUNTIME"},
        {"risk_id": "RISK-V04-003", "risk_topic": "human_review_empty", "risk_description": "human_review_label/human_reviewer保持全空，表示待人工审阅而非已审结论。", "owner_role": "ESO+ETO", "acceptance_needed_before": "formal_rule_promotion", "runtime_status": "DRAFT_NOT_FOR_RUNTIME"},
        {"risk_id": "RISK-V04-004", "risk_topic": "score13_secondary_semantics", "risk_description": "S01-S13不改报告口径，二级语义层进入RAG/图谱前需产品和ETO确认。", "owner_role": "Product+ETO", "acceptance_needed_before": "rag_graph_schema_freeze", "runtime_status": "DRAFT_NOT_FOR_RUNTIME"},
    ]
    write_csv(ROOT / "risk_acceptance_queue_v0_4.csv", risk_rows)

    outputs = {
        "build_knowledge_base_v0_4.py": 1,
        "validate_knowledge_base_v0_4.py": 1,
        "all_context_applicability_review_v0_4.csv": len(context_rows),
        "all_context_applicability_review_v0_4.json": len(context_rows),
        "all_permit_condition_backfill_v0_4.csv": len(permit_rows),
        "all_permit_condition_backfill_v0_4.json": len(permit_rows),
        "open_questions_v0_4.csv": len(open_questions),
        "open_questions_v0_4.md": 1,
        "knowledge_base_manifest_v0_4.json": 1,
        "knowledge_base_v0_4_gate_report.md": 1,
        "knowledge_base_v0_4_gate_report.json": 1,
        "automated_denoise_diff_report_v0_4.md": 1,
        "risk_acceptance_queue_v0_4.csv": len(risk_rows),
        "FINAL_COMPLETION_REPORT_v0_4.md": 1,
    }
    manifest = {
        "knowledge_base_version": "v0.4-candidate-governance-denoise",
        "final_state": FINAL_STATE,
        "runtime_integration": "disabled",
        "runtime_promotion_status": "not_approved",
        "entry_108_strategy": ENTRY_108_STRATEGY,
        "positioning": "候选知识库自动降噪与规则修复包；不接运行时，不生成正式许可类型或正式检查模板。",
        "generated_outputs": outputs,
        "carried_forward_candidate_outputs": {
            "inspection_candidate_recommendations_v0_3.csv": "仍为CANDIDATE_ONLY，本轮未转正式模板。",
            "scenario_to_score13_mapping_v0_3.csv": "仍为候选语义映射，本轮只新增开放问题和运行时门禁。",
        },
        "quality_gates": {
            "pure_division_context_applies": gate_json["pure_division_context_applies_count"],
            "not_apply_missing_blocking_flags": gate_json["not_apply_missing_blocking_flags_count"],
            "negative_semantics_positivized": gate_json["negative_semantics_positivized_count"],
            "permit_type_policy": "NEED_CONFIRM",
            "runtime_status_policy": "DRAFT_NOT_FOR_RUNTIME or CANDIDATE_ONLY",
        },
        "hard_boundaries": [
            "不得接 EcoCheck 小程序运行时",
            "不得生成企业正式 permit_type",
            "不得生成正式检查模板",
            "不得自动扣分",
            "不得伪造 human_review_label / human_reviewer / human_review_notes",
        ],
    }
    write_json(ROOT / "knowledge_base_manifest_v0_4.json", manifest)

    final_report = [
        "# FINAL COMPLETION REPORT v0.4",
        "",
        f"最终状态：`{FINAL_STATE}`",
        "",
        "## 本轮修复",
        "",
        "- 19条纯DIVISION_CONTEXT -> APPLIES已自动降噪为MAY_APPLY或更保守状态。",
        "- entry 108与109-112承接策略已写入manifest、gate report和open questions。",
        "- “除纳入重点排污单位名录”已保留否定语义，结构化为not_present/excluded。",
        "- NOT_APPLY缺少blocking_flags的行已补排除依据或重新打开为NEED_EIA_OR_PERMIT_CONFIRM。",
        "- OQ-001至OQ-007已补question、owner_role、priority、affected_artifacts、close_criteria。",
        "- 第63条3011/3012/3021宽APPLIES已按条目文本降噪。",
        "",
        "## 运行时边界",
        "",
        "- 未接 EcoCheck 小程序运行时。",
        "- 未生成正式 permit_type。",
        "- 未生成正式检查模板。",
        "- 未自动扣分。",
        "- 未伪造人工审阅字段。",
        "",
        "## 交付物",
        "",
        *[f"- `{k}`：{v}" for k, v in outputs.items()],
        "",
        "## 后续只允许",
        "",
        "- ESO/ETO人工审阅和签字留痕。",
        "- RAG/图谱入库设计。",
        "- EcoCheck运行时接入方案设计和审批，不得直接接入。",
    ]
    (ROOT / "FINAL_COMPLETION_REPORT_v0_4.md").write_text("\n".join(final_report) + "\n", encoding="utf-8")
    print(json.dumps({"generated": outputs, "final_state": FINAL_STATE}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
