---
name: check-cmsis-environment
description: Verify the CMSIS tools environment exported by the CMSIS Solution extension, CMSIS-Toolbox, CMake, Ninja, and available compiler toolchains. Use before creating or building a CMSIS solution project.
---

# Check CMSIS Environment

## Target & Persona

- **Role:** Verification Engineer
- **Objective:** Establish whether the current process can build CMSIS solution projects with CMSIS-Toolbox and at least one compiler.

## Prerequisites & Context

- **Expected input:** The workspace root and, when present, its `.cmsis/tools-environment.yml` and `vcpkg-configuration.json` files.
- **Dependencies:** An already installed CMSIS-Toolbox `cbuild` executable, CMake, Ninja, and compiler artifacts. The Arm Tools Environment Manager and the CMSIS Solution extension are optional discovery sources, not required tools.
- **Portability:** Applies to CMSIS solution workspaces on supported host operating systems. It has no MCU-, RTOS-, debugger-, or board-specific assumptions; compiler registrations are discovered from the workspace environment.

## Execution Steps (Strict Workflow)

1. **Analysis:** Inspect the generated CMSIS tools environment or, when it is absent, the workspace manifest and already-installed tool artifacts it selects.
2. **Processing:** Import or reproduce the selected tool environment only in the current process, then run the detailed checks below.
3. **Validation:** Confirm `cbuild`, CMake, Ninja, and the required compiler toolchain through the listed `cbuild` commands.
4. **Formatting:** Return the defined `PASS` or `FAIL` report with the observed paths, versions, and missing requirements.

### Detailed procedure

1. Before running `cbuild`, directly test whether
   `.cmsis/tools-environment.yml` exists in the workspace root; do not infer
   absence from a file listing.
2. When the file exists:
   - Parse it as YAML. Require one `cmsis-tools-environment` mapping containing
     string `version`, `generated-by`, and `solution` values; an `environment`
     mapping with a string array `path` and a string-to-string mapping
     `variables`; and a `tools` array whose consumed entries contain string
     `name`, `origin`, and `directory` values plus a `provider` mapping. Stop
     when YAML parsing fails or any consumed field has the wrong structure. Do
     not infer or consume unknown fields.
   - When an active `arm.cmsis-csolution` extension installation is available,
     use `schemas/tools-environment.schema.json` beneath its installation
     directory. Read the accepted `cmsis-tools-environment.version` constraint
     from that schema; do not hardcode a format version. Perform full schema
     validation when the schema accepts the document version. Otherwise report
     why full validation was skipped and continue with the consumed-field
     validation above. Record whether the installed extension version agrees
     with `generated-by`; a missing installation or version mismatch is
     diagnostic information, not a failure.
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
3. Only when `.cmsis/tools-environment.yml` is absent, check for
   `vcpkg-configuration.json`. When the manifest exists, read its `requires`
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
5. Resolve the effective `cbuild` executable and run `cbuild --version`. Confirm
   that the command succeeds and record both its path and reported
  CMSIS-Toolbox version. Stop when `cbuild` is unavailable. When the generated
  file lists CMSIS-Toolbox, confirm that the effective executable comes from
  its selected directory and that the reported version matches the listed
  version.
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

## Missing Tools

Do not install, upgrade, repair, or reconfigure development tools as part of this
skill.

- When CMake or Ninja is missing, return `FAIL` and recommend that the user set up
  the build environment outside this skill. In VS Code, use Arm Environment
  Manager; otherwise follow the manual CMSIS-Toolbox installation instructions.
- When no compiler is detected, return `FAIL` and recommend that the user set up a
  compiler outside this skill. In VS Code, use Arm Environment Manager; otherwise
  follow the CMSIS-Toolbox compiler toolchain instructions.
- When a requested vcpkg artifact is not already installed, return `FAIL` and ask
  the user to activate or repair the workspace environment outside this skill.
- When `.cmsis/tools-environment.yml` has structural errors in fields consumed
  by this skill, is stale, or references missing paths, return `FAIL` and ask
  the user to convert the solution or reactivate the tools environment in the
  CMSIS Solution extension. An unavailable schema, extension-version mismatch,
  or document-version mismatch alone is a warning, not a failure. Do not
  silently fall back to `vcpkg-configuration.json` when the generated file
  exists but is unusable.

After the user completes the external setup, restart from the
`.cmsis/tools-environment.yml` check and repeat the complete workflow. VS Code
is an optional setup method and is not required by this skill.

## Guardrails & Constraints (Strict Rules)

- **No fabrication:** Do not invent artifact locations, tool versions, compiler registrations, or command results.
- **Portability:** Do not add persistent host settings or assume a compiler family beyond the artifacts selected by the workspace.
- **Critical blockers:** Stop when a selected artifact is absent or ambiguous, `cbuild` is unavailable, or a required environment check fails.
- **Scope:** Verify the existing environment only; do not install, update, repair, or reconfigure tools.
- **Tone and style:** Respond factually and directly. Omit conversational filler.

## Expected Output

Report:

- status: `PASS` or `FAIL`;
- workspace `.cmsis/tools-environment.yml` path, format version, generator,
  resolved solution, selected tools, schema-validation level, and any extension
  provenance mismatch, or report that no generated environment exists and the
  fallback was used;
- fallback `vcpkg-configuration.json` path and requested artifacts, when used;
- process-local environment entries and whether they came from the generated
  environment or fallback artifact discovery;
- effective `cbuild` path and CMSIS-Toolbox version;
- CMake and Ninja detection results from `cbuild list environment`;
- detected compiler identifiers and versions from `cbuild list toolchains`;
- each missing requirement and the applicable setup reference when status is
  `FAIL`.

## Validation Resources

- CMSIS tools environment format, when the extension is installed:
  `<active-arm.cmsis-csolution-extension>/schemas/tools-environment.md`
- CMSIS tools environment schema, when the extension is installed:
  `<active-arm.cmsis-csolution-extension>/schemas/tools-environment.schema.json`
- [CMSIS-Toolbox build tools](https://open-cmsis-pack.github.io/cmsis-toolbox/build-tools/)
- [CMSIS-Toolbox installation](https://open-cmsis-pack.github.io/cmsis-toolbox/installation/)
- [CMSIS-Toolbox compiler toolchains](https://open-cmsis-pack.github.io/cmsis-toolbox/installation/#compiler-toolchains)
- [Arm Tools Environment Manager](https://github.com/ARM-software/vscode-environment-manager)
