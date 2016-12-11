#!/usr/bin/env python
import unittest

from pyhoh.component_manager import ComponentManager

class TestComponentManager(unittest.TestCase):
    def test_init(self):
        cm = ComponentManager()
        self.assertIsNotNone(cm.event_manager)
        self.assertTrue(cm.running)
        self.assertEqual(cm.profile, 'default')
        self.assertEqual(cm.config_file.path, 'config/config.yml')

    def test_start_event(self):
        cm = ComponentManager({'profile_data': {'start_event': 'letsgo'}})
        # before: the letsgo event has not been fired yet
        self.assertEqual(cm.event_manager.getEvent('letsgo')._fireCount, 0)
        cm.setup()
        # the configure start event is fired after setup completes
        self.assertEqual(cm.event_manager.getEvent('letsgo')._fireCount, 1)
