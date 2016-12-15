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
        omxvideo = OmxVideo({'input_events': {'play': 'play_event'}})
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
        omxvideo = OmxVideo({'input_events': {'pause': 'pause_event'}})
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
        omxvideo = OmxVideo({'input_events': {'toggle': 'toggle_event'}})
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
        omxvideo = OmxVideo({'input_events': {'stop': 'stop_event'}})
        em = EventManager()
        self.assertEqual(len(em.get('stop_event')), 0)
        omxvideo.setup(em)
        self.assertEqual(len(em.get('stop_event')), 1) # registered
        self.assertEqual(omxvideo.stopEvent._fireCount, 0)
        omxvideo.event_manager.fire('stop_event')
        self.assertEqual(omxvideo.stopEvent._fireCount, 1)
        omxvideo.destroy()
        self.assertEqual(len(em.get('stop_event')), 0) # unregistered

    def test_multiple_input_event(self):
        all_event_names = (
            'play_event1', 'play_event2',
            'pause_event1', 'pause_event2',
            'toggle_event1', 'toggle_event2',
            'stop_event1', 'stop_event2')


        omxvideo = OmxVideo({'input_events': {
            'play': ['play_event1', 'play_event2'],
            'pause': ['pause_event1', 'pause_event2'],
            'toggle': ['toggle_event1', 'toggle_event2'],
            'stop': ['stop_event1', 'stop_event2']
        }})

        em = EventManager()
        for name in all_event_names:
            self.assertEqual(len(em.get(name)), 0) # not yet registered
        omxvideo.setup(em)
        for name in all_event_names:
            self.assertEqual(len(em.get(name)), 1) # registered

        self.assertEqual(omxvideo.playEvent._fireCount, 0)
        self.assertEqual(omxvideo.pauseEvent._fireCount, 0)
        self.assertEqual(omxvideo.toggleEvent._fireCount, 0)
        self.assertEqual(omxvideo.stopEvent._fireCount, 0)

        for name in all_event_names:
            omxvideo.event_manager.fire(name)

        self.assertEqual(omxvideo.playEvent._fireCount, 2)
        self.assertEqual(omxvideo.pauseEvent._fireCount, 2)
        self.assertEqual(omxvideo.toggleEvent._fireCount, 2)
        self.assertEqual(omxvideo.stopEvent._fireCount, 2)

        omxvideo.destroy()

        for name in all_event_names:
            self.assertEqual(len(em.get(name)), 0) # unregistered

        #   # start: '' # requires vid playlist number
        #   stop: ''
        #   seek: '' # jump to specified playback position (specified in seconds from start of video)
        #   load: '' # load a video (by playlist number)
