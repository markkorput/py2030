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
        self.assertIsNone(osc2event.mapping)

    def test_setup(self):
        osc2event = OscToEvent()
        osc_input = OscInput()
        event_manager = EventManager()
        osc2event.setup(osc_input, event_manager)
        # assert result
        self.assertEqual(osc2event.osc_input, osc_input)
        self.assertEqual(osc2event.event_manager, event_manager)
        self.assertEqual(osc2event.mapping, {})
        self.assertTrue(osc2event._onOscMessage in osc_input.messageEvent)

    def test_destroy(self):
        osc2event = OscToEvent()
        osc_input = OscInput()
        event_manager = EventManager()
        osc2event.setup(osc_input, event_manager)
        self.assertEqual(osc2event.mapping, {})
        osc2event.destroy()
        self.assertIsNone(osc2event.mapping)
        self.assertFalse(osc2event._onOscMessage in osc_input.messageEvent)
        self.assertIsNone(osc2event.event_manager)
        self.assertIsNone(osc2event.osc_input)

    def test_ignores_non_string_options(self):
        osc2event = OscToEvent({'verbose': True, 'foo': 3})
        osc_input = OscInput()
        event_manager = EventManager()
        osc2event.setup(osc_input, event_manager)
        # before
        self.assertEqual(event_manager.getEvent('True')._fireCount, 0)
        self.assertEqual(event_manager.getEvent('true')._fireCount, 0)
        self.assertEqual(event_manager.getEvent(3)._fireCount, 0)
        self.assertEqual(event_manager.getEvent('3')._fireCount, 0)
        # tigger
        osc_input.messageEvent('verbose')
        osc_input.messageEvent('foo')
        # after
        self.assertEqual(event_manager.getEvent('True')._fireCount, 0)
        self.assertEqual(event_manager.getEvent('true')._fireCount, 0)
        self.assertEqual(event_manager.getEvent(3)._fireCount, 0)
        self.assertEqual(event_manager.getEvent('3')._fireCount, 0)

    def test_osc_messages_trigger_specified_events(self):
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
