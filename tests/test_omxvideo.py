#!/usr/bin/env python
import unittest
import helper
from pyhoh.components.omxvideo import OmxVideo

class TestOmxVideo(unittest.TestCase):
    def test_init(self):
        omxvideo = OmxVideo()
        self.assertEqual(omxvideo.player, None)

    def test_args_option(self):
        # default; black background (to hide console) and disable OSD
        self.assertEqual(OmxVideo().args, ['--no-osd', '-b'])
        # customizable through 'args' option
        args = ['--no-osd', '-adev', 'both', '-b', '--loop']
        omxvideo = OmxVideo({'args': args})
        self.assertEqual(omxvideo.args, args)
