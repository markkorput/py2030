import logging

try:
    from omxsync import Receiver
    from omxsync import Broadcaster
except ImportError:
    logging.getLogger(__name__).warning("Can't import omxsync")
    Receiver = None
    Broadcaster = None

class OmxSync:
    def __init__(self, options = {}):
        # config
        self.options = options
        # attributes
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG if 'verbose' in options and options['verbose'] else logging.INFO)
        self.receiver = None
        self.broadcaster = None
        self.player = None

    def __del__(self):
        self.destroy()

    def setup(self, player):
        self.destroy()
        self.player = player

        if player:
            if self.isMaster():
                if not Broadcaster:
                    self.logger.warning("omxsync not loaded, can't create Broadcaster instance")
                    return
                self.broadcaster = Broadcaster(player, self.options)
            else:
                if not Receiver:
                    self.logger.warning("omxsync not loaded, can't create Receiver instance")
                    return
                self.receiver = Receiver(player, self.options)

    def destroy(self):
        if self.receiver:
            self.receiver.destroy()
            self.receiver = None

        self.player = None

    def update(self):
        if self.receiver:
            self.receiver.update()
        if self.broadcaster:
            self.broadcaster.update()

    def isMaster(self):
        return 'master' in self.options and self.options['master']
