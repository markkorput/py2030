#!/usr/bin/env python
import unittest
from os.path import dirname, join
from glob import glob

from py2030.component_manager import ComponentManager

class TestComponentManager(unittest.TestCase):
    def test_init(self):
        cm = ComponentManager()
        self.assertIsNotNone(cm.event_manager)
        self.assertFalse(cm.running)
        self.assertEqual(cm.profile, 'default')
        self.assertEqual(cm.config_file.path, 'config.yml')

    def test_setup_without_components_will_abort(self):
        cm = ComponentManager()
        cm.setup()
        self.assertEqual(len(cm.components), 0)
        self.assertFalse(cm.running)

    def test_setup(self):
        cm = ComponentManager({'profile_data': {'osc_outputs': {'sender': {'ip': '127.0.0.1'}}}})
        cm.setup()
        self.assertEqual(len(cm.components), 1)
        self.assertEqual(cm.components[0].__class__.__name__, 'OscOutput')
        self.assertTrue(cm.running)

    def test_start_event(self):
        cm = ComponentManager({'profile_data': {'start_event': 'go'}})
        # before: the letsgo event has not been fired yet
        self.assertEqual(cm.event_manager.get('go')._fireCount, 0)
        cm.setup()
        # the configure start event is fired after setup completes
        self.assertEqual(cm.event_manager.get('go')._fireCount, 1)

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
        self.assertEqual(cm.event_manager.get('ramones')._fireCount, 0)
        self.assertEqual(cm.event_manager.get('heyholetsgo')._fireCount, 0)
        self.assertFalse(cm._onReloadEvent in cm.event_manager.get('reload'))
        # setup from param config
        cm.setup()
        # after first setup
        self.assertTrue(cm._onReloadEvent in cm.event_manager.get('reload'))
        self.assertEqual(cm.event_manager.get('ramones')._fireCount, 1)
        self.assertEqual(cm.event_manager.get('heyholetsgo')._fireCount, 0)
        # trigger reload
        cm.event_manager.get('reload').fire()
        cm.update() # have to run update, 'cause the reload event handler queues the actual reload operation
        # after second setup
        self.assertEqual(cm.event_manager.get('ramones')._fireCount, 1)
        self.assertEqual(cm.event_manager.get('heyholetsgo')._fireCount, 1)
        self.assertEqual(len(cm.event_manager.get('reload')), 0)
        self.assertEqual(len(cm.event_manager.get('reload2')), 1)
        # cleanup
        cm.destroy()
        # verify
        self.assertEqual(len(cm.event_manager.get('reload2')), 0)

    def test_stop_event(self):
        cm = ComponentManager({'profile_data': {'stop_event': 'quit', 'osc_outputs': {'sender': {'ip': '127.0.0.1'}}}})
        cm.setup()
        # before
        self.assertTrue(cm.running)
        # trigger the stop_event
        cm.event_manager.get('quit').fire()
        # after
        self.assertFalse(cm.running)

    def test_stop_event_same_as_start_event(self):
        cm = ComponentManager({'profile_data': {'stop_event': 'quit', 'start_event': 'quit'}})
        cm.setup()
        self.assertFalse(cm.running)

    def test_found_component_classes(self):
        self.assertEqual(map(lambda cls: cls.__name__, ComponentManager()._found_component_classes()), [
            'DelayItem',
            'EventToEvent',
            'MidiInput',
            'OmxSyncer',
            'OmxVideo',
            'OscInput',
            'OscOutput',
            'OsxOscVideoResumer',
            'SshRemote',
            'WebServer'])
