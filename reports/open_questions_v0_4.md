# Open Questions v0.4

- `OQ-001` [P0/ETO] 1512/1513等GB/T 4754小类名称与早期映射是否存在错配？正式化前需以GB/T 4754-2017原表核准代码、名称和行业边界。  
  close_criteria: 代码名称冲突经原始GB/T 4754表格复核并形成修正记录。
- `OQ-002` [P1/ETO] 第22条等许可名录条目使用代表性小类或行业短语时，是否可外推到同组/同大类其他小类？  
  close_criteria: 形成代表性小类外推规则，明确可外推、不可外推和需环评确认边界。
- `OQ-003` [P1/ETO] 第36条纸浆制造221与2211、222、223之间的继承边界如何确认，是否仅限221相关小类？  
  close_criteria: 纸浆/造纸/纸制品相邻中类边界经名录和GB/T代码复核。
- `OQ-004` [P1/ETO] 第38条纸制品制造223是否不得继承到2211/222类条目，工业废水/废气条件如何触发？  
  close_criteria: 纸制品相关条件形成条目-小类适用规则和现场确认问题。
- `OQ-005` [P1/ETO] 第15条等食品/农副食品条目的通用工序触发是否只作为候选召回，不得直接推导企业许可管理类型？  
  close_criteria: 通用工序触发被统一限定为NEED_EIA_OR_PERMIT_CONFIRM或MAY_APPLY。
- `OQ-006` [P1/ETO] 第80条等装备/金属制品相关条目中，3311等相邻小类与表面处理、喷涂、热处理等通用工序如何确认？  
  close_criteria: 形成3311及相关小类的工序触发边界和确认证据要求。
- `OQ-007` [P0/Product+ETO] 候选排查章节、候选子章和S18/S19等知识库章节编号是否只作为未来候选，不得映射为当前EcoCheck正式模板章节？  
  close_criteria: 产品和ETO确认正式模板章节映射方案；未经审批不得接运行时。
- `V03_CONTEXT_SCOPE_001` [P1/ETO] DIVISION_CONTEXT条目-小类适用关系需要人工审阅后才能从MAY_APPLY/NEED_EIA升级。  
  close_criteria: 形成书面业务口径或保持为BLOCKS_RUNTIME开放问题。
- `V03_PERMIT_TYPE_001` [P1/ETO] 所有target_management_condition只代表名录单元格类型，不得作为企业正式permit_type。  
  close_criteria: 形成书面业务口径或保持为BLOCKS_RUNTIME开放问题。
- `V03_GENERAL_PROCESS_001` [P1/ETO] 109-112通用工序触发需依据企业锅炉、炉窑、表面处理、水处理事实确认。  
  close_criteria: 形成书面业务口径或保持为BLOCKS_RUNTIME开放问题。
- `V03_SCENARIO_TEMPLATE_001` [P1/ETO] 尾矿库、餐饮油烟、实验室废液、垃圾焚烧/填埋等是否需要新增场景模板，需后续业务评审。  
  close_criteria: 形成书面业务口径或保持为BLOCKS_RUNTIME开放问题。
- `V03_ECOCHECK_RUNTIME_001` [P1/ETO] 候选排查项不得接EcoCheck运行时，需模板章节和扣分口径专项审批。  
  close_criteria: 形成书面业务口径或保持为BLOCKS_RUNTIME开放问题。
- `V04_ENTRY_108_CONTEXT_001` [P0/ETO] 第108条是“除1-107外的其他行业，涉及通用工序”的兜底交叉引用条目；v0.4不直接展开为条目-小类适用关系，避免被误读为独立行业覆盖。其治理口径由109-112通用工序候选关系承接，并在正式化前作为开放问题确认。  
  close_criteria: 确认第108条是否只作为109-112通用工序兜底引用，或需新增显式关系表。
- `V04_HUMAN_REVIEW_EMPTY_001` [P0/ETO+ESO] 主适用关系表human_review_label/human_reviewer/human_review_notes保持全空是待审队列状态；正式化前需定义标签枚举、抽样/全量策略、责任人和签字闭环。  
  close_criteria: 完成审阅标签枚举、审阅责任和签字留痕制度。
- `V04_SCORE13_PROMOTION_001` [P1/Product+ETO] S01-S13报告口径保持不变，但S07/S08/S10/S13等二级语义层如何进入RAG/图谱和报告段落映射？  
  close_criteria: 形成二级语义层字段与报告展示策略，不直接改名或拆分S01-S13。
- `V04_RUNTIME_APPROVAL_GATE_001` [P0/Product+Tech Lead] 候选知识库何时、由谁、以何种验证证据批准进入EcoCheck运行时？  
  close_criteria: 形成运行时接入审批门禁、回滚方案和小程序契约测试方案。
- `V04_NEGATION_POLARITY_001` [P0/ETO] 含除/不含/以外/无/未的条件是否均已保留排除语义，特别是“除纳入重点排污单位名录”的not_present谓词？  
  close_criteria: 否定语义谓词经抽检无正向化，必要时补充规则库单测。
- `V04_DIVISION_CONTEXT_APPLIES_001` [P0/ETO] 纯DIVISION_CONTEXT不得自动升级为APPLIES；未来如需升级，需直接代码/名称/条件文本证据和人工审阅记录。  
  close_criteria: 0条纯DIVISION_CONTEXT->APPLIES，升级路径有人工审阅字段和证据链。
- `V04_NOT_APPLY_BLOCKING_FLAGS_001` [P0/ETO] NOT_APPLY必须有/、明确排除文本、相邻条目/小类排除或forced_denoise依据；无法解释的应降为待确认。  
  close_criteria: 0条NOT_APPLY缺少blocking_flags或明确排除依据。
