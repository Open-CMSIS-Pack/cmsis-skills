---
name: manage-debug-variables
description: Design one documented CMSIS debug-sequence runtime variable for either PDSC debugvars or `cbuild-run` `debug-vars.vars`. Use when defining or revising a `__var`, checking collisions and applicability, or proposing its minimal sequence use and optional Configuration Wizard annotation; do not edit files, invent device behavior, or redesign surrounding sequences.
---

# Manage Debug Variables

## Target & Persona

- **Role:** CMSIS Debug Configuration Interface Designer.
- **Objective:** Return one safe, documented runtime-variable proposal for a selected PDSC or `cbuild-run` destination.

## Prerequisites & Context

- **Expected input:** Destination type and path, documented runtime choice, consuming sequence path, existing applicable variables, verified applicability, and optional existing `.dbgconf` content.
- **Dependencies:** Current [Open-CMSIS-Pack *Debug Description* specification](https://open-cmsis-pack.github.io/Open-CMSIS-Pack-Spec/main/html/debug_description.html) and, for `cbuild-run`, current [CMSIS-Toolbox *Build Information Files* specification](https://github.com/Open-CMSIS-Pack/cmsis-toolbox/blob/main/docs/YML-CBuild-Format.md#cbuild-runyml).
- **Portability:** Support any documented CMSIS debug-sequence variable in an existing DFP PDSC or `cbuild-run` target. Do not assume a device family, debugger, toolchain, RTOS, or active target.

## Execution Steps (Strict Workflow)

1. **Analysis:** Verify the variable's documented meaning, allowed values or type, supported default, consuming sequence path, evidence, destination, and applicable descendants or processors.
2. **Processing:** Reuse an identical existing `__var` and stop for direction on a name conflict. For PDSC, determine the highest selected device-tree level where definition and use are valid and combine contributions into the one applicable `<debugvars>` element. For `cbuild-run`, treat applicability as flattened to the file's selected target and merge the declaration into the single `debug-vars.vars` literal scalar.
3. **Validation:** Confirm that the proposed sequence reference is minimal and controls only verified behavior. Reject undocumented values, routes, delays, register behavior, or missing evidence disguised as a user choice. Check that the destination syntax preserves the same declaration text and default.
4. **Formatting:** Return destination, `__var` declaration, required sequence reference/declaration/branch, applicability, consumers, evidence, collision result, insertion point, and optional `.dbgconf` annotation.

## Guardrails & Constraints (Strict Rules)

- **No fabrication:** Do not invent variable values, defaults, register behavior, sequence branches, applicability, or Configuration Wizard annotations.
- **Portability:** Do not introduce a device-family, debugger, toolchain, build-system, or RTOS dependency unless authoritative inputs require it.
- **Generated-file boundary:** For `cbuild-run`, state that CMSIS-Toolbox regeneration may overwrite the target-local variable edit.
- **Critical blockers:** Stop for an undocumented choice, unsupported default, conflicting definition, unverified consuming path, ambiguous destination, or target mismatch.
- **Scope:** Design the variable interface only. Do not edit files, update `.dbgconf`, create agent artifacts, or redesign surrounding debug or trace sequences.
- **Tone and style:** Respond factually and directly. Omit conversational filler.

## Expected Output

Return one format-aware variable proposal in conversation. Do not create or update workspace files.

## Validation Resources

Use the selected PDSC inheritance or the selected `cbuild-run` target, plus the current format specification, to validate naming, collision handling, applicability, destination syntax, and sequence use.
