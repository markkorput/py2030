import socket, logging
from glob import glob

try:
    from scp import SCPClient, SCPException
except ImportError as err:
    SCPClient = False
    SCPException = False
    logging.getLogger(__name__).warning("importing of SCP classes failed, SshRemote component will not work.")

try:
    import paramiko
except ImportError as err:
    paramiko = False
    logging.getLogger(__name__).warning("importing of paramiko failed, SshRemote component will not work.")

class SshRemote:
    def __init__(self, options = {}):
        self.options = options
        self.ip = self.options['ip'] if 'ip' in options else None
        self.hostname = self.options['hostname'] if 'hostname' in self.options else None
        self.username = self.options['username'] if 'username' in self.options else None
        self.password = self.options['password'] if 'password' in self.options else None
        self.connected = False
        self.client = None
        self._operations = {}
        self.event_manager = None

        self.logger = logging.getLogger(__name__)
        if 'verbose' in self.options and self.options['verbose']:
            self.logger.setLevel(logging.DEBUG)

    def __del__(self):
        self.destroy()

    def setup(self, event_manager=None):
        self.event_manager = event_manager
        if 'files' in self.options:
            for local_pattern, remote_path in self.options['files'].items():
                local_files = glob(local_pattern)
                for local_file in local_files:
                    self._operations[local_file] = remote_path

        if self.ip == None:
            self.ip = SshRemote._hostname_to_ip(self.hostname)

        if self.ip == None:
            self.logger.warning("Could not resolve IP address from hostname: {0}".format(self.hostname))
            return

        if not self.connect():
            self.logger.warning('Failed to connect, cannot perform file sync')
            return

    def destroy(self):
        self.ip = self.options['ip'] if 'ip' in self.options else None

        if self.connected:
            self.disconnect()

        self._operations = {}
        self.event_manager = None

    def update(self):
        if self.isDone():
            return

        if not self.connected:
            if not self.connect():
                self.logger.warning('Failed to connect, cannot perform file sync')
                return

        key = self._operations.keys()[0]
        if self.process(key, self._operations[key]):
            del self._operations[key]

        if self.isDone():
            if self.event_manager and 'done_event' in self.options:
                self.event_manager.fire(self.options['done_event'])

    def isDone(self):
        return len(self._operations) <= 0

    def connect(self):
        if not paramiko:
            self.logger.warning("Paramiko not loaded, can't connect")
            return False

        if not self.ip:
            self.logger.warning("Can't connect without ip")
            return False

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.client.connect(self.ip, username=self.username, password=self.password)
        except paramiko.ssh_exception.AuthenticationException as err:
            self.logger.error("ssh authentication failed with host {0}".format(self.hostname if self.hostname else self.ip))
            return False

        self.connected = True
        return True

    def disconnect(self):
        if self.client:
            self.client.close()
            self.logger.debug("ssh connection closed with host {0}".format(self.hostname if self.hostname else self.ip))
            self.client = None
        self.connected = False

    def cmd(self, command, wait=True):
        self.logger.debug('Performing command: {0}'.format(command))
        self.stdin, self.stdout, self.stderr = self.client.exec_command(command)

        if not wait:
            return

        for line in self.stdout:
            pass

        errlines = []
        for line in self.stderr:
            errlines.append(str(line.strip('\n')))

        if len(errlines) > 0:
            try:
                self.logger.warning("stderr response:\n{0}".format("\n".join(errlines)))
            except UnicodeEncodeError as err:
                print 'unicode issue with printing stderr response'

    def put(self, local_file_path, remote_file_name):
        self.logger.debug('PUT ({2}) {0} -> {1} '.format(local_file_path, remote_file_name, self.ip if self.ip else self.hostname))

        if not SCPClient:
            self.logger.warning("SCPClient not available, cannot perform SCP-PUT operation")
            return

        with SCPClient(self.client.get_transport()) as scp:
            try:
                scp.put(local_file_path, remote_file_name)
            except SCPException as exception:
                self.logger.error('File transfer error:\n\n'+str(exception))

    def get(self, remote_file_name):
        self.logger.debug('Performing get command with remote file path {0}'.format(remote_file_name))

        if not SCPClient:
            self.logger.warning("SCPClient not available, cannot perform SCP-GET operation")
            return

        with SCPClient(self.client.get_transport()) as scp:
            scp.get(remote_file_name)

    def process(self, local_path, remote_path):
        self.put(local_path, remote_path)
        return True

    @classmethod
    def _hostname_to_ip(cls, hostname):
        if hostname == None:
            return None

        try:
            return socket.gethostbyname(hostname)
        except socket.gaierror as err:
            pass

        try:
            return socket.gethostbyname(hostname+'.local')
        except socket.gaierror as err:
            pass

        return
