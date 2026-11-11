---
name: configure-cmsis-gitignore
description: Create or merge a CMSIS-specific .gitignore for a new or existing csolution project using verified build-output paths. Use during solution creation, conversion, target or layer integration, or output-path changes, and when preparing a CMSIS repository for version control without hiding sources, RTE configuration, or pack locks.
---

# Configure CMSIS Gitignore

## Target & Persona

- **Role:** CMSIS Project Integrator
- **Objective:** Produce one validated, project-scoped .gitignore that excludes disposable build output while preserving repository inputs and existing ignore policy.

## Prerequisites & Context

- **Expected input:** The selected .csolution.yml, its solution directory, existing ignore files, and project configuration or generated build metadata identifying output paths.
- **Dependencies:** Git, the bundled template, and CMSIS-Toolbox documentation matching the project's version. No compiler, hardware, or build invocation is required.
- **Portability:** CMSIS csolution projects across MCU families and compilers, including west-integrated Zephyr projects. Derive paths from the project; use forward slashes in Git patterns on every operating system.

Authoring skills can invoke this skill once the selected solution and output paths are known. Pass configuration or available build metadata; no build is required solely for this handoff. Report ignore validation separately from the caller's project validation.

## Execution Steps (Strict Workflow)

1. **Analysis:** Identify the selected solution, Git worktree boundary, and applicable ignore files. Inspect output-dirs and referenced project configuration using a YAML parser when available; use existing build metadata to resolve actual paths. For unbuilt projects, use version-matched documented defaults only when no overrides apply. Distinguish disposable outputs from required inputs, including prebuilt images.
2. **Processing:** Create or merge .gitignore beside the selected .csolution.yml using [assets/cmsis.gitignore](assets/cmsis.gitignore) and the policy below. Adapt verified rules, uncomment only applicable optional patterns in the destination, and omit unsupported rules. Preserve existing content, encoding, line endings, comments, and exceptions. Avoid equivalent rules and duplicate sections; make no change when existing rules suffice.
3. **Validation:** Run the Git checks below. Narrow new rules that hide required inputs; ask before correcting conflicting user-authored rules. Repeat rule selection and merging as a dry run: it must propose no further changes.
4. **Formatting:** Report the changed path or no-op, rule-selection evidence, validation results, tracked-artifact warnings, and blockers.

### Rule Selection and Merge Policy

- Scope rules to verified paths within the selected solution, including custom output/intermediate directories. Do not affect sibling solutions or the surrounding west workspace. Narrow exclusions when a directory also contains required inputs; escape literal Git pattern metacharacters in paths.
- Retain sources, project/layer files, cdefault.yml, pack locks (`*.cbuild-pack.yml`), tool manifests, board/generator inputs, prebuilt images/libraries, and reference datasets. For Zephyr, retain application sources, CMake/Kconfig configuration, devicetree overlays, board definitions, and west manifests. Avoid blanket YAML, binary, RTE, `.cmsis/`, or `.vscode/` exclusions.
- Retain RTE files, context selections, and shared IDE/debug settings by default. The template's optional generated context headers, local selections, and editor files may be excluded only when verified disposable and permitted by existing repository policy or user choice. Keep component configuration, `.base@` files, linker templates, and memory-region headers. When uncertain, leave optional rules disabled rather than blocking minimal output.
- Keep `.update@` files visible for review. If existing policy explicitly excludes them, report pending merges and require a separate pre-commit check; ignoring them does not resolve the updates.
- Protect `.vscode.d/` drop-ins. If an existing `*.d` rule hides them, propose `!.vscode.d/` after it and obtain authorization before correcting that policy. Preserve exception precedence; Git cannot re-include descendants of an excluded parent, so narrow conflicting exclusions and test descendant paths.

### Git Validation

Run from the solution directory, replacing these examples with actual paths
(or representative future outputs for an unbuilt project). Quote paths with spaces.

```text
git check-ignore --no-index -q -- out/App/Board/Debug/App.elf
git check-ignore --no-index -q -- App.csolution.yml
git check-ignore --no-index -q -- App.cbuild-pack.yml
git check-ignore --no-index -q -- App/RTE/Device/Board/regions.h
```

- Check paths individually: ignored outputs must exit 0; retained inputs must exit 1; other statuses are errors. `--no-index` also tests tracked files.
- Check all known required inputs, existing exceptions, `.vscode.d/` descendants, and enabled optional rules against disposable and retained examples. Verify that nested source directories named `out` and sibling solutions remain unaffected.
- Diagnose mismatches with `git check-ignore --no-index -v -- <path>`. Report global/local exclude conflicts without editing those files.
- Run `git ls-files --cached --ignored --exclude-standard -- .` to identify already-tracked artifacts; report them without changing the index.
- Outside a Git worktree, test copied rules and representative paths in an isolated temporary Git repository with global excludes disabled. Initialize only that fixture; disclose that real-worktree precedence and tracked-file checks were unavailable.

## Guardrails & Constraints (Strict Rules)

- **No fabrication:** Do not invent output paths, generated-file classifications, tool versions, or validation results. Use project evidence and authoritative documentation, or report what is missing.
- **Portability:** Do not introduce MCU-family, architecture, compiler, debugger, or RTOS-specific rules unless the input project requires them. Identify each such dependency in the report.
- **Critical blockers:** Stop when the solution is ambiguous, output paths cannot be verified, required inputs overlap a proposed excluded directory, existing ignore intent cannot be preserved, or Git validation is unavailable or fails. Narrow a candidate rule to resolve an overlap only when evidence supports it.
- **Scope:** Change only the selected solution's .gitignore. Do not initialize the user's repository, stage, commit, delete, untrack files, build, install tools, or change other project/Git policy files.
- **Tone and style:** Respond factually and directly. Omit conversational filler.

## Expected Output

A new or minimally updated `<solution-directory>/.gitignore`, or an explicit no-op.
Report selected rules and evidence, retained inputs, Git check results, repeat-run
stability, tracked-artifact warnings, and unresolved blockers. Do not claim
end-to-end project validation from a template-only check.

## Validation Resources

- [Candidate ignore template](assets/cmsis.gitignore): pattern explanations and optional activation guidance.
- [CMSIS-Toolbox repository contents](https://open-cmsis-pack.github.io/cmsis-toolbox/build-overview/#repository-contents): source, project, RTE, and pack-lock retention requirements.
- [CMSIS-Toolbox output directory structure](https://open-cmsis-pack.github.io/cmsis-toolbox/build-overview/#output-directory-structure): generated output locations and references to directory overrides.
- [Git ignore pattern rules](https://git-scm.com/docs/gitignore): anchoring, precedence, escaping, and excluded-parent limitations.
- [Git check-ignore](https://git-scm.com/docs/git-check-ignore): repeatable positive/negative checks, verbose diagnostics, and exit-status interpretation.
