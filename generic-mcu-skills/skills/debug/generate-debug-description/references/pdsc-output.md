# PDSC debug-description output

Use the current [Open-CMSIS-Pack *Debug Description* specification](https://open-cmsis-pack.github.io/Open-CMSIS-Pack-Spec/main/html/debug_description.html) as the grammar authority.

Render verified connection defaults and topology as inherited or local `debugconfig`, `debug`, `debug-port`, `access-port`, and `dbg_datapatch` definitions. Provide explicit `debugconfig` and `debug` elements for every verified connection model. Add `accessportV1` or `accessportV2` only when required by the verified topology. Preserve PDSC attribute names, numeric spelling conventions, device-tree ordering, and unrelated content.

Place a shared definition at the highest selected common family, subfamily, device, or variant ancestor where it is valid. Place only proven deviations on outer leaf variants. Preserve all `<debugvars>`, `<sequences>`, trace configuration, and unrelated PDSC content. Do not use `__` as a prefix for DFP-defined local sequence variables.

Present exact XML and placement for confirmation, then run `$apply-confirmed-pdsc-proposal`. Validate with `$validate-pdsc-sequence-xml`; for a non-sequence-only change, record that no C-like block content was introduced and inspect every relevant file-wide match returned by the validator.
