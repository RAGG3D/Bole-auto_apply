# v0.6 JSON 契约

保留 v0.5 facts/config 基础字段（workflows/setup.md），增加可选的事实来源和身份字段。
生成文件使用 v2 verdict；旧申请包先补全文/证据并按 v2 重审。脚本仍可读取旧包状态，但 run/continue 拒绝旧版未审核包。新增字段不能混入 facts 作为未经确认的历史事实。

## 档案

`facts.experiences[]` 除 id/role/org/start/end/location/facts/tech/suits_archetypes，可含：

- kind: project | employment；purpose、audience、architecture（字符串或列表）；
- ownership: 真实团队角色；achievements: 已确认成果列表；
- publication_state: local | private | invitation-only | preview | public；approved_links；
- must_include: 用户要求所有相关简历必须保留；provenance: 来源及确认时间。

`facts.confirmations[]` 可记录新增技能和纠正：id、user_statement、confirmed_at、scope、
experience_ids。experience_ids 空只证明个人技能，不能推定任何命名项目中的使用历史。
Stretch 新增内容保存在各岗 tailoring.json，不写回上述事实，除非用户确实确认。

config 新字段：excluded_employers（默认空）、adjacent_title_regex（由确认能力产生，
不是全局推荐所有 consultant）、match_tolerance（旧 stretch 的无歧义替代）、
materials（页数和布局偏好，可选）。

## Bole 完整版 verdict

以下是虚构、可改写的结构例子；每个 bool 必须来自实际检查，不能复制为默认 true：

```json
{
  "schema_version": 2,
  "jd_key": "Example :: Analyst :: req-001",
  "company": "Example", "title": "Analyst",
  "url": "https://example.test/jobs/req-001", "apply_url": "https://example.test/jobs/req-001",
  "source": "manual", "source_id": "req-001", "apply_type": "direct",
  "workflow_variant": "full", "material_mode": "strict", "submission_policy": "authorized_only",
  "jd_completeness": "full", "job_open": true, "eligible": true,
  "location_compatible": true, "domain_fit": true, "employer_excluded": false,
  "documents_complete": true,
  "seniority_band": "junior", "fit": 75, "redline_core_count": 0, "redline_flags": [],
  "decision": "generate", "rationale": "Evidence-based explanation",
  "required_documents": ["cv", "cover"],
  "requirements": [
    {"id": "r1", "kind": "must", "quote": "Analyse data using SQL", "source": "JD.txt",
     "coverage": "verified", "evidence_refs": ["exp1.facts[1]"], "material_refs": ["cv:exp1"]}
  ],
  "recommended_salary_note": "No reference range", "recommended_salary_form": {"amount": null, "currency": "AUD", "includes_super": null}
}
```

`documents_complete` 是 JD/附件/所需文件清单已完整取得，不表示输出 PDF 已经完成。
输出完成由 review 检查。material_files 可将 cv/cover/ksc 等键映射到岗位目录中的准确 PDF 文件名；附加文件必须指定，CV/cover 未指定时也必须只有一个候选文件。`requirements[].kind` 用 eligibility/must/preferred/soft/document。
coverage 只能 verified/transferable/gap/proposed；缺口不能有虚假 evidence_refs。
score_breakdown 保存七项得分和证据，jd_sources 保存每页/附件出处及完整性状态。
`submission_policy=never` 用于任何仅文件请求；strict 可用 authorized_only，Lite 用
manual_only，Stretch 必须 never。是否被允许上传同时受会话授权和全局配置约束。

Stretch 增加：

```json
{"material_mode":"stretch", "submission_policy":"never",
 "stretch_authorization":{"user_request":"用户本次原话", "scope":["req-001 的必备技术"]}}
```

## 轻量版 verdict

Lite 不需要 full 的评分字段或 discovery 配置。保留 title/company/url/material_mode/
workflow_variant=lite/submission_policy、required_documents、requirements 即可。
strict 用 manual_only；仅文件或 Stretch 用 never。Lite 不调用 generate/submit 闸门，
但仍必须完整 JD 和资格核对，运行 review。

## 内容、审核和模式

`_content/cv.json` / cover.json 基本 schema 见 materials.md，加 target_title。
CV 经历条目加 experience_id（facts 稳定 ID）。所有真实项目/工作经历都要标 ID；
教育/技能条目不混入相同 section。Stretch 基线 CV 和扩展 CV 共享相同元数据，只在
对应经历原 bullets 之后加新条目；不能在 profile/教育/技能区偷偷添加拟写历史。

`tailoring.json`：identity_reviewed、claims_reviewed、coverage_reviewed、layout_reviewed
四个检查结果；claim_map 记录 requirement_id/experience_id/material_text/evidence_refs/
status；additions 为 Stretch 新增记录（字段见 stretch.md）。严格模式 additions 可空。
审核元数据不放 `_content`，避免被误当简历内容扫描/上传。
`review.json` 由脚本产生，包含源材料、PDF/HTML、JD、verdict、基线及事实台账哈希。
机器不判断引文真假或自然语言语义；agent 必须完成证据复核，不能用布尔值代替检查。
