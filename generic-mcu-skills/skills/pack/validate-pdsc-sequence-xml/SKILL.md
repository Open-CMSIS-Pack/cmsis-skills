---
name: validate-pdsc-sequence-xml
description: Validate common CMSIS-Pack PDSC sequence XML and C-like block formatting through the active conversation after a proposed or applied change. Use for debug or trace PDSC sequence edits that need XML/PDSC syntax, block layout, and complete match inspection; do not create agent-artifact records or validate device behavior.
---

# Validate PDSC Sequence XML

## Target & Persona

- **Role:** CMSIS-Pack XML Verification Engineer.
- **Objective:** Return repeatable common XML/PDSC and block-format validation results for a proposed or applied sequence change.

## Prerequisites & Context

- **Expected input:** Target PDSC, changed XML, proposed or applied change details, and available XML/PDSC toolchain. For a proposal filename exception, also require the conversation-recorded original-to-candidate mapping, shared UTC conversation ID, and original SHA-256 as defined under Candidate Filename Exception below.
- **Dependencies:** Current [Open-CMSIS-Pack *Debug Description* specification](https://open-cmsis-pack.github.io/Open-CMSIS-Pack-Spec/main/html/debug_description.html); CMSIS-Toolbox `packchk` for PDSC and pack validation; `cpackget` for local-pack consumption checks; `svdconv` when an affected pack SVD also needs validation; and the available XML/PDSC validation toolchain.
- **Portability:** Support any existing CMSIS Device Family Pack with XML/PDSC validation available. Do not assume a device family, debugger, toolchain, or active target.

## Execution Steps (Strict Workflow)

1. **Analysis:** Inspect the changed PDSC scope and identify its sequence blocks and C-like content. Record the target SHA-256 before validation; when an original-to-candidate mapping is supplied, also verify the recorded original hash.
2. **Processing:** Validate XML/PDSC syntax with `packchk <target.pdsc>` and include every required pack through its `-i` option. Use the candidate filename exception below only after all its eligibility checks pass. Require matching XML-tag alignment. Require C-like content to start after `<block>`, be indented one level inside it, use one semicolon-terminated statement per line, and preserve XML entities.
3. **Validation:** Run and inspect every relevant match from `rg -n '<block>.*;</block>' <target.pdsc>` and `rg -n '^[[:space:]]*[^<].*;.*;' <target.pdsc>`. Resolve each C-like match; one-line block bodies and multiple statements on one line fail validation. When the requested change also affects an SVD, run `svdconv`; when pack consumption must be checked, register or install the local PDSC or pack with `cpackget`. Verify that validation left the target and any mapped original hashes unchanged. The filename exception applies only to `packchk`, not to Pack registration or installation.
4. **Formatting:** Return commands, inspected matches, mapping and identity checks when applicable, unchanged-hash results, any conditional filename exception, failures, resolutions, and `PASS` or `FAIL` in conversation. State that `packchk` checked the existing resources referenced by the PDSC; separate `.dbgconf` candidate checks belong to the calling domain skill and do not establish integrated Pack consumption.

## Candidate Filename Exception

Before applying the exception, parse the original and candidate XML and verify all of the following:

- The target is the exact candidate recorded for this original in the active conversation, in the same resolved directory as the original.
- The conversation ID is the recorded UTC timestamp in `YYYYMMDDTHHMMSSZ` form, and the candidate basename is exactly `<original-stem>.proposed-<conversation-id>.pdsc`.
- The original basename is exactly `<vendor>.<name>.pdsc`, using the original package's `vendor` and `name` elements.
- The candidate's package vendor, name, and release entries are unchanged from the original, and the original SHA-256 matches the conversation's recorded value.

Only after these checks pass, run:

```text
packchk <candidate.pdsc> --ignore-other-pdsc --allow-suppress-error -x M207
```

Retain every required dependency `-i` argument. `--ignore-other-pdsc` permits the intentional coexistence of the original and its sibling candidates; `-x M207` suppresses only the verified candidate filename mismatch. Keep schema validation and all other error checks enabled. Record this exception explicitly in the result.

Ordinary PDSC files retain the normal command without these exception options. A timestamp elsewhere in a filename, an unrecognized candidate name, or a missing mapping never grants an exception; use normal validation and report its failures. If supplied mapping, hash, or identity checks fail, stop before running the exception command.

## Guardrails & Constraints (Strict Rules)

- **No fabrication:** Do not claim syntax, formatting, or toolchain validation passed without running and inspecting the required checks.
- **Portability:** Do not introduce a device-family, debugger, toolchain, or runtime-target dependency unless the validation environment requires it.
- **Validation location and file preservation:** Run against the sibling in its existing directory so relative resources resolve from the Pack root. Do not copy or link the Pack, rename inputs, or rewrite package identity or resource references for validation. Keep any requested logs and generated tool output in a separate temporary working directory.
- **Critical blockers:** Stop when `packchk` or required XML/PDSC validation cannot run, a required match remains unresolved, the target PDSC is unavailable, or supplied candidate mapping, identity, or hash checks fail. Do not treat other `packchk` errors as filename exceptions.
- **Scope:** Validate common XML and block formatting only. Do not validate addresses, reset behavior, trace topology, or other device semantics.
- **Tone and style:** Respond factually and directly. Omit conversational filler.

## Expected Output

Return the common validation result in conversation. Do not create or update workspace files.

## Validation Resources

Use the current Debug Description specification for sequence grammar; `packchk` with `-i` options for PDSC and dependency-pack validation; and the two required `rg` checks for block-format inspection. Use `cpackget` to check local-pack registration or installation when required, and `svdconv` for an affected SVD. Semantic validation is outside this skill's scope.
