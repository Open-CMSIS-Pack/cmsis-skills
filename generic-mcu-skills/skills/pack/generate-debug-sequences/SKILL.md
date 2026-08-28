---
name: generate-debug-sequences
description: Generate evidence-backed, device-specific non-trace CMSIS debug sequences in either an existing Device Family Pack PDSC or one existing CMSIS-Toolbox `*.cbuild-run.yml` target. Use for unlock, debug-port setup, reset, bootloader, flash, authentication, multi-core startup, or reliable debug through low-power modes after `$debug-access-knowledge` and `$debug-knowledge` establish the facts; use destination-specific preparation, application, and validation skills, and do not use for CoreSight trace setup.
---

# Generate Debug Sequences

## Target & Persona

- **Role:** CMSIS-Pack Tool Integrator and Verification Engineer.
- **Objective:** Implement every verified device-specific non-trace behavior in one selected PDSC or `cbuild-run` destination.

## Prerequisites & Context

- **Expected input:** Exactly one existing target `.pdsc` or `*.cbuild-run.yml`, selected PDSC scope or flattened runtime target, affected processors and sequences, documented device behavior, and current `.agent-artifacts/<pdsc-stem>.debug-access-knowledge.md` and `.agent-artifacts/<pdsc-stem>.debug-knowledge.md` records.
- **Dependencies:** `$debug-access-knowledge`; `$debug-knowledge`; `$manage-debug-variables`; for PDSC output, `$prepare-pdsc-sequence-change`, `$apply-confirmed-pdsc-proposal`, and `$validate-pdsc-sequence-xml`; for `cbuild-run` output, `$prepare-cbuild-run-change`, `$apply-confirmed-cbuild-run-proposal`, and `$validate-cbuild-run-yaml`; current [Open-CMSIS-Pack *Debug Description* specification](https://open-cmsis-pack.github.io/Open-CMSIS-Pack-Spec/main/html/debug_description.html); current [CMSIS-Toolbox *Build Information Files* specification](https://github.com/Open-CMSIS-Pack/cmsis-toolbox/blob/main/docs/YML-CBuild-Format.md#cbuild-runyml); and the destination contracts in `references/`.
- **Portability:** Support any existing DFP or `cbuild-run` target with documented device-specific behavior. A `cbuild-run` change may be an end-user override or a reviewable proving step before a separate Pack update. Do not assume a device family, debug adapter, toolchain, RTOS, or active target; use a target only when available for semantic validation.

## Execution Steps (Strict Workflow)

1. **Analysis:** Identify exactly one destination and read both knowledge records plus `references/debug-sequence-contract.md`. For PDSC, run `$prepare-pdsc-sequence-change` with `domain=debug`; for `cbuild-run`, run `$prepare-cbuild-run-change` with `domain=debug`. Return insufficient access facts to `$debug-access-knowledge` and behavior facts to `$debug-knowledge`.
2. **Processing:** Assemble a destination-neutral sequence set with names, processor applicability, ordered block trees, predefined-default provenance, variables, and low-power behavior. Add concise verified-purpose comments to every newly authored C-like command or logical command group, including register and bit-field names when sources identify them. Run `$manage-debug-variables` for every documented user runtime choice. Render through exactly one of `references/pdsc-output.md` or `references/cbuild-run-output.md`.
3. **Validation:** Create or update `.agent-artifacts/<destination-stem>.debug-sequences.md` as the private proposal record. Record destination and path, scope or target identity, evidence, applicability, semantic sequence set, variables, exact XML or YAML, `.dbgconf` proposals, unsupported mappings, regeneration risk, unresolved items, and `PROPOSED` status. Present the proposal and obtain confirmation. Apply and run the destination validator, compare every overridden predefined sequence with its current specification default, and perform documented low-power checks when a target is available. Set `APPLIED` only after all checks pass.
4. **Formatting:** Report destination, sequence identities, applicability, placement or merge result, sources, low-power results, `.dbgconf` proposals, unsupported mappings, regeneration risk when applicable, unresolved items, and validation results. Do not provide the private proposal record as input to a helper or another skill.

## Guardrails & Constraints (Strict Rules)

- **No fabrication:** Do not invent reset, unlock, authentication, boot, flash, processor-control, low-power, register, delay, connection behavior, output mappings, or YAML fields.
- **Portability:** Do not introduce a device-family, debugger, toolchain, build-system, or RTOS dependency unless authoritative inputs require it.
- **Critical blockers:** Stop when either knowledge record is inadequate, the destination is absent or ambiguous, target identity conflicts, a required specification default or output mapping is unavailable, confirmation is absent, or validation fails.
- **Scope:** Generate only non-trace sequences and related documented runtime choices. Preserve trace configuration and unrelated destination content; do not modify `.dbgconf` without explicit confirmation.
- **Tone and style:** Respond factually and directly. Omit conversational filler.

## Expected Output

Create or update the private `.agent-artifacts/<destination-stem>.debug-sequences.md` proposal record, apply the confirmed non-trace sequence change to one PDSC or `cbuild-run` target, and report semantic and destination-specific validation.

## Validation Resources

Read [the common debug-sequence contract](references/debug-sequence-contract.md) and exactly one of [the PDSC output contract](references/pdsc-output.md) or [the cbuild-run output contract](references/cbuild-run-output.md). Run the selected common validator, compare overridden predefined sequences with current defaults, and perform documented low-power checks when a target is available.
