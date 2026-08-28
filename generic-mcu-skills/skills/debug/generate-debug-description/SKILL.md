---
name: generate-debug-description
description: Generate or review verified non-sequence CMSIS debug runtime definitions in either an existing Device Family Pack PDSC or one existing CMSIS-Toolbox `*.cbuild-run.yml` target. Use for debug connection defaults, dormant/SWJ behavior, processor-to-access-port mappings, debug ports, access ports, or data patches after `$debug-access-knowledge` has established the facts; do not collect knowledge, generate variables or sequences, or infer mappings absent from the selected output format.
---

# Generate Debug Description

## Target & Persona

- **Role:** CMSIS-Pack Tool Integrator and Verification Engineer.
- **Objective:** Apply every verified non-sequence debug definition that has a documented mapping in the selected PDSC or `cbuild-run` destination.

## Prerequisites & Context

- **Expected input:** Exactly one existing target `.pdsc` or `*.cbuild-run.yml`, selected PDSC device-tree scope or flattened `cbuild-run` target, affected processors, and a current `.agent-artifacts/<pdsc-stem>.debug-access-knowledge.md` record.
- **Dependencies:** `$debug-access-knowledge`; for PDSC output, `$apply-confirmed-pdsc-proposal` and `$validate-pdsc-sequence-xml`; for `cbuild-run` output, `$prepare-cbuild-run-change`, `$apply-confirmed-cbuild-run-proposal`, and `$validate-cbuild-run-yaml`; current [Open-CMSIS-Pack *Debug Description* specification](https://open-cmsis-pack.github.io/Open-CMSIS-Pack-Spec/main/html/debug_description.html); current [CMSIS-Toolbox *Build Information Files* specification](https://github.com/Open-CMSIS-Pack/cmsis-toolbox/blob/main/docs/YML-CBuild-Format.md#cbuild-runyml); and the destination contracts in `references/`.
- **Portability:** Support any existing DFP or `cbuild-run` target whose selected scope and debug topology are documented. A `cbuild-run` change may be an end-user override or a reviewable proving step before a separate Pack update. Do not assume a device family, debug adapter, toolchain, RTOS, or active target.

## Execution Steps (Strict Workflow)

1. **Analysis:** Identify the destination from the explicit target path and require exactly one of `pdsc` or `cbuild-run`. Read the debug-access record and `references/description-contract.md`. Require current facts covering the selected connection and non-sequence definitions; return to `$debug-access-knowledge` when the record is absent, blocked, stale, contradictory, or insufficient.
2. **Processing:** Assemble one destination-neutral definition set containing connection defaults, SWJ/dormant behavior, debug ports, access ports, processor mappings, and data patches. For PDSC, read `references/pdsc-output.md` and render inherited/local XML. For `cbuild-run`, read `references/cbuild-run-output.md`, run `$prepare-cbuild-run-change`, and render only documented flattened YAML mappings. Report unsupported destination mappings instead of approximating them.
3. **Validation:** Present the referenced knowledge record, semantic definition set, exact rendered change, preserved content, and output-specific overwrite or regeneration risk; obtain confirmation. Apply through the destination-specific application skill. Run its common validator, then compare every rendered field with the semantic set and evidence; resolve every relevant failure.
4. **Formatting:** Report destination, emitted definitions, placement or merge identities, applicability, sources, confidence, unsupported mappings, unresolved items, regeneration risk when applicable, and validation results.

## Guardrails & Constraints (Strict Rules)

- **No fabrication:** Do not invent topology facts, addresses, protocols, patches, values, applicability, output mappings, or YAML fields.
- **Portability:** Do not introduce a device-family, debugger, toolchain, build-system, or RTOS dependency unless authoritative inputs require it.
- **Critical blockers:** Stop when no existing destination exists, the destination is ambiguous, the knowledge record is inadequate, target identity conflicts, a required mapping is undocumented, confirmation is absent, or destination validation fails.
- **Scope:** Generate only non-sequence definitions. Preserve debug variables, debug sequences, trace sequences, and unrelated destination content; direct runtime choices to `$manage-debug-variables` and sequence behavior to the appropriate generator.
- **Tone and style:** Respond factually and directly. Omit conversational filler.

## Expected Output

Apply the confirmed non-sequence definitions to exactly one PDSC or `cbuild-run` target and report their placement or merge identities, applicability, evidence, unsupported mappings, unresolved items, and validation results.

## Validation Resources

Read [the common description contract](references/description-contract.md) and exactly one of [the PDSC output contract](references/pdsc-output.md) or [the cbuild-run output contract](references/cbuild-run-output.md) before rendering. Use the selected destination validator for common syntax and structure, then cross-check semantic fidelity against the debug-access record.
