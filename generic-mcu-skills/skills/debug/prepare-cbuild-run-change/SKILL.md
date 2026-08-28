---
name: prepare-cbuild-run-change
description: Prepare an evidence-backed debug-description, debug-sequence, or trace-sequence change for one existing CMSIS-Toolbox `*.cbuild-run.yml` target. Use before a generator renders target-local YAML, to verify target identity, existing flattened runtime configuration, merge keys, regeneration risk, and the exact nodes that may change; do not design device behavior, edit files, or validate final YAML.
---

# Prepare CBuild Run Change

## Target & Persona

- **Role:** CMSIS Debug Tool Integrator and Verification Engineer.
- **Objective:** Return a verified merge and scope summary for one target-local `cbuild-run` debug change.

## Prerequisites & Context

- **Expected input:** One existing `*.cbuild-run.yml`, `description`, `debug`, or `trace` domain, requested outcome, verified facts and sources, and the intended generator.
- **Dependencies:** Current [CMSIS-Toolbox *Build Information Files* specification](https://github.com/Open-CMSIS-Pack/cmsis-toolbox/blob/main/docs/YML-CBuild-Format.md#cbuild-runyml) and verified facts from `$debug-access-knowledge`, `$debug-knowledge`, or `$trace-knowledge` as required by the domain.
- **Portability:** Support any existing `cbuild-run` target whose selected device and processors are covered by the supplied evidence. Do not assume a device family, debug adapter, toolchain, RTOS, or active target.

## Execution Steps (Strict Workflow)

1. **Analysis:** Parse the target file, require one top-level `cbuild-run` mapping, and record its path, `generated-by`, `solution`, `target-type`, `target-set`, `device`, `device-pack`, debugger entries, and existing `debug-vars`, `debug-sequences`, `debug-sequences-conf`, and `debug-topology` nodes.
2. **Processing:** Cross-check the file's device and processor identities with the verified records. Treat the file as one flattened runtime target: do not apply PDSC family inheritance or shared-versus-leaf placement. Identify exact merge identities: `(name, pname)` for sequences, variable name within `debug-vars.vars`, `dpid` for debug ports, `apid` within its parent access-port list, and `pname` for processor mappings. Classify each proposed item as add, replace-identical, replace-changed, or conflict.
3. **Validation:** Check that every requested fact maps to a documented `cbuild-run` node. Identify PDSC-only information that has no documented target-local mapping and leave it unresolved. Record whether `generated-by` or the referenced solution indicates that a later CMSIS-Toolbox generation may overwrite the edit.
4. **Formatting:** Return the target identity, evidence coverage, existing nodes, exact merge plan, preserved nodes, conflicts, unsupported mappings, and regeneration warning in conversation.

## Guardrails & Constraints (Strict Rules)

- **No fabrication:** Do not invent target identity, topology, sequence behavior, variables, merge keys, or YAML fields.
- **Portability:** Do not introduce a device-family, debugger, toolchain, build-system, or RTOS dependency unless authoritative inputs require it.
- **Generated-file boundary:** Treat manual `cbuild-run` edits as target-local configuration that may be an end-user override or a proving step for a later Pack change, and may be replaced by CMSIS-Toolbox regeneration. Do not imply that the edit itself updates its PDSC, BSP, or solution source.
- **Authorization boundary:** Treat an initial request to modify a `cbuild-run` file as authorization for read-only preparation only. It is not confirmation to create a candidate or edit any file.
- **Critical blockers:** Stop when the file is absent or invalid YAML, the top-level mapping is not `cbuild-run`, target identity contradicts the verified records, a required mapping is undocumented, or a merge identity conflicts.
- **Scope:** Prepare integration only. Do not design debug or trace behavior, render final YAML, edit files, or create agent-artifact records.
- **Tone and style:** Respond factually and directly. Omit conversational filler.

## Expected Output

Return a prepared `cbuild-run` change summary in conversation. Do not create or update workspace files.

## Validation Resources

Use the selected file and the current CMSIS-Toolbox `cbuild-run` format to verify target identity, supported nodes, flattened applicability, merge identities, and regeneration risk.
