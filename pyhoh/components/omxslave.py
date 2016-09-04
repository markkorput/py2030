import logging

try:
    from omxsync import Receiver
except ImportError:
    logging.getLogger(__name__).warning("Can't import omxsync")
    Receiver = None

class OmxSlave:
    def __init__(self, options = {}):
        # config
        self.options = options
        # attributes
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG if 'verbose' in options and options['verbose'] else logging.INFO)
        self.receiver = None
        self.player = None

    def __del__(self):
        self.destroy()

    def setup(self, player):
        self.destroy()
        self.player = player
        if player:
            if not Receiver:
                self.logger.warning("omxsync not loaded, can't create omxsync.Receiver instance")
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
