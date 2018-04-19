# import logging, threading, time, socket, os
# import http.client
# import urllib.parse
#
# from py2030.base_component import BaseComponent
# from BaseHTTPServer import HTTPServer
# from SimpleHTTPServer import SimpleHTTPRequestHandler
#
# def createRequestHandler(event_manager = None, _options = {}):
#     class CustomHandler(SimpleHTTPRequestHandler, object):
#         def __init__(self, *args, **kwargs):
#             # do_stuff_with(self, init_args)
#             self.options = _options
#             self.root_path = self.options['serve'] if 'serve' in _options else '.'
#             self.event_manager = event_manager
#             self.logger = logging.getLogger(__name__)
#             self.response_code = None
#             self.response_type = None
#             self.response_content = None
#
#             if 'verbose' in self.options and self.options['verbose']:
#                 self.logger.setLevel(logging.DEBUG)
#
#             if 'response_content_event' in self.options and self.event_manager:
#                 self.event_manager.get(self.options['response_content_event']).subscribe(self._onResponseContent)
#
#             super(CustomHandler, self).__init__(*args, **kwargs)
#
#         def process_request(self):
#             # print("PATH: " + self.path)
#             urlParseResult = urllib.parse.urlparse(self.path)
#             # print("URLPARSERESULT:", urlParseResult)
#
#
#             if self.event_manager != None and 'output_events' in self.options:
#                 if urlParseResult.path in self.options['output_events']:
#                     self.event_manager.fire(self.options['output_events'][urlParseResult.path])
#                     self.response_code = 200
#
#             if self.event_manager != None and 'output_options' in self.options:
#                 if urlParseResult.path in self.options['output_options']:
#                     event_name = self.options['output_options'][urlParseResult.path]
#                     event = self.event_manager.get(event_name)
#                     opts = {}
#
#                     try:
#                         opts = dict(qc.split("=") for qc in urlParseResult.query.split("&"))
#                     except ValueError as err:
#                         opts = {}
#
#                     # self.logger.warn('triggering options event `'+event_name+'` with: '+str(opts))
#                     self.response_code = 200
#                     event.fire(opts)
#
#             if 'responses' in self.options and urlParseResult.path in self.options['responses']:
#                 self.response_content = self.options['responses'][urlParseResult.path]
#                 # self.send_response(200)
#                 # self.send_header("Content-type", "text/plain")
#                 # self.end_headers()
#                 # # print('headers done')
#                 # self.wfile.write()
#                 # self.wfile.close()
#
#             if self.response_code == None:
#                 self.send_response(404)
#                 self.end_headers()
#                 self.wfile.close()
#                 return False
#
#             self.send_response(self.response_code)
#             self.send_header("Content-type", self.response_type if self.response_type else "text/plain")
#             self.end_headers()
#             if self.response_content:
#                self.wfile.write(self.response_content)
#             self.wfile.close()
#             return True
#
#         def do_HEAD(self):
#             if self.process_request():
#                 return
#             super(CustomHandler, self).do_HEAD()
#
#         def do_GET(self):
#             if self.process_request():
#                 return
#             super(CustomHandler, self).do_GET()
#
#         def do_POST(self):
#             if self.process_request():
#                 return
#             super(CustomHandler, self).do_POST()
#
#         def translate_path(self, path):
#             if self.event_manager != None and 'output_events' in self.options:
#                 if path in self.options['output_events']:
#                     self.event_manager.fire(self.options['output_events'][path])
#                     # self.send_error(204)
#                     self.send_response(200)
#                     self.wfile.write('OK')
#                     self.wfile.close()
#                     return ''
#
#             relative_path = path[1:] if path.startswith('/') else path
#             return SimpleHTTPRequestHandler.translate_path(self, os.path.join(self.root_path, relative_path))
#
#         def _onResponseContent(self, json):
#             # self.logger.warn('response CONTENT: '+str(json))
#             self.response_type = "application/json"
#             self.response_content = json
#
#     return CustomHandler
#
# class WebServer(BaseComponent, threading.Thread):
#     config_name = 'web_servers'
#
#     def __init__(self, options = {}):
#         threading.Thread.__init__(self)
#         self.options = options
#         self.http_server = None
#         self.event_manager = None
#         self.threading_event = None
#         self.daemon=True
#
#         # attributes
#         self.logger = logging.getLogger(__name__)
#         if 'verbose' in options and options['verbose']:
#             self.logger.setLevel(logging.DEBUG)
#
#     def __del__(self):
#         self.destroy()
#
#     def setup(self, event_manager=None):
#         self.event_manager = event_manager
#         self.logger.debug("Starting http server thread")
#         self.threading_event = threading.Event()
#         self.threading_event.set()
#         self.start() # start thread
#
#     def destroy(self):
#         self.event_manager = None
#
#         if not self.isAlive():
#             return
#
#         self.threading_event.clear()
#         self.logger.debug('Sending dummy HTTP request to stop HTTP server from blocking...')
#         try:
#             connection = http.client.HTTPSConnection("127.0.0.1", self.port())
#             connection.request('HEAD', '/')
#             connection.getresponse()
#         except socket.error:
#             pass
#
#         self.join()
#
#     # thread function
#     def run(self):
#         self.logger.info('Starting HTTP server on port {0}'.format(self.port()))
#         HandlerClass = createRequestHandler(self.event_manager, self.options)
#         self.http_server = HTTPServer(('', self.port()), HandlerClass)
#
#         # self.httpd.serve_forever()
#         # self.httpd.server_activate()
#         while self.threading_event.is_set(): #not self.kill:
#             try:
#                 self.http_server.handle_request()
#             except Exception as exc:
#                 print('http exception:')
#                 print(exc)
#
#         self.logger.info('Closing HTTP server at port {0}'.format(self.port()))
#         self.http_server.server_close()
#         self.http_server = None
#
#     def port(self):
#         return self.options['port'] if 'port' in self.options else 2031
#
# # for testing
# if __name__ == '__main__':
#     logging.basicConfig()
#     ws = WebServer({'verbose': True, 'serve': 'examples'})
#     try:
#         ws.setup()
#         while True:
#             time.sleep(.1)
#     except KeyboardInterrupt:
#         print('KeyboardInterrupt. Quitting.')
#
#     ws.destroy()
