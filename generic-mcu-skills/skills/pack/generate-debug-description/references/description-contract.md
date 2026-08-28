# Non-sequence debug-description contract

Use `.agent-artifacts/<pdsc-stem>.debug-access-knowledge.md` from `$debug-access-knowledge` as read-only input. Never create, update, or feed rendered PDSC or `cbuild-run` implementation details back into that record.

## Semantic definition set

Translate only verified access knowledge into a destination-neutral set containing the selected connection model, protocol and clock defaults, SWJ and dormant behavior, debug ports, access ports, processor-to-AP mappings, reset-sequence selection when documented, and data patches. Preserve stable `dpid`, `apid`, and `pname` identities.

Omit optional topology entries that merely restate a documented format default unless the selected destination already expresses them or an explicit definition is required for the verified topology. Include an APv1, APv2, or mixed design only when evidence requires it. Apply dormant behavior only when the knowledge record contains device-specific evidence.

Include every verified data patch with its parent access port, address, value, mask, access type, applicability, information text, and workaround evidence. Do not generate or update debug variables or sequences. Do not use a missing hardware fact or runtime choice to omit an evidenced definition.

## Destination selection

Require one explicit existing destination. Use `pdsc-output.md` for a `.pdsc`; use `cbuild-run-output.md` for `*.cbuild-run.yml`. Do not render both destinations in one invocation and do not translate an unsupported destination field into a superficially similar field.

Before editing a user-owned destination, present the knowledge record, semantic definition set, exact rendered change, preserved content, and destination-specific overwrite or regeneration risk. Apply only confirmed facts. After application, run the destination validator and compare the parsed affected fields with the semantic set.

Report emitted definitions, placement or merge identities, applicability, sources, confidence, unsupported mappings, unresolved items, and validation results. Return missing or contradictory hardware facts to `$debug-access-knowledge`.
