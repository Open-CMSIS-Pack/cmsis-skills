# PDSC debug-sequence output

Run `$prepare-pdsc-sequence-change` with `domain=debug`. Place shared definitions at the highest selected common device-tree ancestor and only proven deviations on outer leaf variants. Merge variable contributions through `$manage-debug-variables` into the one applicable `<debugvars>` element.

Render each semantic sequence as `<sequence name="...">` with optional `info` and `Pname`. Render executable blocks as `<block>`, atomic execution with the supported PDSC atomic form, and conditional or loop nodes as `<control>` with `if`, `while`, `timeout`, and `info` attributes as applicable. XML-escape C-like operators and strings exactly once. Preserve one semicolon-terminated statement per line and the file's indentation style.

Preserve unrelated PDSC content and all trace configuration. Suggest matching `.dbgconf` Configuration Wizard annotations for new user variables, but do not edit `.dbgconf` without explicit confirmation.

Record exact XML and placement in the private proposal, obtain confirmation, then run `$apply-confirmed-pdsc-proposal` and `$validate-pdsc-sequence-xml`. Compare parsed sequence names, `Pname` applicability, block order, expressions, and variable declarations with the semantic proposal.
