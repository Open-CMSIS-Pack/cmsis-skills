---
name: configure-cmsis-vscode-dropins
description: Create, validate, or relocate solution-specific VS Code launch and task overrides into .vscode.d beside their CMSIS solution files. Use when a workspace has custom debug configuration, multiple *.csolution.yml files, or a misplaced shared .vscode.d directory.
---

# Configure CMSIS VS Code Drop-ins

## Target & Persona

- **Role:** CMSIS Project Integrator
- **Objective:** Leave each CMSIS solution's version-controlled VS Code overrides in a valid solution-local `.vscode.d` directory without treating generated workspace `.vscode` files as their source.

## Prerequisites & Context

- **Expected input:** The workspace, every applicable `*.csolution.yml`, existing `.vscode.d`, `.vscode/launch.json`, and `.vscode/tasks.json` files, and the intended solution ownership of each custom override.
- **Dependencies:** A JSON parser and the CMSIS Solution extension documentation. The extension is optional for static validation and required only to verify the final generated workspace merge.
- **Portability:** Applies to CMSIS Solution workspaces on every host operating system. It does not depend on an MCU family, compiler, debugger, or RTOS.

The CMSIS Solution extension consumes drop-ins only from `<solution-dir>/.vscode.d`, where `<solution-dir>` is the directory containing the related `*.csolution.yml`. A workspace-root `.vscode.d` applies only when the related solution is also at the workspace root.

## Execution Steps (Strict Workflow)

1. **Analysis:** Inventory every `*.csolution.yml`, `.vscode.d/launch.json`, `.vscode.d/tasks.json`, workspace `.vscode/launch.json`, and workspace `.vscode/tasks.json`. Determine which solution owns each custom configuration, task, and input from names, referenced paths, targets, existing generated entries, and project documentation. Ask for a mapping when ownership is ambiguous.
2. **Processing:** For each confirmed owner, create or merge the applicable drop-in under the directory containing that solution. When one override intentionally applies to several solutions, place a copy beside each applicable `*.csolution.yml`; do not assume every solution needs it. Preserve unrelated workspace entries and existing solution-local overrides.
3. **Validation:** Parse every changed drop-in, enforce the supported structures and merge identifiers below, verify that each is co-located with its owning solution, and confirm that no source content remains only in a non-consumed location. When the extension is available, update debug tasks and launch configurations and inspect the generated workspace merge.
4. **Formatting:** Report each owning solution, created or changed drop-in, moved or duplicated entry, static and extension validation, remaining ambiguous content, and any obsolete source location that is now safe to remove.

### Placement and content rules

- Store launch overrides at `<solution-dir>/.vscode.d/launch.json`. The extension consumes its `configurations` array and matches entries by `name`.
- Store task overrides at `<solution-dir>/.vscode.d/tasks.json`. The extension consumes its `tasks` and `inputs` arrays, matching tasks by `label` and inputs by `id`.
- Drop-ins participate in the final merge; they do not replace the whole workspace `.vscode/launch.json` or `.vscode/tasks.json` files.
- Treat workspace `.vscode/launch.json` and `.vscode/tasks.json` as generated merge destinations when their CMSIS entries are extension-managed. Do not move generated entries into drop-ins unless they are intentional custom overrides.
- Do not keep one workspace-root `.vscode.d` as a shared source for solutions located in child directories. Map its custom content to the owning solutions first.
- Before removing an old drop-in, verify that every intended custom configuration, task, and input exists in all applicable solution-local destinations. Preserve the old directory when ownership or coverage remains ambiguous.
- Ensure ignore policy retains all intended solution-local `.vscode.d` files. Use `configure-cmsis-gitignore` separately when ignore rules need changes.

### Validation checks

- Require valid JSON objects. When present, require `configurations`, `tasks`, and `inputs` to be arrays.
- Require a non-empty string `name` for every consumed launch configuration, `label` for every consumed task, and `id` for every consumed input. Report duplicate merge identifiers within one file.
- Resolve file and command paths according to VS Code variable semantics and the owning solution context; do not rewrite paths without evidence.
- With the extension available, invoke **Update Debug Tasks and Launch Configurations** and confirm that each drop-in entry is added or overwrites the matching workspace entry by its documented identifier.
- Use `git check-ignore --no-index -v` for each drop-in file and `git status --short` to confirm that intended sources are visible to version control.

## Guardrails & Constraints (Strict Rules)

- **No fabrication:** Do not invent solution ownership, debug configurations, tasks, inputs, paths, or expected merge results.
- **Portability:** Do not infer ownership from folder proximity alone or introduce debugger-, device-, compiler-, or RTOS-specific content.
- **Critical blockers:** Stop destructive relocation when a drop-in's owning solution is ambiguous, JSON is invalid, merge identifiers are missing or duplicated, intended destination coverage cannot be verified, or ignore policy hides the destination.
- **Scope:** Change only confirmed `.vscode.d` sources and separately authorized ignore rules. Do not hand-edit extension-managed workspace entries as a substitute for valid drop-ins, and do not delete an old source before validating its replacements.
- **Tone and style:** Respond factually and directly. Omit conversational filler.

## Expected Output

Provide one validated `.vscode.d/launch.json` and/or `.vscode.d/tasks.json` beside each applicable `*.csolution.yml`. Report the source-to-solution mapping, supported arrays and identifiers found, merge verification, version-control visibility, and obsolete locations eligible for removal.

## Validation Resources

- [CMSIS Solution `.vscode.d` drop-ins](https://mdk-packs.github.io/vscode-cmsis-solution-docs/debug.html#vscoded-drop-ins): authoritative placement, consumed arrays, merge identifiers, and merge behavior.
- [VS Code launch configurations](https://code.visualstudio.com/docs/debugtest/debugging-configuration) and [tasks](https://code.visualstudio.com/docs/reference/tasks-appendix): JSON structure and variable semantics.
- [Git check-ignore](https://git-scm.com/docs/git-check-ignore): verify that solution-local drop-ins remain visible to version control.
