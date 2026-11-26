---
name: toolchain-migrator
description: Migrate Keil Studio and CMSIS solution projects from Arm Compiler 6 (armclang, armasm, armlink) to LLVM Clang, LLD, and Picolibc or LLVM Libc. Use for Toolchain Migrator requests, AC6-to-Clang migration planning or execution, CMSIS project migration discovery, recovery from migration visibility problems, and validation of startup, linker, map, RTOS, middleware, TrustZone, or runtime-contract equivalence.
---

# Toolchain Migrator

Migrate CMSIS embedded projects conservatively. Treat a clean build as necessary but insufficient; require linker, startup, map, and symbol evidence before claiming runtime equivalence.

## Load the contract

Before inspecting a target project, read these bundled references to EOF in this order:

1. [Migration workflow and runtime contract](references/migration-workflow.md)
2. [Discovery guard](references/discovery-guard.md)
3. [CMSIS build validation](references/build-validation.md)

Also obey applicable `AGENTS.md` files and repository instructions in the target workspace. If they conflict, follow the stricter safety or evidence requirement and report the conflict.

## Select the C runtime

Use Picolibc by default unless the user selects another runtime. When the user requests LLVM Clang + LLVM libc, include the required `solution.misc` options in the project's `*.csolution.yml` as described in [LLVM libc configuration](references/migration-workflow.md#llvm-libc-configuration). Propose this configuration in Phase 1 and apply it in Phase 2 when its subtask is selected.

## Run the workflow

1. Establish the workspace root and perform read-only discovery. Inspect only the YAML allowlist in the contract plus relevant non-YAML source, startup, scatter, linker, map, and configuration files.
2. Run Phase 1 only. Emit the exact sentinel-wrapped `Proposed subtasks` and `Execution confirmation` payload. Do not edit migration files.
3. Stop and wait for an accepted explicit selection such as `execute 1, 2` or `execute all`. Treat `continue`, `go ahead`, `do it`, or the original migration request as insufficient authorization.
4. In a later turn, run the Phase 2 preflight and execute only selected subtasks. Create all required backups before the first edit to any existing file.
5. Validate through the resolved CMSIS-Toolbox `cbuild` executable only. Do not invoke CMake, Ninja, or generated build systems separately.
6. Perform the post-link map, ELF, symbol, runtime, and AC6-baseline audits.
7. Create or update `MIGRATION_REPORT.md`, including the exact completion evidence table.
8. Begin the final response with one permitted `Status:` line and follow the required summary structure.

## Preserve hard stops

- Never combine initial Phase 1 discovery and Phase 2 edits in one turn.
- Never optimize for build success over backup, startup-template, linker-template, provenance, or evidence-table rules.
- Stop with `LINKER_TEMPLATE_CONTRACT_VIOLATION` when linker authority or template constraints cannot be satisfied.
- Use `MIGRATION_INCOMPLETE` or `MIGRATION_BLOCKED` when runtime equivalence remains unproven.
- Never call a migration complete because compilation or linking succeeded.
- Preserve unrelated user changes and avoid destructive source rewrites.

## Example invocations

- `Use $toolchain-migrator to migrate this CMSIS project from Arm Compiler 6 to LLVM Clang.`
- `Use $toolchain-migrator to run Phase 1 on this Keil Studio workspace.`
- `Use $toolchain-migrator and execute 1, 3 from the previously proposed subtasks.`
- `Use $toolchain-migrator to diagnose why migration discovery cannot see the csolution.`
