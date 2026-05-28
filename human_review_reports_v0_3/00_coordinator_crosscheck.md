# v0.3 人工审阅总控交叉校验

## 基础统计
- 许可条件表: 336 行, entry=112, condition={'KEY': 112, 'SIMPLIFIED': 112, 'REGISTRATION': 112}
- 主适用关系表: 22815 行, industry=1382, entry=111, gate={'NEED_EIA_OR_PERMIT_CONFIRM': 19894, 'MAY_APPLY': 1756, 'NOT_APPLY': 941, 'APPLIES': 224}
- 样本审阅表: 408 行, industry=35
- 开放问题: 13 行
- 候选排查项: 22 行

## 交叉发现
- 主适用关系表未直接覆盖的许可名录 entry: [108]
  - 缺失 entry 需要判断是否因兜底/交叉引用被 109-112 替代；当前已知 entry 108 是通用工序兜底条。
- candidate_relation_id 重复数: 0
- 许可条件表 permit/runtime 违规: 0
- 主适用关系表 permit/runtime 违规: 0
- 候选排查项 runtime 违规: 0
- 主表 human_review_label 已填写: 0/22815
- 样本表 human_review_label 已填写: 0/408
- APPLIES 按 relation_source: {'DIRECT_CODE_MATCH+DIVISION_CONTEXT': 205, 'DIVISION_CONTEXT': 19}
- APPLIES 中非明显直接证据来源: 224
  - CTXV03_1311_9_REGISTRATION: industry=1311 entry=9 cond=REGISTRATION source=DIRECT_CODE_MATCH+DIVISION_CONTEXT reason=EXPLICIT_GROUP_CODE
  - CTXV03_1312_9_REGISTRATION: industry=1312 entry=9 cond=REGISTRATION source=DIRECT_CODE_MATCH+DIVISION_CONTEXT reason=EXPLICIT_GROUP_CODE
  - CTXV03_1313_9_REGISTRATION: industry=1313 entry=9 cond=REGISTRATION source=DIRECT_CODE_MATCH+DIVISION_CONTEXT reason=EXPLICIT_GROUP_CODE
  - CTXV03_1314_9_REGISTRATION: industry=1314 entry=9 cond=REGISTRATION source=DIRECT_CODE_MATCH+DIVISION_CONTEXT reason=EXPLICIT_GROUP_CODE
  - CTXV03_1319_9_REGISTRATION: industry=1319 entry=9 cond=REGISTRATION source=DIRECT_CODE_MATCH+DIVISION_CONTEXT reason=EXPLICIT_GROUP_CODE
  - CTXV03_1321_10_SIMPLIFIED: industry=1321 entry=10 cond=SIMPLIFIED source=DIRECT_CODE_MATCH+DIVISION_CONTEXT reason=EXPLICIT_GROUP_CODE
  - CTXV03_1321_10_REGISTRATION: industry=1321 entry=10 cond=REGISTRATION source=DIRECT_CODE_MATCH+DIVISION_CONTEXT reason=EXPLICIT_GROUP_CODE
  - CTXV03_1329_10_SIMPLIFIED: industry=1329 entry=10 cond=SIMPLIFIED source=DIRECT_CODE_MATCH+DIVISION_CONTEXT reason=EXPLICIT_GROUP_CODE
  - CTXV03_1329_10_REGISTRATION: industry=1329 entry=10 cond=REGISTRATION source=DIRECT_CODE_MATCH+DIVISION_CONTEXT reason=EXPLICIT_GROUP_CODE
  - CTXV03_1331_11_SIMPLIFIED: industry=1331 entry=11 cond=SIMPLIFIED source=DIVISION_CONTEXT reason=forced_sample_review

## 人工审阅优先行业 Top 20 by NEED_EIA_OR_PERMIT_CONFIRM
- 3012 石灰和石膏制造: 33
- 3021 水泥制品制造: 33
- 3022 砼结构构件制造: 33
- 3023 石棉水泥制品制造: 33
- 3024 轻质建筑材料制造: 33
- 3029 其他水泥类似制品制造: 33
- 3031 粘土砖瓦及建筑砌块制造: 33
- 3032 建筑用石加工: 33
- 3033 防水建筑材料制造: 33
- 3034 隔热和隔音材料制造: 33
- 3039 其他建筑材料制造: 33
- 3041 平板玻璃制造: 33
- 3042 特种玻璃制造: 33
- 3049 其他玻璃制造: 33
- 3051 技术玻璃制品制造: 33
- 3052 光学玻璃制造: 33
- 3053 玻璃仪器制造: 33
- 3054 日用玻璃制品制造: 33
- 3055 玻璃包装容器制造: 33
- 3056 玻璃保温容器制造: 33

## 强制样本主表分布
- 4620 污水处理及其再生利用: rows=18, gate={'NOT_APPLY': 3, 'APPLIES': 3, 'NEED_EIA_OR_PERMIT_CONFIRM': 12}, entries=['109', '110', '111', '112', '98', '99']
- 7721 水污染治理: rows=15, gate={'NEED_EIA_OR_PERMIT_CONFIRM': 13, 'NOT_APPLY': 2}, entries=['103', '109', '110', '111', '112']
- 2211 木竹浆制造: rows=21, gate={'APPLIES': 1, 'NOT_APPLY': 8, 'NEED_EIA_OR_PERMIT_CONFIRM': 12}, entries=['109', '110', '111', '112', '36', '37', '38']
- 2530 核燃料加工: rows=21, gate={'NOT_APPLY': 9, 'NEED_EIA_OR_PERMIT_CONFIRM': 12}, entries=['109', '110', '111', '112', '42', '43', '44']

## open_questions 字段
- headers: ['question_id', 'topic', 'question', 'blocking_level', 'status', 'source_basis', 'runtime_status']
  - question_id: empty=0/13
  - topic: empty=0/13
  - question: empty=7/13
  - blocking_level: empty=0/13
  - status: empty=0/13
  - source_basis: empty=0/13
  - runtime_status: empty=0/13
