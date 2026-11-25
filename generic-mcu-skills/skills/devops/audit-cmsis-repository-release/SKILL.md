---
name: audit-cmsis-repository-release
description: Audit an existing CMSIS solution repository before public release. Use to find stale generated artifacts, misplaced editor configuration, unsafe ignore rules, inconsistent generated metadata, and missing release validation without changing the repository.
---

# Audit CMSIS Repository Release

## Target & Persona

- **Role:** CMSIS Release Verification Engineer
- **Objective:** Produce an evidence-backed, read-only release audit that distinguishes required project inputs from reproducible outputs and identifies concrete publication blockers.

## Prerequisites & Context

- **Expected input:** A Git worktree containing one or more `*.csolution.yml` files, its documented generation and test procedures, and the intended release scope.
- **Dependencies:** Git and read access to the repository. CMSIS-Toolbox and project-specific generators are required only when the requested audit includes reproducibility checks. Use `configure-cmsis-gitignore` separately when the user authorizes ignore-policy changes.
- **Portability:** Applies to CMSIS solution repositories across MCU families, compilers, RTOSes, and host operating systems. Derive repository policy from tracked documentation and configuration rather than from one example layout.

## Execution Steps (Strict Workflow)

1. **Analysis:** Establish the Git worktree boundary and inventory every solution, its solution directory, committed project inputs, generated contracts, generated model or code layers, editor drop-ins, documented tools, and test commands. Record pre-existing changes and do not attribute them to the audit.
2. **Processing:** Classify suspicious files using repository evidence and the checks below. Compare related solutions and generated artifact families, but do not assume that all targets require identical files or settings.
3. **Validation:** Run read-only Git checks, syntax or structural validators, documented tests that do not mutate tracked inputs, and reproducibility checks explicitly requested by the user. Recheck the worktree afterward and report any side effects.
4. **Formatting:** Return `READY`, `READY WITH WARNINGS`, or `NOT READY`, followed by blockers, warnings, verified retained inputs, generated-artifact findings, validation evidence, and suggested separately authorized corrections.

### Repository policy and placement checks

- Inspect `.gitignore`, `.gitattributes`, local contribution guidance, and version-matched CMSIS Solution templates when available. Flag temporary personal directories, obsolete migration comments, blanket binary or YAML rules, and exceptions that no longer match repository policy.
- Use `git check-ignore --no-index -v` on representative required inputs and disposable outputs. Use `git ls-files --cached --ignored --exclude-standard -- .` to find tracked files hidden by current policy.
- Treat `*.csolution.yml`, project and layer inputs, pack locks, target configuration, intentionally committed prebuilt programs, and external MLOps contracts as potential repository inputs. Do not classify a file as disposable from its extension alone.
- Require each `.vscode.d` drop-in beside the `*.csolution.yml` it belongs to, as defined by the CMSIS Solution extension. A workspace-root `.vscode.d` is valid only for a solution at that root. Use `configure-cmsis-vscode-dropins` when relocation is authorized.
- Flag root or solution-local editor files only when repository documentation, extension templates, or duplication evidence establishes that they are obsolete, generated, misplaced, or host-specific.

### Generated-artifact consistency checks

- Group generated artifacts by their authoritative input and target. Use manifests, layer files, generated metadata, reports, and documented commands to determine the current set; do not infer it solely from matching filename stems.
- Compare recorded generator versions, selected targets, runtime versions, NPU and Vela settings, output paths, and report section contracts across artifacts that claim the same generation run.
- Flag dangling references, missing referenced files, obsolete alternate-model outputs, duplicate summaries, and artifacts not named by the current contract. Require evidence before recommending deletion.
- For MLOps-enabled solutions, use `prepare-cmsis-mlops-handoff` to validate `*.cbuild-mlops.yml`, referenced target configuration, and the returned model-layer directory.
- Check text files with `git diff --check` and repository line-ending policy. Treat generator-produced line endings as a policy issue to normalize or declare with `.gitattributes`, not as evidence that the semantic content is stale.

### Release validation

- Run the repository's documented focused tests first, then broader tests proportional to the changes. Keep environment changes process-local and report injected variables that can invalidate isolation.
- When regenerating for comparison is explicitly requested, use the repository-selected or exported CMSIS-Toolbox. If none is selected, use the CMSIS Solution extension's bundled Toolbox only after verifying the exact path and version. Never mix its executable with another installation's configuration directory.
- Compare regenerated output in staging or through version control. Preserve user changes and do not overwrite, delete, stage, commit, or push during this audit.
- Report commands that could not run because compilers, packs, Python packages, simulators, or credentials are unavailable. Do not install or persistently configure them.

## Guardrails & Constraints (Strict Rules)

- **No fabrication:** Do not invent repository policy, file ownership, generation provenance, tool versions, stale-artifact status, or test results.
- **Portability:** Do not universalize one repository's `.vscode`, `.vscode.d`, MLOps, Vela, Zephyr, compiler, or binary-artifact policy.
- **Critical blockers:** Return `NOT READY` when required inputs are ignored or missing, generated artifacts contradict their authoritative inputs, validation fails, secrets or personal data are present, documented release tests fail, or the worktree cannot be audited without overwriting user changes.
- **Scope:** This skill is read-only. Do not modify ignore rules, normalize files, regenerate in place, delete artifacts, stage, commit, push, publish, or open a pull request.
- **Tone and style:** Respond factually and directly. Omit conversational filler.

## Expected Output

Provide a release-audit report containing:

- status: `READY`, `READY WITH WARNINGS`, or `NOT READY`;
- audited worktree, branch, release scope, solutions, and pre-existing changes;
- blockers and warnings with exact paths and evidence;
- required inputs confirmed retained, ignored-path results, and editor-placement findings;
- generated-artifact families, provenance and version consistency, stale candidates, and missing or dangling references;
- commands run, results, skipped validation, and any audit side effects; and
- narrowly scoped corrective actions that require separate authorization.

## Validation Resources

- [CMSIS-Toolbox repository contents](https://open-cmsis-pack.github.io/cmsis-toolbox/build-overview/#repository-contents): source, project, generated, and reproducibility artifacts.
- [CMSIS-Toolbox output directory structure](https://open-cmsis-pack.github.io/cmsis-toolbox/build-overview/#output-directory-structure): default and configurable output locations.
- [CMSIS Solution `.vscode.d` drop-ins](https://mdk-packs.github.io/vscode-cmsis-solution-docs/debug.html#vscoded-drop-ins): authoritative solution-local placement and merge behavior.
- [Git check-ignore](https://git-scm.com/docs/git-check-ignore) and [Git attributes](https://git-scm.com/docs/gitattributes): observable ignore and line-ending policy checks.
- Repository contribution guidance, generation documentation, extension templates, and test instructions are authoritative for repository-specific policy.
