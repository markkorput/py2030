import json, socket
import logging
from evento import Event

try:
    import OSC
except ImportError:
    logging.getLogger(__name__).warning("importing embedded version of pyOSC library")
    import py2030.dependencies.OSC as OSC

DEFAULT_PORT = 2030
DEFAULT_HOST = '255.255.255.255'

class OscOutput:
    def __init__(self, options = {}):
        # config
        self.options = options

        # attributes
        self.logger = logging.getLogger(__name__)
        if 'verbose' in options and options['verbose']:
            self.logger.setLevel(logging.DEBUG)

        self.client = None
        self.connected = False
        self.running = False
        self.host_cache = None

        # events
        self.connectEvent = Event()
        self.disconnectEvent = Event()
        self.messageEvent = Event()

    def __del__(self):
        self.destroy()

    def setup(self):
        self.start()

    def destroy(self):
        if self.running:
            self.stop()

    def start(self):
        if self._connect():
            self.running = True

    def stop(self):
        self._disconnect()
        self.running = False

    def port(self):
        return int(self.options['port']) if 'port' in self.options else DEFAULT_PORT

    def hostname(self):
        return self.options['hostname'] if 'hostname' in self.options else None

    def host(self):
        if self.host_cache:
            return self.host_cache

        if not 'ip' in self.options and 'hostname' in self.options:
            try:
                self.host_cache = socket.gethostbyname(self.options['hostname'])
                return self.host_cache
            except socket.gaierror as err:
                self.logger.error("Could not get IP from hostname: {0}".format(self.options['hostname']))
                self.logger.error(str(err))

        # default is localhost
        self.host_cache = self.options['ip'] if 'ip' in self.options else None
        return self.host_cache

    def _connect(self):
        target = self.host()
        if not target:
            self.logger.warning("no host, can't connect")
            return

        try:
            self.client = OSC.OSCClient()
            if target.endswith('.255'):
                self.logger.info('broadcast target detected')
                self.client.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.client.connect((target, self.port()))
        except OSC.OSCClientError as err:
            self.logger.error("OSC connection failure: {0}".format(err))
            return False

        self.connected = True
        self.connectEvent(self)
        self.logger.info("OSC client connected to {0}:{1} (hostname: {2})".format(self.host(), str(self.port()), self.hostname()))
        return True

    def _disconnect(self):
        if self.client:
            self.client.close()
            self.client = None
            self.disconnectEvent(self)
            self.logger.info("OSC client ({0}:{1}) closed".format(self.host(), self.port()))

        self.connected = False

    def sendMessage(self, addr, data=[]):
        msg = OSC.OSCMessage()
        msg.setAddress(addr) # set OSC address

        for item in data:
            msg.append(item)

        if self.connected:
            try:
                self.client.send(msg)
            except OSC.OSCClientError as err:
                pass
            except AttributeError as err:
                self.logger.error('[osc-out {0}:{1}] error:'.format(self.host(), self.port()))
                self.logger.error(str(err))
                # self.stop()

        self.logger.debug('osc-out {0}:{1} - {2} [{3}]'.format(self.host(), self.port(), addr, ", ".join(map(lambda x: str(x), data))))
        self.messageEvent(msg, self)
