# 材料写作和核对

先同步当前确认事实及纠正，建立经历索引：id、目的、用户、原有技能/架构、功能、
个人/团队归属、日期、成果、公开状态、可用链接。用户指定 must_include 的相关经历
必须出现；从完整项目索引选择与 JD 最有证据关系的项目，不能只复用旧简历漏掉新项目。
不把个人项目当作受雇经历，功能性 title 可贴近职责但保留真实团队角色和职级。

每个项目第一条说明做了什么、为谁、实现什么；后续条目说明与 JD 有关的具体实施
步骤、数据流、部署、错误恢复、维护或协作。目的优先于关键词覆盖。不得把本地工具
改写成企业云平台、将团队项目写成独立开发、将 README 预览写成公开可运行产品。
领域没有直接经历时可以写兴趣和可迁移工作，不虚构客户、用户规模或商业落地。

每岗生成当前材料→逐项核对 JD→复核遗漏项目→最后改求职信。求职信使用具体例子和
自然个人动机，避免 keyword 列表及套话；与 CV 的 title、日期、技术归属、成果一致。
只在有实质性缺口时自然解释差距，不为凑“一句缺口”硬造短板。目标岗位 title 在
cv.target_title/cover.target_title/verdict.title 一致，历史职务不会被目标 title 替代。

内容 JSON 兼容 `build_docs.py` 的 cv/cover schema。CV 使用 name/subtitle/contact/
profile/sections；每节 heading/entries；条目 role/org/meta/bullets；新增
experience_id 对应事实台账的稳定 ID。每份内容加 target_title。默认 CV 两页 A4、
cover 一页，可按用户要求调整。技术技能紧接 profile；项目/雇佣经历次序按用户偏好。
JD 要求 KSC/其他文件时也要完成，文件要求矩阵不能遗漏：可用当前 agent 的文档工具
生成并保存 `_content/<kind>.json`，没有相应渲染能力就保留草稿并集中报告阻断，
不得谎称包完整。核心 Python renderer 只支持 cv/cover。

先扫描 `_content/`（这里只放实际材料，不放含 JD 红线词的审核笔记），再构建：

```sh
python3 scripts/redline_scan.py --facts profile/facts.json --content '<job>/_content/'
python3 scripts/build_docs.py '<job>/_content/cv.json' '<job>/Name - CV.pdf' --fit-pages 2 --facts profile/facts.json
python3 scripts/build_docs.py '<job>/_content/cover.json' '<job>/Name - Cover Letter.pdf' --fit-pages 1 --facts profile/facts.json
```

扫描未通过即停止该材料。专名警告要逐项与证据比较；“未命中红线”不等于真实。
构建后读 PDF 提取文本并看每页：无截断、缺字、空白页、段落拆裂、超小字号；核对
全部必需内容仍在、顺序/语言/文件名一致。无法查看 PDF 就 layout_reviewed=false。
HTML fallback 不作为已完成 PDF，不进入自动提交。修改之后重新构建和检查。

`tailoring.json` 记录 identity_reviewed、claims_reviewed、coverage_reviewed、
layout_reviewed；必须实际检查才设 true。保留 requirement→evidence→最终句子的映射，
审核报告引用当前版本，不能沿用修改前的“全部覆盖”。最后运行：

```sh
python3 scripts/workflow_guard.py review --job '<job>' --facts profile/facts.json
```

生成 `review.json` 记录材料和事实台账哈希，后续改字/换 PDF/修改事实使投前审核失效。
机器校验约束、对应关系和新旧版本；目的/架构/技能归属是否属实仍需 agent 查原始证据。
