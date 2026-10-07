---
name: bole-lite
description: 根据用户手动提供的全部招聘广告链接或完整 JD，生成遵守事实红线的定制简历；明确要求 Stretch/编写硬缺口时生成保留原经历技能、架构和成果的扩展草稿。用户负责找工作和手动投递，不发现职位、不上传、不自动投递。
---

# Bole Lite

仅做完整 JD 理解、证据对应、简历生成与核对。每次输入全部广告链接（或全文）、当前
事实/项目档案、红线、材料语言。已有资料直接复用；只问影响内容的关键缺失，不要求
完整 Bole 的五轮建档。用户手动寻找广告和投递；默认只出 CV，cover 仅明确要求时生成。

在仓库中共享资源根目录是本文件的 `../`；独立安装包中共享资源就在本文件同级。
先定位含 `references/materials.md` 的根目录，后续命令用该根目录下绝对路径。
只读取本文件、`references/materials.md`、`references/contracts.md` 中材料/模式字段；
Stretch 时再读 `references/stretch.md`。不加载发现、薪资、ATS、邮箱或投递文档。

1. 把用户提供的**每个** URL 写入 `state/lite_inputs.json`。抓完整 JD、必要附件，保留
   URL 和状态。可用 `scripts/sources.py jd --source url --url '<URL>'` 或当前 agent
   的网页工具；遇墙请用户贴全文，其他链接继续。不得搜索新广告或静默丢掉输入。
2. 对每岗提取硬要求/加分项/客观资格，逐项映射已确认事实及经历 id。不做发现排名或
   分数阈值筛选。资格/全文/红线冲突列为 blocked 并报告；有真实差距的材料如实写，
   不冒充覆盖。必要附件未知先不出最终 CV。
3. 默认 strict：只使用已确认经历，事实与最新明确纠正同步。遵守全部 red_lines 和
   phrasing_rules；保留项目目的、受众、原技能/架构、团队角色、日期和 achievement。
   选择相关项目并核对 must_include，不因压页丢掉最有证据的经历。
4. 只有明确要求 “Stretch”、“编写”模式或“编写/编造 JD 硬缺口”才走共享 Stretch 流程；普通“编写
   一份简历”保持 strict。合理新增技术过程写进最适配经历，拟写和事实在 sidecar 分开；
   不改变原架构/成果。没有兼容归属保留 gap，不强行覆盖。
5. 生成 `_content/cv.json`、PDF/HTML、完整 `JD.txt`、`verdict.json`、`tailoring.json`、
   简短 README；默认 `Applications/Lite/<Company - Role>/`，Stretch 放
   `Applications/Stretch/<Company - Role>/`。verdict 包含 title、material_mode、
   workflow_variant=lite、submission_policy=manual_only（Stretch 为 never）、
   required_documents、requirements；不需要 Bole 的 fit 和发现字段。
6. 运行红线扫描、带 `--facts` 的构建及 `workflow_guard.py review`；核对 CV/cover
   一致性和每页排版。完成后输出每个输入的结果、文件路径、拟写项/缺口。

**永不自动上传、填表、投递或调用 submit.py/OpenClaw**。strict CV 交给用户本人手动
投递；Stretch 草稿仅审阅。进入真实申请须补事实及归属证据并重新生成 strict 包。
不读取全聊天历史、不建立搜索队列、不为每岗重复加载整套说明；小批处理并复用档案摘要。
预算口径见按需读取的 `references/token-budget.md`；不要为估 token 扩大常规上下文。
