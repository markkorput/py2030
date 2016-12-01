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

  def setup(self):
      pass

  def destroy(self):
    if self.player:
      self._unload()

  def update(self):
      pass

  def _unload(self):
    if self.player:
      self.player.quit()
      self.player = None
      self.unloadEvent(self)

  def load(self, vidNumber):
      path = self._getVidPath(vidNumber)
      if not path:
          self.logger.warning('invalid video number: {0}'.format(vidNumber))
          return False

      result = self._loadPath(path)
      self.loadIndexEvent(self, vidNumber)
      return result

  def play(self):
    if not self.player:
        self.logger.warning("can't start playback, no video loaded")
        return

    self.player.play()
    self.playEvent(self)
    self.logger.debug('video playback started')

  def start(self, vidNumber):
      self.load(vidNumber)
      self.play()
      self.startEvent(self, vidNumber)

  def pause(self):
    if not self.player:
      self.logger.warning("can't pause video, no video loaded")
      return

    self.player.pause()
    self.pauseEvent(self)
    self.logger.debug("video playback paused")

  def toggle(self):
    if not self.player:
      self.logger.warning("can't toggle play/pause video playback, no video loaded")
      return

    self.player.play_pause()
    self.toggleEvent(self)
    self.logger.debug('toggle; video playback {0}'.format('resumed' if self.player.playback_status() == 'Playing' else 'paused'))

  def stop(self):
    if not self.player:
      self.logger.warning("can't stop video playback, no video loaded")
      return

    self.player.stop()
    self.logger.debug('video playback stopped')
    self.stopEvent(self)

  def seek(self, pos):
    if not self.player:
      self.logger.warning("can't seek video playback position, no video loaded")
      return

    try:
        pos = float(pos)
    except ValueError as err:
        self.logger.warning('invalid pos value: {0}'.format(pos))
        return

    self.player.set_position(pos)
    self.logger.debug('video payback position changed to {0}'.format(pos))
    self.seekEvent(self, pos)

  def speed(self, speed):
    if not self.player:
      self.logger.warning("can't change video playback speed, no video loaded")
      return

    # speed -1 means 'slower'
    # speed 1 means 'faster'

    if speed == -1:
      self.player.action(1)
      self.logger.debug("video playback slower")
      self.speedEvent(self, -1)
      return

    if speed == 1:
      self.player.action(2)
      self.logger.debug("video playback faster")
      self.speedEvent(self, 1)
      return

    self.logger.warning("invalid speed value: {0}".format(speed))

  def _loadPath(self, videoPath):
    # close existing video
    if self.player:
      self._unload()

    # this will be paused by default
    if not OMXPlayer:
        self.logger.warning('No OMXPlayer not available, cannot load file: {0}'.format(videoPath))
        return

    self.logger.debug('loading player with command: {0} {1}'.format(videoPath, ' '.join(self.args)))
    # start omx player without osd and sending audio through analog jack
    self.player = OMXPlayer(videoPath, args=self.args) #['--no-osd', '--adev', 'local', '-b'])
    self.loadEvent(self, videoPath)

  def _getVidPath(self, number):
    # make sure we have an int
    try:
      number = int(number)
    except:
      return None

    # make sure the int is not out of bounds for our array
    if number < 0 or number >= len(self.playlist):
      return None

    return self.playlist[number]
