# FINAL_COMPLETION_REPORT_v1_8_noise_radiation_extension

final_state: `NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY`

本轮没有新建独立规则库，而是在现有环保语义规则库上增量补齐噪声和辐射/放射两个知识域。

## 完成内容

- 将新增法规标准资料纳入 `reference_sources/noise` 与 `reference_sources/radiation`。
- 新增 4 个噪声场景模板和 10 个辐射/放射场景模板。
- 补齐 3 个既有工序证据回填场景模板，消除激活规则悬空引用。
- 保留旧模板兼容关系，并标注噪声、辐射应由新细分模板承接。
- 更新 13维映射候选、现场排查候选、工序触发字典和工序-场景激活规则。
- 生成 `noise_radiation_reference_sources_v1_8.csv/json` 作为 PDF 资料可审计索引。
- 去除重复 PDF 索引，资料索引按文件内容和规范化路径保持唯一。

## 禁止事项

- 不接 EcoCheck runtime。
- 不生成正式 permit_type。
- 不生成正式检查模板。
- 不自动扣分。
- 辐射/放射不做全行业默认适用。

## 验证

```powershell
python build_noise_radiation_domain_extension_v1_8.py
python validate_noise_radiation_domain_extension_v1_8.py
```
