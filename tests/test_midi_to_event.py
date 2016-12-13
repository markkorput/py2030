#!/usr/bin/env python
import unittest

from py2030.components.midi_to_event import MidiToEvent
from py2030.event_manager import EventManager
from py2030.components.midi_input import MidiInput

class TestMidiToEvent(unittest.TestCase):
    def setUp(self):
        self.midi2event = MidiToEvent({144: {36: 'fooEvent'}})
        self.event_manager = EventManager()
        self.midi_input = MidiInput()
        self.midi2event.setup(self.midi_input, self.event_manager)

    def test_init(self):
        midi2event = MidiToEvent()
        self.assertIsNone(midi2event.midi_input)
        self.assertIsNone(midi2event.event_manager)

    def test_setup(self):
        self.assertEqual(self.midi2event.midi_input, self.midi_input)
        self.assertEqual(self.midi2event.event_manager, self.event_manager)

    def test_unknown_midi_note(self):
        fooEvent = self.event_manager.get('fooEvent')
        # fooEvent didn't get called
        self.assertEqual(fooEvent._fireCount, 0)
        # trigger midi note without event
        self.midi_input.messageEvent([[144, 35]])
        # fooEvent didn't get called
        self.assertEqual(fooEvent._fireCount, 0)

    def test_midi_note_triggers_event(self):
        fooEvent = self.event_manager.get('fooEvent')
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
