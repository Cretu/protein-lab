---
name: protein-lab-tool-execution
description: "Use for operating online or local dry-lab tools for Protein Lab after experiment design is prepared: AlphaFold Server, future structure prediction tools, sequence analysis, omics tools, target biology services, browser-based tools, downloads, job status tracking, and tool-specific execution evidence."
---

# Protein Lab Tool Execution

Use this skill for the tool-running layer. It should not design the scientific panel or write the final interpretation by itself.

## General Execution Contract

For every tool run, record:

- tool name and URL or local command
- exact input files and parameters
- submission time and job id or URL
- account/login/permission state
- queue or run status
- downloaded raw outputs and local paths
- failure reason and retry state

Update `status_log.md` in the active round after each meaningful state change.

## Browser Tool Guardrails

- Prefer stable UI element targeting over coordinate-only clicks.
- Keep browser actions small and incremental; avoid heavy full-page reads when the site is slow.
- Stop for user input on login, captcha, payment, quota exhaustion, or irreversible submission uncertainty.
- Distinguish draft/import success from formal job submission.

## AlphaFold Server Current Support

AlphaFold Server is currently the first supported online tool family.

For AF Server JSON imports:

1. Upload the JSON.
2. Treat `Submit N jobs as drafts` as draft creation only.
3. Open each draft, continue to preview, verify job name, seed, chain count, and chain lengths.
4. Click formal submit only after verification.
5. Record Remaining jobs changes and job status.
6. Download raw zip results into the current round.

AF Server does not currently provide a stable public batch-confirm API in this workflow. Do not rely on hidden browser endpoints unless the user explicitly requests risky exploration.

## Handoff

- Send generated inputs back to `protein-lab-experiment-design` if they need correction.
- Send raw AF Server zips to `protein-lab-afserver-interpretation`.
- Send completed outputs to `protein-lab-reporting-postmortem` for Chinese reporting and Feishu-ready summaries.
