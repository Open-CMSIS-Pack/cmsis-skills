---
name: check-cmsis-environment
description: Verify the CMSIS tools environment exported by the CMSIS Solution extension, CMSIS-Toolbox, CMake, Ninja, and available compiler toolchains. Use before creating or building a CMSIS solution project.
---

# Check CMSIS Environment

## Target & Persona

- **Role:** Verification Engineer
- **Objective:** Verify tool discovery and the selected environment for CMSIS solution projects. This does not establish successful compilation or license checkout.

## Prerequisites & Context

- **Expected input:** The workspace root, the active or explicitly requested `.csolution.yml` file when present, its solution-local `.cmsis/tools-environment.yml`, and the workspace `vcpkg-configuration.json` when present.
- **Dependencies:** An already installed CMSIS-Toolbox `cbuild` executable, CMake, Ninja, and compiler artifacts. The Arm Tools Environment Manager and the CMSIS Solution extension are optional discovery sources, not required tools.
- **Portability:** Applies to CMSIS solution workspaces on supported host operating systems. It has no MCU-, RTOS-, debugger-, or board-specific assumptions; compiler registrations are discovered from the workspace environment.

## Execution Steps (Strict Workflow)

1. **Analysis:** Inspect the generated CMSIS tools environment or, when it is absent, the workspace manifest and already-installed tool artifacts it selects.
2. **Processing:** Import or reproduce the selected tool environment only in the current process, then run the detailed checks below.
3. **Validation:** Confirm `cbuild`, CMake, Ninja, and the required compiler toolchain through the listed `cbuild` commands.
4. **Formatting:** Return the defined `PASS` or `FAIL` report with the observed paths, versions, and missing requirements.

### Detailed procedure

1. Before running `cbuild`, identify the explicitly requested solution or, when
  none is specified, the active solution from reliable extension state. If
  selection remains ambiguous, ask which solution to check; do not choose
  another solution's export. Directly test whether
  `<solution-directory>/.cmsis/tools-environment.yml` exists. The solution
  directory may differ from the workspace root; do not infer absence from a
  root-level lookup or a file listing. Record the exact checked path and whether
  it was found, absent, or could not be checked. A failed read is not evidence
  of absence. When checking tools before a solution exists, record that no
  solution-specific export applies and use the manifest fallback.
2. When the file exists:
   - Parse it as YAML. Require one `cmsis-tools-environment` mapping containing
     string `version`, `generated-by`, and `solution` values; an `environment`
     mapping with a string array `path` and a string-to-string mapping
     `variables`; and a `tools` array whose consumed entries contain string
     `name`, `origin`, and `directory` values plus a `provider` mapping. Stop
     when YAML parsing fails or any consumed field has the wrong structure. Do
     not infer or consume unknown fields.
   - This procedure supports export format version `1.0.0`. For any other
     `cmsis-tools-environment.version`, stop before importing the environment
     and report an unsupported format, not a defective tool installation. Do
     not infer compatibility from field names alone.
   - Validate only consumed fields and the semantic checks below. Do not locate
     or read an installed extension schema, discover validator dependencies,
     or perform full JSON Schema validation. Record `generated-by` as reported
     metadata, not proof of trust; do not locate an extension installation just
     to compare its version. Do not claim full schema conformance.
   - Resolve `cmsis-tools-environment.solution` relative to the generated file
     and confirm that it identifies the solution being checked. Stop when it
     resolves outside the workspace, does not exist, or identifies a different
     solution.
   - Treat `environment.path`, `environment.variables`, and `tools` as the
     extension-resolved source of truth. Do not rediscover precedence from the
     vcpkg artifact store or choose another installation when this file is
     valid.
   - Prepend the listed `environment.path` entries to the current process
     `PATH` in their listed order, preserving their precedence, and export every
     `environment.variables` entry process-locally. Do not persist variables or
     edit the generated file; the CMSIS Solution extension is its sole writer.
   - Confirm that every imported path exists. For each `tools` entry, record its
     name, version when present, origin, provider, and directory, and confirm
     that its directory exists. Stop on a missing path or tool directory.
3. Only when the expected solution-local export is confirmed absent, or no
  solution exists yet, check for `vcpkg-configuration.json` at the workspace
  root. When the manifest exists, read its `requires`
   entries and treat their exact artifact versions as the intended workspace
   tools. Arm Tools Environment Manager activation is local to its VS Code
   instance and is not inherited by every shell or agent process.
   If the manifest is absent, still check the VS Code CMSIS Solution extension
   for its bundled toolbox before failing.
4. In that fallback case, reproduce the already-installed workspace environment
   in the current process:
   - Locate each exact requested artifact in the local vcpkg artifact store. Do
     not acquire, download, install, update, or select a different version. Stop
     when an artifact is absent or when its location is ambiguous.
   - Prepend each selected tool's executable directory to `PATH`.
   - Export the CMSIS-Toolbox registration variable for each compiler using its
     family and normalized version, for example
     `GCC_TOOLCHAIN_15_3_1=<artifact>/bin` for GCC 15.3.1.
   - If the manifest selects CMSIS-Toolbox, use that exact artifact. Otherwise,
     when the workspace uses the VS Code CMSIS Solution extension, use its
     bundled `tools/cmsis-toolbox/bin` directory. Stop when multiple extension
     installations make the selection ambiguous.
   - Set `CMSIS_COMPILER_ROOT` to the `etc` directory belonging to the selected
     CMSIS-Toolbox. Do not combine a `cbuild` executable with another
     CMSIS-Toolbox installation's configuration directory.
   Keep all exported variables process-local; do not modify persistent user or
   system settings.
5. Resolve the effective `cbuild` executable and confirm that it belongs to the
   selected CMSIS-Toolbox installation, for both export and fallback selection.
   Run `cbuild --version`, confirm success, and record its path and reported
   **cbuild component version** separately from the **CMSIS-Toolbox package
   version**, when known. Stop when `cbuild` is unavailable or resolves to a
   different installation.
   - Package and component versions need not match. Their difference alone is
     neither a failure nor a reason to warn about a defect, stop verification,
     or recommend repair. For example, Toolbox package 2.14.1 can contain
     cbuild 2.14.0. This rule applies to export and manifest fallback alike.
   - Compare a component version only with metadata explicitly identifying the
     expected version of that component. If such metadata is unavailable,
     report the observed versions separately and continue the required checks.
     Do not require package hashing to resolve a package/component difference.
6. Run `cbuild list environment`. Record the reported environment and confirm
   that CMake and Ninja are both found.
7. Run `cbuild list toolchains`. Record every detected compiler identifier and
   version. Use `cbuild list toolchains --verbose` to verify compiler paths and
   registration variables.

Return `PASS` only when `cbuild` is available, CMake and Ninja are found, and at
least one compiler toolchain is detected. When the generated environment
identifies a compiler through `tools` or a compiler registration variable, also
require `cbuild list toolchains` to report that compiler and version. When the
manifest fallback is used and requests a compiler, require the reported compiler
and version to match that request.

Record each required command's outcome. Stop only for a demonstrated blocker
that prevents reliable continuation; identify each skipped check and its reason.
A package/component version difference must not skip environment or compiler
discovery. Optional diagnostic failures do not override independently successful
required checks unless they demonstrate a violation of a required criterion.

## Missing Tools

Do not install, upgrade, repair, or reconfigure development tools as part of this
skill. Recommend setup or repair only for an observed missing requirement or a
demonstrated inconsistency, never merely for different package/component versions.

- When CMake or Ninja is missing, return `FAIL` and recommend that the user set up
  the build environment outside this skill. In VS Code, use Arm Environment
  Manager; otherwise follow the manual CMSIS-Toolbox installation instructions.
- When no compiler is detected, return `FAIL` and recommend that the user set up a
  compiler outside this skill. In VS Code, use Arm Environment Manager; otherwise
  follow the CMSIS-Toolbox compiler toolchain instructions.
- When a requested vcpkg artifact is not already installed, return `FAIL` and ask
  the user to activate or repair the workspace environment outside this skill.
- When the solution-local `.cmsis/tools-environment.yml` has structural errors
  in consumed fields, identifies a different solution, or references missing
  paths, return `FAIL` and ask
  the user to convert the solution or reactivate the tools environment in the
  CMSIS Solution extension. For an unsupported export format, return `FAIL`
  with the verification limitation; do not recommend tool repair solely for
  that reason. Do not silently fall back to `vcpkg-configuration.json` when
  the generated file exists but is unusable.

After the user completes the external setup, restart from the
solution-local `.cmsis/tools-environment.yml` check and repeat the complete workflow. VS Code
is an optional setup method and is not required by this skill.

## Guardrails & Constraints (Strict Rules)

- **No fabrication:** Do not invent artifact locations, tool versions, compiler registrations, or command results.
- **Portability:** Do not add persistent host settings or assume a compiler family beyond the artifacts selected by the workspace.
- **Critical blockers:** Stop when a selected artifact is absent or ambiguous, the selected export is unusable, `cbuild` is unavailable or from the wrong installation, or a demonstrated failure prevents reliable continuation. Report skipped checks and their reasons; version-label differences alone are not blockers.
- **Evidence-bound reporting:** Distinguish confirmed absence from an unreadable or unchecked path. Do not infer workspace-wide export absence from a missing file at one location or prescribe repair without evidence.
- **Scope:** Verify the existing environment only; do not install, update, repair, or reconfigure tools.
- **Tone and style:** Respond factually and directly. Omit conversational filler.

## Expected Output

Report:

- status: `PASS` or `FAIL`;
- selected solution and exact export path checked, with discovery status:
  `found`, `absent at the checked path`, or `unable to determine`; when no
  solution exists yet, report `not applicable` rather than export absence;
- when found, export format version, generator, resolved solution, selected
  tools, and consumed-field and semantic check results; full schema conformance
  is not checked;
- selected environment source and reason for fallback, when used;
- fallback `vcpkg-configuration.json` path and requested artifacts, when used;
- process-local environment entries and whether they came from the generated
  environment or fallback artifact discovery;
- effective `cbuild` path, reported cbuild component version, and separately the
  selected CMSIS-Toolbox package version when known;
- CMake and Ninja detection results from `cbuild list environment`;
- detected compiler identifiers and versions from `cbuild list toolchains`;
- each required check's result, including skipped checks and reasons; list
  blockers separately from warnings and optional diagnostic failures;
- each demonstrated missing requirement or inconsistency and the applicable
  setup reference when status is `FAIL`;
- scope limitation: discovery does not establish build success or license
  checkout.

## Validation Resources

- [CMSIS-Toolbox build tools](https://open-cmsis-pack.github.io/cmsis-toolbox/build-tools/)
- [CMSIS-Toolbox installation](https://open-cmsis-pack.github.io/cmsis-toolbox/installation/)
- [CMSIS-Toolbox compiler toolchains](https://open-cmsis-pack.github.io/cmsis-toolbox/installation/#compiler-toolchains)
- [Arm Tools Environment Manager](https://github.com/ARM-software/vscode-environment-manager)
