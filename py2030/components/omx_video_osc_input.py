from .osc_input import OscInput
from evento import Event

class OmxVideoOscInput(OscInput):
    def set_omxvideo(self, omxvideo):
        self.omxvideo = omxvideo

    def _onDefault(self, addr, tags, data, client_address):
        if hasattr(self, 'omxvideo') and self.omxvideo:
            if addr == '/py2030/vid/play':
                self.omxvideo.play()
                return

            if addr == '/py2030/vid/start' and len(data) == 1:
                self.omxvideo.start(data[0])
                return

            if addr.startswith('/py2030/vid/start/'):
                try:
                    number = int(addr.replace('/py2030/vid/start/', ''))
                except ValueError:
                    self.logger.warning('invalid osc message: {0}'.format(addr))
                    return
                self.omxvideo.start(number)
                return

            if addr == '/py2030/vid/stop':
                self.omxvideo.stop()
                return

            if addr == '/py2030/vid/pause':
                self.omxvideo.pause()
                return

            if addr == '/py2030/vid/toggle':
                self.omxvideo.toggle()
                return

            if addr == '/py2030/vid/seek' and len(data) == 1:
                self.omxvideo.seek(data[0])
                return

            if addr.startswith('/py2030/vid/seek/'):
                try:
                    number = float(addr.replace('/py2030/vid/seek/', ''))
                except ValueError:
                    self.logger.warning('invalid osc message: {0}'.format(addr))
                    return
                self.omxvideo.seek(number)
                return

            if addr == '/py2030/vid/load' and len(data) == 1:
                self.omxvideo.load(data[0])
                return

            if addr.startswith('/py2030/vid/load/'):
                try:
                    number = int(addr.replace('/py2030/vid/load/', ''))
                except ValueError:
                    self.logger.warning('invalid osc message: {0}'.format(addr))
                    return
                self.omxvideo.load(number)
                return
        else:
            self.logger.warning('no omxvideo provided')

        OscInput._onDefault(self, addr, tags, data, client_address)
