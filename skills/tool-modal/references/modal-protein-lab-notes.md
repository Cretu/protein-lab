# Modal Notes For Protein Lab

Source set reviewed on 2026-06-17: `https://modal.com/docs`, `https://modal.com/llms.txt`, `https://modal.com/llms-full.txt`, pricing, core Guide pages, and computational-biology examples.

## Platform Shape

- Modal is a Python-native serverless cloud for CPU/GPU code, batch jobs, web functions, sandboxes, notebooks, and durable storage.
- The core deployable unit is a `modal.App`. Work executes through `modal.Function` or `modal.Cls`.
- Functions scale independently and default to scale-to-zero when idle, so a deployed app does not imply idle compute cost.
- Ephemeral apps are created by `modal run`; persistent apps are created by `modal deploy`.
- Modal code always has a local initialization side and a remote execution side. Avoid top-level reads of local-only files and put remote-only imports inside functions or `image.imports()`.

## Account And Setup

- A user account is required. Typical setup is `python3 -m pip install -U modal` followed by `python3 -m modal setup`.
- `modal setup` creates local authentication; do not run it without user intent.
- Shared workspaces can use service users for CI/CD through `MODAL_TOKEN_ID` and `MODAL_TOKEN_SECRET`; store those only in a secret manager.
- Environments isolate apps, volumes, secrets, dicts, and queues. The default environment is `main`; use `--env` or `MODAL_ENVIRONMENT` for non-main runs.

## Compute And Scaling

- GPU choices in docs include `T4`, `L4`, `A10`, `L40S`, `A100`, `A100-40GB`, `A100-80GB`, `RTX-PRO-6000`, `H100`/`H100!`, `H200`, and `B200`/`B200+`.
- Modal recommends L40S as a strong starting point for many inference workloads because it balances cost/performance and has 48 GB GPU RAM.
- GPU count can be requested as `gpu="H100:8"` etc.; more than two GPUs may increase wait time.
- `gpu="H100"` may auto-upgrade to H200 at the same H100 cost; use `H100!` when benchmarking or strict hardware assumptions matter.
- `gpu="A100"` requests 40 GB and may auto-upgrade to 80 GB at the same cost; request `A100-80GB` when memory is required.
- Use `gpu=[...]` fallbacks only when all listed GPU types are compatible with the code and CUDA stack.
- Autoscaling controls: `max_containers`, `min_containers`, `buffer_containers`, `scaledown_window`. Warm pools lower latency but increase cost.
- `.map()` is for bounded parallel maps; `.spawn()` is for async jobs. `.spawn()` can support much larger pending input counts than normal pending inputs.

## Images, Dependencies, And CUDA

- Define dependencies in `modal.Image`, not only local virtualenv files.
- Prefer `modal.Image.debian_slim(python_version="...").uv_pip_install(...)`; use `pip_install`, `micromamba_install`, Dockerfile, or registry images when appropriate.
- Pin dependency versions and upstream model/library revisions for reproducibility.
- Modal GPU workers already include NVIDIA driver/user-level components; install higher-level CUDA libraries through packages such as Torch wheels or supported CUDA images.
- For complex CUDA packages such as flash-attn, use a supported CUDA base image or existing image pattern.

## Data And Storage

- Pass small serializable input data as function arguments.
- Use `modal.Volume` for model weights, checkpoints, large input/output artifacts, and repeated inference runs.
- Volumes are optimized for write-once/read-many ML workloads and need explicit `commit()` after writes to make changes visible outside the current container.
- Use `reload()` when another container or local client needs to see fresh Volume contents.
- For huge datasets, download and transform in `/tmp`, then copy final artifacts to a Volume and commit.
- Prefer sharded/archive/table formats for many tiny files: tar shards, WebDataset, Parquet, or similar.
- Cloud bucket mounts support AWS S3, Cloudflare R2, and Google Cloud Storage. They are useful when data already lives in cloud object storage.

## Reliability, Timeouts, And Cost

- Default function timeout is 300 seconds. Set explicit timeouts between 1 second and 24 hours.
- A separate `startup_timeout` can cover model loading/import-heavy startup.
- Functions can use `retries=...` or `modal.Retries`; each map input retries independently.
- Functions are preemptible by default. Long runs should be idempotent and checkpointed. GPU Functions do not support `nonpreemptible=True`.
- Web Function HTTP request timeout is 150 seconds. Long APIs should spawn a background Function and return a call id for polling.
- Billing is monthly and serverless. Current pricing must be checked live, but docs emphasize pay for used/requested compute, no reservations, and no minimum usage-time increments.
- CPU and memory billing uses whichever is higher: requested or actual usage. Disk requests increase memory billing at a 20:1 ratio.
- Region selection adds multipliers: broad regions 1.5x, narrow regions 1.75x. Avoid setting region for exploratory runs unless latency/data locality requires it.

## Security And Data Boundaries

- Use `modal.Secret.from_name(...)` for keys; never print or store secrets in outputs.
- Function inputs and outputs are retained up to 7 days. App/container logs are plan-dependent. Volumes and Images persist until deleted.
- Modal states it does not use source code, function inputs/outputs, or stored data; logs/metadata may be stored and accessed with user permission for troubleshooting.
- All user data is encrypted in transit and at rest according to Modal's security docs.
- HIPAA-compatible workloads require Enterprise/BAA. Volumes v1, Images, Memory Snapshots, and user code are out of BAA scope; Volumes v2 are HIPAA compliant.

## Computational Biology Examples

- Chai-1 example: install `chai_lab`, cache model weights in a Volume, run H100 inference from FASTA, return CIF and score files.
- ESMFold2 example: pin Biohub `esm` revision, cache weights in a Volume, use `@app.cls` with `@modal.enter()` to load the model once, return mmCIF plus pLDDT/pTM/ipTM.
- Boltz-2 example: install `boltz`, cache weights/CCD in a Volume, pass YAML input, run `boltz predict --use_msa_server`, return a tarball containing structure and affinity outputs.
- ESMFold2 binder-design example: use micromamba plus pinned Biohub esm, cache roughly 50 GB of weights, run H100 `@app.cls`, fan out design jobs with `.spawn()`, gather and select top candidates.

## Protein Lab Operating Pattern

Use Modal for workflows that need custom execution and are too expensive or awkward locally:

1. Create a local round first.
2. Put source FASTA/YAML/JSON and planned Modal app name in `status_log.md`.
3. Run a tiny Modal smoke test before real GPU work.
4. Cache model weights in a named Volume.
5. Run one representative input, inspect outputs, and record spend.
6. Scale up only after the pilot is reproducible and cost is visible.
7. Download raw outputs locally and route interpretation to the relevant Protein Lab skill.

Avoid using Modal as the first choice for AF Server-only validation or as a replacement for no-code candidate generation platforms.
