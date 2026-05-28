import csv
import json
import re
from collections import Counter
from pathlib import Path
from kb_paths import artifact_path


ROOT = Path(__file__).resolve().parent
SAMPLES = artifact_path("high_priority_permit_condition_backfill_audit_samples.csv")
DETAIL = artifact_path("high_priority_permit_condition_backfill_detail_v0_2.csv")
TARGET_REVIEW_CODES = {"4620", "7721", "2211", "2530"}


FORCED_DECISIONS = {
    ("4620", "98"): "名录条目98原文指向自来水生产和供应461、海水淡化处理463、其他水处理利用469；不含4620污水处理及其再生利用。",
    ("2211", "37"): "名录条目37为造纸222代码候选；2211木竹浆制造应优先核对条目36纸浆制造，不能继承222条目。",
    ("2530", "42"): "名录条目42为原油加工及石油制品制造251候选；2530核燃料加工不应继承该条目。",
    ("2530", "43"): "名录条目43为炼焦252候选；2530核燃料加工不应继承该条目。",
    ("2530", "44"): "名录条目44为煤制燃料加工254候选；2530核燃料加工不应继承该条目。",
}

FORCED_LABELS = {
    ("4620", "98"): ("NOT_APPLY", "FORCED_HIGH_RISK_CONTEXT_DENOISE", FORCED_DECISIONS[("4620", "98")]),
    ("4620", "99"): ("APPLIES", "FORCED_EXPLICIT_CATALOG_CATEGORY_MATCH", "条目99明确为污水处理及其再生利用462，但仍需按日处理能力等条件确认。"),
    ("7721", "103"): ("NEED_EIA_OR_PERMIT_CONFIRM", "FORCED_BUSINESS_SCOPE_CONFIRM", "条目103类别覆盖环境治理业772，但条件限定危废/一般工业固废贮存利用处理处置；水污染治理默认业务不必然适用。"),
    ("2211", "36"): ("APPLIES", "FORCED_EXPLICIT_GROUP_CATEGORY_MATCH", "条目36为纸浆制造221，覆盖2211木竹浆制造；仍需核对条目条件。"),
    ("2211", "37"): ("NOT_APPLY", "FORCED_HIGH_RISK_CONTEXT_DENOISE", FORCED_DECISIONS[("2211", "37")]),
    ("2211", "38"): ("NOT_APPLY", "FORCED_HIGH_RISK_CONTEXT_DENOISE", "名录条目38为纸制品制造223，不覆盖2211木竹浆制造。"),
    ("2530", "42"): ("NOT_APPLY", "FORCED_HIGH_RISK_CONTEXT_DENOISE", FORCED_DECISIONS[("2530", "42")]),
    ("2530", "43"): ("NOT_APPLY", "FORCED_HIGH_RISK_CONTEXT_DENOISE", FORCED_DECISIONS[("2530", "43")]),
    ("2530", "44"): ("NOT_APPLY", "FORCED_HIGH_RISK_CONTEXT_DENOISE", FORCED_DECISIONS[("2530", "44")]),
    ("1331", "11"): ("APPLIES", "FORCED_SAMPLE_REVIEW_MATCH", "条目11对应植物油加工133，覆盖1331食用植物油加工；仍需确认工艺与星号条件。"),
    ("2671", "51"): ("APPLIES", "FORCED_SAMPLE_REVIEW_MATCH", "条目51对应炸药、火工及焰火产品制造267，覆盖2671。"),
    ("2710", "53"): ("APPLIES", "FORCED_SAMPLE_REVIEW_MATCH", "条目53对应化学药品原料药制造271。"),
    ("3011", "63"): ("APPLIES", "FORCED_SAMPLE_REVIEW_MATCH", "条目63包含水泥（熟料）制造，覆盖3011水泥制造。"),
    ("4413", "95"): ("NOT_APPLY", "FORCED_HIGH_RISK_CONTEXT_DENOISE", "条目95条件列4411/4412/4417，不含4413水力发电。"),
    ("4413", "96"): ("NOT_APPLY", "FORCED_HIGH_RISK_CONTEXT_DENOISE", "条目96为锅炉通用工序，不能仅因44大类上下文适用于4413。"),
    ("4610", "98"): ("APPLIES", "FORCED_SAMPLE_REVIEW_MATCH", "条目98覆盖自来水生产和供应461。"),
    ("4610", "99"): ("NOT_APPLY", "FORCED_HIGH_RISK_CONTEXT_DENOISE", "条目99为污水处理及其再生利用462，不覆盖4610。"),
    ("4630", "98"): ("APPLIES", "FORCED_SAMPLE_REVIEW_MATCH", "条目98覆盖海水淡化处理463。"),
    ("4630", "99"): ("NOT_APPLY", "FORCED_HIGH_RISK_CONTEXT_DENOISE", "条目99为污水处理及其再生利用462，不覆盖4630。"),
    ("8421", "107"): ("NOT_APPLY", "FORCED_HIGH_RISK_CONTEXT_DENOISE", "条目107覆盖841医院和843专业公共卫生服务，不含842社区卫生服务中心（站）。"),
}

for code in ["7711", "7712", "7713"]:
    FORCED_LABELS[(code, "103")] = (
        "NOT_APPLY",
        "FORCED_HIGH_RISK_CONTEXT_DENOISE",
        "条目103为环境治理业772相关固废/危废处理处置候选，不覆盖771生态保护管理类小类。",
    )

for entry in ["9", "10", "12", "13", "14", "15", "16"]:
    FORCED_LABELS[("1331", entry)] = (
        "NOT_APPLY",
        "FORCED_HIGH_RISK_CONTEXT_DENOISE",
        "1331食用植物油加工优先适用条目11；该条目为同大类兄弟条目，不应继承。",
    )
for entry in ["45", "46", "47", "48", "49", "50", "52"]:
    FORCED_LABELS[("2671", entry)] = (
        "NOT_APPLY",
        "FORCED_HIGH_RISK_CONTEXT_DENOISE",
        "2671炸药及火工产品制造优先适用条目51；该条目为同大类兄弟条目，不应继承。",
    )
for entry in ["54", "55", "56", "57", "58", "59"]:
    FORCED_LABELS[("2710", entry)] = (
        "NOT_APPLY",
        "FORCED_HIGH_RISK_CONTEXT_DENOISE",
        "2710化学药品原料药制造优先适用条目53；该条目为同大类兄弟条目，不应继承。",
    )
for entry in ["64", "65", "66", "67", "68", "69", "70"]:
    FORCED_LABELS[("3011", entry)] = (
        "NOT_APPLY",
        "FORCED_HIGH_RISK_CONTEXT_DENOISE",
        "3011水泥制造优先适用条目63；该条目为同大类兄弟条目，不应继承。",
    )

DOWNGRADE_FLAGS = {
    "else_condition_requires_peer_condition_exclusion",
    "requires_general_process_cross_reference_109_112",
    "requires_external_key_pollutant_unit_list",
}


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fields):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def compact(text):
    return re.sub(r"\s+", "", text or "")


def token_match(industry_code, group_code, industry_name, group_name, text):
    body = compact(text)
    if industry_code and industry_code in body:
        return "CLASS_CODE", industry_code
    if group_code and group_code in body:
        return "GROUP_CODE", group_code
    if industry_name and compact(industry_name) in body:
        return "INDUSTRY_NAME", industry_name
    if group_name and compact(group_name) in body:
        return "GROUP_NAME", group_name
    return "", ""


def audit_flags(row):
    return json.loads(row["audit_flags_json"] or "[]")


def initial_decision(row):
    key = (row["industry_code"], row["catalog_entry_no"])
    if row["raw_condition"].strip() == "/":
        return "NOT_APPLY", "SLASH_NOT_APPLICABLE", "raw_condition", "/", "HIGH", "该管理条件单元格为/，不适用于该条件类型。", ["catalog_cell_slash_not_applicable"]

    if key in FORCED_LABELS:
        label, reason_code, reason = FORCED_LABELS[key]
        confidence = "MEDIUM" if label == "APPLIES" else "LOW"
        flags = [] if label == "APPLIES" else ["division_context_default_apply_blocked"]
        return label, reason_code, "manual_override", row["catalog_entry_no"], confidence, reason, flags

    flags = set(audit_flags(row))

    match_type, evidence = token_match(
        row["industry_code"],
        row["group_code"],
        row["industry_name"],
        row["group_name"],
        row["raw_condition"],
    )
    evidence_field = "raw_condition" if match_type else "none"
    if not match_type:
        match_type, evidence = token_match(
            row["industry_code"],
            row["group_code"],
            row["industry_name"],
            row["group_name"],
            row["industry_category_text"],
        )
        evidence_field = "industry_category_text" if match_type else "none"

    blocking_flags = []
    if flags & DOWNGRADE_FLAGS:
        blocking_flags.extend(sorted(flags & DOWNGRADE_FLAGS))

    if "CODE_MATCH" in row["backfill_scope"] and match_type and not blocking_flags:
        confidence = "HIGH" if match_type in {"CLASS_CODE", "INDUSTRY_NAME"} else "MEDIUM"
        return "APPLIES", f"EXPLICIT_{match_type}_IN_{evidence_field.upper()}", evidence_field, evidence, confidence, "名录条目或条件文本明确出现该小类/中类/名称，仍需按条件和现场事实确认。", []
    if "CODE_MATCH" in row["backfill_scope"] and match_type:
        confidence = "HIGH" if match_type in {"CLASS_CODE", "INDUSTRY_NAME"} else "MEDIUM"
        return "MAY_APPLY", f"EXPLICIT_{match_type}_WITH_CONDITIONAL_FLAGS", evidence_field, evidence, confidence, "文本有明确代码/名称命中，但存在其他/重点名单/通用工序等条件，不能直接升级为适用。", blocking_flags
    if "CODE_MATCH" in row["backfill_scope"]:
        return "MAY_APPLY", "DIRECT_CODE_REVIEW_WITHOUT_TEXT_MATCH", "none", "", "MEDIUM", "来源为代码复核表直接匹配，但本条件单元格未再次出现该小类文本，需核对同条目其他单元格。", blocking_flags
    if match_type:
        confidence = "HIGH" if match_type in {"CLASS_CODE", "INDUSTRY_NAME"} else "MEDIUM"
        return "MAY_APPLY", f"CONTEXT_WITH_EXPLICIT_{match_type}", evidence_field, evidence, confidence, "虽为大类上下文，但文本出现该代码/名称，只能作为候选复核，不能默认适用。", blocking_flags or ["division_context_default_apply_blocked"]
    return "NEED_EIA_OR_PERMIT_CONFIRM", "DIVISION_ONLY_NO_DIRECT_EVIDENCE", "none", "", "LOW", "仅因同大类上下文进入候选，不能升级为APPLIES，需环评、排污许可或现场事实确认。", blocking_flags or ["requires_eia_or_permit_confirmation"]


def build_rows():
    sample_codes = {row["industry_code"] for row in read_csv(SAMPLES)} | TARGET_REVIEW_CODES
    detail_rows = [
        row for row in read_csv(DETAIL)
        if row["industry_code"] in sample_codes
    ]
    rows = []
    for row in detail_rows:
        decision, basis, evidence_field, evidence_text, confidence, reason, blocking_flags = initial_decision(row)
        rows.append({
            "industry_code": row["industry_code"],
            "industry_name": row["industry_name"],
            "division_code": row["division_code"],
            "division_name": row["division_name"],
            "group_code": row["group_code"],
            "group_name": row["group_name"],
            "catalog_entry_no": row["catalog_entry_no"],
            "major_category_text": row["major_category_text"],
            "industry_category_text": row["industry_category_text"],
            "target_management_condition": row["target_management_condition"],
            "backfill_scope": row["backfill_scope"],
            "raw_condition": row["raw_condition"],
            "applies_status": row["applies_status"],
            "division_context_gate_status": decision,
            "division_context_gate_reason": basis,
            "division_context_evidence_field": evidence_field,
            "division_context_evidence_text": evidence_text,
            "division_context_gate_confidence": confidence,
            "division_context_blocking_flags": ";".join(dict.fromkeys(blocking_flags)),
            "initial_review_reason": reason,
            "human_review_label": "",
            "human_reviewer": "",
            "human_review_notes": "",
            "confirmation_question": "该名录条目/条件是否真实适用于该四位小类及企业现场事实？请核对环评、批复、排污许可、登记回执和现场工序。",
            "runtime_status": "DRAFT_NOT_FOR_RUNTIME",
        })
    return rows


def validate(rows):
    errors = []
    allowed = {"APPLIES", "MAY_APPLY", "NOT_APPLY", "NEED_EIA_OR_PERMIT_CONFIRM"}
    labels = Counter(row["division_context_gate_status"] for row in rows)
    if not rows:
        errors.append("review table is empty")
    bad_labels = [row for row in rows if row["division_context_gate_status"] not in allowed]
    if bad_labels:
        errors.append(f"bad labels: {len(bad_labels)}")
    bad_runtime = [row for row in rows if row["runtime_status"] != "DRAFT_NOT_FOR_RUNTIME"]
    if bad_runtime:
        errors.append(f"bad runtime status: {len(bad_runtime)}")
    context_applies = [
        row for row in rows
        if row["backfill_scope"] == "DIVISION_CONTEXT"
        and row["division_context_gate_status"] == "APPLIES"
        and row["division_context_evidence_field"] in {"none", ""}
    ]
    slash_bad = [
        row for row in rows
        if row["raw_condition"].strip() == "/" and row["division_context_gate_status"] != "NOT_APPLY"
    ]
    if slash_bad:
        errors.append(f"slash condition not NOT_APPLY: {len(slash_bad)}")
    missing_gate_fields = [
        row for row in rows
        if not row["division_context_gate_reason"] or not row["division_context_evidence_field"]
    ]
    if missing_gate_fields:
        errors.append(f"missing gate fields: {len(missing_gate_fields)}")
    if context_applies:
        errors.append(f"DIVISION_CONTEXT upgraded to APPLIES: {len(context_applies)}")
    return {
        "review_row_count": len(rows),
        "sample_industry_count": len({row["industry_code"] for row in rows}),
        "label_counts": dict(sorted(labels.items())),
        "context_applies_count": len(context_applies),
        "runtime_status": "DRAFT_NOT_FOR_RUNTIME",
        "validation_status": "PASS" if not errors else "FAIL",
        "errors": errors,
    }


def main():
    rows = build_rows()
    fields = [
        "industry_code",
        "industry_name",
        "division_code",
        "division_name",
        "group_code",
        "group_name",
        "catalog_entry_no",
        "major_category_text",
        "industry_category_text",
        "target_management_condition",
        "backfill_scope",
        "raw_condition",
        "applies_status",
        "division_context_gate_status",
        "division_context_gate_reason",
        "division_context_evidence_field",
        "division_context_evidence_text",
        "division_context_gate_confidence",
        "division_context_blocking_flags",
        "initial_review_reason",
        "human_review_label",
        "human_reviewer",
        "human_review_notes",
        "confirmation_question",
        "runtime_status",
    ]
    write_csv(artifact_path("context_applicability_review_audit_samples.csv"), rows, fields)
    validation = validate(rows)
    (artifact_path("context_applicability_review_validation.json")).write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    md = [
        "# 条目-小类适用关系审阅表",
        "",
        "## 定位",
        "",
        "本表用于对 34 条 audit samples 的许可名录条目-四位小类适用关系做人工审阅降噪。它不是正式许可结论，不接运行时。",
        "",
        "## 标签",
        "",
        "- `APPLIES`：文本明确命中小类/中类/名称，且无兜底/重点名单/通用工序等降级条件；仍需按条件和现场事实确认。",
        "- `MAY_APPLY`：存在直接复核来源或文本弱命中，需人工确认。",
        "- `NOT_APPLY`：当前条目明显不适用于该小类或该条件单元格为 `/`。",
        "- `NEED_EIA_OR_PERMIT_CONFIRM`：仅大类上下文候选，必须回到环评/许可/现场确认。",
        "",
        "## 门禁",
        "",
        "- `DIVISION_CONTEXT` 默认不得直接升级为 `APPLIES`。",
        "- `target_management_condition` 不得当成企业正式许可类型。",
        "- 人工复核应填写 `human_review_label`、`human_reviewer`、`human_review_notes`。",
        "",
        f"校验状态：`{validation['validation_status']}`",
    ]
    (artifact_path("context_applicability_review_audit.md")).write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    if validation["validation_status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
