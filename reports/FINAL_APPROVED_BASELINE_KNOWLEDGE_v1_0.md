# FINAL_APPROVED_BASELINE_KNOWLEDGE_v1_0

final_state: `APPROVED_BASELINE_KNOWLEDGE`

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
