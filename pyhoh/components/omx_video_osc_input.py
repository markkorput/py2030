from osc_input import OscInput
from utils.event import Event

class OmxVideoOscInput(OscInput):
    def set_omxvideo(self, omxvideo):
        self.omxvideo = omxvideo

    def _onDefault(self, addr, tags, data, client_address):
        if hasattr(self, 'omxvideo') and self.omxvideo:
            if addr == '/pyhoh/vid/play':
                self.omxvideo.play()
                return

            if addr == '/pyhoh/vid/start' and len(data) == 1:
                self.omxvideo.start(data[0])
                return

            if addr == '/pyhoh/vid/stop':
                self.omxvideo.stop()
                return

            if addr == '/pyhoh/vid/pause':
                self.omxvideo.pause()
                return

            if addr == '/pyhoh/vid/seek' and len(data) == 1:
                self.omxvideo.seek(data[0])
                return

            if addr == '/pyhoh/vid/load' and len(data) == 1:
                self.omxvideo.load(data[0])
                return
        else:
            self.logger.warning('no omxvideo provided')

        super(OmxVideoOscInput, self)._onDefault(addr, tags, data, client_address)
