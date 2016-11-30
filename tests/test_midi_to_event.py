#!/usr/bin/env python
import unittest
import helper
from pyhoh.components.midi_to_event import MidiToEvent
from pyhoh.dynamic_events import DynamicEvents
from pyhoh.components.midi_input import MidiInput

class TestMidiToEvent(unittest.TestCase):
    def test_init(self):
        midi2event = MidiToEvent()
        self.assertIsNone(midi2event.midi_input)
        self.assertIsNone(midi2event.dynamic_events)

    def test_setup(self):
        midi2event = MidiToEvent({'144': {'36': 'fooEvent'}})
        dynevents = DynamicEvents()
        midiinput = MidiInput()
        midi2event.setup(midiinput, dynevents)
        self.assertEqual(midi2event.midi_input, midiinput)
        self.assertEqual(midi2event.dynamic_events, dynevents)

        dynevents.getEvent('fooEvent').subscribe(self._onFooEvent)
        self._onFooEventCount = 0
        # trigger midi note without event
        midiinput.messageEvent([['144', '35']])
        # fooEvent didn't get called
        self.assertEqual(self._onFooEventCount, 0)
        # trigger midi note that maps to fooEvent
        midiinput.messageEvent([['144', '36']])
        # called once
        self.assertEqual(self._onFooEventCount, 1)
        # trigger midi note that maps to fooEvent again
        midiinput.messageEvent([['144', '36']])
        # called twice now
        self.assertEqual(self._onFooEventCount, 2)

    def _onFooEvent(self):
        self._onFooEventCount = self._onFooEventCount + 1 if hasattr(self, '_onFooEventCount') else 1
