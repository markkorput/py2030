import logging, threading, time, socket, httplib, os

from py2030.base_component import BaseComponent
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler

def createRequestHandler(event_manager = None, _options = {}):
    class CustomHandler(SimpleHTTPRequestHandler, object):
        def __init__(self, *args, **kwargs):
            # do_stuff_with(self, init_args)
            self.options = _options
            self.root_path = self.options['serve'] if 'serve' in _options else '.'
            self.event_manager = event_manager
            super(CustomHandler, self).__init__(*args, **kwargs)

        def process_request(self):
            result = False
            if self.event_manager != None and 'output_events' in self.options:
                if self.path in self.options['output_events']:
                    self.event_manager.fire(self.options['output_events'][self.path])
                    result = True

            if 'responses' in self.options and self.path in self.options['responses']:
                self.wfile.write(self.options['responses'][self.path])
                # self.wfile.close()
                result = True
            elif result == True:
                self.send_response(200)
                self.end_headers()

            return result

        def do_HEAD(self):
            if self.process_request():
                return
            super(CustomHandler, self).do_HEAD()

        def do_GET(self):
            if self.process_request():
                return
            super(CustomHandler, self).do_GET()

        def do_POST(self):
            if self.process_request():
                return
            super(CustomHandler, self).do_POST()

        def translate_path(self, path):
            if self.event_manager != None and 'output_events' in self.options:
                if path in self.options['output_events']:
                    self.event_manager.fire(self.options['output_events'][path])
                    # self.send_error(204)
                    self.send_response(200)
                    self.wfile.write('OK')
                    self.wfile.close()
                    return ''

            relative_path = path[1:] if path.startswith('/') else path
            return SimpleHTTPRequestHandler.translate_path(self, os.path.join(self.root_path, relative_path))

    return CustomHandler

class WebServer(BaseComponent, threading.Thread):
    config_name = 'web_servers'

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
        self.logger.info('Starting HTTP server on port {0}'.format(self.port()))
        HandlerClass = createRequestHandler(self.event_manager, self.options)
        self.http_server = HTTPServer(('', self.port()), HandlerClass)

        # self.httpd.serve_forever()
        # self.httpd.server_activate()
        while self.threading_event.is_set(): #not self.kill:
            try:
                self.http_server.handle_request()
            except Exception as exc:
                print 'http exception:'
                print exc

        self.logger.info('Closing HTTP server at port {0}'.format(self.port()))
        self.http_server.server_close()
        self.http_server = None

    def port(self):
        return self.options['port'] if 'port' in self.options else 2031

# for testing
if __name__ == '__main__':
    logging.basicConfig()
    ws = WebServer({'verbose': True, 'serve': 'examples'})
    try:
        ws.setup()
        while True:
            time.sleep(.1)
    except KeyboardInterrupt:
        print 'KeyboardInterrupt. Quitting.'

    ws.destroy()
