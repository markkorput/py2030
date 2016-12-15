import logging

try:
    from OSC import OSCServer, NoCallbackError
except ImportError:
    logging.getLogger(__name__).warning("importing embedded version of pyOSC library")
    from py2030.dependencies.OSC import OSCServer, NoCallbackError

from evento import Event
import json

DEFAULT_PORT = 2030
DEFAULT_IP = ''

class OscInput:
    def __init__(self, options = {}):
        # attributes
        self.osc_server = None
        self.connected = False
        self.running = False
        self.osc_map = None
        self.logger = logging.getLogger(__name__)
        self.event_manager = None

        if 'verbose' in options and options['verbose']:
            self.logger.setLevel(logging.DEBUG)

        # events
        self.connectEvent = Event()
        self.disconnectEvent = Event()
        self.messageEvent = Event()

        # configuration
        self.options = {}
        self.configure(options)

    def __del__(self):
        self.destroy()

    def configure(self, options):
        previous_options = self.options
        self.options.update(options)

        if 'verbose' in options:
            if options['verbose']:
                self.logger.setLevel(logging.DEBUG)
            else:
                self.logger.setLevel(logging.INFO)

    def setup(self, event_manager=None):
        self.event_manager = event_manager
        if self.event_manager:
            self.output_events = self.options['output_events'] if 'output_events' in self.options else {}
        self.start()

    def destroy(self):
        self.output_events = None
        self.event_manager = None
        self.stop()

    def start(self):
        if self._connect():
            self.running = True

    def stop(self):
        if self.connected:
            self._disconnect()
        self.running = False

    def update(self):
        if not self.connected:
            return

        # we'll enforce a limit to the number of osc requests
        # we'll handle in a single iteration, otherwise we might
        # get stuck in processing an endless stream of data
        limit = 50
        count = 0

        # clear timed_out flag
        self.osc_server.timed_out = False

        # handle all pending requests then return
        # NOTE; if you get weird bugs because self.osc_server is None,
        # one of handled OSC messages probably triggered the destruction
        # of this component. This should not happen until after this update
        # loop is finished, so destructive operations should be queued for later
        while self.osc_server.timed_out == False and count < limit:
            try:
                self.osc_server.handle_request()
                count += 1
            except Exception as exc:
                self.logger.error("Something went wrong while handling incoming OSC messages:")
                self.logger.error(exc)

    def port(self):
        # default is 2030
        return int(self.options['port']) if 'port' in self.options else DEFAULT_PORT

    def host(self):
        # default is localhost
        return self.options['ip'] if 'ip' in self.options else DEFAULT_IP

    def _connect(self):
        if self.connected:
            self.logger.warning('already connected')
            return False

        try:
            self.osc_server = OSCServer((self.host(), self.port()))
        except Exception as err:
            # something went wrong, cleanup
            self.connected = False
            self.osc_server = None
            # notify
            self.logger.error("{0}\nOSC Server could not start @ {1}:{2}".format(err, self.host(), str(self.port())))
            # abort
            return False

        # register time out callback
        self.osc_server.handle_timeout = self._onTimeout
        self.osc_server.addMsgHandler('default', self._onDefault)

        # set internal connected flag
        self.connected = True
        # notify
        self.connectEvent(self)
        self.logger.info("OSC Server running @ {0}:{1}".format(self.host(), str(self.port())))
        return True

    def _disconnect(self):
        if self.osc_server:
            self.osc_server.close()
            self.connected = False
            self.osc_server = None
            self.disconnectEvent(self)
            self.logger.info('OSC Server ({0}:{1}) stopped'.format(self.host(), str(self.port())))

    def _onTimeout(self):
        if self.osc_server:
            self.osc_server.timed_out = True

    def _onDefault(self, addr, tags=[], data=[], client_address=''):
        # skip touch osc touch-up events
        # if len(data) == 1 and data[0] == 0.0:
        #     return
        self.logger.debug('osc-in {0}:{1} {2} [{3}] from {4}'.format(self.host(), self.port(), addr, ", ".join(map(lambda x: str(x), data)), client_address))
        self.messageEvent(addr, tags, data, client_address)

        # trigger events based on incoming messages if configured
        if addr in self.output_events:
            self.logger.debug('triggering output event: {0}'.format(self.output_events[addr]))
            self.event_manager.fire(self.output_events[addr])
        elif self.output_events['auto'] == True:
            self.logger.debug('triggering auto-output event: {0}'.format(addr))
            self.event_manager.fire(addr)
