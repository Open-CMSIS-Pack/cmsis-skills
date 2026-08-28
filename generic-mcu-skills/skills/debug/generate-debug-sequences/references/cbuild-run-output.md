# CBuild Run debug-sequence output

Run `$prepare-cbuild-run-change` with `domain=debug`. Treat the file as one flattened runtime target and merge each sequence by `(name, pname)`. Never apply PDSC family inheritance or replace all processor-specific entries by name alone.

Render the semantic tree under `cbuild-run.debug-sequences`:

- Map sequence `name`, optional information, and optional processor applicability to `name`, `info`, and `pname`.
- Map each executable block to `- execute: |` and preserve its C-like semantics. Use the destination's established entity convention; otherwise render raw C-like operators because YAML does not require XML escaping.
- Map a conditional or loop node to a block item with `if` or `while`, optional `info` and `timeout`, and nested `blocks`.
- Map atomic execution to an executable block containing `atomic:` and `execute: |`; do not combine `atomic` with nested `blocks`.
- Keep ordered blocks in their semantic order and use literal scalars for command text.

Merge variable declarations through `$manage-debug-variables` into the single `cbuild-run.debug-vars.vars` literal scalar. Preserve unrelated sequences, variables, topology, debugger settings, output images, programming information, comments, numeric spelling, and root-node order.

Treat the initial request to modify the `cbuild-run` file as authorization to prepare this proposal only. Select an unused sibling path named `<base>.proposed-<conversation-id>.cbuild-run.yml`; record and present that exact path with the exact YAML and merge identities before requesting confirmation. Only a subsequent user response can confirm that displayed proposal. Then run `$apply-confirmed-cbuild-run-proposal`, which may write only the displayed sibling candidate and must leave the original unchanged, followed by `$validate-cbuild-run-yaml` on the candidate. Compare parsed sequence identities, block tree, expression text after normalizing any preserved XML entities, and variables with the semantic proposal. State that CMSIS-Toolbox regeneration may overwrite a later integration of the target-local change.
