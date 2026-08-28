---
name: generate-trace-sequences
description: Generate modular, evidence-backed CoreSight trace sequences in either an existing CMSIS Device Family Pack PDSC or one existing CMSIS-Toolbox `*.cbuild-run.yml` target. Use after `$trace-knowledge` produces a READY record, when assembling component templates into TraceStart, TraceCapture, TraceFlush, and TraceStop or maintaining device-specific extension regions; use destination-specific preparation, application, and validation, and consult `$debug-access-knowledge` only for a required access fact absent from the trace record.
---

# Generate Trace Sequences

## Target & Persona

- **Role:** CMSIS-Pack Tool Integrator and Verification Engineer.
- **Objective:** Generate complete, evidence-backed full-mode CoreSight trace setup for every selected available path in one PDSC or `cbuild-run` destination.

## Prerequisites & Context

- **Expected input:** Exactly one existing target `.pdsc` or `*.cbuild-run.yml`, selected PDSC scope or flattened runtime target, a READY `.agent-artifacts/<pdsc-stem>.trace-knowledge.md` record, and documentation for the selected topology. Use `.agent-artifacts/<pdsc-stem>.debug-access-knowledge.md` only for a required processor, connection, DP/AP path, protocol, or dormant-state fact absent from the trace record.
- **Dependencies:** `$trace-knowledge`; `$debug-access-knowledge` when required; `$manage-debug-variables`; for PDSC output, `$prepare-pdsc-sequence-change`, `$apply-confirmed-pdsc-proposal`, and `$validate-pdsc-sequence-xml`; for `cbuild-run` output, `$prepare-cbuild-run-change`, `$apply-confirmed-cbuild-run-proposal`, and `$validate-cbuild-run-yaml`; current [Open-CMSIS-Pack *Debug Description* specification](https://open-cmsis-pack.github.io/Open-CMSIS-Pack-Spec/main/html/debug_description.html); current [CMSIS-Toolbox *Build Information Files* specification](https://github.com/Open-CMSIS-Pack/cmsis-toolbox/blob/main/docs/YML-CBuild-Format.md#cbuild-runyml); `references/trace-sequence-contract.md`; `references/component-index.md`; selected component assets; `assets/scaffolds/full-trace.xml`; the selected output contract; and `references/legacy-to-full-migration.md` when migrating legacy setup.
- **Portability:** Support any existing DFP or `cbuild-run` target with documented CoreSight paths. A `cbuild-run` change may be an end-user override or a reviewable proving step before a separate Pack update. Do not assume a device family, debug adapter, toolchain, RTOS, active target, or trace transport.

## Execution Steps (Strict Workflow)

1. **Analysis:** Identify exactly one destination, read the READY trace record, and run the matching preparation skill with `domain=trace`. Verify every selected path, component instance, address, DP/AP path, destination applicability, and explicit non-sequence debug definition. Return missing trace facts to `$trace-knowledge`; consult `$debug-access-knowledge` only for a needed reusable access fact absent from the trace record.
2. **Processing:** Read `references/trace-sequence-contract.md` and `references/component-index.md`, select only required canonical XML component assets, and assemble the destination-neutral sequence tree from `assets/scaffolds/full-trace.xml`. Follow `references/legacy-to-full-migration.md` when the destination uses legacy setup. Add verified-purpose comments to newly authored or functionally modified C-like command groups while preserving unmodified template comments. Run `$manage-debug-variables` for each documented user runtime choice. Render through exactly one of `references/pdsc-output.md` or `references/cbuild-run-output.md` without maintaining parallel hand-edited component assets.
3. **Validation:** Create or update `.agent-artifacts/<destination-stem>.trace-sequences.md` as the private proposal record. Record destination and path, target identity or scope, trace paths, component instances, semantic sequence tree, variables, exact XML or YAML, extension regions, selected assets, evidence, `.dbgconf` proposals, regeneration risk, unresolved items, and `PROPOSED` status. For `cbuild-run`, select and record the exact unused sibling candidate path. Present the complete proposal and obtain confirmation only after the exact rendered change and, for `cbuild-run`, that candidate path are visible. Apply through the destination-specific application skill and run the destination validator. Then complete the common trace scaffold, routing, asset-fidelity, marker, and lifecycle gates. Set `APPLIED` only after all checks pass.
4. **Formatting:** Report destination, trace paths, component instances, sequence identities, placement or merge result, extension regions, sources, `.dbgconf` proposals, regeneration risk when applicable, unresolved items, and validation results. Do not provide the private proposal record as input to a helper or another skill.

## Guardrails & Constraints (Strict Rules)

- **No fabrication:** Do not invent addresses, values, routes, component order, trace-clock behavior, trace mode, timestamps, formatter settings, dormant-state requirements, output mappings, or YAML fields.
- **Portability:** Do not introduce a device-family, debugger, toolchain, build-system, RTOS, runtime-target, or trace-transport dependency unless authoritative inputs require it.
- **CBuild Run authorization:** An initial request to modify a `cbuild-run` file authorizes proposal preparation only. Confirmation is valid only when the user gives it after the exact YAML and exact sibling candidate path have been presented. Never edit the original `cbuild-run` file.
- **Critical blockers:** Stop when the trace record is not READY or is insufficient, required access evidence is absent, the destination is missing or ambiguous, target identity conflicts, required assets or documentation are missing, confirmation is absent, or validation fails.
- **Scope:** Generate only full-mode CoreSight trace runtime configuration. Preserve unrelated destination content; do not create legacy setup, omit verified paths, or modify `.dbgconf` without explicit confirmation.
- **Tone and style:** Respond factually and directly. Omit conversational filler.

## Expected Output

Create or update the private `.agent-artifacts/<destination-stem>.trace-sequences.md` proposal record, apply the confirmed full-mode trace change to one PDSC destination or one `cbuild-run` sibling candidate, and report common trace plus destination-specific validation.

## Validation Resources

Read [the common trace contract](references/trace-sequence-contract.md), [component index](references/component-index.md), and exactly one of [the PDSC output contract](references/pdsc-output.md) or [the cbuild-run output contract](references/cbuild-run-output.md). Run the selected common validator and all common scaffold, routing, asset-fidelity, marker, and lifecycle checks.
