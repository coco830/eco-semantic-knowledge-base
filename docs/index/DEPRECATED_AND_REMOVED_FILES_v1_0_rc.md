# DEPRECATED_AND_REMOVED_FILES_v1_0_rc

final_state: `NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY`
runtime_integration: `disabled`

以下文件属于早期试跑或旧运行时接入口径，已不属于当前 v1.0-rc design-only baseline 主线。

## 已移除

- `12个优先行业规则库_v1.1接入版.json`: 早期 12 行业接入版，直接给出 `permit_type` 并声明可接入小程序，和当前候选治理边界冲突。
- `v1.1更新说明.md`: 旧接入版说明，包含“可直接导入小程序使用”等过时口径。
- `generate_rules_v1_1_complete.py`: 旧接入版生成脚本。
- `build_knowledge_base.py`: 依赖旧 v1.1 JSON 的历史构建入口。

## 保留但不作为当前主入口

早期 v0.1-v0.3 产物保留为审计链路和可追溯证据；当前主入口以 `PROJECT_INDEX_v1_0_rc.md`、`knowledge_base_manifest_v1_0_rc.json` 和 `FINAL_COMPLETION_REPORT_v1_0_rc.md` 为准。

## 迁移说明

12个优先行业已经纳入 1382 个四位小类候选底座，不再需要旧接入版文件。后续若要做运行时接入，必须从 v1.0-rc 闸门设计另起实现，不得恢复旧接入版直接导入路径。
