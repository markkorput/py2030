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

            if addr.startswith('/pyhoh/vid/start/'):
                try:
                    number = int(addr.replace('/pyhoh/vid/start/', ''))
                except ValueError:
                    self.logger.warning('invalid osc message: {0}'.format(addr))
                    return
                self.omxvideo.start(number)
                return

            if addr == '/pyhoh/vid/stop':
                self.omxvideo.stop()
                return

            if addr == '/pyhoh/vid/pause':
                self.omxvideo.pause()
                return

            if addr == '/pyhoh/vid/toggle':
                self.omxvideo.toggle()
                return

            if addr == '/pyhoh/vid/seek' and len(data) == 1:
                self.omxvideo.seek(data[0])
                return

            if addr.startswith('/pyhoh/vid/seek/'):
                try:
                    number = float(addr.replace('/pyhoh/vid/seek/', ''))
                except ValueError:
                    self.logger.warning('invalid osc message: {0}'.format(addr))
                    return
                self.omxvideo.seek(number)
                return

            if addr == '/pyhoh/vid/load' and len(data) == 1:
                self.omxvideo.load(data[0])
                return

            if addr.startswith('/pyhoh/vid/load/'):
                try:
                    number = int(addr.replace('/pyhoh/vid/load/', ''))
                except ValueError:
                    self.logger.warning('invalid osc message: {0}'.format(addr))
                    return
                self.omxvideo.load(number)
                return
        else:
            self.logger.warning('no omxvideo provided')

        OscInput._onDefault(self, addr, tags, data, client_address)
