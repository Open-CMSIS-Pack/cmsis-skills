# Device debug-sequence contract

## Scope and evidence

Reuse the read-only `.agent-artifacts/<pdsc-stem>.debug-access-knowledge.md` and `.agent-artifacts/<pdsc-stem>.debug-knowledge.md` records. Cross-check the selected destination, processors, DP/AP/APID mappings, existing sequence identities, and device behavior. Return missing connection facts to `$debug-access-knowledge` and missing behavior facts to `$debug-knowledge`.

Use the current [Open-CMSIS-Pack *Debug Description* specification](https://open-cmsis-pack.github.io/Open-CMSIS-Pack-Spec/main/html/debug_description.html) as the authority for sequence names, execution context, predefined behavior, variables, functions, and C-like expressions. For `cbuild-run`, also use the current [CMSIS-Toolbox *Build Information Files* specification](https://github.com/Open-CMSIS-Pack/cmsis-toolbox/blob/main/docs/YML-CBuild-Format.md#cbuild-runyml) for serialization only.

Assemble a destination-neutral proposal containing sequence name, optional information text, optional processor applicability, and an ordered recursive tree of executable, conditional, loop, and atomic blocks. Keep expression text free of XML escaping until destination rendering. Record every register address, value, delay, condition, call, source, and predefined-default provenance; never invent device behavior.

For verified device unlock behavior, prefer a `DebugDeviceUnlock` implementation that supplements debugger defaults. Override another predefined sequence only when `DebugDeviceUnlock` cannot provide the required documented behavior. Obtain the current default, copy its complete semantic structure, then apply only evidence-backed changes and record each difference.

Implement every evidenced device-specific non-trace behavior in the selected scope or flattened target. For each documented end-user runtime choice, run `$manage-debug-variables`; do not use a variable to defer missing evidence or omit verified behavior.

## Low-power and sleep-mode debug

For each relevant documented mode, determine whether the processor, DP/AP, debug clocks and power, pins, reset, and wake path remain accessible. Use only documented pre-entry, wake, reset, or reconnect actions. Never prevent sleep, force a higher-power mode, or write undocumented registers merely to keep a probe connected.

Record applicability, expected access, required action, affected sequence, evidence, and validation in the private proposal record. When a target is available, enter the mode, check access where supported, then wake or recover it and confirm that the processor and DP/AP path remain usable; otherwise record the required test and documented recovery path.

## CPU applicability

Compare every affected CPU connection, including `pname` and initial `__ap` or `__apid`. Prefer one sequence without processor restriction when connection context is the only difference. Use connection-based dispatch only when the remaining behavior is demonstrably identical; use processor-specific definitions only for a verified difference that cannot be expressed through connection context.

For PDSC placement and XML rules, use `pdsc-output.md`. For flattened target applicability and YAML rules, use `cbuild-run-output.md`.

## Semantic validation

For every overridden predefined sequence, compare the semantic proposal with the current default and record every evidence-backed difference. Confirm every `Sequence("...")` call resolves to a proposed, existing, or predefined identity. Run documented low-power checks when a target is available, or record the required test. Report changed sequence identities, per-CPU applicability, sources, and destination validation.
