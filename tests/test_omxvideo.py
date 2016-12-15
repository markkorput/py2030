#!/usr/bin/env python
import unittest

from py2030.components.omxvideo import OmxVideo
from py2030.event_manager import EventManager

class TestOmxVideo(unittest.TestCase):
    def test_init(self):
        omxvideo = OmxVideo()
        self.assertEqual(omxvideo.player, None)
        self.assertIsNone(omxvideo.event_manager)

    def test_args_option(self):
        # default; black background (to hide console) and disable OSD
        self.assertEqual(OmxVideo().args, ['--no-osd', '-b'])
        # customizable through 'args' option
        args = ['--no-osd', '-adev', 'both', '-b', '--loop']
        omxvideo = OmxVideo({'args': args})
        self.assertEqual(omxvideo.args, args)

    def test_setup(self):
        omxvideo = OmxVideo()
        em = EventManager()
        omxvideo.setup(em)
        self.assertEqual(omxvideo.event_manager, em)

    def test_setup_doesnt_require_event_manager(self):
        omxvideo = OmxVideo()
        omxvideo.setup()
        self.assertIsNone(omxvideo.event_manager)

    def test_input_event_play(self):
        omxvideo = OmxVideo({'input_events': {'play_event': 'play'}})
        em = EventManager()
        self.assertEqual(len(em.get('play_event')), 0) # no yet registered
        omxvideo.setup(em)
        self.assertEqual(len(em.get('play_event')), 1) # registered
        self.assertEqual(omxvideo.playEvent._fireCount, 0) # not fire
        omxvideo.event_manager.fire('play_event')
        self.assertEqual(omxvideo.playEvent._fireCount, 1) # fired
        omxvideo.destroy()
        self.assertEqual(len(em.get('play_event')), 0) # unregistered

    def test_input_event_pause(self):
        omxvideo = OmxVideo({'input_events': {'pause_event': 'pause'}})
        em = EventManager()
        self.assertEqual(len(em.get('pause_event')), 0)
        omxvideo.setup(em)
        self.assertEqual(len(em.get('pause_event')), 1) # registered
        self.assertEqual(omxvideo.pauseEvent._fireCount, 0)
        omxvideo.event_manager.fire('pause_event')
        self.assertEqual(omxvideo.pauseEvent._fireCount, 1)
        omxvideo.destroy()
        self.assertEqual(len(em.get('pause_event')), 0) # unregistered

    def test_input_event_toggle(self):
        omxvideo = OmxVideo({'input_events': {'toggle_event': 'toggle'}})
        em = EventManager()
        self.assertEqual(len(em.get('toggle_event')), 0)
        omxvideo.setup(em)
        self.assertEqual(len(em.get('toggle_event')), 1) # registered
        self.assertEqual(omxvideo.toggleEvent._fireCount, 0)
        omxvideo.event_manager.fire('toggle_event')
        self.assertEqual(omxvideo.toggleEvent._fireCount, 1)
        omxvideo.destroy()
        self.assertEqual(len(em.get('toggle_event')), 0) # unregistered

    def test_input_event_stop(self):
        omxvideo = OmxVideo({'input_events': {'stop_event': 'stop'}})
        em = EventManager()
        self.assertEqual(len(em.get('stop_event')), 0)
        omxvideo.setup(em)
        self.assertEqual(len(em.get('stop_event')), 1) # registered
        self.assertEqual(omxvideo.stopEvent._fireCount, 0)
        omxvideo.event_manager.fire('stop_event')
        self.assertEqual(omxvideo.stopEvent._fireCount, 1)
        omxvideo.destroy()
        self.assertEqual(len(em.get('stop_event')), 0) # unregistered

    def test_input_event_start(self):
        omxvideo = OmxVideo({'input_events': {'start_event': 'start'}})
        em = EventManager()
        self.assertEqual(len(em.get('start_event')), 0)
        omxvideo.setup(em)
        self.assertEqual(len(em.get('start_event')), 1) # registered
        self.assertEqual(omxvideo.startEvent._fireCount, 0)
        omxvideo.event_manager.fire('start_event') # fire without params
        self.assertEqual(omxvideo.startEvent._fireCount, 1) # performed
        omxvideo.event_manager.get('start_event').fire(3) # fire with number param
        self.assertEqual(omxvideo.startEvent._fireCount, 2) # performed again
        omxvideo.destroy()
        self.assertEqual(len(em.get('start_event')), 0) # unregistered

    def test_input_event_load(self):
        omxvideo = OmxVideo({'input_events': {'load_event': 'load'}, 'playlist': ['1', '2', '3', '4']})
        em = EventManager()
        self.assertEqual(len(em.get('load_event')), 0)
        omxvideo.setup(em)
        self.assertEqual(len(em.get('load_event')), 1) # registered
        self.assertEqual(omxvideo.loadEvent._fireCount, 0)
        omxvideo.event_manager.fire('load_event') # fire without params
        self.assertEqual(omxvideo.loadEvent._fireCount, 1) # performed
        omxvideo.event_manager.get('load_event').fire(3) # fire with number param
        self.assertEqual(omxvideo.loadEvent._fireCount, 2) # performed again
        omxvideo.destroy()
        self.assertEqual(len(em.get('load_event')), 0) # unregistered

    def test_input_event_seek(self):
        omxvideo = OmxVideo({'input_events': {'seek_event': 'seek'}})
        em = EventManager()
        self.assertEqual(len(em.get('seek_event')), 0)
        omxvideo.setup(em)
        self.assertEqual(len(em.get('seek_event')), 1) # registered
        self.assertEqual(omxvideo.seekEvent._fireCount, 0)
        omxvideo.event_manager.fire('seek_event') # fire without params
        self.assertEqual(omxvideo.seekEvent._fireCount, 1) # performed
        omxvideo.event_manager.get('seek_event').fire(3) # fire with number param
        self.assertEqual(omxvideo.seekEvent._fireCount, 2) # performed again
        omxvideo.destroy()
        self.assertEqual(len(em.get('seek_event')), 0) # unregistered

    def test_multiple_input_events(self):
        input_events = {
            'play_event1': 'play',
            'play_event2': 'play',
            'pause_event1': 'pause',
            'pause_event2': 'pause',
            'toggle_event1': 'toggle',
            'toggle_event2': 'toggle',
            'stop_event1': 'stop',
            'stop_event2': 'stop',
            'load_event1': 'load',
            'load_event2': 'load',
            'start_event1': 'start',
            'start_event2': 'start',
            'seek_event1': 'seek',
            'seek_event2': 'seek'
        }

        omxvideo = OmxVideo({'input_events': input_events, 'playlist': ['1']})
        em = EventManager()

        for name in input_events.keys():
            self.assertEqual(len(em.get(name)), 0) # not yet registered

        omxvideo.setup(em)

        for name in input_events.keys():
            self.assertEqual(len(em.get(name)), 1) # registered

        self.assertEqual(omxvideo.playEvent._fireCount, 0)
        self.assertEqual(omxvideo.pauseEvent._fireCount, 0)
        self.assertEqual(omxvideo.toggleEvent._fireCount, 0)
        self.assertEqual(omxvideo.stopEvent._fireCount, 0)
        self.assertEqual(omxvideo.startEvent._fireCount, 0)
        self.assertEqual(omxvideo.loadEvent._fireCount, 0)
        self.assertEqual(omxvideo.seekEvent._fireCount, 0)

        for name in input_events.keys():
            omxvideo.event_manager.fire(name)

        self.assertEqual(omxvideo.playEvent._fireCount, 4) # the two 'start' actions also call play
        self.assertEqual(omxvideo.pauseEvent._fireCount, 2)
        self.assertEqual(omxvideo.toggleEvent._fireCount, 2)
        self.assertEqual(omxvideo.stopEvent._fireCount, 2)
        self.assertEqual(omxvideo.startEvent._fireCount, 2)
        self.assertEqual(omxvideo.loadEvent._fireCount, 4) # the two start actions also load
        self.assertEqual(omxvideo.seekEvent._fireCount, 2)

        omxvideo.destroy()

        for name in input_events.keys():
            self.assertEqual(len(em.get(name)), 0) # unregistered
