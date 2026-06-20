---
name: tool-modal
description: "Use for Protein Lab Modal compute work: evaluating whether Modal fits a dry-lab task, setting up or verifying the Modal CLI, running Modal Functions/Apps/Notebooks for custom CPU/GPU workflows, adapting Modal bio examples such as Chai-1, ESMFold2, Boltz-2, or binder-design sweeps, managing Volumes/Secrets/cost limits, and handing results back to local-rounds, AF Server, Tamarind, experiment, or reporting skills."
---

# Tool Modal

Use this skill when Protein Lab needs Modal as a custom cloud execution layer. Modal is best for Python-native CPU/GPU work, batch fan-out, model inference, result APIs, and reproducible containers. It is not a no-code protein design platform.

For detailed reference, read `references/modal-protein-lab-notes.md` when you need current Modal concepts, cost guardrails, or bio example patterns.

## Default Role In Protein Lab

- Treat Modal as the execution layer for custom GPU/CPU workflows: structure predictors, candidate scoring, embeddings, batch transforms, custom notebooks, and lightweight APIs.
- Keep AF Server as the preferred free AlphaFold validation path when the task only needs AF复核.
- Keep Tamarind/PepMLM in `tool-tamarind-*` when the task is specifically Tamarind platform or PepMLM candidate generation.
- Use `local-rounds` for local project folders, inputs, payloads, raw outputs, parsed tables, and `status_log.md`.
- Use `experiment` for wet-lab panel decisions and `reporting` for final Chinese summaries.

## Preflight

Before running paid or authenticated Modal work:

1. Verify user intent: setup, dry-run, official example, custom pilot, deployed app, or report-only research.
2. Check local client state:

```bash
command -v modal
python3 -m pip show modal
modal --version
modal token current
```

3. If the client is missing, install only after user intent is clear:

```bash
python3 -m pip install -U modal
python3 -m modal setup
```

4. Verify workspace/account state in the Dashboard or CLI before nontrivial runs: plan, included credits, usage, workspace budget, environment, and GPU concurrency.
5. Do not create or transmit Modal tokens, payment details, service-user secrets, or private files unless the user explicitly authorized that action.

## First Pilot Pattern

Prefer a small, bounded pilot before moving any real Protein Lab workflow:

1. Create or choose a local round.
2. Set a budget cap in Modal Dashboard before GPU work when possible.
3. Run a tiny CPU hello-world or a single official bio example.
4. Confirm logs, Dashboard metrics, output files, and actual spend.
5. Only then scale to batch inputs or higher-end GPUs.

Good first pilots:

- Chai-1 single FASTA structure prediction.
- ESMFold2 single-chain or small complex prediction.
- Boltz-2 sample YAML prediction.
- A tiny custom `@app.function(gpu="T4" | "L4" | "L40S")` smoke test that returns `torch.cuda.is_available()`.

## Modal Coding Defaults

- Use `import modal` and qualified names such as `modal.App`, `modal.Image`, `modal.Volume`, and `modal.Secret`.
- Put dependencies in `modal.Image`, pin versions tightly, and prefer `uv_pip_install` unless docs or package constraints require another installer.
- Put remote-only imports inside the function body or inside `with image.imports():` when local Python lacks those packages.
- Use `modal.App(name="protein-lab-...")` with kebab-case names.
- Use `@app.local_entrypoint()` to read local FASTA/YAML/JSON files, then pass serializable contents into remote functions.
- Use `modal.Volume` for model weights, large datasets, and durable results; do not rely on remote container scratch disk after a function exits.
- Call `volume.commit()` after writing outputs that must persist.
- Use `modal.Secret.from_name(...)` for API keys and credentials; do not print secrets or store them in logs.
- For long or flaky tasks, set explicit `timeout`, `retries`, and checkpointing. Default function timeout is 5 minutes; Modal supports up to 24 hours per execution attempt.
- Design GPU functions to tolerate preemption. GPU functions cannot use `nonpreemptible=True`.

## Batch And Cost Guardrails

- Start with low concurrency and cheap GPUs; prefer `L40S` for many inference workloads unless memory or package support forces `A100`/`H100`.
- Use GPU fallbacks only when the code is compatible with every listed GPU.
- Avoid `min_containers`, long `scaledown_window`, and large warm pools for exploratory Protein Lab work unless latency matters more than spend.
- Use `.map()` for bounded parallel batches, `.spawn()` for async jobs, and polling for long web/API flows.
- Keep Web Function requests short. For long jobs, make the endpoint spawn a Function and return a call id for polling.
- Record app name, environment, GPU type, timeout, input count, output path, and observed spend in `status_log.md`.

## Bio Workflow Handoff

When adapting official Modal bio examples:

1. Keep upstream example source and commit/revision pins in the local round notes.
2. Cache model weights in a named Volume, usually one Volume per model family.
3. Pass user inputs as file content from the local entrypoint.
4. Write structures, scores, tarballs, and summaries to local-round outputs or a Modal Volume.
5. Download or parse outputs locally before scientific interpretation.
6. For AF-style validation, route final candidates to `tool-af-server` unless the user explicitly wants Modal-based prediction.

## Stop Rules

- Stop before any action that adds payment details, raises budget, creates a service user, exposes a public endpoint for private data, deletes Modal resources, or runs an unexpectedly expensive GPU batch.
- Stop if estimated cost is unclear for a large run; do a pilot and inspect real spend first.
- Stop if a docs/API mismatch appears; re-open official Modal docs before proceeding.
- Stop if raw outputs are missing, expired, or only visible in logs. Do not infer scientific conclusions from execution success alone.
