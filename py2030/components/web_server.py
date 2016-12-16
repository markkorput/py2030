import logging, threading, time, socket, httplib

from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler

class LocalRequestHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # print '[MyRequestHandler] translate_path:', path
        if path.endswith('config.yaml'):
            #     print 'assumed config.yaml'
            return SimpleHTTPRequestHandler.translate_path(self, '/config/config.yaml')

        return SimpleHTTPRequestHandler.translate_path(self, path)


class WebServer(threading.Thread):
    def __init__(self, options = {}):
        threading.Thread.__init__(self)
        self.options = options
        self.http_server = None
        self.event_manager = None
        self.threading_event = None
        self.daemon=True

        # attributes
        self.logger = logging.getLogger(__name__)
        if 'verbose' in options and options['verbose']:
            self.logger.setLevel(logging.DEBUG)

    def __del__(self):
        self.destroy()

    def setup(self, event_manager=None):
        self.event_manager = event_manager
        self.logger.debug("Starting http server thread")
        self.threading_event = threading.Event()
        self.threading_event.set()
        self.start() # start thread

    def destroy(self):
        self.event_manager = None

        if not self.isAlive():
            return

        self.threading_event.clear()
        self.logger.debug('Sending dummy HTTP request to stop HTTP server from blocking...')
        try:
            connection = httplib.HTTPConnection('127.0.0.1', self.port())
            connection.request('HEAD', '/')
            connection.getresponse()
        except socket.error:
            pass

        self.join()

    # thread function
    def run(self):
        self.logger.debug('Starting HTTP server on port {0}'.format(self.port()))
        self.http_server = HTTPServer(('', self.port()), LocalRequestHandler)

        # self.httpd.serve_forever()
        # self.httpd.server_activate()
        while self.threading_event.is_set(): #not self.kill:
            try:
                self.http_server.handle_request()
            except Exception as exc:
                print 'http exception:'
                print exc

        self.logger.debug('Closing HTTP server at port {0}'.format(self.port()))
        self.http_server.server_close()
        self.http_server = None

    def port(self):
        return self.options['port'] if 'port' in self.options else 2031

# for testing
if __name__ == '__main__':
    logging.basicConfig()
    ws = WebServer({'verbose': True})
    try:
        ws.setup()
        while True:
            time.sleep(.1)
    except KeyboardInterrupt:
        print 'KeyboardInterrupt. Quitting.'
        ws.destroy()
        print 'thread closed'
