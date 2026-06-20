---
name: tool-tamarind-api
description: "Use for Protein Lab Tamarind Bio platform API work: API-key preflight, tool discovery, submit-job, submit-batch, job polling, result URL retrieval, result download, file upload/listing, and conservative handling of stop/delete operations before tool-specific Tamarind skills interpret outputs."
---

# Tool Tamarind API

Use this skill for Tamarind Bio platform mechanics. It owns authentication, REST calls, polling, downloads, and file operations. Tool-specific scientific inputs and interpretation belong in dedicated `tool-tamarind-*` skills.

## When To Use

- The user mentions Tamarind API, `app.tamarind.bio/api-docs`, API key, `/tools`, `/submit-job`, `/submit-batch`, `/jobs`, `/result`, uploads, job status, or result downloads.
- A Tamarind tool skill needs a shared platform call.
- You need to check whether a Tamarind tool and its settings are currently available.

Do not use this skill to interpret PepMLM candidates, AlphaFold outputs, wet-lab meaning, or Feishu updates.

## Fixed API Facts

- REST base URL: `https://app.tamarind.bio/api/`
- Auth header: `x-api-key: <TAMARIND_API_KEY>`
- API key source: environment variable `TAMARIND_API_KEY` only.
- Rate limit from Tamarind docs: 10 requests per second.
- Results are tool-dependent. Do not assume a fixed result schema after download.

Tamarind docs expose an OpenAPI file, but its server examples can differ from the app docs. Use the app API docs and examples as the operational source of truth for this plugin.

## Script

Use the bundled helper for API calls:

```bash
python3 "${PROTEIN_LAB_PLUGIN_ROOT}/skills/tool-tamarind-api/scripts/tamarind_api.py" tools --tool pepmlm
python3 "${PROTEIN_LAB_PLUGIN_ROOT}/skills/tool-tamarind-api/scripts/tamarind_api.py" submit-job --payload <payload.json> --confirm
python3 "${PROTEIN_LAB_PLUGIN_ROOT}/skills/tool-tamarind-api/scripts/tamarind_api.py" jobs --job-name <jobName>
python3 "${PROTEIN_LAB_PLUGIN_ROOT}/skills/tool-tamarind-api/scripts/tamarind_api.py" download-result --job-name <jobName> --out <raw.zip>
```

The script prints JSON or streams the requested result file. It never reads API keys from files and never writes secrets. `submit-job` and `submit-batch` require `--confirm`; without it they print a dry-run summary and exit non-zero. Downloads and uploads stream to/from disk; transient `429/502/503/504` responses are retried with exponential backoff.

## Core Workflow

1. Confirm `TAMARIND_API_KEY` exists in the current environment.
2. Use `tools --tool <tool-name>` for read-only schema discovery before new tool work.
3. Submit using a JSON payload file rather than shell-escaped inline JSON.
4. Poll `jobs --job-name <jobName>` until `JobStatus` is `Complete`.
5. For batch jobs, poll the parent job and prefer `batchStatus`; subjobs may finish before aggregated output is downloadable.
6. Download raw results into the active `local-rounds` folder.
7. Hand raw outputs to the tool-specific skill for audit and interpretation.

## Request Shapes

Single job:

```json
{
  "jobName": "myJobName",
  "type": "pepmlm",
  "settings": {
    "targetSequence": "MQRGK...",
    "peptideLength": 15,
    "numDesigns": "8"
  }
}
```

Batch job:

```json
{
  "batchName": "myBatchName",
  "type": "pepmlm",
  "settings": [
    {
      "targetSequence": "MQRGK...",
      "peptideLength": 15,
      "numDesigns": "8"
    }
  ],
  "jobNames": ["job1"]
}
```

## Guardrails

- Do not paste, print, store, or commit API keys.
- Do not submit real jobs during validation unless the user explicitly requests a submission.
- Do not delete files or jobs without a fresh user instruction and a `--confirm` flag.
- If `/result` returns a presigned URL, treat it as short-lived and download immediately into the local round.
- If a 403 appears, treat it as budget/quota/permission state; do not retry aggressively.
- If a 429 appears, back off and preserve the current job metadata in `status_log.md`.
- If API docs disagree, re-open the relevant app API page before using a destructive endpoint.

## Handoff

- Use `tool-tamarind-pepmlm` for PepMLM payloads, candidate extraction, and interpretation.
- Use `local-rounds` to store payloads, job metadata, raw zips, parsed tables, and reports.
- Use `reporting` only after the tool-specific interpretation exists.
