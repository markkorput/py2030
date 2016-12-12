import logging

try:
    from omxsync import Receiver
    from omxsync import Broadcaster
except ImportError:
    logging.getLogger(__name__).warning("Can't import omxsync")
    Receiver = None
    Broadcaster = None

class OmxSyncer:
    def __init__(self, options = {}):
        # config
        self.options = options
        # attributes
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG if 'verbose' in options and options['verbose'] else logging.INFO)
        self.receiver = None
        self.broadcaster = None
        self.omxvideo = None
        self.player = None

    def __del__(self):
        self.destroy()

    def setup(self, omxvideo):
        self.destroy()
        self.set_omxvideo(omxvideo)

    def destroy(self):
        self.set_player(None)
        self.set_omxvideo(None)

    def update(self):
        if self.receiver:
            self.receiver.update()
        if self.broadcaster:
            self.broadcaster.update()

    def isMaster(self):
        return 'master' in self.options and self.options['master']

    def set_omxvideo(self, omxvideo):
        # unregister from any previous omxvideo
        if self.omxvideo:
            self.omxvideo.loadEvent -= self._onLoad
            self.omxvideo.unloadEvent -= self._onUnload

        # register with new omxvideo
        self.omxvideo = omxvideo
        if self.omxvideo:
            self.omxvideo.loadEvent += self._onLoad
            self.omxvideo.unloadEvent += self._onUnload
            # loads player
            self.set_player(self.omxvideo.player)

    def set_player(self, player):
        if self.receiver:
            self.receiver.destroy()
            self.receiver = None

        if self.broadcaster:
            self.broadcaster.destroy()
            self.broadcaster = None

        if not player:
            return

        if self.isMaster():
            if Broadcaster:
                self.broadcaster = Broadcaster(player, self.options)
                self.broadcaster.setup()
            else:
                self.logger.warning("omxsync not loaded, can't create Broadcaster instance")
            return

        if Receiver:
            self.receiver = Receiver(player, self.options)
            self.receiver.setup()
        else:
            self.logger.warning("omxsync not loaded, can't create Receiver instance")

    def _onLoad(self, omxvideo, path):
        self.set_player(omxvideo.player)

    def _onUnload(self, omxvideo):
        self.set_player(None)
