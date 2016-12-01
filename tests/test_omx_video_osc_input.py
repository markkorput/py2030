#!/usr/bin/env python
import unittest

from pyhoh.components.omx_video_osc_input import OmxVideoOscInput

class TestOmxVideoOscInput(unittest.TestCase):
    def test_init(self):
        ovoinput = OmxVideoOscInput()
        self.assertFalse(ovoinput.connected)
        self.assertFalse(ovoinput.running)
