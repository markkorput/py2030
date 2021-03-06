import socket
import logging
from py2030.base_component import BaseComponent

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

        # if type(message) == type([]) or type(message) == type(()):
        if hasattr(message, '__iter__'):
            tmp = self
            if len(message) > 0:
                self.message = message[0] # first one is the OSC-message
                self.arguments= message[1:] # all except first one are the OSC arguments
        else:
            self.message = message # only a message
            self.arguments = [] # no arguments

        self.event += self._send

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self.event:
            self.event -= self._send
            self.event = None

    def _send(self, *args, **kargs):
        if len(args) == 0:
            # take arguments from the initial configuration
            self.osc_output.send(self.message, self.arguments)
        else:
            # take arguments from the triggered event
            self.osc_output.send(self.message, args)

class OscOutput(BaseComponent):
    config_name = 'osc_outputs'

    def __init__(self, options = {}):
        BaseComponent.__init__(self, options)

        self.client = None
        self.connected = False
        self.host_cache = None
        self._event_messages = []

    def __del__(self):
        self.destroy()

    def setup(self, event_manager=None):
        BaseComponent.setup(self, event_manager)

        # events
        self.connectEvent = self.getOutputEvent('connect')
        self.disconnectEvent = self.getOutputEvent('disconnect')
        self.messageEvent = self.getOutputEvent('message', dummy=False)

        if event_manager != None:
            self._registerCallbacks()

        if self.getOption('autoStart', True):
            self._connect()

    def destroy(self):
        if self.event_manager != None:
            self._registerCallbacks(False)
            self.event_manager = None

        if self.connected:
            self._disconnect()

    def _registerCallbacks(self, _register=True):
        # UNregister
        if not _register:
            for event_message in self._event_messages:
                event_message.destroy()
            self._event_messages = []
            return

        # nothing to register?
        if not 'input_events' in self.options:
            return

        for event_id, message in self.options['input_events'].items():
            self._registerEventMessage(event_id, message)

    def _registerEventMessage(self, event_id, message):
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
        if self.messageEvent:
            self.messageEvent(msg, self)
