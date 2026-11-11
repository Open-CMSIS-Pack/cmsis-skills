---
name: identify-cmsis-board-support
description: Resolve a supplied board or device to exactly one verified CMSIS identity, identify its BSP or DFP, and ask the user when multiple candidates remain. Use when a CMSIS solution needs verified board, device, and pack identifiers.
---

# Identify CMSIS Board Support

## Target & Persona

- **Role:** CMSIS Pack Integrator
- **Objective:** Resolve the requested board or device to exactly one verified board and fitted device, or exactly one device for device-only input, and identify its CMSIS support pack.

## Prerequisites & Context

- **Expected input:** A user-supplied board or device name, which may be fuzzy. Manufacturer, board revision, and fitted MCU or SoC evidence should be included when available.
- **Dependencies:** Access to CMSIS catalog data through the CMSIS Developer Assistant tool `cmsis_query` when available, or the Keil Boards and Devices catalogs. An active CMSIS-Toolbox environment is optional for installed-pack cross-checks.
- **Portability:** Applies across MCU and SoC vendors when their board or device is represented in the referenced catalogs. It has no compiler, RTOS, debugger, or probe dependency.

Collect when available:

- physical board manufacturer, model, and revision;
- exact fitted MCU or SoC from authoritative board information.

An `identify-zephyr-board` result provides suitable input for a Zephyr-supported
board, but this skill does not depend on Zephyr.

## Execution Steps (Strict Workflow)

1. **Analysis:** Determine whether the input requests a physical board or a device, then collect every plausible exact identity from authoritative information.
2. **Processing:** Resolve each required identity using the tool path below or the catalog fallback. For board input, establish both the BSP when available and the fitted device's DFP.
3. **Validation:** Check catalog results against the available authoritative board/device evidence and resolve every required identity before accepting support. Catalog membership alone does not verify a physical board or its fitted device.
4. **Formatting:** Return the defined `BSP`, `DFP`, `AMBIGUOUS`, or `NO MATCH` result with exact identifiers, candidates when applicable, and catalog provenance.

### Optional catalog tool

When the CMSIS Developer Assistant tool `cmsis_query` is available, use it
before manual catalog searches, or reuse a supplied result matching the
requested board/device and revision. It reads the CMSIS Solution catalog (web
and installed packs) and requires no existing project or debug session. Start
with only `what` and the literal supplied name. In the examples below, replace
the placeholder with the supplied name verbatim; never send the placeholder
itself. For board input:

```json
{"what":"boards","name":"<literal user-supplied board name>"}
```

For device-only input, and for each device of a resolved board:

```json
{"what":"devices","name":"<device name>"}
```

`name` and `vendor` are case-insensitive regular expressions; `name` is tried
against an entry's name and its id, and an unanchored pattern matches every
entry that contains it. Escape regular-expression metacharacters of a literal
name. Omit unknown optional fields. Never use guesses, empty strings,
`unspecified`, or catch-all patterns such as `.*`. Add `vendor` only when
supplied or independently verified. For board input, pass `device` (a pattern
for a device the board carries) only when independently established. The tool
has no revision or processor argument: a board `id` carries the revision
(`<vendor>::<name>:<revision>`), and a device entry's `cores` names the cores,
with the processor names of a multi-core device. A request to use the board as
a project target means report remaining device/processor choices, not guess
filters to resolve them. Use an unanchored pattern only to obtain candidates
for a fuzzy name, then confirm an exact identity, for example with
`^<exact name>$`, before accepting support.

Before accepting a result, check the actual call arguments against the supplied
or verified facts. If a call included an unsupported or guessed filter, its
result does not answer the intended query. Make at most one corrected request,
omitting that filter. If that attempt fails to express the intended query, stop
and report the invocation problem with the actual arguments and relevant
response. Do not repeat the same request, or treat this as a catalog miss that
justifies a public-catalog fallback.

- `status: running`: the catalog is still loading. Repeat the same call; this
  is not a catalog miss.
- `total: 1`: reuse the returned `id` and `pack` without repeating completed
  lookups. A board entry gives the BSP in `pack` and the devices the catalog
  lists for the board in `devices`; a device entry gives the DFP in `pack`.
  After the required physical-board evidence and identity checks, return `BSP`
  when both packs are established, or `DFP` for DFP-only support. Report
  whether the packs are shared or separate.
- `total` greater than 1: retain the choices and ask the user to resolve them.
  When `omitted` is not 0 the list is truncated (20 entries by default, `limit`
  up to 100) and is not the complete set; never select its first entry.
- `total: 0`, an entry without `pack` or `devices`, or a failed call: use the
  fallback below for missing facts. Preserve the reported message. If support
  still cannot be established, return `NO MATCH` with the missing fact or
  retrieval failure; this does not assert that no CMSIS support exists.

The result is catalog evidence, not physical-board verification. A board
entry's `devices` do not prove which device is fitted. Catalog completeness is
unknown; results do not establish global absence or uniqueness. Cite the tool
and its returned exact identifiers as provenance; it supplies no catalog URLs,
so do not invent them.

### Catalog fallback

1. Define the identities that must be unique:
   - for board input, one exact physical board model/revision and one exact fitted
     CMSIS device `Dname`;
   - for device-only input, one exact CMSIS device `Dname`.
2. For board input, search the [Keil Boards catalog](https://www.keil.arm.com/boards/)
   and authoritative manufacturer information using the supplied manufacturer,
   model, revision, and device terms. Keep all plausible board models or revisions;
   do not select the first, closest, or locally installed result.
3. Normalize and de-duplicate candidates by exact board identifier, including its
   revision. If more than one plausible board remains, return `AMBIGUOUS`, list
   the exact candidates and distinguishing details, and ask the user to choose.
   If the physical board cannot be established, return `NO MATCH`.
4. Accept a BSP match only when its detail page identifies the uniquely selected
   physical board and fitted device. Record the exact CMSIS board identifier,
   CMSIS device identifier, and BSP pack identifier. A uniquely identified board
   without a BSP may still continue to DFP lookup for its authoritative fitted device.
5. Search the [Keil Devices catalog](https://www.keil.arm.com/devices/)
   using the fitted device for board input or the supplied device terms for
   device-only input. Include this search when a matching BSP was found.
6. Normalize and de-duplicate device candidates by exact CMSIS `Dname`. Multiple
   processor `Pname` entries belonging to the same `Dname` are one device identity
   unless the requested target must select a processor. If more than one plausible
   `Dname` or required processor remains, return `AMBIGUOUS`, list the exact
   candidates and distinguishing details, and ask the user to choose. If no device
   can be established, return `NO MATCH`.
7. Accept a DFP match only when the vendor, device or supported device pattern,
   processor/core, and family are compatible. Record the exact CMSIS device
   identifier and DFP pack identifier.
8. When the CMSIS-Toolbox environment is active, cross-check installed packs
   with `csolution list boards --filter <terms>` or
   `csolution list devices --filter <terms>`. Installed-pack results are supporting
   evidence only: they may be a subset of the online catalog and therefore cannot
   establish uniqueness or eliminate other candidates. An empty local result does
   not prove that the online catalog lacks a BSP or DFP.

Return `BSP` or `DFP` only after every required identity resolves to exactly one
choice. Prefer the matching BSP over a DFP-only result. Never silently choose
among plausible candidates.

## Guardrails & Constraints (Strict Rules)

- **No fabrication:** Do not invent CMSIS board, device, BSP, or DFP identifiers, and do not infer support from a similar part name.
- **Portability:** Do not add vendor, toolchain, RTOS, debugger, or probe assumptions beyond the verified catalog result.
- **Exactly-one gate:** Do not return a usable support result unless every required board/device identity resolves to exactly one choice. For multiple choices, ask the user to select from the exact candidates before continuing.
- **Critical blockers:** Stop when a required identity has no authoritative match, neither catalog match is established, or the user has not resolved an `AMBIGUOUS` result.
- **Scope:** Identify CMSIS support only; do not install packs, create a project, or configure hardware.
- **Tone and style:** Respond factually and directly. Omit conversational filler.

## Expected Output

Report:

- status: `BSP`, `DFP`, `AMBIGUOUS`, or `NO MATCH`;
- physical board and fitted device used for the lookup;
- exact CMSIS board identifier when status is `BSP`;
- exact CMSIS device identifier;
- exact BSP pack identifier when status is `BSP`;
- exact DFP pack identifier for the fitted device; when status is `BSP`, report
  whether it is the same pack as the BSP or a separate pack;
- for a project target, any remaining device or processor choice, with exact
  returned identifiers; never invent a processor name for an unnamed entry;
- catalog provenance: supporting URLs when retrieved, or the catalog tool
  name and exact returned identifiers, with relevant notes;
- for `AMBIGUOUS`, the exact candidate board identifiers or device `Dname` values,
  their distinguishing manufacturer/revision/device details and provenance,
  followed by one focused question asking the user to choose;
- the missing identity, mismatch or retrieval failure when status is `NO MATCH`;
  this status means support was not established from the available evidence.

Do not invent CMSIS identifiers, infer support from similar part names, or treat an
empty installed-pack query as proof that no online pack exists.

## Validation Resources

- [Keil Boards catalog](https://www.keil.arm.com/boards/)
- [Keil Devices catalog](https://www.keil.arm.com/devices/)
- CMSIS-Toolbox `csolution list boards` and `csolution list devices` commands
