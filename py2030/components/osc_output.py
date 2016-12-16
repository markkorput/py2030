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

class EventMessage:
    def __init__(self, osc_output, event, message):
        self.event = event
        self.osc_output = osc_output
        self.message = message
        self.event += self._send

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self.event:
            self.event -= self._send
            self.event = None

    def _send(self):
        self.osc_output.send(self.message)

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
        self.host_cache = None
        self.event_manager = None
        self._event_messages = []

        # events
        self.connectEvent = Event()
        self.disconnectEvent = Event()
        self.messageEvent = Event()

    def __del__(self):
        self.destroy()

    def setup(self, event_manager=None):
        self._connect()
        self.event_manager = event_manager
        if event_manager != None:
            self._registerCallbacks()

    def destroy(self):
        if self.event_manager != None:
            self._registerCallbacks(False)
            self.event_manager = None

        if self.connected:
            self._disconnect()

    def _registerCallbacks(self, _register=True):
        if not _register:
            for event_message in self._event_messages:
                event_message.destroy()
            self._event_messages = []
            return

        if not 'input_events' in self.options:
            return

        for event_id, message in self.options['input_events'].items():
            self._event_messages.append(EventMessage(self, self.event_manager.get(event_id), message))

    def _onEvent(self, event_id):
        if event_id in self.options['input_events']:
            self.send(self.options['input_events'][event_id])

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

    def send(self, addr, data=[]):
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
