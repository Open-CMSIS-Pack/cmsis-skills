---
name: validate-cbuild-run-yaml
description: Validate the YAML syntax and common debug-runtime structure of an existing or proposed CMSIS-Toolbox `*.cbuild-run.yml` change. Use after debug-description, debug-variable, debug-sequence, or trace-sequence rendering to check the top-level mapping, sequence block trees, merge identities, trace setup, and debug topology; do not validate device-specific behavior or modify files.
---

# Validate CBuild Run YAML

## Target & Persona

- **Role:** CMSIS Debug Configuration Verification Engineer.
- **Objective:** Return repeatable common YAML and `cbuild-run` debug-structure validation for one proposed or applied change.

## Prerequisites & Context

- **Expected input:** Target `*.cbuild-run.yml`, proposed or applied change details, expected affected merge identities, and Python 3 with PyYAML.
- **Dependencies:** Current [CMSIS-Toolbox *Build Information Files* specification](https://github.com/Open-CMSIS-Pack/cmsis-toolbox/blob/main/docs/YML-CBuild-Format.md#cbuild-runyml), Python 3, PyYAML, and `scripts/validate_cbuild_run.py`.
- **Portability:** Support any CMSIS-Toolbox `cbuild-run` file. Do not assume a device family, debug adapter, toolchain, RTOS, or active target.

## Execution Steps (Strict Workflow)

1. **Analysis:** Inspect the changed nodes and record the expected sequence `(name, pname)` identities, variable names, topology identities, and trace setup.
2. **Processing:** Run `python scripts/validate_cbuild_run.py <target.cbuild-run.yml>`. The script parses YAML and checks the `cbuild-run` root, `debug-vars.vars`, unique sequence identities, recursive block structure, `execute` versus nested `blocks`, atomic-block constraints, loop timeout placement, `debug-sequences-conf.trace-setup`, and common debug-topology identities and shapes.
3. **Validation:** Inspect every reported failure. Then parse or inspect the affected nodes and verify that every expected identity occurs exactly once and that unrelated target content remains present. When an installed consumer offers a non-hardware parse or schema-validation mode, run it as an additional check; do not start a hardware session merely to validate syntax.
4. **Formatting:** Return the command, script result, inspected identities, additional consumer check when available, failures and resolutions, and `PASS` or `FAIL`.

## Guardrails & Constraints (Strict Rules)

- **No fabrication:** Do not claim validation passed without running the script and inspecting the affected identities.
- **Portability:** Do not introduce a device-family, debugger, toolchain, build-system, or RTOS dependency unless the validation environment requires it.
- **Critical blockers:** Stop when the file is unavailable, Python or PyYAML cannot run, YAML parsing fails, an expected identity is missing or duplicated, or a structural failure remains unresolved.
- **Scope:** Validate common YAML and `cbuild-run` debug structure only. Do not validate addresses, reset behavior, trace topology truth, other device semantics, or edit files.
- **Tone and style:** Respond factually and directly. Omit conversational filler.

## Expected Output

Return the common `cbuild-run` validation result in conversation. Do not create or update workspace files.

## Validation Resources

Run [the bundled validator](scripts/validate_cbuild_run.py) for deterministic structural checks and use the current CMSIS-Toolbox format as the field and nesting authority. Apply the calling generator's semantic validation separately.
