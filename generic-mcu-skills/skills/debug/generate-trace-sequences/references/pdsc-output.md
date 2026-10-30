# PDSC trace-sequence output

Run `$prepare-pdsc-sequence-change` with `domain=trace`. Use the current Open-CMSIS-Pack Debug Description specification as the XML authority.

Place shared content at the highest selected common device-tree ancestor and only proven deviations on leaves. Maintain one applicable `<debugvars>` element and one `<sequences traceSetup="full">` element. Copy selected canonical assets' child `debugvars` and `sequence` elements, not their standalone wrapper. Render extension markers as XML comments and preserve the exact marker text from the common contract.

Preserve unrelated elements, inheritance, comments, numeric spelling, and sequence order. For legacy or omitted `traceSetup`, follow the migration contract before setting `traceSetup="full"`.

Present exact XML, placement, and affected files for confirmation. Apply through `$apply-confirmed-pdsc-proposal`, validate through `$validate-pdsc-sequence-xml`, and then run:

```text
rg -n 'INSERT-CORESIGHT-SNIPPET-CALLS-HERE' <target.pdsc>
```

Resolve every scaffold-only marker left in active content. Compare all rendered sequences and variables with the common semantic contract and canonical-asset checklist.
