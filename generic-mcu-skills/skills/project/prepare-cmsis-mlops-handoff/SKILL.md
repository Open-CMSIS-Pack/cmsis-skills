---
name: prepare-cmsis-mlops-handoff
description: Generate and validate the files exchanged between a CMSIS solution and an external MLOps conversion system. Use when a solution has an mlops node and model conversion runs separately from the embedded build.
---

# Prepare CMSIS MLOps Handoff

## Target & Persona

- **Role:** CMSIS Project and MLOps Integrator
- **Objective:** Produce a verified `*.cbuild-mlops.yml` handoff and identify the complete generated model-layer output returned to the embedded build.

## Prerequisites & Context

- **Expected input:** One selected `*.csolution.yml`, its active target, the solution's `mlops:` configuration, and the documented model-conversion entry point when conversion is in scope.
- **Dependencies:** CMSIS-Toolbox with `cbuild`; the packs selected by the solution; and any project-specific model-conversion environment. Use `check-cmsis-environment` when the effective Toolbox installation is not already verified.
- **Portability:** Applies to CMSIS solutions across MCU families, model frameworks, embedded software frameworks, and host operating systems. Vela configuration applies only when the selected target emits it.

The generated `*.cbuild-mlops.yml` is the contract between the embedded project and the MLOps system. The embedded project supplies that file and any configuration files it references. Model source can remain in a provider-controlled MLOps environment when the contract and conversion implementation support that arrangement.

## Execution Steps (Strict Workflow)

1. **Analysis:** Select exactly one solution and active target. Confirm that the solution contains `mlops:` and identify the expected `*.cbuild-mlops.yml` beside the solution. Inspect project documentation for its model-conversion command and output policy; do not infer a framework or script.
2. **Processing:** Use the verified CMSIS-Toolbox environment and run:

   ```text
   cbuild setup <solution>.csolution.yml --active <target> --packs
   ```

   Omit `--packs` when acquisition is not authorized or all required packs must already be present. Use `--frozen-packs` when the repository requires its committed pack lock to remain unchanged. Do not select a compiler registration merely to generate the MLOps contract unless the selected project processing actually requires that compiler.
3. **Validation:** Parse the generated YAML and validate the contract and all project-provided handoff files as described below. When conversion is requested, run only the project's documented entry point and validate the returned model layer against the contract.
4. **Formatting:** Report the exact solution, target, effective `cbuild` path and version, handoff inputs, conversion command when run, returned output directory, validation results, and blockers.

### Validate the handoff input

- Require one `cbuild-mlops` mapping and record `generated-by`, `processor`, optional `npu`, optional `vela`, and `model` without inventing missing values.
- Require `model.clayer` and resolve it relative to the `*.cbuild-mlops.yml` file. Reject an output path outside the intended workspace unless the project explicitly documents it.
- Treat the generated `*.cbuild-mlops.yml` and every referenced target-configuration file, such as a Vela INI file under `.cmsis`, as the files supplied by the embedded project to the MLOps system. Confirm that each referenced file exists and is readable.
- Do not require an external Vela INI when no such file is referenced. The requirement comes from the selected target, not from CMSIS, Zephyr, an RTOS, or a model framework.
- Treat model properties as a conversion contract, not proof that model source must be stored in or disclosed by the embedded repository. Report unresolved model inputs according to the documented provider boundary.

### Run and validate conversion

- Use the project-documented conversion entry point. If the project provides `model_conversion/create_ai_layer.py`, a typical invocation is:

  ```text
  python model_conversion/create_ai_layer.py <solution>.cbuild-mlops.yml
  ```

  This is an example, not a CMSIS-Toolbox requirement. A provider may adapt or replace the implementation while preserving the handoff contract and output.
- Keep environment changes process-local. Remove unrelated Python path injection when the conversion documentation requires an isolated virtual environment; do not modify persistent user or system variables.
- Require the complete directory containing the `model.clayer` destination as the MLOps output returned to the embedded build. Confirm that the declared layer file exists and that all files it references exist.
- Derive expected generated artifacts from the contract, layer, conversion documentation, or a freshly staged conversion. Flag extra model programs, reports, summaries, or generated sources as stale only when that evidence shows they are not part of the current output.
- When the conversion records tool or runtime versions, confirm they match the project's declared version authority. Do not substitute an installed package, software pack, or unrelated distribution version for that authority.

## Guardrails & Constraints (Strict Rules)

- **No fabrication:** Do not invent MLOps fields, model paths, Vela settings, target capabilities, conversion commands, or expected artifacts.
- **Portability:** Do not infer Vela, Ethos-U, Zephyr, a model framework, or a compiler requirement from directory names or adjacent examples.
- **Critical blockers:** Stop when the solution or target is ambiguous, `mlops:` is absent, generation fails, the contract is invalid, a referenced handoff file is missing, the conversion entry point is undocumented, or the declared layer output is incomplete.
- **Scope:** Do not disclose, copy, or commit provider-owned model source. Do not delete stale candidates, rewrite project policy, install tools, stage files, commit, or push unless separately authorized.
- **Tone and style:** Respond factually and directly. Omit conversational filler.

## Expected Output

Provide or verify:

- `<solution>.cbuild-mlops.yml` and its referenced target-configuration files as the embedded-project input to MLOps;
- the complete directory containing the `model.clayer` path as the MLOps output returned to the embedded build; and
- a report of the selected target, generation command, effective tool version, conversion command when run, resolved inputs and output, version checks, stale-artifact candidates, and blockers.

## Validation Resources

- [CMSIS-Toolbox MLOps integration](https://open-cmsis-pack.github.io/cmsis-toolbox/build-overview/#mlops-integration): purpose and contents of `*.cbuild-mlops.yml`.
- [CMSIS-Toolbox csolution project format](https://open-cmsis-pack.github.io/cmsis-toolbox/YML-Input-Format/#mlops-management): `mlops:` input configuration.
- [CMSIS-Toolbox build information format](https://open-cmsis-pack.github.io/cmsis-toolbox/YML-CBuild-Format/#cbuild-mlopsyml): generated contract fields and path semantics.
- The selected repository's model-conversion documentation defines its executable conversion command, model-provider boundary, output contents, and version authority.
