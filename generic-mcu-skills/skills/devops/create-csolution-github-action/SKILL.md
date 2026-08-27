---
name: create-csolution-github-action
description: Create a GitHub Actions workflow that builds selected targets from the currently loaded CMSIS solution and optionally tests configured FVP targets. Use when a CMSIS solution workspace needs single-target or target-matrix CI.
---

# Create CMSIS Solution GitHub Action

## Target & Persona

- **Role:** DevOps Engineer
- **Objective:** Create one GitHub Actions workflow that builds the requested targets of the loaded CMSIS solution and optionally tests its FVP targets.

## Prerequisites & Context

- **Expected input:** A Git repository containing `.vscode/cmsis.json`, the loaded `*.csolution.yml`, and a reproducible CI tool configuration.
- **Dependencies:** CMSIS-Toolbox, GitHub Actions, and the project tools. The templates use `ARM-software/cmsis-actions/vcpkg@v1` with `vcpkg-configuration.json` and assume all required CMSIS packs are public.
- **Portability:** The workflow runs on `ubuntu-latest`. Device, compiler, RTOS, and debugger dependencies come only from the selected project. FVP tests require an FVP provided by the project tool environment.

## Execution Steps (Strict Workflow)

1. **Analysis:** Resolve the loaded solution and active target, inspect its target-types and debugger settings, and ask for target and FVP scope only when choices exist.
2. **Processing:** Adapt the single-target or matrix workflow asset and add only setup required by the project.
3. **Validation:** Parse the generated YAML, verify its paths and target names, and prove that non-FVP targets cannot start a simulator.
4. **Formatting:** Report the workflow, selected targets, FVP coverage, output checks, and validation result.

### Discover the project

1. Find the Git repository root and parse `.vscode/cmsis.json` as JSON.
2. Read `targetSet`. Its key identifies the loaded solution and `activeTargetType` identifies the active target. If several solutions are listed, ask the user which one to use.
3. Resolve the key to exactly one `*.csolution.yml` by explicit path or exact filename/stem. Stop if it is missing or ambiguous.
4. Parse the solution as structured YAML and verify that `activeTargetType` exists under `solution.target-types`.
5. Locate `vcpkg-configuration.json`. If the repository uses another CI tool setup, use it only when the user identifies it. Do not invent tool installation commands.

### Select targets

- With one target-type, use it without asking.
- With multiple target-types, ask whether to build only the active target or all targets. Use [workflow-single.yml](assets/workflow-single.yml) for the active target and [workflow-matrix.yml](assets/workflow-matrix.yml) for all targets.
- Use `cbuild <solution>.csolution.yml --active <target-type> --packs`. Do not replace `--active` with a context expression.

### Select FVP tests

Read `debugger:` directly from each target's selected `target-set` in the `*.csolution.yml`.

- A target is FVP-capable when `debugger.model` starts with `FVP`. Use that value as the FVP command and use `debugger.config-file` as its configuration.
- Ignore `debugger.args`. Invoke the model with `--simlimit 120`.
- When at least one selected target is FVP-capable, offer to add **test on FVP simulation model**. Add no simulator steps when the user declines.
- For a mixed matrix, set both `fvp` and `fvp_config` to empty strings for non-FVP targets. FVP steps must use `if: matrix.fvp != ''`.
- Load the built HEX output with `-a out/*/<target-type>/*/*.hex`. Do not inspect `*.cbuild-run.yml` or add separate image-discovery logic.

When FVP testing is selected, offer to run an existing local test to obtain representative output. Run it only after the user agrees.

- Show candidate success lines and require user confirmation before adding exact `grep -Fq` checks.
- If no output is run or confirmed, retain the template's `test -s fvp.log` stub. It checks only that the simulator produced output and must not be reported as a functional pass.

### Generate the workflow

Replace every `__NAME__` token in the selected asset.

- Write `.github/workflows/build-<solution-name>.yml` when no FVP runs.
- Write `.github/workflows/test-<solution-name>.yml` when at least one FVP runs.
- Derive `<solution-name>` from the `*.csolution.yml` stem, lowercased with unsupported filename characters replaced by `-`.
- Use the solution directory as `working-directory`.
- Insert solution paths, target names, FVP models, and FVP config files directly where they are used. Do not add `env:` aliases for these values.
- Always add `ARM-software/cmsis-actions/armlm@v1` without inputs. Note that its default license setup is for evaluation only.
- Let `cbuild --packs` install all required public packs. Do not add `cpackget init`, `cpackget update-index`, or local-pack registration.
- In a single-target build-only workflow, remove the FVP run and output-check steps and omit `fvp.log` from the uploaded paths.
- Preserve evidenced project-specific preprocessing. Do not copy Ethos-U Vela steps into unrelated projects.
- In a matrix, create one row per selected target with `target_type`, `fvp`, and `fvp_config`. Use a unique artifact name for every row.

### Validate the result

1. Parse the completed workflow with a YAML parser. Run `actionlint` when it is already installed; do not install it.
2. Verify the solution, active target, every matrix target, manifest path, and FVP config path against the project.
3. Confirm that non-FVP rows have `fvp: ""` and cannot execute FVP steps.
4. Search for unresolved `__NAME__` tokens and machine-specific absolute paths.
5. Run `git diff --check`. Do not commit, push, or trigger the workflow unless separately requested.

## Guardrails & Constraints (Strict Rules)

- **No fabrication:** Do not invent targets, tools, packs, FVP models, config files, image paths, or expected output.
- **Portability:** Derive all project-specific dependencies from the selected solution and repository.
- **Critical blockers:** Stop when the loaded solution is ambiguous, the active target is invalid, CI tool provisioning is undefined, a required pack is not public, an FVP configuration is incomplete, or the workflow fails YAML validation.
- **Scope:** Create or update only the requested workflow. Do not modify project metadata, sources, packs, or tool manifests.
- **Tone and style:** Respond factually and directly. Omit conversational filler.

## Expected Output

Create one workflow:

- `.github/workflows/build-<solution-name>.yml`; or
- `.github/workflows/test-<solution-name>.yml`.

Report the asset used, selected targets, FVP rows, whether output assertions are confirmed or remain a stub, and validation results.

## Validation Resources

- [CMSIS-Toolbox build tools](https://open-cmsis-pack.github.io/cmsis-toolbox/build-tools/)
- [CMSIS GitHub Actions](https://github.com/ARM-software/cmsis-actions)
- [Single-target asset](assets/workflow-single.yml)
- [Target-matrix asset](assets/workflow-matrix.yml)
