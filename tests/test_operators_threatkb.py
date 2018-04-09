import unittest
try:
    from unittest.mock import patch, ANY as MOCK_ANY
except ImportError:
    from mock import patch, ANY as MOCK_ANY

import operators.threatkb
import artifacts


class TestThreatKB(unittest.TestCase):

    @patch('threatkb.ThreatKB')
    def setUp(self, ThreatKB):
        self.threatkb = operators.threatkb.ThreatKB('a', 'b', 'c', 'd')

    def test_handle_domain_creates_domain(self):
        self.threatkb.handle_artifact(artifacts.Domain('test.com', '', ''))
        self.threatkb.api.create.assert_called_once_with('c2dns', MOCK_ANY)

    def test_handle_ipaddress_creates_ipaddress(self):
        self.threatkb.handle_artifact(artifacts.IPAddress('123.123.123.123', '', ''))
        self.threatkb.api.create.assert_called_once_with('c2ips', MOCK_ANY)

    def test_handle_yarasignature_creates_yarasignature(self):
        self.threatkb.handle_artifact(artifacts.YARASignature('test', '', ''))
        self.threatkb.api.create.assert_called_once_with('import', MOCK_ANY)
