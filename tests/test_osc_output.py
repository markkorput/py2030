#!/usr/bin/env python
import unittest
import helper
from pyhoh.components.osc_output import OscOutput

class TestOscInput(unittest.TestCase):
    def test_init(self):
        oscoutput = OscOutput()
        self.assertFalse(oscoutput.connected)
        self.assertFalse(oscoutput.running)
        self.assertIsNotNone(oscoutput.connectEvent)
        self.assertIsNotNone(oscoutput.disconnectEvent)
        self.assertIsNotNone(oscoutput.messageEvent)
