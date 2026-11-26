# Toolchain Migrator for Codex

`toolchain-migrator` is a Codex Skill for migrating Keil Studio and CMSIS solution projects from Arm Compiler 6 (`armclang`, `armasm`, and `armlink`) to LLVM Clang, LLD, and Picolibc or LLVM Libc.

It preserves the original agent's contract-first workflow: Phase 1 proposes numbered subtasks, Phase 2 starts only after explicit confirmation, and a successful build does not count as runtime-equivalence evidence by itself.

## Install

Codex discovers personal skills from `$CODEX_HOME/skills` or, when `CODEX_HOME` is unset, `~/.codex/skills`.

From this repository, copy the skill folder:

```sh
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R toolchain-migrator "${CODEX_HOME:-$HOME/.codex}/skills/"
```

For local skill development, symlink it instead so repository edits take effect immediately:

```sh
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -s "$(pwd)/toolchain-migrator" "${CODEX_HOME:-$HOME/.codex}/skills/toolchain-migrator"
```

Remove an existing destination first only if you are certain it is an older copy you intend to replace. Start a new Codex session after installation so the skill catalog refreshes.

## Use

Open Codex in the CMSIS project workspace and invoke the skill explicitly:

```text
Use $toolchain-migrator to migrate this project from Arm Compiler 6 to LLVM Clang.
```

The first response is discovery only. It returns numbered subtasks and waits. Continue in a later turn with an explicit selection:

```text
execute 1, 2
```

or:

```text
execute all
```

Generic replies such as `continue`, `go ahead`, or `do it` do not authorize migration edits.

Other useful prompts:

```text
Use $toolchain-migrator to run Phase 1 only on this CMSIS workspace.
Use $toolchain-migrator to diagnose a migration discovery visibility problem.
Use $toolchain-migrator and execute 1, 3 from the previously proposed subtasks.
```

## Prerequisites

The skill assumes the source and target toolchains, CMSIS packs, and the Arm CMSIS Solution VS Code extension are already installed and configured. It handles project migration, not toolchain installation.

Build validation uses the extension-bundled CMSIS-Toolbox `cbuild` executable. The skill derives the solution and active target from the workspace and does not invoke CMake or Ninja directly.

## Skill contents

- `toolchain-migrator/SKILL.md` — Codex entry point and execution gates
- `toolchain-migrator/agents/openai.yaml` — Codex UI metadata
- `toolchain-migrator/references/migration-workflow.md` — full migration and runtime-equivalence contract
- `toolchain-migrator/references/discovery-guard.md` — YAML scope and visibility fallback rules
- `toolchain-migrator/references/build-validation.md` — CMSIS solution, target, executable, and timeout rules

The original GitHub Copilot files remain under `.github/` as legacy source material; the installable Codex Skill is self-contained under `toolchain-migrator/`.
