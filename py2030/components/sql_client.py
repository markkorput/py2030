import logging, _mssql
from evento import Event
from py2030.base_component import BaseComponent

class SqlClient(BaseComponent):
    config_name = 'sql_clients'

    def __init__(self, options = {}):
        self.options = options
        self.event_manager = None
        self._connected = False
        self._connection = None

        self.logger = logging.getLogger(__name__)
        if 'verbose' in options and options['verbose']:
            self.logger.setLevel(logging.DEBUG)

        # events
        # self.connectEvent = Event()
        # self.disconnectEvent = Event()
        # self.messageEvent = Event()

    def __del__(self):
        self.destroy()

    def setup(self, event_manager=None):
        self.event_manager = event_manager
        if self.event_manager:
            # self.output_events = self.options['output_events'] if 'output_events' in self.options else {}
            if 'config_options' in self.options:
                self.event_manager.get(self.options['config_options']) += self._onConfig
        # connect, only if we have all info we need
        if 'host' in self.options and 'database' in self.options and 'username' in self.options and 'password' in self.options:
            self._connect()

    def destroy(self):
        self.output_events = None
        self.event_manager = None
        self._disconnect()

    def _connect(self):
        if(self._connected)
            self._disconnect()

        host = self.options['host'] if 'host' in self.options else '127.0.0.1'
        port = self.options['port'] if 'port' in self.options else 1433
        db = self.options['database'] if 'database' in self.options else 'master'
        usr = self.options['username'] if 'username' in self.options else 'username'
        psw = self.options['password'] if 'password' in self.options else 'password'

        self.logger.info("SqlClient connecting to: "+host+':'+str(port))
        self._connection = _mssql.connect(server=host+':'+str(port), user=usr, password=psw, database=db)
        self._connected = True
        return self._connected

    def _disconnect(self):
        if self._connected:
            pass
            self._connected = False

    def _onConfig(self, opts={}):
        self.options.update(opts)
        if 'host' in self.options and 'database' in self.options and 'username' in self.options and 'password' in self.options:
            self._connect() # (re-)connect


# #!/usr/bin/env python
# from optparse import OptionParser
#
# import _mssql
#
# def doInfo(opts):
#     # jdbc:jtds:sqlserver://192.168.1.25:1433
#     print("\nserver: "+opts.server)
#     print("database: "+opts.db)
#     print("usr: "+opts.user)
#     print("psw: "+opts.password)
#
#     conn = _mssql.connect(server=opts.server, user=opts.user, password=opts.password, database=opts.db)
#     query = "SELECT TOP 3 * FROM dbo.medialibrary;"
#     print("\nRunning query:\n"+query)
#     result = conn.execute_row(query)
#     print("\nResult:")
#     print(str(result)+"\n")
#
#
# if __name__ == '__main__':
#     parser = OptionParser()
#     parser.add_option("-i", "--info", dest="info", action="store_true")
#     parser.add_option("-s", "--server", dest="server", default="192.168.1.25:1433")
#     parser.add_option("-d", "--db", dest="db", default="cubo")
#     parser.add_option("-u", "--user", dest="user", default="cubo")
#     parser.add_option("-p", "--psw", "--password", dest="password", default="cubo")
#
#     options, args = parser.parse_args()
#
#     if options.info:
#         doInfo(options)
