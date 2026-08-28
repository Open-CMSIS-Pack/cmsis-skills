# CBuild Run debug-description output

Use the current [CMSIS-Toolbox *Build Information Files* specification](https://github.com/Open-CMSIS-Pack/cmsis-toolbox/blob/main/docs/YML-CBuild-Format.md#cbuild-runyml) as the YAML structure authority. Run `$prepare-cbuild-run-change` with `domain=description` before rendering.

Treat the file as one flattened runtime target. Do not reproduce PDSC family inheritance, device-tree placement, or definitions for devices and processors outside the target. Require its `device`, optional `device-pack`, and processor identities to agree with the knowledge record.

Map only documented equivalents:

| Semantic definition | `cbuild-run` destination |
| --- | --- |
| Selected debug protocol and clock | The explicitly selected `debugger` entry's `protocol` and `clock` |
| SWJ and dormant behavior | `debug-topology.swj` and `debug-topology.dormant` |
| Debug port and JTAG/SWD selection | `debug-topology.debugports[]`, keyed by `dpid` |
| APv1/APv2 access path | Nested `accessports[]`, keyed by `apid`, using `index` or `address` as documented |
| AP protection properties | The selected access port's `HPROT` and `SPROT` |
| Processor-to-AP and reset mapping | `debug-topology.processors[]`, keyed by `pname` |
| Data patch | The selected access port's `datapatch[]` |

Do not choose a debugger entry when multiple candidates remain, and do not map a PDSC-only attribute when the current `cbuild-run` format has no documented equivalent. Preserve all unrelated root nodes and existing list entries.

Select the exact sibling path and render the exact YAML and merge identities, then run `$apply-confirmed-cbuild-run-proposal`. That application skill owns authorization handling, candidate lifecycle, original-file protection, common validation, and the integration boundary. Present its validated sibling path and the exact YAML with the completed proposal. Compare every affected `dpid`, `apid`, `pname`, debugger field, and patch with the semantic definition set, and report the regeneration risk returned by the application skill.
