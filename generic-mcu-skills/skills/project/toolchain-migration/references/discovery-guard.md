# Discovery Guard

Apply this guard during migration planning and execution.

## Allowed discovery

- Locate only `*.csolution.yml`, `*.cproject.yml`, `*.cgen.yml`, and `*.clayer.yml` during Phase 1, plus relevant non-YAML startup, scatter, linker, source, header, assembly, map, and list files.
- Do not read any other YAML during Phase 1, including `cdefault.yml` and generated `*.cbuild*.yml`.
- During Phase 2 validation and post-link audit only, read generated `*.cbuild*.yml` to prove the active compiler, linker script, region header, and output artifacts. Never edit it or use it for Phase 1 discovery.
- Ignore CMake, Ninja, clangd, and generated build-system files as migration inputs.
- Read at least one allowed solution or project manifest directly before claiming missing context.

## Fallback sequence

If search output is empty, incomplete, or contradictory:

1. Search filenames directly with `rg --files` and allowlisted globs.
2. Open discovered allowed files directly.
3. Continue Phase 1 with verified partial evidence.
4. Report a codebase-visibility blocker only after both search and direct reads fail.

List exact unreadable or missing filenames in a blocker. Do not report a generic workspace-access problem when any read mechanism still works.

If relevant information appears to exist only in a disallowed YAML file, add a manual-review subtask describing the unknown setting without naming that YAML path under `Impacted files`.
