#!/usr/bin/env python
import unittest

from py2030.components.osc_output import OscOutput
from py2030.event_manager import EventManager

class TestOscOutput(unittest.TestCase):
    def test_init(self):
        oscoutput = OscOutput()
        self.assertFalse(oscoutput.connected)
        self.assertIsNotNone(oscoutput.connectEvent)
        self.assertIsNotNone(oscoutput.disconnectEvent)
        self.assertIsNotNone(oscoutput.messageEvent)

    def test_setup_without_event_manager(self):
        oscoutput = OscOutput({'ip': '127.0.0.1'})
        oscoutput.setup()
        self.assertIsNone(oscoutput.event_manager)
        self.assertIsNotNone(oscoutput.client)
        self.assertTrue(oscoutput.connected)

    def test_setup_with_event_manager(self):
        em = EventManager()
        oscoutput = OscOutput({'ip': '127.0.0.1'})
        oscoutput.setup(em)
        self.assertEqual(oscoutput.event_manager, em)
        self.assertIsNotNone(oscoutput.client)
        self.assertTrue(oscoutput.connected)

class TestOscOutputInputEvents(unittest.TestCase):
    def test_input_event_triggers_osc_message(self):
        oscoutput = OscOutput({'input_events': {'some_event': '/some/message'}})
        oscoutput.setup(EventManager())
        self.message_addresses = []
        oscoutput.messageEvent += self._onMessage
        self.assertEqual(oscoutput.messageEvent._fireCount, 0)
        oscoutput.event_manager.fire('some_event')
        self.assertEqual(oscoutput.messageEvent._fireCount, 1)
        self.assertEqual(self.message_addresses, ['/some/message'])
        oscoutput.event_manager.fire('some_event_tother')
        self.assertEqual(oscoutput.messageEvent._fireCount, 1)
        self.assertEqual(self.message_addresses, ['/some/message'])
        oscoutput.event_manager.fire('some_event')
        self.assertEqual(self.message_addresses, ['/some/message', '/some/message'])

    def _onMessage(self, msg, osc_output):
        self.message_addresses.append(msg.address)

    def test_input_event_with_params(self):
        oscoutput = OscOutput({'input_events': {'params_event': '/some/message'}})
        oscoutput.setup(EventManager())

        # capture all outgoing messages
        self._messages = []
        oscoutput.messageEvent += self._onMessage2

        oscoutput.event_manager.get('params_event').fire('param1', 2, 3.0)
        self.assertEqual(self._messages[-1].values(), ['param1', 2, 3.0])

    def _onMessage2(self, msg, osc_output):
        self._messages.append(msg)
