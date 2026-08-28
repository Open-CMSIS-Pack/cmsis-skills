# Trace sequence assembly contract

## Shared integration ownership

Use `.agent-artifacts/<pdsc-stem>.trace-knowledge.md` from `$trace-knowledge` as read-only input. Consult `.agent-artifacts/<pdsc-stem>.debug-access-knowledge.md` from `$debug-access-knowledge` only when implementation requires a processor, debug connection, DP/AP path, protocol, or dormant-state fact not supplied by the trace record. Run `$manage-debug-variables` for documented runtime choices. The selected output contract owns preparation, rendering, application, and common validation.

Use the current [Open-CMSIS-Pack *Debug Description* specification](https://open-cmsis-pack.github.io/Open-CMSIS-Pack-Spec/main/html/debug_description.html) as the sequence-language authority. Its `Sequence("name")` function calls another debug access sequence, and a supplied predefined sequence replaces the debugger-provided behavior. Use the current [CMSIS-Toolbox *Build Information Files* specification](https://github.com/Open-CMSIS-Pack/cmsis-toolbox/blob/main/docs/YML-CBuild-Format.md#cbuild-runyml) for YAML field and nesting rules.

## Required semantic output

Always generate full trace setup: the emitted sequences configure each selected trace sink and data path rather than relying on debugger a-priori CoreSight configuration. Trace setup is device-level by default. Unless the user narrows scope, cover all processors and all evidence-backed trace paths in the selected PDSC subtree or flattened `cbuild-run` target.

Configure every evidenced path by default. When an end-user choice is documented, emit or update a debug variable with a supported default. For PDSC output, also propose matching Configuration Wizard annotations in `.dbgconf`; do not edit `.dbgconf` without explicit confirmation.

Preserve these extension markers exactly in the destination representation defined by the output contract:

```text
CMSIS-PACK-TRACE: ADD-DEVICE-SPECIFIC-HERE BEGIN
CMSIS-PACK-TRACE: ADD-DEVICE-SPECIFIC-HERE END
CMSIS-PACK-TRACE: INSERT-CORESIGHT-SNIPPET-CALLS-HERE
```

The `ADD-DEVICE-SPECIFIC-HERE` pair remains around user-maintained work. The single CoreSight insertion marker is scaffold-only and must be removed after selected component calls replace it. Do not add redundant CoreSight begin/end wrappers.

The markers establish this order:

```text
TraceStart:   device-specific region -> mode-specific CoreSight start helpers
TraceCapture: DoTraceFlush -> device-specific region -> mode-specific CoreSight capture helpers
TraceFlush:   mode-specific CoreSight flush/read helpers -> device-specific region
TraceStop:    mode-specific CoreSight stop helpers -> device-specific region
```

Enable trace clocks in `DebugDeviceUnlock` before auto-detection unless evidence or explicit direction requires otherwise. Also configure trace clocks in the device-specific region of `TraceStart`, before CoreSight start helpers, because unlock-time clock state may not survive reset.

`TraceCapture` calls `DoTraceFlush` exactly once before preparing any components for the next capture. Component capture sequences must not call `DoTraceFlush`; otherwise, a multi-component route is flushed repeatedly while it is being reconfigured. The debugger calls `TraceFlush` before `TraceStop`. A verified sequence may reuse `DoTraceFlush_<mode>`, but `TraceStop` and `DoTraceStop_<mode>` must not call `DoTraceFlush` or a `DoTraceFlush_<mode>` helper again.

## Component selection and placement

Map the selected target, its processors, and every evidence-backed trace path. For PDSC, group descendants with identical verified configuration at their topmost selected common ancestor and put only proven deviations on leaves. For `cbuild-run`, emit only the flattened target and its processors.

Select one canonical XML asset per required physical CoreSight instance. Omit unused assets, variables, and calls. Merge every selected asset's variable contribution through `$manage-debug-variables`; identical names require identical meaning and value, otherwise stop for direction.

Number non-predefined sequences by component type from `0` in ascending verified base-address order while preserving existing numbers: `CS_<COMPONENT>_0_*`, `CS_<COMPONENT>_1_*`, and so on. Use `CS_<COMPONENT>_<instance>_<operation>[_<subvariant>]`, and rename every sequence and `Sequence("...")` call consistently.

## Standard component-operation routing

Call a component operation only from the helper for its active mode:

| Operation | Helper destination | Applies to |
| --- | --- | --- |
| `Configure` | `DoTraceStart_<mode>` | Active path only |
| `Capture` | `DoTraceCapture_<mode>` | Active path only |
| `Flush` | `DoTraceFlush_<mode>` | Active path only; never call top-level `TraceFlush` from a helper |
| `ReadBuffer` | `DoTraceRead_Buffer` after `DoTraceFlush` | Trace-buffer path only |

For start and capture, call operations in route order: funnels, other glue such as ETF hardware-FIFO mode, then the sink or output component.

| Trace mode | Applicable component route |
| --- | --- |
| SWO | Funnels, then a standalone SWO component or Cortex-M TPIU in SWO mode. |
| Sync | Funnels, applicable glue, then the synchronous TPIU trace port. |
| Trace buffer | Funnels, applicable glue, then the verified ETB, circular-buffer ETF, ETR, or other buffer sink. |

Do not emit a call merely because an asset exists. A verified non-standard component role may be called from the applicable device-specific region; exclude it from the standard helper path so it is not operated twice.

## Canonical asset fidelity

The XML assets are canonical semantic templates for both output formats. Their wrapper exists only to make each asset well-formed; never copy the wrapper. Resolve instance suffixes, component base addresses/APs, selected calls, and routing only from evidence. The output contract translates the selected child elements without maintaining parallel hand-edited YAML assets.

A user-provided snippet or selected asset is the behaviorally fixed source template for its operations unless the deviation gate below is completed. Retain its comments, `__var` declarations, checks, controls, waits, cleanup, register-operation order, and sequence bodies. Without confirmed deviation, permitted adaptations are limited to evidence-backed parameter values, consistent instance suffixes and call names, placement in the scaffold, and representation-preserving XML/YAML syntax. Do not handwrite a shorter replacement or change functional logic without that confirmation.

Determine technical suitability before rendering. If the destination, evidence, or required lifecycle would require changing control flow, register operations or ordering, checks, waits, cleanup, sequence lifecycle, or any other functional behavior, present a deviation request containing the exact conflict, supporting evidence, affected original snippet region, exact proposed replacement or diff, and semantic impact. Stop before rendering until the user explicitly confirms that displayed deviation. The initial request, an earlier approval, or a general instruction to complete the destination change is not deviation confirmation.

After confirmation, apply only the displayed deviation; any additional functional change requires a new deviation request and confirmation. Record the confirmed deviation and its evidence in `.agent-artifacts/<destination-stem>.trace-sequences.md`, render the complete XML or YAML proposal, and obtain the normal destination confirmation separately. For `cbuild-run`, deviation confirmation never replaces the requirement to present and confirm the exact rendered YAML and sibling candidate path.

In `.agent-artifacts/<destination-stem>.trace-sequences.md`, record a line-level merge checklist for each snippet or asset and identify the permitted adaptations plus every explicitly confirmed deviation. Compare rendered output against the source snippet after normalizing approved suffixes, parameter values, placement, representation syntax, and confirmed deviations; any other semantic difference fails the fidelity gate.

## Structure and lifecycle gates

Start from `assets/scaffolds/full-trace.xml`. Preserve every required top-level sequence and applicable `DoTrace*_<mode>` helper, including its opening trace-mode variable block. Follow `references/legacy-to-full-migration.md` for legacy destinations. Do not flatten or inline helpers.

Put each routing sequence's `__var` declarations before executable statements. `TraceStart`, `TraceCapture`, `DoTraceFlush`, `TraceFlush`, `TraceStop`, and their mode helpers begin with `swoTrace`, `syncTrace`, and `bufferTrace` derived from `__traceout`; component sequences declare only variables they use.

When a scaffold sequence contains no C-like content after its standard mode variables, retain a representation-appropriate `No trace operation is required for this mode.` comment. A scaffold-only insertion marker may follow it; remove both when an operation is added.

Do not invent addresses, values, routes, timestamp settings, formatter settings, component order, or dormant-state requirements. Honor the trace record's dormant decision or obtain it from `$debug-access-knowledge` when required.

Write `.agent-artifacts/<destination-stem>.trace-sequences.md` at the project root. Record destination format and path, selected scope, placement or merge identities, component instances, emitted names, extension markers, sources, asset merge checklists, regeneration risk, and validation. Add a `Documents requiring user download` table when required evidence cannot be retrieved.

Agent artifacts may be updated without confirmation. Before changing an existing PDSC, `cbuild-run`, `.dbgconf`, or other user-owned file, present the exact proposal and obtain confirmation. After confirmation, apply and validate the complete change in the same turn. Stop on missing evidence, drift, conflicts, or validation failure rather than emitting a partial sequence set.
