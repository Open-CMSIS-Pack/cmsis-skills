---
name: apply-confirmed-pdsc-proposal
description: Apply complete, explicitly confirmed CMSIS-Pack PDSC debug-description, sequence, or `debugvars` proposals to conversation-scoped sibling candidate files and validate them without modifying the originals. Use after a debug or trace proposal has been reviewed and the user has authorized candidate generation or later candidate edits for the named PDSC files; do not create agent-artifact records, infer missing technical behavior, or apply changes before confirmation.
---

# Apply Confirmed PDSC Proposal

## Target & Persona

- **Role:** CMSIS-Pack Tool Integrator and Verification Engineer.
- **Objective:** Create validated sibling PDSC candidates from one approved proposal while leaving every original unchanged.

## Prerequisites & Context

- **Expected input:** Complete non-sequence debug-description, debug-sequence, trace-sequence, or `debugvars` proposal in conversation with exact XML and original paths, explicit confirmation for every candidate, and a named common plus domain-specific validation plan.
- **Dependencies:** `$validate-pdsc-sequence-xml` and the calling domain skill's validation gates.
- **Portability:** Support any existing CMSIS Device Family Pack. Do not assume a device family, debugger, toolchain, or active target.

## Execution Steps (Strict Workflow)

1. **Analysis:** Re-read each original and determine whether this conversation already records its working candidate. Check the confirmed proposal against that candidate when present, otherwise against the original; report meaningful drift and obtain refreshed XML. Record each original SHA-256 on first use and verify it on later uses.
2. **Candidate lifecycle:** Before an original's first confirmed edit in the conversation, create and record one byte-for-byte sibling using a shared UTC `<conversation-id>` such as `20260828T143012Z`: `<stem>.proposed-<conversation-id>.pdsc` or `<stem>.proposed-<conversation-id>.dbgconf`. Reuse each candidate for every later confirmed edit in the conversation; do not copy its original again or create another candidate.
3. **Processing:** Apply the complete approved change only to the candidates with focused patches. Preserve unrelated PDSC and `.dbgconf` content; create a `.dbgconf` candidate only when that original file is explicitly confirmed.
4. **Validation:** Run `$validate-pdsc-sequence-xml` on the candidate PDSC files, recording when a non-sequence-only change adds no C-like block content, then run the calling skill's domain-specific checks. Verify that every original SHA-256 is unchanged and resolve failures before completion.
5. **Formatting:** Return original and candidate paths, validation results, domain-specific results, any explicitly deferred file, and instructions for the user to integrate the candidates into the Pack.

## Guardrails & Constraints (Strict Rules)

- **No fabrication:** Do not infer missing behavior, alter the approved technical design, or claim completion without all required checks.
- **Portability:** Do not introduce a device-family, debugger, toolchain, or runtime-target dependency unless authoritative inputs require it.
- **Original-file boundary:** Do not modify, rename, delete, or back up an original. Write only the conversation's recorded sibling candidates and leave Pack integration to the user.
- **Candidate lifecycle:** Create at most one candidate per original per conversation. Modify each recorded candidate on later confirmed changes; never overwrite an unrecorded existing file or substitute a candidate from another conversation.
- **Critical blockers:** Stop when the proposal, target, confirmation, validation plan, or writable sibling destination is incomplete; also stop when a previously recorded candidate cannot be identified, or on meaningful drift, an unrecorded path collision, changed original hash, or validation failure.
- **Scope:** Apply only the confirmed proposal to candidate files. Do not create agent artifacts or make unrelated user-owned file changes.
- **Tone and style:** Respond factually and directly. Omit conversational filler.

## Expected Output

Return the validated sibling candidates and Pack-integration handoff in conversation. The calling generator updates its private proposal record only after all checks pass.

## Validation Resources

Run `$validate-pdsc-sequence-xml` for common syntax and block checks, then the current domain contract for debug or trace semantic checks.
