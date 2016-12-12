import logging

class OmxOscOutput:
    def __init__(self, options = {}):
        # config
        self.options = options
        # attributes
        self.omxvideo = None
        self.osc_output = None
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG if 'verbose' in options and options['verbose'] else logging.INFO)
        # osc messages
        self.msgLoad = None
        self.msgLoadIndex = None
        self.msgUnload = None
        self.msgStart = None
        self.msgStop = None
        self.msgPlay = None
        self.msgPause = None
        self.msgToggle = None
        self.msgSeek = None
        self.msgSpeed = None

    def __del__(self):
        self.destroy()

    def setup(self, omxvideo, osc_output):
        self.destroy()
        self.omxvideo = omxvideo
        self.osc_output = osc_output

        if not omxvideo or not osc_output:
            self.logger.warning("didn't get both video and osc_output")
            return

        # osc messages
        self.msgLoad = self._getOption('load')
        self.msgLoadIndex = self._getOption('loadIndex')
        self.msgUnload = self._getOption('unload')
        self.msgStart = self._getOption('start')
        self.msgStop = self._getOption('stop')
        self.msgPlay = self._getOption('play')
        self.msgPause = self._getOption('pause')
        self.msgToggle = self._getOption('toggle')
        self.msgSeek = self._getOption('seek')
        self.msgSpeed = self._getOption('speed')

        # register callback
        if self.omxvideo:
            if self.msgLoad:
                self.omxvideo.loadEvent += self._onLoad
            if self.msgLoadIndex:
                self.omxvideo.loadIndexEvent += self._onLoadIndex
            if self.msgUnload:
                self.omxvideo.unloadEvent += self._onUnload
            if self.msgStart:
                self.omxvideo.startEvent += self._onStart
            if self.msgStop:
                self.omxvideo.stopEvent += self._onStop
            if self.msgPlay:
                self.omxvideo.playEvent += self._onPlay
            if self.msgPause:
                self.omxvideo.pauseEvent += self._onPause
            if self.msgToggle:
                self.omxvideo.toggleEvent += self._onToggle
            if self.msgSeek:
                self.omxvideo.seekEvent += self._onSeek
            if self.msgSpeed:
                self.omxvideo.speedEvent += self._onSpeed

    def destroy(self):
        if self.omxvideo:
            if self.msgLoad:
                self.omxvideo.loadEvent -= self._onLoad
            if self.msgLoadIndex:
                self.omxvideo.loadIndexEvent -= self._onLoadIndex
            if self.msgUnload:
                self.omxvideo.unloadEvent -= self._onUnload
            if self.msgStart:
                self.omxvideo.startEvent -= self._onStart
            if self.msgStop:
                self.omxvideo.stopEvent -= self._onStop
            if self.msgPlay:
                self.omxvideo.playEvent -= self._onPlay
            if self.msgPause:
                self.omxvideo.pauseEvent -= self._onPause
            if self.msgToggle:
                self.omxvideo.toggleEvent -= self._onToggle
            if self.msgSeek:
                self.omxvideo.seekEvent -= self._onSeek
            if self.msgSpeed:
                self.omxvideo.speedEvent -= self._onSpeed

            self.omxvideo = None
        self.osc_output = None

    def _onLoad(self, omxvideo, path):
        self.osc_output.sendMessage(self.msgLoad, [path])

    def _onLoadIndex(self, omxvideo, idx):
        self.osc_output.sendMessage(self.msgLoadIndex, [idx])

    def _onUnload(self, omxvideo):
        self.osc_output.sendMessage(self.msgUnload)

    def _onStart(self, omxvideo, idx):
        self.osc_output.sendMessage(self.msgStart, [idx])

    def _onStop(self, omxvideo):
        self.osc_output.sendMessage(self.msgStop)

    def _onPlay(self, omxvideo):
        self.osc_output.sendMessage(self.msgPlay)

    def _onPause(self, omxvideo):
        self.osc_output.sendMessage(self.msgPause)

    def _onToggle(self, omxvideo):
        self.osc_output.sendMessage(self.msgToggle)

    def _onSeek(self, omxvideo, pos):
        self.osc_output.sendMessage(self.msgSeek, [pos])

    def _onSpeed(self, omxvideo, direction):
        self.osc_output.sendMessage(self.msgSpeed, [direction])

    def _getOption(self, optName):
        return self.options[optName] if optName in self.options else None
