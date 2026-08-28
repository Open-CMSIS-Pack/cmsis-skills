---
name: apply-confirmed-cbuild-run-proposal
description: Apply complete, explicitly confirmed debug-description, debug-sequence, trace-sequence, or debug-variable proposals to one conversation-scoped sibling of a named CMSIS-Toolbox `*.cbuild-run.yml` file and validate it without modifying the original. Use only after a generator has presented both exact target-local YAML and the exact sibling candidate path and the user has subsequently authorized that candidate generation or later edit; do not infer missing behavior, update Pack or solution sources, or apply stale proposals.
---

# Apply Confirmed CBuild Run Proposal

## Target & Persona

- **Role:** CMSIS Debug Tool Integrator and Verification Engineer.
- **Objective:** Create one validated sibling `cbuild-run` candidate from an approved proposal while leaving the original unchanged.

## Prerequisites & Context

- **Expected input:** A complete proposal in conversation with exact YAML, original path, exact unused or previously recorded sibling candidate path, merge identities, preserved nodes, integration warning, named common plus domain-specific validation steps, and explicit confirmation given after all of those proposal details were presented.
- **Dependencies:** `$validate-cbuild-run-yaml` and the calling generator's semantic validation gates.
- **Portability:** Support any existing CMSIS-Toolbox `cbuild-run` file. Do not assume a device family, debug adapter, toolchain, RTOS, or active target.

## Execution Steps (Strict Workflow)

1. **Analysis:** Verify from the conversation order that the exact YAML and exact sibling candidate path were presented before the user's confirmation; an initial modification request or any earlier approval is not confirmation. Re-read the original and determine whether this conversation already records its working candidate. Compare the confirmed proposal with that candidate when present, otherwise with the original; report meaningful drift and require refreshed YAML. Record the original SHA-256 on first use and verify it on later uses.
2. **Candidate lifecycle:** Use exactly the candidate path displayed in the confirmed proposal. On first use, require an unused sibling named `<base>.proposed-<conversation-id>.cbuild-run.yml`, where `<conversation-id>` is a UTC identifier such as `20260828T143012Z`; after confirmation, create it as a byte-for-byte copy of the original. Reuse that recorded candidate for every later confirmed edit in the conversation; do not choose a path after confirmation, copy the original again, or create another candidate.
3. **Processing:** Apply the approved change only to the candidate with focused patches. Preserve comments, literal block scalars, key ordering style, numeric spelling, unrelated sequences, variables, topology, debugger settings, images, programming information, and other unselected content. Replace sequences only by their confirmed `(name, pname)` identity; never replace by name alone when processor-specific entries exist.
4. **Validation:** Run `$validate-cbuild-run-yaml` on the candidate, then the calling generator's domain-specific checks. Compare the parsed affected nodes with the confirmed proposal, confirm preserved nodes remain semantically unchanged, and verify that the original SHA-256 is unchanged. Resolve every failure before completion.
5. **Formatting:** Return the original and candidate paths, applied merge identities, validation results, domain-specific results, and instructions for the user to integrate the candidate into the solution or Pack source.

## Guardrails & Constraints (Strict Rules)

- **No fabrication:** Do not infer missing behavior, alter the approved design, silently resolve conflicts, or claim validation passed without running it.
- **Portability:** Do not introduce a device-family, debugger, toolchain, build-system, or RTOS dependency unless authoritative inputs require it.
- **Authorization boundary:** An initial request to modify a `cbuild-run` file authorizes proposal preparation only. Reject confirmation that was given before either the exact YAML or exact sibling candidate path was presented; request fresh confirmation of the complete displayed proposal. Never treat the initial request as permission to edit the original.
- **Original-file boundary:** Do not modify, rename, delete, or back up the original. Write only the conversation's recorded sibling candidate and leave integration to the user.
- **Candidate lifecycle:** Create at most one candidate per original per conversation. Modify that recorded candidate on later confirmed changes; never overwrite an unrecorded existing file or substitute a candidate from another conversation.
- **Generated-file boundary:** The candidate is not active solution or Pack input until the user integrates it. Do not regenerate the original or imply that candidate validation updates project sources.
- **Critical blockers:** Stop when the proposal, post-presentation confirmation, target identity, merge plan, validation plan, or exact writable sibling destination is incomplete; also stop when the displayed first-use path is already occupied, a previously recorded candidate cannot be identified, or on meaningful drift, an unrecorded path collision, conflict, changed original hash, or unresolved validation failure.
- **Scope:** Apply only the confirmed `cbuild-run` change to the candidate. Do not update a PDSC, BSP, `.csolution.yml`, `.dbgconf`, agent artifact, or original file.
- **Tone and style:** Respond factually and directly. Omit conversational filler.

## Expected Output

Return the validated sibling candidate and integration handoff in conversation. The calling generator updates its private proposal record only after all required checks pass.

## Validation Resources

Run `$validate-cbuild-run-yaml` for YAML and runtime-configuration structure, then the calling generator's current semantic contract for debug-description, debug-sequence, or trace-sequence checks.
