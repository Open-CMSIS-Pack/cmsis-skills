# generated with AI
"""Regression tests for target-wide access-port identities."""

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


if __name__ == "__main__":
    unittest.main()
