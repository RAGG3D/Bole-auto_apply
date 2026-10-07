# 完整 JD 匹配与召回

## 发现不等于匹配

从确认项目中提取职责/能力词族，覆盖用户未直接说出的相邻岗位；例如自动化可扩展到
workflow、integration、business process、AI assistant、implementation consultant。
把词族写入本轮搜索计划，兼顾入门/中级和行业。consultant 只增加召回，不直接加分：
若实际职责是无关平台咨询且缺少目标自动化工作，不应因名称相近入选。

按当前可用能力搜索配置来源、公司公开 ATS，以及用户要求的 SEEK/Indeed/搜索引擎。
脚本不支持的站点可用当前 agent 的公开网页检索；搜到 snippet 只保留链接，不当完整 JD。
没有该工具/遇墙就记录来源缺口，不能说已“全网搜完”或仅有 N 个合适岗位。
人工提供的链接必入本轮清单，不能被标题正则淘汰；雇主 blocklist 仍生效。

`triage.py` 仅作标题优先级：SCORE 和 REVIEW 都读全文；LIST_other 要检查一轮相邻
职责候选，无法完成的写 pending_review。企业 graduate program 不等于政府公民限制。
标题/公司中的 clearance 或 redline 是待核实信号，不是事实闸门。Senior/Lead+ 默认
排除；双职级、非管理含义的 manager/lead 标题按真实职责复核，记录依据。

每来源记录：查询词、时间窗口、抓取成功/失败、分页限制、候选数、唯一数、待补全文数。
中央索引保证每个候选都有一个去向；pending_full_jd、pending_review、因 max_generate
暂缓的岗位必须保留到下轮，不能被 seen 台账永久吞掉。新增项目后对相关旧 list-only
岗位重评。人工明示重评绕过“已见”过滤，但不能绕过“已提交/未知”的防重投。

## 全文和资格

保存网页 URL、取得时间、完整正文、JD 引用的 PD/selection criteria 附件来源与状态。
800 字符只是疑似 stub 提示，不是完整性证明。必须下载并读到必要附件；正文长也可能
缺关键资格/申请文件要求。站点提供等价完整官方正文时可用，记录替代依据。
缺失必要附件、页面截断或岗位状态不明时列中央 blocker，不生成、不投递。

把要求拆成：资格/年限/地点、核心任务、必备技术、可替代技能（A OR B）、加分项、
软技能、文件要求。逐项保存原文及来源，区分 must、preferred、negation、AND/OR。
“citizen OR PR OR valid visa”不能当成 citizen-only；完整工作权利不能写成永久居民。
无法确认的硬资格不当作已满足；普通地点/驻场/搬迁约束同样先核对。

资格符合后按证据评分（固定七项，总计 100）：核心职责 30、技术技能 25、交付/生产
经验 15、行业 10、资历 10、协作沟通 5、加分项 5。记录每项证据/缺口和得分。
Senior 封顶默认 45，Lead+ 38，均不生成。身份与年限不由可迁移技能抵消。
行业关键词可用于说明兴趣/目标场景，不能伪造已有行业经历。领域目标明显不同则
`domain_fit=false`，分数再高也不生成。

严格分开 verified / transferable / gap / proposed。只有 verified 算完整覆盖；
transferable 不是已做过，proposed 是 Stretch 草稿，不回写事实或抬高基础 fit。
禁止承诺 100% 硬要求覆盖或为达百分比改项目本质。覆盖率分别报已验证/部分/缺口，
未确认客观条件单列；无理想要求时分母为零写 N/A。

生成沿用配置阈值（默认 70，合理 entry/junior/mid 可到 60，核心红线最多一项），
红线技能本身仍不得写入材料；说明缺口。`match_tolerance` 只调节候选阈值，旧
`config.stretch` 是兼容别名，**不是**编写模式。默认按分数分配 max_generate，超额
写 deferred，不是“不合适”。资格、全文、职责和雇主闸门优先于分数。
