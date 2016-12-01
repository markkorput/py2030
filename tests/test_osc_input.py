#!/usr/bin/env python
import unittest
import helper
from pyhoh.components.osc_input import OscInput

class TestOscInput(unittest.TestCase):
    def test_init(self):
        oscinput = OscInput()
        self.assertFalse(oscinput.connected)
        self.assertFalse(oscinput.running)
