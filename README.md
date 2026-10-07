# Bole（伯乐）

[English](README.en.md)

> 千里马常有，而伯乐不常有——现在有了。

Bole 是本地求职技能包：发现职位、按完整 JD 匹配、生成简历和求职信，并在用户授权后
投递。Claude、Codex 和其他能读写文件、运行 Python 的 agent 共用同一工作流。
默认材料只使用确认事实；明确要求 **Stretch／编写硬缺口** 时生成保留原经历的扩展
草稿，**只生成文件，不上传、不投递**。

## 选择 Bole 或 Bole Lite

| | Bole | Bole Lite |
|---|---|---|
| 招聘广告 | 按配置发现 + 用户补充 | **用户手动提供全部链接/完整 JD** |
| 匹配 | 全文资格闸门、职责匹配、评分和召回复核 | 逐条要求与事实对应，不搜索/排名 |
| 默认输出 | CV、cover、JD 要求的其他材料 | **CV**，cover 仅按用户要求 |
| Stretch | 明确触发，只出文件 | 同样支持，只出文件 |
| 投递 | 可选，默认关闭；授权后使用 OpenClaw | **用户手动投递** |
| 中心 token 预算/岗 | 约 **13.1 万**（含投递） | 约 **2.83 万**（CV） |

这是 agent 驱动的技能，不是无人监管的独立程序或保证覆盖全部网站的搜索服务。

## 开始使用

需要 Python ≥3.10、Git，以及能访问此目录的 agent。Chrome/Chromium/Edge 用于 PDF；
没有浏览器保留 HTML，手动打印。自动投递另需可用 OpenClaw；Lite 不需要。

```sh
git clone https://github.com/RAGG3D/Bole-auto_apply.git bole
cd bole
bash install.sh
```

然后给当前 agent 以下指令之一：

```text
读取 SKILL.md，使用 Bole 建立我的资料并匹配最近 7 天的职位，只生成文件。

读取 bole-lite/SKILL.md，使用 Bole Lite。以下是全部广告链接：……
根据我的确认资料和红线，为每岗生成英文两页 CV，我自己投递。

使用 Bole Lite Stretch，为以上岗位编写合理的硬技能实施过程。
保留每段经历原有的目的、技术架构和 achievement，只生成文件，不投递。
```

Claude Code 可使用 `/doctor` → `/setup` → `/scan`；其他 agent 直接读取同一份
`references/workflows/`。已有事实资料只补缺失/矛盾部分，无需每次重做采访。
AGENTS.md 和 CLAUDE.md 都指向共享入口，没有两套会漂移的核心规则。

复制到任意 agent 技能目录前，可构建自包含包（目标不能已存在）：

```sh
python3 scripts/package_skill.py --variant full --out /tmp/bole
python3 scripts/package_skill.py --variant lite --out /tmp/bole-lite
```

包只取公共资源，不含个人事实、聊天、生成简历或凭据。不同平台的自动发现机制由其
自身决定；直接让 agent 读取 SKILL.md 即可。[跨 agent 说明](references/agents.md)。

## v0.6 修复了什么

- **匹配错误与遗漏**：按实际职责扩展相邻职位，不只看 title；consultant 不自动等于
  AI automation。记录来源覆盖、失败和待复核项，不把漏抓说成没有岗位。
- **完整 JD 闸门**：正文和必需 PD/selection criteria 附件读全才生成。800 字符只是
  提示，长正文也不能掩盖缺附件。资格不符、关闭、雇主排除只进中央报告。
- **防止过早筛除**：标题中的公民/clearance/红线信号送 REVIEW；企业毕业生项目不
  等于政府身份限制。用户链接进入全文核对。雇主 blocklist 同样约束手动链接。
- **资料与写作**：同步最新确认项目/纠正，检查必留经历；保留项目用途、架构和团队
  角色。CV 定稿后同步 cover，不强制每封信硬塞一句缺口。
- **审核与投递**：CV/cover 目标 title 一致；文件或事实变化使审核过期。严格区分
  verified、transferable、gap、proposed；普通表单文字由 agent 依据事实处理。
  所有合规 tier 都进入已授权队列；超时先核实，有证据才记已提交。

规则来源是近期实际纠错；公开仓库只保留匿名化总结。
[修订依据](references/workflow-audit.md) · [匹配规则](references/matching.md) ·
[材料规则](references/materials.md) · [JSON 契约](references/contracts.md)。

## Strict 与 Stretch

**Strict 默认开启**：只使用确认事实和最新纠正。红线扫描是词汇检查，不能证明材料
真实；agent 仍需核对原始证据、技能归属、日期和成果。不得将 JD 的要求当作事实。

**Stretch 必须明确触发**：“Stretch”、“编写”模式或明确“编写/编造 JD 硬缺口”。普通“编写简历”
以及 config 中旧的 `stretch` 匹配容忍度都不触发。先冻结 strict 基线，再把兼容的技术
实施过程补充到最适合的经历；保留原有技术、架构、目的、成果、时间和团队身份。
不为覆盖关键词把本地工具改成企业平台，也不编学历、证照、客户、年限或数字成果。

新增内容在 `tailoring.json` 标明依据和 verified/proposed，正文保持自然。没有合理
归属就保留 gap，不能承诺完美覆盖。扩展草稿放 `Applications/Stretch/`，其
`material_mode=stretch, submission_policy=never` 由脚本拦截 run、continue、--force。
用户后来补齐事实及项目归属后，须重新生成和审核 strict 包才能进入真实申请流程。
[Stretch 完整说明](references/stretch.md)。

## 每岗 token 估算

| 模式 | 中心预算 | 规划范围 |
|---|---:|---:|
| Bole 全流程（CV+cover+投递核实） | 130,700 | 65,350–392,100 |
| Bole Stretch（文件，不投递） | 80,500 | 40,250–241,500 |
| Lite（CV，用户手动投递） | 28,300 | 14,150–84,900 |
| Lite Stretch（扩展 CV，不投递） | 48,100 | 24,050–144,300 |

**这是估算，尚未实测新版均值**。输入包含缓存命中和重复上下文；不是订阅扣费额度。
默认已有资料、压缩上下文、完整版 5 轮 ATS + 1 轮核实。长会话/反复改稿可能远超范围。
Lite 预算约低 78%，主要因为不搜索、不自动投递、默认不写 cover，输出范围不同。

```sh
python3 scripts/token_budget.py --variant full --jobs 10
python3 scripts/token_budget.py --variant lite --jobs 10 --stretch
python3 scripts/token_budget.py --usage state/usage.jsonl --jobs 10 --submitted 8
```

[计算方法、历史统计局限及实测格式](references/token-budget.md)。

## 文件与投递

运行时只使用 gitignored 的 `profile/`、`Applications/`、`state/`。每岗保留 JD、
verdict、内容 JSON、PDF/HTML、tailoring 审核依据和 review 哈希。真实匹配包按
80+/70–79/<70 分档；Lite 与 Stretch 用各自目录。缺全文或未通过生成闸门的岗位
只出现在中央报告，不创建空目录；待补/超额岗位保留到下轮，避免 seen 台账吞掉。

`/apply` 默认关闭，启用需配置 `auto_submit.enabled=true`、适用的用户授权和确认
策略。只有 ATS 地图允许且在用户白名单内才自动提交。旧包须升级 v2 verdict 重审。
上传前核对岗位专属 PDF 和预览，不使用网站存储的旧简历。只有确认页/权威申请列表/
确认邮件才证明成功；unknown 不自动重投。状态写回岗位 STATUS.md。

登录默认由用户完成；邮箱读取及平台清理只按当前用户明确授权和环境能力处理。真人
验证、在线评测和登录墙不会被绕过。Bole Lite 和 Stretch 不调用投递代理。
[投递协议](references/workflows/apply.md)。

公开来源脚本支持 LinkedIn、Workday、Greenhouse/Lever/Ashby 职位板和直接 URL/手贴
JD。SEEK/Indeed 可借助当前 agent 的公开检索工具发现；遇墙请贴正文。中国站可尝试
详情 URL，支持中文编码；访问验证转手贴，不做登录搜索。BOSS直聘等由用户本人沟通。
不要将个人材料/凭据提交到 Git。远程 agent/模型处理内容仍受其服务数据政策约束；
“本地存储”不等于模型推理一定离线。

## 独立邮件插件

[assHOLassin](plugins/assholassin/README.md) 保留为独立 IMAP 清理插件：
`/mail-setup` → `/mail-rules` → `/mail-clean`，先 dry-run 再按用户确认执行。
求职任务不默认删除邮件、拒信或申请目录。

## 验证与贡献

```sh
python3 scripts/ats_lint.py
python3 -m unittest discover tests
```

测试全离线，使用虚构资料和假的投递代理，不向招聘网站提交申请。
欢迎补充 ATS 能力地图和来源缺陷报告；不要在 issue/PR 中放个人资料。
[贡献指南](CONTRIBUTING.md) · [MIT License](LICENSE)。

材料、职位状态与薪资须结合原始来源核实；软件不保证信息完整、提交成功或获得录用。
