# 同一技能，多种 agent

共同能力要求：读取 Markdown/JSON、编辑本地文件、运行 Python ≥3.10；联网获取 JD
可由内置网页工具或 sources.py 完成。没有抓取能力时用用户提供的完整正文。
不要求某个模型、专有工具名称、计划工具、子 agent 或 Claude 订阅。

- 在 Claude Code 中打开仓库，CLAUDE.md 指向 SKILL.md；`/scan` 等只是薄入口。
- 在遵循 AGENTS.md 的 agent 中打开仓库，读取该入口，再按 SKILL.md 路由。
- 其他 agent：明确指示“读取此目录 SKILL.md，并按它完成任务”。不支持 slash command
  时直接说“Bole 扫描”“Bole 只生成”“Bole Stretch”即可。
- Lite 直接指向 bole-lite/SKILL.md。它不加载整个 Bole，也不依赖其他技能安装。

需要放进任意 agent 的技能目录时，构建一个**自包含、无个人数据**的目录：

```sh
python3 scripts/package_skill.py --variant full --out /tmp/bole
python3 scripts/package_skill.py --variant lite --out /tmp/bole-lite
```

由用户指定目标技能目录后可直接用 --out 该位置。工具不会覆盖已有目录，避免误删用户
修改。不要只拷贝 Lite SKILL.md 而丢掉 references/scripts/templates。每个平台是否自动
发现技能由其自己的加载机制决定；手动读取入口始终可用。无需更改其全局系统配置。

自动投递适配器目前为 OpenClaw（可选），与主 agent 品牌无关。缺少它仍可生成材料。
不同 agent 的浏览器/邮箱权限不继承；不得把另一环境的帐号、凭据或授权拷入技能包。
