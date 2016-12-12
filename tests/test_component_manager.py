#!/usr/bin/env python
import unittest

from py2030.component_manager import ComponentManager

class TestComponentManager(unittest.TestCase):
    def test_init(self):
        cm = ComponentManager()
        self.assertIsNotNone(cm.event_manager)
        self.assertTrue(cm.running)
        self.assertEqual(cm.profile, 'default')
        self.assertEqual(cm.config_file.path, 'config.yml')

    def test_start_event(self):
        cm = ComponentManager({'profile_data': {'start_event': 'go'}})
        # before: the letsgo event has not been fired yet
        self.assertEqual(cm.event_manager.getEvent('go')._fireCount, 0)
        cm.setup()
        # the configure start event is fired after setup completes
        self.assertEqual(cm.event_manager.getEvent('go')._fireCount, 1)

    def test_config_file_option(self):
        cm = ComponentManager({'config_file': 'foo/bar.txt'})
        self.assertEqual(cm.config_file.path, 'foo/bar.txt')

    def test_reload_event(self):
        cm = ComponentManager({
            'config_file': 'tests/data/config.yml',
            'profile': 'reloader',
            'profile_data': {'reload_event': 'reload', 'start_event': 'ramones'}
        })
        # before
        self.assertEqual(cm.event_manager.getEvent('ramones')._fireCount, 0)
        self.assertEqual(cm.event_manager.getEvent('heyholetsgo')._fireCount, 0)
        self.assertEqual(len(cm.event_manager.getEvent('reloader')), 0)
        # setup from param config
        cm.setup()
        # after first setup
        self.assertEqual(len(cm.event_manager.getEvent('reload')), 1)
        self.assertEqual(cm.event_manager.getEvent('ramones')._fireCount, 1)
        self.assertEqual(cm.event_manager.getEvent('heyholetsgo')._fireCount, 0)
        # trigger reload
        cm.event_manager.getEvent('reload').fire()
        cm.update() # have to run update, 'cause the reload event handler queues the actual reload operation
        # after second setup
        self.assertEqual(cm.event_manager.getEvent('ramones')._fireCount, 1)
        self.assertEqual(cm.event_manager.getEvent('heyholetsgo')._fireCount, 1)
        self.assertEqual(len(cm.event_manager.getEvent('reload')), 0)
        self.assertEqual(len(cm.event_manager.getEvent('reload2')), 1)
        # cleanup
        cm.destroy()
        # verify
        self.assertEqual(len(cm.event_manager.getEvent('reload2')), 0)
