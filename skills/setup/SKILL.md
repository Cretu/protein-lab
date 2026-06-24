---
name: setup
description: "Use for Protein Lab first-run onboarding, new-device setup, project workspace selection, environment doctor checks, local configuration, optional Feishu/wiki/tool preflight, and troubleshooting when the plugin or project environment is not ready."
---

# Setup

Use this skill when Protein Lab must become usable on a new machine, a new Codex project, or a new team workspace. It owns environment diagnosis and local configuration. It does not run scientific jobs or write conclusions.

## When To Use

- The user installs the plugin on a new device or in a new team.
- The user asks to initialize Protein Lab in the current project directory.
- A task fails because the local workspace, plugin root, Feishu/Lark, Tamarind, Modal, browser, or Codex skill environment is not ready.
- The user wants to change the local workspace, wiki, team name, or collaboration links.

## Configuration Model

Global configuration lives at `~/.config/protein-lab/config.json` by default. It acts as a local registry of known projects and the active/default project.

Each configured project also gets its own project-local config:

```text
<workspace-root>/.protein-lab/project.json
```

Project-local config is the isolation boundary for workspace root, wiki root, Feishu URLs, team/project labels, and enabled capability flags. This keeps multiple local Protein Lab projects from leaking context into one another.

Never store API keys, tokens, cookies, passwords, payment details, or private credentials in the config file, doctor reports, wiki index, or status logs.

## Multi-Project Isolation

- Prefer the nearest `.protein-lab/project.json` when the current directory is inside a configured project.
- Use the global config only as a registry/fallback when no project-local config is found.
- Keep wiki roots, Feishu task lists, document folders, and round outputs project-specific unless the user explicitly wants a shared team workspace.
- Do not reuse one project's collaboration links or wiki as defaults for another project.

## Workspace Choice

When configuring a new project, guide the user toward one of:

- current Codex project/current directory as the Protein Lab workspace
- an existing directory selected by the user
- a new directory created for this team/project

Prefer current directory when the user opened Codex inside a project they want to initialize.

## Doctor

Run a read-only environment check:

```bash
python3 "${PROTEIN_LAB_PLUGIN_ROOT}/skills/setup/scripts/protein_lab_setup.py" doctor --out-dir <diagnostics-dir>
```

Doctor checks Python, config readability, workspace writability, plugin source/cache presence, optional command availability (`lark-cli`, `modal`, browser), and environment-only secrets such as `TAMARIND_API_KEY` without printing their values.

Outputs:

- `protein_lab_doctor.json`
- `protein_lab_doctor.md`

Classify results as ready, needs_config, optional, or blocked. Give the user a short, human-friendly next step rather than raw command noise.

## Configure

Use configure only after the workspace choice is clear:

```bash
python3 "${PROTEIN_LAB_PLUGIN_ROOT}/skills/setup/scripts/protein_lab_setup.py" configure \
  --workspace-root <project-or-team-root> \
  --plugin-root "${PROTEIN_LAB_PLUGIN_ROOT}" \
  --team-name "<team-or-project-name>"
```

Optional:

```bash
--wiki-root <local-markdown-wiki-root>
--wiki-allow-write
--feishu-task-list-url <url>
--feishu-docs-folder-url <url>
--feishu-tenant-domain <tenant.example.cn>
--enable-feishu
--enable-tamarind
--enable-modal
```

Configure writes both the global registry and `<workspace-root>/.protein-lab/project.json`. After configuring, run doctor from inside the project and then a local-only smoke test with `local-rounds`.

## Handoff

- Use `local-rounds` to initialize the first round in the configured workspace.
- Use `knowledge-base` to initialize or index a local/team wiki.
- Use `collab-feishu` after Feishu URLs and authorization are configured.
- Use `tool-creator` when a third-party tool needs to be added.
- Use `reporting` for a concise setup/diagnostic summary.
