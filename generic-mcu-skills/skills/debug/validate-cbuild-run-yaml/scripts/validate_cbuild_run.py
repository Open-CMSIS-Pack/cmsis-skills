# generated with AI
"""Validate common debug configuration in a CMSIS-Toolbox cbuild-run file."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required: python -m pip install pyyaml", file=sys.stderr)
    raise SystemExit(2)


class UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def construct_unique_mapping(
    loader: UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_unique_mapping
)


SEQUENCE_KEYS = {"name", "info", "blocks", "pname"}
BLOCK_KEYS = {"info", "blocks", "execute", "atomic", "if", "while", "timeout"}
TOPOLOGY_KEYS = {"debugports", "processors", "trace-sinks", "swj", "dormant", "sdf"}
DEBUGPORT_KEYS = {"dpid", "jtag", "swd", "accessports"}
ACCESSPORT_KEYS = {
    "apid",
    "index",
    "address",
    "HPROT",
    "SPROT",
    "datapatch",
    "accessports",
}
DATAPATCH_KEYS = {"address", "value", "mask", "type", "info"}
PROCESSOR_KEYS = {"pname", "punits", "apid", "reset-sequence"}
PUNIT_KEYS = {"punit", "address"}


def is_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def require_mapping(value: Any, location: str, errors: list[str]) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        errors.append(f"{location}: expected a mapping")
        return None
    return value


def require_list(value: Any, location: str, errors: list[str]) -> list[Any] | None:
    if not isinstance(value, list):
        errors.append(f"{location}: expected a list")
        return None
    return value


def reject_unknown_keys(
    value: dict[str, Any], allowed: set[str], location: str, errors: list[str]
) -> None:
    for key in value:
        if key not in allowed:
            errors.append(f"{location}: unsupported key {key!r}")


def require_string(
    value: dict[str, Any], key: str, location: str, errors: list[str], required: bool = False
) -> None:
    if key not in value:
        if required:
            errors.append(f"{location}: missing required key {key!r}")
        return
    if not isinstance(value[key], str) or not value[key].strip():
        errors.append(f"{location}.{key}: expected a non-empty string")


def validate_block(value: Any, location: str, errors: list[str]) -> None:
    block = require_mapping(value, location, errors)
    if block is None:
        return
    reject_unknown_keys(block, BLOCK_KEYS, location, errors)
    require_string(block, "info", location, errors)
    require_string(block, "execute", location, errors)
    require_string(block, "if", location, errors)
    require_string(block, "while", location, errors)

    if "execute" in block and "blocks" in block:
        errors.append(f"{location}: 'execute' and nested 'blocks' are mutually exclusive")
    if "atomic" in block and "blocks" in block:
        errors.append(f"{location}: 'atomic' cannot be combined with nested 'blocks'")
    if "atomic" in block and block["atomic"] is not None and not isinstance(block["atomic"], bool):
        errors.append(f"{location}.atomic: expected null or a boolean")
    if "timeout" in block:
        if not is_integer(block["timeout"]):
            errors.append(f"{location}.timeout: expected an integer")
        if "while" not in block:
            errors.append(f"{location}.timeout: requires a 'while' expression")

    if "blocks" in block:
        nested = require_list(block["blocks"], f"{location}.blocks", errors)
        if nested is not None:
            for index, item in enumerate(nested):
                validate_block(item, f"{location}.blocks[{index}]", errors)


def validate_sequences(root: dict[str, Any], errors: list[str]) -> None:
    if "debug-sequences" not in root:
        return
    sequences = require_list(root["debug-sequences"], "cbuild-run.debug-sequences", errors)
    if sequences is None:
        return

    identities: set[tuple[str, str | None]] = set()
    for index, value in enumerate(sequences):
        location = f"cbuild-run.debug-sequences[{index}]"
        sequence = require_mapping(value, location, errors)
        if sequence is None:
            continue
        reject_unknown_keys(sequence, SEQUENCE_KEYS, location, errors)
        require_string(sequence, "name", location, errors, required=True)
        require_string(sequence, "info", location, errors)
        require_string(sequence, "pname", location, errors)

        name = sequence.get("name")
        pname = sequence.get("pname")
        if isinstance(name, str) and name.strip():
            identity = (name, pname if isinstance(pname, str) else None)
            if identity in identities:
                errors.append(
                    f"{location}: duplicate sequence identity (name={identity[0]!r}, pname={identity[1]!r})"
                )
            identities.add(identity)

        if "blocks" in sequence:
            blocks = require_list(sequence["blocks"], f"{location}.blocks", errors)
            if blocks is not None:
                for block_index, block in enumerate(blocks):
                    validate_block(block, f"{location}.blocks[{block_index}]", errors)


def validate_debug_vars(root: dict[str, Any], errors: list[str]) -> None:
    if "debug-vars" not in root:
        return
    location = "cbuild-run.debug-vars"
    variables = require_mapping(root["debug-vars"], location, errors)
    if variables is None:
        return
    reject_unknown_keys(variables, {"vars"}, location, errors)
    if "vars" in variables and not isinstance(variables["vars"], str):
        errors.append(f"{location}.vars: expected a literal string")


def validate_sequence_config(root: dict[str, Any], errors: list[str]) -> None:
    if "debug-sequences-conf" not in root:
        return
    location = "cbuild-run.debug-sequences-conf"
    config = require_mapping(root["debug-sequences-conf"], location, errors)
    if config is None:
        return
    reject_unknown_keys(config, {"trace-setup"}, location, errors)
    if "trace-setup" in config and config["trace-setup"] not in ("full", "legacy"):
        errors.append(f"{location}.trace-setup: expected 'full' or 'legacy'")


def validate_datapatches(value: Any, location: str, errors: list[str]) -> None:
    patches = require_list(value, location, errors)
    if patches is None:
        return
    for index, item in enumerate(patches):
        item_location = f"{location}[{index}]"
        patch = require_mapping(item, item_location, errors)
        if patch is None:
            continue
        reject_unknown_keys(patch, DATAPATCH_KEYS, item_location, errors)
        for key in ("address", "value"):
            if key not in patch:
                errors.append(f"{item_location}: missing required key {key!r}")
            elif not is_integer(patch[key]):
                errors.append(f"{item_location}.{key}: expected an integer")
        if "mask" in patch and not is_integer(patch["mask"]):
            errors.append(f"{item_location}.mask: expected an integer")
        require_string(patch, "type", item_location, errors)
        if "type" in patch and patch["type"] not in ("AP", "Mem"):
            errors.append(f"{item_location}.type: expected 'AP' or 'Mem'")
        require_string(patch, "info", item_location, errors)


def validate_accessports(value: Any, location: str, errors: list[str]) -> None:
    accessports = require_list(value, location, errors)
    if accessports is None:
        return
    apids: set[int] = set()
    for index, item in enumerate(accessports):
        item_location = f"{location}[{index}]"
        accessport = require_mapping(item, item_location, errors)
        if accessport is None:
            continue
        reject_unknown_keys(accessport, ACCESSPORT_KEYS, item_location, errors)
        apid = accessport.get("apid")
        if not is_integer(apid):
            errors.append(f"{item_location}.apid: expected a required integer")
        elif apid in apids:
            errors.append(f"{item_location}.apid: duplicate AP ID {apid}")
        else:
            apids.add(apid)
        if "index" in accessport and "address" in accessport:
            errors.append(f"{item_location}: 'index' and 'address' are mutually exclusive")
        for key in ("index", "address", "HPROT", "SPROT"):
            if key in accessport and not is_integer(accessport[key]):
                errors.append(f"{item_location}.{key}: expected an integer")
        if "datapatch" in accessport:
            validate_datapatches(accessport["datapatch"], f"{item_location}.datapatch", errors)
        if "accessports" in accessport:
            validate_accessports(accessport["accessports"], f"{item_location}.accessports", errors)


def validate_debugports(value: Any, errors: list[str]) -> None:
    location = "cbuild-run.debug-topology.debugports"
    debugports = require_list(value, location, errors)
    if debugports is None:
        return
    dpids: set[int] = set()
    for index, item in enumerate(debugports):
        item_location = f"{location}[{index}]"
        debugport = require_mapping(item, item_location, errors)
        if debugport is None:
            continue
        reject_unknown_keys(debugport, DEBUGPORT_KEYS, item_location, errors)
        dpid = debugport.get("dpid")
        if not is_integer(dpid):
            errors.append(f"{item_location}.dpid: expected a required integer")
        elif dpid in dpids:
            errors.append(f"{item_location}.dpid: duplicate DP ID {dpid}")
        else:
            dpids.add(dpid)
        if "jtag" in debugport:
            jtag = require_mapping(debugport["jtag"], f"{item_location}.jtag", errors)
            if jtag is not None:
                reject_unknown_keys(jtag, {"tapindex"}, f"{item_location}.jtag", errors)
                if "tapindex" in jtag and not is_integer(jtag["tapindex"]):
                    errors.append(f"{item_location}.jtag.tapindex: expected an integer")
        if "swd" in debugport:
            swd = require_mapping(debugport["swd"], f"{item_location}.swd", errors)
            if swd is not None:
                reject_unknown_keys(swd, {"targetsel"}, f"{item_location}.swd", errors)
                if "targetsel" in swd and not is_integer(swd["targetsel"]):
                    errors.append(f"{item_location}.swd.targetsel: expected an integer")
        if "accessports" in debugport:
            validate_accessports(debugport["accessports"], f"{item_location}.accessports", errors)


def validate_processors(value: Any, errors: list[str]) -> None:
    location = "cbuild-run.debug-topology.processors"
    processors = require_list(value, location, errors)
    if processors is None:
        return
    pnames: set[str] = set()
    for index, item in enumerate(processors):
        item_location = f"{location}[{index}]"
        processor = require_mapping(item, item_location, errors)
        if processor is None:
            continue
        reject_unknown_keys(processor, PROCESSOR_KEYS, item_location, errors)
        require_string(processor, "pname", item_location, errors, required=True)
        require_string(processor, "reset-sequence", item_location, errors)
        pname = processor.get("pname")
        if isinstance(pname, str):
            if pname in pnames:
                errors.append(f"{item_location}.pname: duplicate processor {pname!r}")
            pnames.add(pname)
        if "apid" in processor and not is_integer(processor["apid"]):
            errors.append(f"{item_location}.apid: expected an integer")
        if "punits" in processor:
            punits = require_list(processor["punits"], f"{item_location}.punits", errors)
            if punits is not None:
                unit_ids: set[int] = set()
                for unit_index, unit_value in enumerate(punits):
                    unit_location = f"{item_location}.punits[{unit_index}]"
                    unit = require_mapping(unit_value, unit_location, errors)
                    if unit is None:
                        continue
                    reject_unknown_keys(unit, PUNIT_KEYS, unit_location, errors)
                    for key in PUNIT_KEYS:
                        if key not in unit:
                            errors.append(f"{unit_location}: missing required key {key!r}")
                        elif not is_integer(unit[key]):
                            errors.append(f"{unit_location}.{key}: expected an integer")
                    unit_id = unit.get("punit")
                    if is_integer(unit_id):
                        if unit_id in unit_ids:
                            errors.append(f"{unit_location}.punit: duplicate processor unit {unit_id}")
                        unit_ids.add(unit_id)


def validate_trace_sinks(value: Any, errors: list[str]) -> None:
    location = "cbuild-run.debug-topology.trace-sinks"
    sinks = require_list(value, location, errors)
    if sinks is None:
        return
    trace_buffers = [
        item["tracebuffer"]
        for item in sinks
        if isinstance(item, dict) and "tracebuffer" in item
    ]
    if len(trace_buffers) > 1 and any(
        not isinstance(name, str) or not name.strip() for name in trace_buffers
    ):
        errors.append(f"{location}: multiple trace buffers require a non-empty name for every buffer")
    identities: set[tuple[str, str | None]] = set()
    for index, item in enumerate(sinks):
        item_location = f"{location}[{index}]"
        sink = require_mapping(item, item_location, errors)
        if sink is None:
            continue
        if len(sink) != 1:
            errors.append(f"{item_location}: expected exactly one trace-sink type")
            continue
        sink_type, sink_name = next(iter(sink.items()))
        if sink_type not in {"serialwire", "tracebuffer"}:
            errors.append(f"{item_location}: unsupported trace-sink type {sink_type!r}")
        elif sink_type == "serialwire" and sink_name is not None:
            errors.append(f"{item_location}.serialwire: expected an empty value")
        elif sink_type == "tracebuffer" and sink_name is not None and not isinstance(sink_name, str):
            errors.append(f"{item_location}.tracebuffer: expected an empty value or string name")
        if sink_type in {"serialwire", "tracebuffer"} and (
            sink_name is None or isinstance(sink_name, str)
        ):
            identity = (sink_type, sink_name)
            if identity in identities:
                errors.append(f"{item_location}: duplicate trace-sink identity {identity!r}")
            identities.add(identity)


def validate_topology(root: dict[str, Any], errors: list[str]) -> None:
    if "debug-topology" not in root:
        return
    location = "cbuild-run.debug-topology"
    topology = require_mapping(root["debug-topology"], location, errors)
    if topology is None:
        return
    reject_unknown_keys(topology, TOPOLOGY_KEYS, location, errors)
    for key in ("swj", "dormant"):
        if key in topology and not isinstance(topology[key], bool):
            errors.append(f"{location}.{key}: expected a boolean")
    require_string(topology, "sdf", location, errors)
    if "debugports" in topology:
        validate_debugports(topology["debugports"], errors)
    if "processors" in topology:
        validate_processors(topology["processors"], errors)
    if "trace-sinks" in topology:
        validate_trace_sinks(topology["trace-sinks"], errors)


def validate_document(document: Any) -> list[str]:
    errors: list[str] = []
    top = require_mapping(document, "document", errors)
    if top is None:
        return errors
    if set(top) != {"cbuild-run"}:
        errors.append("document: expected exactly one top-level key named 'cbuild-run'")
    root = require_mapping(top.get("cbuild-run"), "cbuild-run", errors)
    if root is None:
        return errors
    validate_debug_vars(root, errors)
    validate_sequences(root, errors)
    validate_sequence_config(root, errors)
    validate_topology(root, errors)
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path, help="existing *.cbuild-run.yml file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.file.is_file():
        print(f"ERROR: file not found: {args.file}", file=sys.stderr)
        return 2
    try:
        document = yaml.load(args.file.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        print(f"ERROR: cannot parse {args.file}: {exc}", file=sys.stderr)
        return 1

    errors = validate_document(document)
    if errors:
        print(f"FAIL: {args.file} ({len(errors)} issue(s))", file=sys.stderr)
        for issue in errors:
            print(f"ERROR: {issue}", file=sys.stderr)
        return 1

    print(f"PASS: {args.file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
