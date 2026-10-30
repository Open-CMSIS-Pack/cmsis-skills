---
name: apply-confirmed-cbuild-run-proposal
description: Write complete debug-description, debug-sequence, trace-sequence, or debug-variable proposals to one conversation-scoped sibling of a named CMSIS-Toolbox `*.cbuild-run.yml` file and validate it without modifying the original. Use when a generator has rendered exact target-local YAML and selected the exact sibling proposal path; the initial modification request authorizes this proposal write without additional confirmation, but not integration into active project or Pack sources.
---

# Write CBuild Run Proposal

## Target & Persona

- **Role:** CMSIS Debug Tool Integrator and Verification Engineer.
- **Objective:** Create one validated sibling `cbuild-run` proposal while leaving the original unchanged.

## Prerequisites & Context

- **Expected input:** A complete rendered proposal with exact YAML, original path, exact unused or previously recorded sibling path, merge identities, preserved nodes, integration warning, and named common plus domain-specific validation steps.
- **Dependencies:** `$validate-cbuild-run-yaml` and the calling generator's semantic validation gates.
- **Portability:** Support any existing CMSIS-Toolbox `cbuild-run` file. Do not assume a device family, debug adapter, toolchain, RTOS, or active target.

## Execution Steps (Strict Workflow)

1. **Analysis:** Re-read the original and determine whether this conversation already records its working sibling proposal. Compare the rendered proposal with that sibling when present, otherwise with the original; report meaningful drift and require refreshed YAML. Record the original SHA-256 on first use and verify it on later uses.
2. **Candidate lifecycle:** Use exactly the sibling path selected by the generator. On first use, require an unused sibling named `<base>.proposed-<conversation-id>.cbuild-run.yml`, where `<conversation-id>` is a UTC identifier such as `20260828T143012Z`, and create it as a byte-for-byte copy of the original without requesting additional approval. Reuse that recorded sibling for every later proposal edit in the conversation; do not copy the original again or create another candidate.
3. **Processing:** Apply the rendered change only to the sibling with focused patches. Preserve comments, literal block scalars, key ordering style, numeric spelling, unrelated sequences, variables, topology, debugger settings, images, programming information, and other unselected content. Replace sequences only by their proposed `(name, pname)` identity; never replace by name alone when processor-specific entries exist.
4. **Validation:** Run `$validate-cbuild-run-yaml` on the sibling, then the calling generator's domain-specific checks. Compare the parsed affected nodes with the rendered proposal, confirm preserved nodes remain semantically unchanged, and verify that the original SHA-256 is unchanged. Resolve every failure before completion.
5. **Formatting:** Return the original and candidate paths, applied merge identities, validation results, domain-specific results, and instructions for the user to integrate the candidate into the solution or Pack source.

## Guardrails & Constraints (Strict Rules)

- **No fabrication:** Do not infer missing behavior, alter the rendered design, silently resolve conflicts, or claim validation passed without running it.
- **Portability:** Do not introduce a device-family, debugger, toolchain, build-system, or RTOS dependency unless authoritative inputs require it.
- **Authorization boundary:** The initial request to modify a `cbuild-run` file authorizes creating or updating this conversation-scoped sibling proposal; do not request separate approval for that write. The historical skill ID does not impose a confirmation gate. The request never authorizes modifying the original or integrating the sibling into active project or Pack sources.
- **Original-file boundary:** Do not modify, rename, delete, or back up the original. Write only the conversation's recorded sibling candidate and leave integration to the user.
- **Candidate lifecycle:** Create at most one sibling proposal per original per conversation. Modify that recorded sibling on later requested proposal changes; never overwrite an unrecorded existing file or substitute a candidate from another conversation.
- **Generated-file boundary:** The candidate is not active solution or Pack input until the user integrates it. Do not regenerate the original or imply that candidate validation updates project sources.
- **Critical blockers:** Stop when the rendered proposal, target identity, merge plan, validation plan, or exact writable sibling destination is incomplete; also stop when the selected first-use path is already occupied, a previously recorded candidate cannot be identified, or on meaningful drift, an unrecorded path collision, conflict, changed original hash, or unresolved validation failure. Missing confirmation is not a blocker for writing the sibling proposal.
- **Scope:** Apply only the rendered `cbuild-run` proposal to the sibling. Do not update a PDSC, BSP, `.csolution.yml`, `.dbgconf`, agent artifact, original file, or active integration source.
- **Tone and style:** Respond factually and directly. Omit conversational filler.

## Expected Output

Return the validated sibling candidate and integration handoff in conversation. The calling generator updates its private proposal record only after all required checks pass.

## Validation Resources

Run `$validate-cbuild-run-yaml` for YAML and runtime-configuration structure, then the calling generator's current semantic contract for debug-description, debug-sequence, or trace-sequence checks.
