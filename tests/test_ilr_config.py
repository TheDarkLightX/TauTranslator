"""Tests for constants in ilr_config.py."""

import unittest

from tau_translator_omega.core_engine.ilr_config import CORE_ILR_VERSION


class TestILRConfigConstants(unittest.TestCase):
    """Test suite for ILR configuration constants."""

    def test_core_ilr_version_constant(self):
        """Test that CORE_ILR_VERSION has the expected value."""
        self.assertEqual(CORE_ILR_VERSION, "0.1.0")


if __name__ == '__main__':
    unittest.main()
