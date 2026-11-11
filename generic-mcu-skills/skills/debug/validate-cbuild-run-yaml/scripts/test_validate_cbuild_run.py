# generated with AI
"""Regression tests: access-port identities and the shapes of generated files."""

import unittest

from validate_cbuild_run import validate_document


class AccessPortIdentityTests(unittest.TestCase):
    def validate_ports(self, ports):
        return validate_document(
            {"cbuild-run": {"debug-topology": {"debugports": ports}}}
        )

    def test_duplicate_ids_are_rejected_across_the_target(self):
        cases = {
            "same list": [
                {"dpid": 0, "accessports": [{"apid": 7}, {"apid": 7}]}
            ],
            "different debug ports": [
                {"dpid": 0, "accessports": [{"apid": 7}]},
                {"dpid": 1, "accessports": [{"apid": 7}]},
            ],
            "parent and child": [
                {
                    "dpid": 0,
                    "accessports": [{"apid": 7, "accessports": [{"apid": 7}]}],
                }
            ],
            "different nested lists": [
                {
                    "dpid": 0,
                    "accessports": [
                        {"apid": 1, "accessports": [{"apid": 7}]},
                        {"apid": 2, "accessports": [{"apid": 7}]},
                    ],
                }
            ],
        }
        for label, ports in cases.items():
            with self.subTest(label=label):
                errors = self.validate_ports(ports)
                self.assertEqual(len(errors), 1, errors)
                self.assertIn(".apid: duplicate AP ID 7", errors[0])

    def test_distinct_ids_allow_parent_relative_indices_and_addresses(self):
        ports = [
            {
                "dpid": 0,
                "accessports": [
                    {
                        "apid": 1,
                        "index": 0,
                        "accessports": [{"apid": 2, "address": 0x1000}],
                    }
                ],
            },
            {
                "dpid": 1,
                "accessports": [
                    {
                        "apid": 3,
                        "index": 0,
                        "accessports": [{"apid": 4, "address": 0x1000}],
                    }
                ],
            },
        ]
        self.assertEqual(self.validate_ports(ports), [])

    def test_ids_can_be_reused_in_separate_targets(self):
        ports = [{"dpid": 0, "accessports": [{"apid": 7}]}]
        self.assertEqual(self.validate_ports(ports), [])
        self.assertEqual(self.validate_ports(ports), [])


class GeneratedFileShapeTests(unittest.TestCase):
    """Shapes that csolution writes into the files it generates."""

    def validate_root(self, root):
        return validate_document({"cbuild-run": root})

    def test_single_processor_needs_no_pname(self):
        topology = {
            "debugports": [{"dpid": 0, "accessports": [{"apid": 0, "index": 1}]}],
            "processors": [{"apid": 0}],
        }
        self.assertEqual(self.validate_root({"debug-topology": topology}), [])

    def test_several_processors_need_pname(self):
        topology = {"processors": [{"apid": 0}, {"pname": "cm33_core1", "apid": 1}]}
        errors = self.validate_root({"debug-topology": topology})
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("processors[0]: missing required key 'pname'", errors[0])

    def test_conditions_accept_expressions_and_numbers(self):
        blocks = [
            {"while": 1, "timeout": 50000},
            {"if": "canReadPins", "blocks": [{"execute": "DAP_SWJ_Pins(0, 1, 0);"}]},
            {"if": 0, "execute": "__dp = 0;"},
        ]
        sequences = [{"name": "ResetHardware", "blocks": blocks}]
        self.assertEqual(self.validate_root({"debug-sequences": sequences}), [])

    def test_conditions_reject_other_values(self):
        for value in ("", "  ", True, None, []):
            with self.subTest(value=value):
                sequences = [{"name": "DebugDeviceUnlock", "blocks": [{"while": value}]}]
                errors = self.validate_root({"debug-sequences": sequences})
                self.assertEqual(len(errors), 1, errors)
                self.assertIn(".while: expected a non-empty expression string or a number", errors[0])


if __name__ == "__main__":
    unittest.main()
