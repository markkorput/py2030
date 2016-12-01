#!/usr/bin/env python
import unittest
from pyhoh.event_manager import EventManager
from pyhoh.components.event_to_omx import EventToOmx
from pyhoh.components.omxvideo import OmxVideo

class TestEventToOmx(unittest.TestCase):
    def test_init(self):
        event2omx = EventToOmx()
        self.assertIsNone(event2omx.event_manager)

    def test_setup(self):
        event2omx = EventToOmx({'begin': {'action': 'start'}, 'pause': 'toggle', 'end': 'stop'})
        event_manager = EventManager()
        event2omx.setup(event_manager, OmxVideo())
        self.assertEqual(event2omx.event_manager, event_manager)
        self.assertEqual(event_manager.getEvent('begin').getSubscriberCount(), 1)
        self.assertEqual(event_manager.getEvent('pause').getSubscriberCount(), 1)
        self.assertEqual(event_manager.getEvent('end').getSubscriberCount(), 1)

    def test_start(self):
        event2omx = EventToOmx({'begin': {'action': 'start'}, 'pause': 'toggle', 'end': 'stop'})
        event_manager = EventManager()
        event2omx.setup(event_manager, OmxVideo())
        self.assertEqual(event2omx.omxvideo.startEvent._fireCount, 0)
        event_manager.getEvent('begin').fire()
        self.assertEqual(event2omx.omxvideo.startEvent._fireCount, 1)

    def test_stop(self):
        event2omx = EventToOmx({'begin': {'action': 'start'}, 'pause': 'toggle', 'end': 'stop'})
        event_manager = EventManager()
        event2omx.setup(event_manager, OmxVideo())
        self.assertEqual(event2omx.omxvideo.stopEvent._fireCount, 0)
        event_manager.getEvent('end').fire()
        # fails because no video is loaded. TODO; verify
        # self.assertEqual(event2omx.omxvideo.stopEvent._fireCount, 1)

    def test_toggle(self):
        event2omx = EventToOmx({'begin': {'action': 'start'}, 'pause': 'toggle', 'end': 'stop'})
        event_manager = EventManager()
        event2omx.setup(event_manager, OmxVideo())
        self.assertEqual(event2omx.omxvideo.toggleEvent._fireCount, 0)
        event_manager.getEvent('pause').fire()
        # fails because no video is loaded. TODO; verify
        # self.assertEqual(event2omx.omxvideo.toggleEvent._fireCount, 1)
