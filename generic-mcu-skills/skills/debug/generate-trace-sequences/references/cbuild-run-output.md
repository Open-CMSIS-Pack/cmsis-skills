# CBuild Run trace-sequence output

Run `$prepare-cbuild-run-change` with `domain=trace`. Treat the destination as one flattened runtime target and use the current CMSIS-Toolbox `cbuild-run` format as the YAML authority.

Translate the selected canonical XML asset and scaffold children as follows:

| Canonical construct | `cbuild-run` representation |
| --- | --- |
| `<debugvars>` C-like content | `debug-vars.vars` literal scalar |
| `<sequence name="..." info="..." Pname="...">` | `debug-sequences[]` item with `name`, optional `info`, optional `pname`, and `blocks` |
| `<block>` C-like text | `execute` literal scalar on one block item |
| `<block atomic="true">` | `atomic:` plus `execute` on one block item |
| `<control if/while/info/timeout>` | block item with the corresponding fields and nested `blocks` |
| `<sequences traceSetup="full">` | `debug-sequences-conf.trace-setup: full` |
| XML comments and extension markers | YAML comments at the corresponding sequence or block-list position |

Preserve the C-like semantics during translation. Use the destination's established entity convention; otherwise render raw C-like operators because YAML does not require XML escaping. Never combine `execute` with nested `blocks`, or `atomic` with nested `blocks`. Merge sequences by `(name, pname)` and variables by name. Preserve unrelated sequences, variables, topology, debugger settings, images, programming data, comments, literal scalar style, numeric spelling, and root-node order.

Ensure `debug-topology.trace-sinks` already identifies every selected physical sink, or include exact evidence-backed additions in the same confirmed trace proposal. Merge trace-sink entries by their format-defined identity and never infer topology from selected sequence assets alone.

For legacy or omitted `debug-sequences-conf.trace-setup`, follow the migration contract before setting `trace-setup: full`. Render the common extension markers as raw YAML comments without changing their text.

Treat the initial request to modify the `cbuild-run` file as authorization to prepare this proposal only. Select an unused sibling path named `<base>.proposed-<conversation-id>.cbuild-run.yml`; present that exact path with the exact YAML and merge identities before requesting confirmation. Only a subsequent user response can confirm that displayed proposal. Apply through `$apply-confirmed-cbuild-run-proposal`, which may write only the displayed sibling candidate and must leave the original unchanged, validate the candidate through `$validate-cbuild-run-yaml`, and then run:

```text
rg -n 'INSERT-CORESIGHT-SNIPPET-CALLS-HERE' <candidate.cbuild-run.yml>
```

Resolve scaffold-only markers in active content, verify empty-operation comments, and compare every rendered sequence, variable, and trace-sink entry with the common semantic contract and canonical-asset checklist. State that later CMSIS-Toolbox regeneration may overwrite the target-local change.
