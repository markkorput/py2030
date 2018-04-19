import logging, threading
from py2030.base_component import BaseComponent

try:
    from pythonosc import dispatcher
    from pythonosc import osc_server
except ImportError:
    logging.getLogger(__name__).warning("failed to load pythonosc dependency; osc_input component will not work")
    osc_server = None
    dispatcher = None

# try:
#     from OSC import OSCServer, NoCallbackError
# except ImportError:
#     logging.getLogger(__name__).warning("importing embedded version of pyOSC library")
#     # from py2030.dependencies.OSC import OSCServer, NoCallbackError


DEFAULT_PORT = 2030
DEFAULT_IP = ''

class OscInput(BaseComponent):
    config_name = 'osc_inputs'

    def __init__(self, options = {}):
        BaseComponent.__init__(self, options)

        # attributes
        self.osc_server = None
        self.connected = False
        self.running = False
        self.osc_map = None
        self.thread = None

    def __del__(self):
        self.destroy()

    def setup(self, event_manager=None):
        BaseComponent.setup(self, event_manager)

        self.msgEventMapping = self.getOption('output_events', {})
        self.autoAddrToEvent = 'auto' in self.msgEventMapping and self.msgEventMapping['auto']

        # events
        self.connectEvent = self.getOutputEvent('connect')
        self.disconnectEvent = self.getOutputEvent('disconnect')
        self.messageEvent = self.getOutputEvent('message', dummy=False) # can be None if not configured
        self.argEvents = self.getOption('argEvents', {})

        if self.getOption('autoStart', True):
            self.start()

    def destroy(self):
        self.msgEventMapping = None
        self.event_manager = None
        self.stop()

    def start(self):
        if self._connect():
            self.running = True

    def stop(self):
        if self.connected:
            self._disconnect()
        self.running = False

    def port(self):
        return self.getOption('port', DEFAULT_PORT)

    def host(self):
        return self.getOption('ip', DEFAULT_IP)

    def _connect(self):
        if self.connected:
            self.logger.warning('already connected')
            return False

        if osc_server == None:
            self.logger.warning('No pythonosc')
            return False

        disp = dispatcher.Dispatcher()
        disp.map("*", self._onOscMsg)
        # disp.map("/logvolume", print_compute_handler, "Log volume", math.log)

        self.osc_server = osc_server.ThreadingOSCUDPServer((self.host(), self.port()), disp)
        self.osc_server.serve_forever()

        # set internal connected flag
        self.connected = True
        # notify
        self.connectEvent(self)
        self.logger.info("OSC Server running @ {0}:{1}".format(self.host(), str(self.port())))

        return True

    def _disconnect(self):
        if self.osc_server:
            self.osc_server.shutdown()
            self.connected = False
            self.osc_server = None
            self.disconnectEvent(self)
            self.logger.info('OSC Server ({0}:{1}) stopped'.format(self.host(), str(self.port())))

    def _onOscMsg(self, addr, *args):
        # skip touch osc touch-up events
        # if len(data) == 1 and data[0] == 0.0:
        #     return

        self.logger.debug('osc-in {0}:{1} {2} [{3}]'.format(self.host(), self.port(), addr, ", ".join(map(lambda x: str(x), args))))

        if self.messageEvent:
            # self.messageEvent(addr, tags, data, client_address)
            self.messageEvent(addr, args)

        # trigger events based on incoming messages if configured
        if addr in self.msgEventMapping:
            self.logger.debug('triggering output event: {0}'.format(self.msgEventMapping[addr]))
            self.event_manager.fire(self.msgEventMapping[addr])
        elif self.autoAddrToEvent:
            self.logger.debug('triggering auto-output event: {0}'.format(addr))
            self.event_manager.fire(addr)

        # this doesnt work yet?!
        if addr in self.argEvents.keys():
            print('triggering argEvent:', addr)
            self.event_manager.get(self.argEvents[addr]).fire(args)
