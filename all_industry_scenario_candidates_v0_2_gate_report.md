# 全量行业候选规则 v0.2 门禁报告

- 校验状态：`PASS`
- 四位小类底表：1382
- 候选规则：1382
- 覆盖四位小类：1382
- 缺失：0
- 额外：0
- 行业代码重复：0
- candidate_rule_id 重复：0
- permit/runtime 违规：0
- 悬空/冲突场景引用：0
- 服务业过重 BLOCK：0
- 服务业 REVIEW：0

## 运行时边界

`NOT_FOR_RUNTIME_CANDIDATE_KB_ONLY`。不得生成正式 `permit_type`，不得接 EcoCheck 小程序，不得生成正式检查模板。

## 阻塞错误

- 无
