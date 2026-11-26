# CMSIS Build Validation

Use CMSIS-Toolbox `cbuild` directly for migration validation. Do not validate by invoking CMake, Ninja, or generated build files separately.

## Resolve the solution and target

1. Find workspace `*.csolution.yml` files.
2. If exactly one exists, use it. If several exist and the user did not specify one, ask which solution to validate.
3. Read `target-types` from the selected solution. If exactly one target type exists, use its `type` value for `--active`. If several exist and the user did not specify one, ask which target to validate.

Do not hard-code a solution filename or active target.

## Resolve cbuild

Prefer the newest Arm CMSIS Solution VS Code extension bundle instead of a bare `cbuild` from `PATH`.

- Windows: resolve the newest directory matching `$env:USERPROFILE\.vscode\extensions\arm.cmsis-csolution-*\tools\cmsis-toolbox\bin\` and invoke its `cbuild.exe` explicitly.
- macOS/Linux: resolve the newest directory matching `$HOME/.vscode/extensions/arm.cmsis-csolution-*/tools/cmsis-toolbox/bin/` and invoke its `cbuild` executable explicitly.

If no bundled executable exists, report the exact paths searched and the blocker. Do not silently fall back to an unrelated `cbuild` on `PATH`.

## Run validation

Derive the command from the selected solution and target:

```text
<absolute-cbuild-path> <workspace-relative-solution.csolution.yml> --active <target-type>
```

Use incremental `cbuild` during ordinary compile/link iteration after generated state is current. Use `--rebuild` after toolchain or context changes, RTE/generator refresh, source-list or linker-template changes, suspected stale state, and for the final clean validation.

Allow at least 600 seconds for normal validation and up to 1200 seconds for `--rebuild`, pack regeneration, or a first build. If a shorter execution limit interrupts a build, rerun the same command with the longer limit and record the first timeout.

On failure, record the exact `cbuild` command and output. Do not infer missing direct CMake or Ninja setup unless `cbuild` itself reports it.
