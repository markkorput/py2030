#!/usr/bin/env python
import unittest

from pyhoh.components.midi_to_event import MidiToEvent
from pyhoh.dynamic_events import DynamicEvents
from pyhoh.components.midi_input import MidiInput

class TestMidiToEvent(unittest.TestCase):
    def setUp(self):
        self.midi2event = MidiToEvent({144: {36: 'fooEvent'}})
        self.dynamic_events = DynamicEvents()
        self.midi_input = MidiInput()
        self.midi2event.setup(self.midi_input, self.dynamic_events)

    def test_init(self):
        midi2event = MidiToEvent()
        self.assertIsNone(midi2event.midi_input)
        self.assertIsNone(midi2event.dynamic_events)

    def test_setup(self):
        self.assertEqual(self.midi2event.midi_input, self.midi_input)
        self.assertEqual(self.midi2event.dynamic_events, self.dynamic_events)

    def test_unknown_midi_note(self):
        fooEvent = self.dynamic_events.getEvent('fooEvent')
        # fooEvent didn't get called
        self.assertEqual(fooEvent._fireCount, 0)
        # trigger midi note without event
        self.midi_input.messageEvent([[144, 35]])
        # fooEvent didn't get called
        self.assertEqual(fooEvent._fireCount, 0)

    def test_midi_note_triggers_event(self):
        fooEvent = self.dynamic_events.getEvent('fooEvent')
        # not yet called
        self.assertEqual(fooEvent._fireCount, 0)
        # trigger midi note that maps to fooEvent
        self.midi_input.messageEvent([[144, 36]])
        # called once
        self.assertEqual(fooEvent._fireCount, 1)
        # trigger midi note that maps to fooEvent again
        self.midi_input.messageEvent([[144, 36]])
        # called twice
        self.assertEqual(fooEvent._fireCount, 2)
