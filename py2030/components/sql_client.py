import logging, unicodedata, json
from evento import Event
from py2030.base_component import BaseComponent

try:
    import _mssql
except ImportError:
    _mssql = None

def rowToDict(row):
    d = {}
    for k in row.iterkeys():
        if type(k).__name__ == 'unicode':
            value = row[k]
            if type(value).__name__ == 'unicode':
                # value = str(value)
                value = unicodedata.normalize('NFKD', value).encode('ascii','ignore')
            d[str(k)] = value

    return d

def getResponseDict(conn, result=None):
    data = []
    if result:
        data.append(rowToDict(result))

    for row in conn:
        data.append(rowToDict(row))
    return data


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

    def __del__(self):
        self.destroy()

    def setup(self, event_manager=None):
        if not _mssql:
            logging.getLogger(__name__).warning("_mssql module not available, sql_clients will not work")
        self.event_manager = event_manager
        if self.event_manager:
            # self.output_events = self.options['output_events'] if 'output_events' in self.options else {}
            if 'config_options' in self.options:
                self.event_manager.get(self.options['config_options']).subscribe(self._onConfig)

            if 'query_options' in self.options:
                self.event_manager.get(self.options['query_options']).subscribe(self._onQuery)

        # connect, only if we have all info we need
        if 'host' in self.options and 'database' in self.options and 'username' in self.options and 'password' in self.options:
            self._connect()

    def destroy(self):
        self.output_events = None
        self.event_manager = None
        self._disconnect()

    def _connect(self):
        # self.logger.warn('SqlClient _connect')
        if(self._connected):
            self._disconnect()

        host = self.options['host'] if 'host' in self.options else '127.0.0.1'
        port = self.options['port'] if 'port' in self.options else 1433
        db = self.options['database'] if 'database' in self.options else 'master'
        usr = self.options['username'] if 'username' in self.options else 'username'
        psw = self.options['password'] if 'password' in self.options else 'password'

        self.logger.info("SqlClient connecting to: "+host+':'+str(port))
        if _mssql:
            self._connection = _mssql.connect(server=host+':'+str(port), user=usr, password=psw, database=db)
        self._connected = True
        return self._connected

    def _disconnect(self):
        if self._connected:
            pass
            self._connected = False

    def _onConfig(self, opts):
        # self.logger.warn('SqlClient _onConfig, with: '+str(opts))

        self.options.update(opts)
        if 'host' in self.options and 'database' in self.options and 'username' in self.options and 'password' in self.options:
            self._connect() # (re-)connect

    def _onQuery(self, opts={}):
        if not self._connection:
            return
        query = "SELECT TOP 10 * FROM dbo.documents;"
        self.logger.info("running SQL query: "+query)
        result = self._connection.execute_row(query)
        data = getResponseDict(self._connection, result)
        self.logger.debug("query result size: "+str(len(data)))
        if 'response_event' in self.options and self.event_manager:
            event = self.event_manager.get(self.options['response_event'])
            event.fire(json.dumps(data))
