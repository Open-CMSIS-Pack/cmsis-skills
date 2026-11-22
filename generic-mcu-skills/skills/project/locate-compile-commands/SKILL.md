---
name: locate-compile-commands
description: Locate the compile_commands.json files of a CMSIS solution from its generated build information, one per project and context. Use when clangd, IntelliSense, or a static analysis tool needs the compilation database of the active solution, or when a search of the workspace root did not find it.
---

# Locate Compile Commands

## Target & Persona

- **Role:** Tool Integrator
- **Objective:** Return the path of the compilation database (`compile_commands.json`) of each selected context of one CMSIS solution, or report that the database has not been generated.

## Prerequisites & Context

- **Expected input:** The active or explicitly requested `*.csolution.yml` and the build information that the CMSIS-Toolbox generated for it: `<solution-name>.cbuild-idx.yml` and the `*.cbuild.yml` files it names.
- **Dependencies:** None for the lookup; it only reads generated YAML files. CMSIS-Toolbox `cbuild` is needed only when the build information has to be generated first, which is outside this skill.
- **Portability:** Applies to CMSIS solution projects on every host and with every compiler. It has no MCU-, board-, RTOS-, or debugger-specific assumption. A context that the build information lists without a compilation database is reported, not guessed.

## Execution Steps (Strict Workflow)

1. **Analysis:** Identify the solution and read its `*.cbuild-idx.yml`.
2. **Processing:** Follow each listed `*.cbuild.yml` to its `comp-db` output and resolve the path.
3. **Validation:** Confirm that each resolved file exists and is a compilation database.
4. **Formatting:** Return one row per project and context.

### Detailed procedure

1. Take the explicitly requested `*.csolution.yml` or, when none is named, the active solution from reliable tool or extension state. If several solutions are plausible, ask which one is meant. Record the solution directory.
2. Open `<solution-name>.cbuild-idx.yml` in the solution directory. When it does not exist, the build information has not been generated: stop and report that, with the command that generates it (see *Missing build information*).
3. Read the entries of `build-idx.cbuilds`. Each entry names a `*.cbuild.yml` with `cbuild:`, relative to the directory of the `*.cbuild-idx.yml`, and identifies it with `project:` and `configuration:` (`.<build-type>+<target-type>`). Keep the entries that match the requested project or context, or all of them when none is requested.
4. Open each selected `*.cbuild.yml`. Under `build.output`, find the entry with `type: comp-db` whose `file:` is `compile_commands.json`. The list can hold further `comp-db` entries for other files; do not take those.
5. Resolve the path: the directory of the `*.cbuild.yml`, then `build.output-dirs.outdir` relative to that directory, then the `file:` value. When `outdir` is `.`, the database lies beside the `*.cbuild.yml`.
6. Confirm that the resolved file exists and holds a JSON array whose entries have `directory`, `file`, and `command` or `arguments`. A path that the build information names but that does not exist is reported as not generated.

### Missing build information

Do not generate build information as part of this skill. When the `*.cbuild-idx.yml`, a listed `*.cbuild.yml`, or the database itself is missing, report which file is missing and that `cbuild setup` creates the build information files and `compile_commands.json`:

```text
cbuild setup <solution>.csolution.yml --active <target-type>[@<target-set>] --packs
```

The CMSIS Solution extension for VS Code runs this setup itself. Repeat the lookup after the user or the IDE has run it.

## Guardrails & Constraints (Strict Rules)

- **No fabrication:** Do not invent or guess a path, a context, or a file name. Take each path from the build information and confirm it on disk, or report what is missing.
- **Build information first:** Do not conclude from a search of the workspace root that no compilation database exists. The database lies in the output directory of each context, which the build information names.
- **Database, not index:** `compile_commands.json` is the input of clangd. The index of symbols and references that clangd builds from it (by default under `.cache/clangd/` beside the database) is not the compilation database. Do not return, read, or edit index files in its place.
- **Not the intermediate copy:** A `compile_commands.json` below the intermediate directory (`build.output-dirs.intdir`, by default `tmp/`) belongs to the CMake build tree. Return the file that `build.output` names.
- **One per context:** A solution with several entries under `cbuilds:` has several databases. Do not merge them and do not present one as the database of the whole solution.
- **Portability:** Do not assume a compiler, a target name, or the default output directory layout; read `outdir` and `file:` from the build information.
- **Critical blockers:** Stop when the solution is ambiguous, the `*.cbuild-idx.yml` is missing or cannot be parsed, or a listed `*.cbuild.yml` does not exist. Report a context without a `comp-db` entry for `compile_commands.json` as a result, not as a failure of the others.
- **Scope:** Locate and verify only. Do not run a build, change clangd or editor settings, or edit generated files.
- **Tone and style:** Respond factually and directly. Omit conversational filler.

## Expected Output

Report the solution and the `*.cbuild-idx.yml` that was read, then one row per selected entry of `cbuilds:`:

| Project | Configuration | `*.cbuild.yml` | `compile_commands.json` | State |
|---|---|---|---|---|
| `<project>` | `.<build-type>+<target-type>` | path from `cbuild:` | resolved path | `found`, `not generated`, or `no comp-db entry` |

Give paths relative to the solution directory unless absolute paths are requested. When build information is missing, report the missing file and the `cbuild setup` command instead of a table.

## Validation Resources

- [CMSIS-Toolbox Build Information Files](https://open-cmsis-pack.github.io/cmsis-toolbox/YML-CBuild-Format/): `build-idx.cbuilds` of the `*.cbuild-idx.yml`, and `build.output` and `build.output-dirs` of the `*.cbuild.yml`.
- [CMSIS-Toolbox Build Tools: Setup Project (for IDE)](https://open-cmsis-pack.github.io/cmsis-toolbox/build-tools/#setup-project-for-ide): `cbuild setup` creates the build information files and `compile_commands.json`.
- The resolved file itself: it exists, parses as JSON, and the `file` of one of its entries exists.
