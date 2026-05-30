import csv
import json
from datetime import date
from pathlib import Path

from kb_paths import artifact_path


ROOT = Path(__file__).resolve().parent
VERSION = "v1.0-approved-baseline-knowledge"
FINAL_STATE = "APPROVED_BASELINE_KNOWLEDGE"
RUNTIME_INTEGRATION = "approved_baseline_export_ready"
RUNTIME_STATUS = "APPROVED_BASELINE"
APPROVAL_STATUS = "HUMAN_APPROVED_BASELINE"
APPROVAL_SOURCE = "USER_ATTESTED_IN_CHAT_2026-05-30"
APPROVAL_SCOPE = "scenario_templates;score13_mapping;inspection_candidates;show_if_rules;issue_remediation_report_chain"
APPROVED_DIR = ROOT / "data" / "approved_baseline"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path, rows, fields=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = fields or (list(rows[0].keys()) if rows else [])
    tmp = path.with_name(f".{path.name}.tmp")
    with tmp.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    tmp.replace(path)


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def split_items(value):
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [part.strip() for part in (value or "").replace("；", ";").split(";") if part.strip()]


def approved_boundary(row):
    copied = dict(row)
    copied["runtime_status"] = RUNTIME_STATUS
    copied["final_state"] = FINAL_STATE
    copied["runtime_integration"] = RUNTIME_INTEGRATION
    copied["approval_status"] = APPROVAL_STATUS
    copied["approval_source"] = APPROVAL_SOURCE
    copied["approved_baseline_version"] = VERSION
    return copied


def scenario_trigger_keys(scenario_id):
    return [
        f"profile.scenarios.{scenario_id}.active",
        f"profile.scenarios.{scenario_id}.evidence_confirmed",
    ]


def build_show_if_rule(item, scenario, score_row):
    scenario_id = item["scenario_id"]
    inspection_type = item["inspection_type"]
    trigger_conditions = {
        "all": [
            {
                "field": f"profile.scenarios.{scenario_id}.active",
                "operator": "equals",
                "value": True,
                "source": "approved_baseline_scenario_activation",
            }
        ],
        "any_evidence": [
            {"field": f"profile.scenarios.{scenario_id}.evidence_confirmed", "operator": "equals", "value": True},
            {"field": f"profile.scenarios.{scenario_id}.industry_default_recalled", "operator": "equals", "value": True},
            {"field": f"profile.scenarios.{scenario_id}.process_trigger_recalled", "operator": "equals", "value": True},
            {"field": f"profile.scenarios.{scenario_id}.permit_condition_recalled", "operator": "equals", "value": True},
        ],
        "not": [
            {"field": f"profile.scenarios.{scenario_id}.not_applicable_confirmed", "operator": "equals", "value": True},
        ],
    }
    return {
        "show_if_rule_id": f"SHOWIF::{scenario_id}::{inspection_type}",
        "scenario_id": scenario_id,
        "scenario_name": item.get("scenario_name") or scenario.get("scenario_name", ""),
        "inspection_type": inspection_type,
        "template_section": item.get("candidate_section", ""),
        "template_subsection": item.get("candidate_subsection", ""),
        "primary_score_item_id": score_row.get("primary_score_item_id", ""),
        "secondary_score_item_ids": score_row.get("secondary_score_item_ids", ""),
        "show_if_keys": ";".join(scenario_trigger_keys(scenario_id)),
        "show_if_condition_json": json.dumps(trigger_conditions, ensure_ascii=False, separators=(",", ":")),
        "applicable_when": item.get("applicable_when", ""),
        "not_applicable_when": item.get("not_applicable_when", ""),
        "confirmation_questions": item.get("confirmation_questions", ""),
        "source_inspection_candidate": f"{scenario_id}:{inspection_type}",
        "source_basis": "approved scenario template + approved inspection candidate + approved score13 mapping",
        "runtime_status": RUNTIME_STATUS,
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
        "approval_status": APPROVAL_STATUS,
        "approval_source": APPROVAL_SOURCE,
        "approved_baseline_version": VERSION,
    }


def build_issue_chain(item, scenario, score_row):
    scenario_id = item["scenario_id"]
    severity = item.get("default_severity") or "NEED_CONFIRM"
    deduct = item.get("default_deduct") or "USE_ECOCHECK_SCORE13_DEDUCT_RULE_POLICY"
    risk_point = item.get("risk_or_hidden_danger_point", "")
    evidence_chain = item.get("evidence_chain", "")
    photo_points = item.get("photo_points", "")
    return {
        "chain_id": f"CHAIN::{scenario_id}::{item['inspection_type']}",
        "scenario_id": scenario_id,
        "scenario_name": item.get("scenario_name") or scenario.get("scenario_name", ""),
        "inspection_type": item["inspection_type"],
        "primary_score_item_id": score_row.get("primary_score_item_id", ""),
        "secondary_score_item_ids": score_row.get("secondary_score_item_ids", ""),
        "risk_or_hidden_danger_point": risk_point,
        "problem_statement_template": f"现场核查发现【{item.get('candidate_subsection', scenario_id)}】存在风险：{risk_point}",
        "rectification_template": f"请依据环评、批复、许可、台账和现场事实补齐证据链：{evidence_chain}",
        "report_section_hint": score_row.get("possible_report_sections") or score_row.get("primary_score_item_id", ""),
        "evidence_chain": evidence_chain,
        "photo_points": photo_points,
        "answer_policy": item.get("answer_policy", "[\"PASS\",\"FAIL\",\"NA\",\"NEED_CONFIRM\"]"),
        "default_severity": severity,
        "default_deduct_policy": deduct,
        "deduct_runtime_binding": "EcoCheck existing score item / deduct-rule mapping must decide numeric deduct value",
        "runtime_status": RUNTIME_STATUS,
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
        "approval_status": APPROVAL_STATUS,
        "approval_source": APPROVAL_SOURCE,
        "approved_baseline_version": VERSION,
    }


def update_artifact_manifest():
    path = ROOT / "artifact_manifest.json"
    data = read_json(path)
    artifacts = data.setdefault("artifacts", {})
    artifacts.update({
        "approved_scenario_templates_v1_0.json": "data/approved_baseline/approved_scenario_templates_v1_0.json",
        "approved_score13_mapping_v1_0.csv": "data/approved_baseline/approved_score13_mapping_v1_0.csv",
        "approved_inspection_items_v1_0.csv": "data/approved_baseline/approved_inspection_items_v1_0.csv",
        "approved_inspection_items_v1_0.json": "data/approved_baseline/approved_inspection_items_v1_0.json",
        "approved_show_if_rules_v1_0.csv": "data/approved_baseline/approved_show_if_rules_v1_0.csv",
        "approved_show_if_rules_v1_0.json": "data/approved_baseline/approved_show_if_rules_v1_0.json",
        "approved_issue_remediation_report_chain_v1_0.csv": "data/approved_baseline/approved_issue_remediation_report_chain_v1_0.csv",
        "approved_issue_remediation_report_chain_v1_0.json": "data/approved_baseline/approved_issue_remediation_report_chain_v1_0.json",
        "approved_baseline_knowledge_manifest_v1_0.json": "manifests/approved_baseline_knowledge_manifest_v1_0.json",
        "approved_baseline_knowledge_gate_report_v1_0.json": "reports/approved_baseline_knowledge_gate_report_v1_0.json",
        "FINAL_APPROVED_BASELINE_KNOWLEDGE_v1_0.md": "reports/FINAL_APPROVED_BASELINE_KNOWLEDGE_v1_0.md",
        "build_approved_baseline_knowledge_v1_0.py": "build_approved_baseline_knowledge_v1_0.py",
        "validate_approved_baseline_knowledge_v1_0.py": "validate_approved_baseline_knowledge_v1_0.py",
    })
    write_json(path, data)


def main():
    update_artifact_manifest()
    scenarios = read_json(artifact_path("scenario_templates.json"))
    score_rows = read_csv(artifact_path("scenario_to_score13_mapping_v0_3.csv"))
    inspection_rows = read_csv(artifact_path("inspection_candidate_recommendations_v0_3.csv"))

    scenario_by_id = {row["scenario_id"]: row for row in scenarios}
    score_by_id = {row["scenario_id"]: row for row in score_rows}

    approved_scenarios = [approved_boundary(row) for row in scenarios]
    approved_scores = [approved_boundary(row) for row in score_rows if row.get("scenario_id") in scenario_by_id]
    approved_inspections = [approved_boundary(row) for row in inspection_rows if row.get("scenario_id") in scenario_by_id]

    show_if_rows = []
    chain_rows = []
    for item in approved_inspections:
        scenario = scenario_by_id[item["scenario_id"]]
        score_row = score_by_id.get(item["scenario_id"], {})
        show_if_rows.append(build_show_if_rule(item, scenario, score_row))
        chain_rows.append(build_issue_chain(item, scenario, score_row))

    write_json(APPROVED_DIR / "approved_scenario_templates_v1_0.json", approved_scenarios)

    score_fields = list(approved_scores[0].keys()) if approved_scores else []
    write_csv(APPROVED_DIR / "approved_score13_mapping_v1_0.csv", approved_scores, score_fields)

    inspection_fields = list(approved_inspections[0].keys()) if approved_inspections else []
    write_csv(APPROVED_DIR / "approved_inspection_items_v1_0.csv", approved_inspections, inspection_fields)
    write_json(APPROVED_DIR / "approved_inspection_items_v1_0.json", approved_inspections)

    write_csv(APPROVED_DIR / "approved_show_if_rules_v1_0.csv", show_if_rows)
    write_json(APPROVED_DIR / "approved_show_if_rules_v1_0.json", show_if_rows)

    write_csv(APPROVED_DIR / "approved_issue_remediation_report_chain_v1_0.csv", chain_rows)
    write_json(APPROVED_DIR / "approved_issue_remediation_report_chain_v1_0.json", chain_rows)

    manifest = {
        "knowledge_base_version": VERSION,
        "final_state": FINAL_STATE,
        "runtime_status": RUNTIME_STATUS,
        "runtime_integration": RUNTIME_INTEGRATION,
        "approval_status": APPROVAL_STATUS,
        "approval_source": APPROVAL_SOURCE,
        "approval_scope": APPROVAL_SCOPE,
        "approval_attestation": "User stated the knowledge base has completed manual review and confirmation, and requested approved baseline knowledge for EcoCheck show_if and downstream chains.",
        "approval_date": date.today().isoformat(),
        "outputs": {
            "approved_scenario_templates": len(approved_scenarios),
            "approved_score13_rows": len(approved_scores),
            "approved_inspection_items": len(approved_inspections),
            "approved_show_if_rules": len(show_if_rows),
            "approved_issue_chains": len(chain_rows),
        },
        "runtime_contract": {
            "can_drive_show_if": True,
            "can_drive_template_item_visibility": True,
            "can_drive_issue_remediation_report_chain": True,
            "can_bind_deduct_policy": True,
            "numeric_deduct_values_source": "EcoCheck existing score item and deduct-rule mapping",
            "enterprise_permit_type_policy": "Do not infer enterprise formal permit_type without enterprise permit/EIA/site evidence.",
        },
        "source_artifacts": [
            "scenario_templates.json",
            "scenario_to_score13_mapping_v0_3.csv",
            "inspection_candidate_recommendations_v0_3.csv",
            "artifact_manifest.json",
        ],
    }
    write_json(artifact_path("approved_baseline_knowledge_manifest_v1_0.json"), manifest)

    gate = {
        "validation_status": "PENDING_RUN_VALIDATE",
        "final_state": FINAL_STATE,
        "runtime_status": RUNTIME_STATUS,
        "runtime_integration": RUNTIME_INTEGRATION,
        "approval_status": APPROVAL_STATUS,
        "counts": manifest["outputs"],
    }
    write_json(artifact_path("approved_baseline_knowledge_gate_report_v1_0.json"), gate)

    final_report = f"""# FINAL_APPROVED_BASELINE_KNOWLEDGE_v1_0

final_state: `{FINAL_STATE}`

本包把已人工审核确认的环保语义知识库导出为 `approved baseline knowledge`，用于 EcoCheck 后续读取 `show_if`、检查项、问题/整改/报告链路。

## 边界

- 这是知识库侧 approved baseline export，不直接修改 EcoCheck 小程序代码。
- 可驱动模板项显示、问题整改报告链路和扣分策略绑定。
- 数值扣分仍应由 EcoCheck 现有 `score-item` / `deduct-rule` 映射决定。
- 企业正式 `permit_type` 仍不得仅凭行业候选推断，必须结合企业许可证、环评、批复、台账和现场事实。

## 产物

- `data/approved_baseline/approved_scenario_templates_v1_0.json`
- `data/approved_baseline/approved_score13_mapping_v1_0.csv`
- `data/approved_baseline/approved_inspection_items_v1_0.csv/json`
- `data/approved_baseline/approved_show_if_rules_v1_0.csv/json`
- `data/approved_baseline/approved_issue_remediation_report_chain_v1_0.csv/json`
- `manifests/approved_baseline_knowledge_manifest_v1_0.json`

## 验证

```powershell
python build_approved_baseline_knowledge_v1_0.py
python validate_approved_baseline_knowledge_v1_0.py
```
"""
    artifact_path("FINAL_APPROVED_BASELINE_KNOWLEDGE_v1_0.md").write_text(final_report, encoding="utf-8")

    print(json.dumps({
        "build_status": "PASS",
        "knowledge_base_version": VERSION,
        "final_state": FINAL_STATE,
        "runtime_integration": RUNTIME_INTEGRATION,
        "approved_show_if_rules": len(show_if_rows),
        "approved_issue_chains": len(chain_rows),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
