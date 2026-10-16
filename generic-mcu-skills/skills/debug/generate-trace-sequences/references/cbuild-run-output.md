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

Ensure `debug-topology.trace-sinks` already identifies every selected physical sink, or include exact evidence-backed additions in the same trace proposal. Merge trace-sink entries by their format-defined identity and never infer topology from selected sequence assets alone.

For legacy or omitted `debug-sequences-conf.trace-setup`, follow the migration contract before setting `trace-setup: full`. Render the common extension markers as raw YAML comments without changing their text.

Select the exact sibling path and render the exact YAML and merge identities, then run `$apply-confirmed-cbuild-run-proposal`. That application skill owns authorization handling, candidate lifecycle, original-file protection, common validation, and the integration boundary. Present its validated sibling path and the exact YAML with the completed proposal, then run:

```text
rg -n 'INSERT-CORESIGHT-SNIPPET-CALLS-HERE' <candidate.cbuild-run.yml>
```

Resolve scaffold-only markers in active content. Compare every rendered sequence, variable, and trace-sink entry with the common semantic contract and canonical-asset checklist. Report the regeneration risk returned by the application skill.
