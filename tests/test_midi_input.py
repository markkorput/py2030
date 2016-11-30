#!/usr/bin/env python
import unittest
import helper
from pyhoh.components.midi_input import MidiInput

class TestMidiInput(unittest.TestCase):
    def test_init(self):
        midiinput = MidiInput()
        self.assertFalse(midiinput.connected)
        self.assertIsNone(midiinput.midiin)
        self.assertIsNone(midiinput.port_name)
        self.assertIsNone(midiinput.port)
        self.assertIsNotNone(midiinput.messageEvent)
