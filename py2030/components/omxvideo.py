try:
    from omxplayer import OMXPlayer
except:
    print "Could not load OMXPlayer"
    OMXPlayer = None

import logging

from evento import Event

class OmxVideo:
  def __init__(self, options = {}):
    # config
    self.options = options

    # attributes
    self.player = None
    self.logger = logging.getLogger(__name__)
    if 'verbose' in options and options['verbose']:
        self.logger.setLevel(logging.DEBUG)

    # get video paths
    self.playlist = []
    self.playlist = options['playlist'] if 'playlist' in options else []
    self.logger.debug('playlist: {0}'.format(", ".join(self.playlist)))

    self.args = self.options['args'] if 'args' in self.options else ['--no-osd', '-b']
    self.event_manager = None
    # events
    self.loadEvent = Event()
    self.loadIndexEvent = Event()
    self.unloadEvent = Event()
    self.startEvent = Event()
    self.stopEvent = Event()
    self.playEvent = Event()
    self.pauseEvent = Event()
    self.toggleEvent = Event()
    self.seekEvent = Event()
    self.speedEvent = Event()

  def __del__(self):
      self.destroy()

  def setup(self, _event_manager = None):
      self.event_manager = _event_manager
      self._registerCallbacks()

  def destroy(self):
    self._registerCallbacks(False)
    if self.player:
      self._unload()

  def _unload(self):
    if self.player:
      self.player.quit()
      self.player = None
      self.unloadEvent(self)

  def load(self, idx=0):
      path = self._getVidPath(idx)
      if not path:
          self.logger.warning('invalid video number: {0}'.format(idx))
          return False

      result = self._loadPath(path)
      self.loadIndexEvent(self, idx)
      return result

  def play(self):
    if self.player:
        self.player.play()
    else:
        self.logger.warning("can't start playback, no video loaded")

    self.logger.debug('video playback started')
    self.playEvent(self)

  def start(self, idx=0):
      self.load(idx)
      self.play()
      self.startEvent(self, idx)

  def pause(self):
    if self.player:
        self.player.pause()
    else:
        self.logger.warning("can't pause video, no video loaded")

    self.logger.debug("video playback paused")
    self.pauseEvent(self)

  def toggle(self):
    if self.player:
        self.player.play_pause()
        self.logger.debug('toggle; video playback {0}'.format('resumed' if self.player.playback_status() == 'Playing' else 'paused'))
    else:
        self.logger.warning("can't toggle play/pause video playback, no video loaded")

    self.toggleEvent(self)

  def stop(self):
    if self.player:
        self.player.stop()
    else:
        self.logger.warning("can't stop video playback, no video loaded")

    self.logger.debug('video playback stopped')
    self.stopEvent(self)

  def seek(self, pos=0.0):
    try:
        pos = float(pos)
    except ValueError as err:
        self.logger.warning('invalid pos value: {0}'.format(pos))
        return

    if self.player:
        self.player.set_position(pos)
    else:
        self.logger.warning("can't seek video playback position, no video loaded")

    self.logger.debug('video payback position changed to {0}'.format(pos))
    self.seekEvent(self, pos)

  def speed(self, speed=0):
    if not self.player:
      self.logger.warning("can't change video playback speed, no video loaded")

    # speed -1 means 'slower'
    # speed 1 means 'faster'

    if speed == -1:
        if self.player:
            self.player.action(1)
        self.logger.debug("video playback slower")
        self.speedEvent(self, -1)
        return

    if speed == 1:
        if self.player:
            self.player.action(2)
        self.logger.debug("video playback faster")
        self.speedEvent(self, 1)
        return

    self.logger.warning("invalid speed value: {0}".format(speed))

  def _loadPath(self, videoPath):
    # close existing video
    if self.player:
      self._unload()

    self.logger.debug('loading player with command: {0} {1}'.format(videoPath, ' '.join(self.args)))
    # this will be paused by default

    if OMXPlayer:
        # start omx player without osd and sending audio through analog jack
        self.player = OMXPlayer(videoPath, args=self.args) #['--no-osd', '--adev', 'local', '-b'])
    else:
        self.logger.warning('No OMXPlayer not available, cannot load file: {0}'.format(videoPath))

    self.loadEvent(self, videoPath)

  def _getVidPath(self, idx):
    # make sure we have an int
    try:
      idx = int(idx)
    except:
      return None

    # make sure the int is not out of bounds for our array
    if idx < 0 or idx >= len(self.playlist):
      return None

    return self.playlist[idx]

  def _registerCallbacks(self, _register=True):
      # we'll need an event_manager
      if self.event_manager == None:
          self.logger.warning('no event manager')
          return

      # we'll need input event config data
      if not 'input_events' in self.options:
          return

      # all known actions
      action_funcs = {
        'play': self.play,
        'pause': self.pause,
        'toggle': self.toggle,
        'stop': self.stop,
        'start': self.start,
        'load': self.load,
        'seek': self.seek
      }

      for event_name, action_name in self.options['input_events'].items():
          if not action_name in action_funcs:
              self.logger.warning('unknown input event action: {0}'.format(action_name))
              continue

          if _register:
              self.event_manager.get(event_name).subscribe(action_funcs[action_name])
          else:
              self.event_manager.get(event_name).unsubscribe(action_funcs[action_name])
