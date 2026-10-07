# Bole

[中文](README.md)

Bole is a local job-application skill for Claude, Codex and other agents that can read files and
run Python. It discovers jobs, evaluates full descriptions, writes tailored documents, and can
submit applications with authorization. **Strict mode uses confirmed facts. Explicit Stretch
requests produce expanded drafts for local review only: no uploading or submission.**

## Full or Lite?

| | Bole | Bole Lite |
|---|---|---|
| Job advertisements | Configured discovery plus user links | User supplies **all links or full JDs** |
| Matching | Eligibility, responsibilities, scoring, recall review | Requirement-to-evidence mapping; no discovery/ranking |
| Default documents | CV, cover, other documents requested by the JD | CV; cover only when requested |
| Stretch | Explicit opt-in, documents only | Same boundaries |
| Submission | Optional OpenClaw, disabled by default | **User submits manually** |
| Central token budget per job | ~130,700 including submission | ~28,300 for a CV |

This is an agent-driven skill, not a standalone unattended program or an exhaustive search service.

## Getting started

Use Python ≥3.10, Git and an agent with access to this directory. Chrome/Chromium/Edge enables PDF
printing; without one, HTML remains available for manual printing. OpenClaw is optional for full
Bole submission; Lite does not use it.

```sh
git clone https://github.com/RAGG3D/Bole-auto_apply.git bole
cd bole
bash install.sh
```

Ask your agent:

```text
Read SKILL.md. Use Bole to set up my profile and match jobs from the last seven days.
Generate documents only.

Read bole-lite/SKILL.md. Here are all my job advertisement links: ...
Use my confirmed profile and red lines to generate a two-page English CV for each job.
I will submit them myself.

Use Bole Lite Stretch for these jobs. Add plausible implementation details for technical
requirements while preserving each experience's original skills, architecture and achievements.
Generate local files only; do not upload or submit.
```

Claude Code can use `/doctor` → `/setup` → `/scan`. Other agents read the same procedures in
`references/workflows/`. AGENTS.md and CLAUDE.md route to the shared skill; slash commands do not
maintain separate rules. Reuse an existing confirmed profile and resolve only missing/conflicting facts.

Build a self-contained directory for your chosen agent's skill location:

```sh
python3 scripts/package_skill.py --variant full --out /tmp/bole
python3 scripts/package_skill.py --variant lite --out /tmp/bole-lite
```

The destination must not exist. Packaging copies an allowlist of public resources, never profiles,
chat logs, credentials or generated applications. Automatic discovery depends on the host agent;
explicitly asking it to read SKILL.md remains available. [Agent portability](references/agents.md).

## What changed in v0.6

- **Recall and false matches:** expand role families using actual responsibilities. A consultant
  may perform automation work, but the title alone is not evidence. Report source coverage and
  fetch failures instead of claiming that undiscovered jobs do not exist.
- **Full-JD gate:** read the description and required PD/selection-criteria attachments before
  generating. Character count is only a warning. Closed, excluded, ineligible or incomplete roles
  stay in a central report without empty application folders.
- **Conservative title filtering:** citizenship, clearance and red-line title signals go to REVIEW.
  Corporate graduate programs are not automatically treated as citizenship-restricted government
  jobs. Manual links get full review; the employer blocklist still applies.
- **Current evidence and writing:** incorporate confirmed new projects and corrections; check required
  experiences. Preserve project purpose, architecture, ownership, dates and achievements. Finalize
  the CV before polishing its cover. Do not invent a weakness to satisfy a mandatory gap sentence.
- **Review and submission:** check CV/cover target-title consistency and hash reviewed artifacts.
  Changed files or facts invalidate review. All eligible tiers enter the authorized queue. Confirm
  the selected upload instead of reusing the platform's old CV. Verify timeouts before resuming.

The public audit summarizes recent real corrections without copying personal records or account
permissions. [Audit](references/workflow-audit.md) · [Matching](references/matching.md) ·
[Documents](references/materials.md) · [JSON contracts](references/contracts.md).

## Strict and Stretch

Strict is the default. Confirmed facts and explicit current corrections are evidence; JD requirements
and earlier model-generated resumes are not. Red-line scanning checks terms and limited rules:
**it cannot prove truthfulness**. The agent must still verify attribution, dates, skills and outcomes.

Stretch requires an explicit request for “Stretch” or invented/expanded hard-skill implementation
claims. Ordinary “write a resume” and the legacy `config.stretch` matching tolerance do not enable it.
Freeze a strict baseline, then append compatible implementation details to the most suitable existing
experience. Preserve original technologies, architecture, purpose, dates, team role and achievements.
Never turn a local tool into an enterprise platform or invent credentials, clients, tenure or metrics.

`tailoring.json` distinguishes verified and proposed additions and explains their placement. Unsupported
requirements remain gaps; no guaranteed perfect coverage. Drafts go under `Applications/Stretch/` with
`material_mode=stretch, submission_policy=never`. The submission script blocks run, continue and force.
To use the substance in a real application, confirm both the skill and its project attribution, then
build and review a new strict package. [Stretch procedure](references/stretch.md).

## Token budget per job

| Mode | Central estimate | Planning range |
|---|---:|---:|
| Full Bole: CV + cover + ATS + verification | 130,700 | 65,350–392,100 |
| Bole Stretch: files only | 80,500 | 40,250–241,500 |
| Lite: CV, manual submission | 28,300 | 14,150–84,900 |
| Lite Stretch: expanded CV, no submission | 48,100 | 24,050–144,300 |

**These are scenario estimates, not measured averages for v0.6.** They count input plus output,
including cached input and repeated context. They do not represent subscription charges. Assumptions:
existing profile, compact stage context, five ATS calls and one verification for full Bole. Long chat
history, revisions, extra documents and retries can exceed the range. Lite's central estimate is about
78% lower because discovery, default cover writing and automated submission are removed; output scope differs.

```sh
python3 scripts/token_budget.py --variant full --jobs 10
python3 scripts/token_budget.py --variant lite --jobs 10 --stretch
python3 scripts/token_budget.py --usage state/usage.jsonl --jobs 10 --submitted 8
```

[Stage arithmetic, historical limitations and observed-usage format](references/token-budget.md).
Observed usage requires per-call records from every participating agent and submission adapter;
cumulative session counters must not be summed or divided by an unrelated batch's job count.

## Files and submission

Runtime data stays in gitignored `profile/`, `Applications/` and `state/`. Each package includes its JD,
verdict, content JSON, PDF/HTML, tailoring notes and review hashes. Full packages use 80+/70–79/<70 tiers;
Lite and Stretch use separate directories. Pending full-JD, review and capacity-deferred items survive
into the next run rather than disappearing behind the seen ledger.

`/apply` requires `auto_submit.enabled=true`, applicable user authorization and the configured confirmation
strategy. ATS routing must also allow the site. Old packages must be upgraded to a v2 verdict and reviewed.
Only a confirmation page, authoritative application list or confirmation email proves submission; unknown
outcomes are never blindly retried. STATUS.md tracks each package's state.

Users handle login by default. Mail access and platform cleanup depend on explicit current authorization
and available tools; a previous individual's permissions never become distributed skill defaults. Human
verification and assessments are not bypassed. Lite and Stretch never invoke the submission agent.
[Submission protocol](references/workflows/apply.md).

Source scripts support LinkedIn, Workday, Greenhouse/Lever/Ashby boards, direct URLs and pasted JDs.
The current agent's public search tools can locate SEEK/Indeed links; paste the complete text when access
is blocked. Chinese direct URLs support common encodings; login search and bot-wall evasion are excluded.
BOSS-style recruiter communication remains manual. Local file storage does not imply remote model inference
is offline: the host agent/model's data policies still apply. Never commit application data or credentials.

## Independent mail plugin

[assHOLassin](plugins/assholassin/README.md) remains an independent IMAP cleanup plugin:
`/mail-setup` → `/mail-rules` → `/mail-clean`, with a dry run before confirmed changes.
Job-search tasks do not automatically delete mail, rejection messages or application folders.

## Validation and contribution

```sh
python3 scripts/ats_lint.py
python3 -m unittest discover tests
```

Tests are offline and use fictional profiles and a fake submission adapter. Contributions to ATS maps
and source-failure reports are welcome; exclude personal information from issues and PRs.
[Contributing](CONTRIBUTING.md) · [MIT License](LICENSE).

Verify documents, job status and salary against original sources. The software does not guarantee complete
information, successful submission or employment.
