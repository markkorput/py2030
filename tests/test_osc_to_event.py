#!/usr/bin/env python
import unittest
from pyhoh.event_manager import EventManager
from pyhoh.components.osc_input import OscInput
from pyhoh.components.osc_to_event import OscToEvent

class TestOscToEvent(unittest.TestCase):
    def test_init(self):
        osc2event = OscToEvent()
        self.assertIsNone(osc2event.osc_input)
        self.assertIsNone(osc2event.event_manager)

    def test_setup(self):
        osc2event = OscToEvent()
        osc_input = OscInput()
        event_manager = EventManager()
        osc2event.setup(osc_input, event_manager)
        # assert result
        self.assertEqual(osc2event.osc_input, osc_input)
        self.assertEqual(osc2event.event_manager, event_manager)

    def test_osc_messages_trigger_events(self):
        osc2event = OscToEvent({'/start': 'startE', '/stop': 'stopE'})
        osc_input = OscInput()
        event_manager = EventManager()
        osc2event.setup(osc_input, event_manager)
        # before
        self.assertEqual(event_manager.getEvent('startE')._fireCount, 0)
        self.assertEqual(event_manager.getEvent('stopE')._fireCount, 0)
        # trigger start
        osc_input.messageEvent('/start')
        self.assertEqual(event_manager.getEvent('startE')._fireCount, 1)
        self.assertEqual(event_manager.getEvent('stopE')._fireCount, 0)
        osc_input.messageEvent('/stop')
        self.assertEqual(event_manager.getEvent('startE')._fireCount, 1)
        self.assertEqual(event_manager.getEvent('stopE')._fireCount, 1)
        osc_input.messageEvent('/start')
        self.assertEqual(event_manager.getEvent('startE')._fireCount, 2)
        self.assertEqual(event_manager.getEvent('stopE')._fireCount, 1)
