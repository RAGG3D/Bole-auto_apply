---
name: bole
description: 本地求职工作流，供 Claude、Codex 或其他能读文件和运行 Python 的 agent 发现职位、按完整 JD 匹配、生成定制材料并在授权后投递。明确要求 Stretch 或编写硬缺口时生成保留原经历的扩展草稿，只生成不上传；用户自带全部链接且自行投递时使用 Bole Lite。
---

# Bole（伯乐）v0.6

这是 agent 驱动的技能包，不是服务。当前 agent 负责理解 JD、证据匹配和写作；Python
负责抓取、分诊、构建及记账。Claude、Codex 和其他 agent 使用同一流程，不要求
Claude CLI、某个模型或子 agent。所有路径相对于本技能根目录；先确定绝对根目录。
运行数据仅写入该工作目录的 `profile/`、`Applications/`、`state/`，不进入 Git。

## 路由

- 初次使用：`references/workflows/doctor.md` → `references/workflows/setup.md`。
  已有确认资料直接复用，只补缺失或有冲突的事实。
- 扫描、匹配、生成：`references/workflows/scan.md`。先读
  `references/matching.md`、`references/materials.md` 和 `references/contracts.md`。
- 自动投递：仅用户本次或既有明确授权适用时读 `references/workflows/apply.md`，
  同时要求 `config.auto_submit.enabled=true`；按已授权的清单/确认策略执行。
- **Stretch**：只有用户在本次任务明确要求 “Stretch”、“编写”模式或“编写/编造 JD 硬缺口”
  才读 `references/stretch.md`。普通“编写简历”、JD 中的 stretch、旧
  `config.stretch` 和“匹配积极些”都不触发。明确要求 Stretch 本身足够，无需再确认开关。
- **Lite**：用户自带全部广告链接、自行投递时读 `bole-lite/SKILL.md`，不用运行发现流程。
- token 估算/实测：按需读 `references/token-budget.md`。

## 共同边界

1. 默认 strict：已确认的事实及用户最新明确纠正是事实来源；更新事实台账、摘要和相关
   文档，不能将 JD 的要求、模型推测或旧生成简历当作证据。来源相互矛盾时保留缺口。
2. `facts.red_lines` 与 `phrasing_rules` 适用于两种模式。红线扫描只检查词及有限规则，
   **不能证明内容真实**。经历归属、技能等级、数字和架构还必须按证据人工式核对。
3. 每段经历的目的、用户、原有技术/架构、角色归属、时间和 achievement 是固定边界。
   明确区分团队贡献和独立交付、个人练习和正式上线、可访问产品和仅文档预览。
4. 先读完整 JD/必需附件再生成；资格不符、已关闭、雇主排除、核心职责不匹配等只进
   中央报告。抓取失败属于待补全文，不能记成“不适合”。不为阻断岗位创建申请文件夹。
5. Stretch 与“只生成不投递”包具有 `submission_policy=never`；禁止上传、填表、发送
   和调用投递代理。Lite 永远手动投递。不得用路径改名、--force 或 continue 绕过。
6. 验证码/评测/真人验证按环境权限转手动；不得代做评测或绕过验证。凭据不进入材料、
   日志或 Git。邮箱读取、帐号操作、平台文件删除只用当前用户授权和环境支持的能力，
   不能从某个历史用户的授权推成全局默认。默认登录由用户完成。
7. 已提交/未知状态先只读核实再恢复，不盲目重投。只把确认页、权威申请列表或确认邮件
   当作提交证据。无浏览器保留 HTML，并清楚注明 PDF 未生成、未验证排版。
8. 按 `config.ui_language` 对话；材料语言独立取 `facts.language_of_materials`。
   继续处理批次中可完成的项目，集中报告阻断项，不把一个缺失 JD 扩散成全批停止。

Claude slash commands 只是 `references/workflows/` 的入口。其他 agent 直接读同一文件。
跨 agent 使用和可复制安装包见 `references/agents.md`。独立邮件清理插件说明见
`plugins/assholassin/README.md`，求职任务不自动触发邮件删除。
