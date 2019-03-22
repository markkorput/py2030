#!/usr/bin/env python
import sys, termios, tty, os, time
from evento import Event
from py2030.base_component import BaseComponent

class Keys(BaseComponent):
  config_name = 'keys'

  def __init__(self, options):
    super().__init__(options)
    # self.charEvent = Event()
    self.charEvents = {}

  def setup(self, event_manager):
    super().setup(event_manager)

    data = self.getOutputEventsData()

    if 'down' in data:
      for char in data['down']:
        evtname = data['down'][char]
        evt = self.event_manager.get(evtname)
        # self.charEvent += lambda c: evt()
        self.charEvents[char] = evt

  def update(self):
    v = self.getch()
    if v:
        self.logger.debug('keys inout: {0}'.format(v))
        # self.charEvent(v)
        if v in self.charEvents:
          self.logger.debug('invoking event for key: {0}'.format(v))
          self.charEvents[v]()

  # adapted from http://www.jonwitts.co.uk/archives/896
  # adapted from https://github.com/recantha/EduKit3-RC-Keyboard/blob/master/rc_keyboard.py
  def getch(self):
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch
