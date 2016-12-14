import socket, logging, paramiko

class SshRemote:
    def __init__(self, options = {}):
        self.options = options
        self.ip = self.options['ip'] if 'ip' in options else None
        self.hostname = self.options['hostname'] if 'hostname' in self.options else None
        self.username = self.options['username'] if 'username' in self.options else None
        self.password = self.options['password'] if 'password' in self.options else None
        self.connected = False
        self.client = None

        self.logger = logging.getLogger(__name__)
        if 'verbose' in self.options and self.options['verbose']:
            self.logger.setLevel(logging.DEBUG)

    def __del__(self):
        self.destroy()

    def setup(self):
        if self.ip == None:
            self.ip = SshRemote._hostname_to_ip(self.hostname)

        if self.ip == None:
            self.logger.warning("Could not resolve IP address from hostname: {0}".format(self.hostname))
            return

        if not self.connect():
            self.logger.warning('Failed to connect, cannot perform file sync')
            return

        self.perform_sync()

    def destroy(self):
        self.ip = self.options['ip'] if 'ip' in self.options else None

        if self.connected:
            self.disconnect()

    def perform_sync(self):
        # get remote file timestamps

        # copy local file to remote if newer
        pass

    def connect(self):
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
        self.logger.debug('Performing put command with local file path {0} remote file path {1}'.format(local_file_path, remote_file_name))
        with SCPClient(self.client.get_transport()) as scp:
            scp.put(local_file_path, remote_file_name)

    def get(self, remote_file_name):
        self.logger.debug('Performing get command with remote file path {0}'.format(remote_file_name))
        with SCPClient(self.client.get_transport()) as scp:
            scp.get(remote_file_name)

    @classmethod
    def _hostname_to_ip(cls, hostname):
        try:
            return socket.gethostbyname(hostname)
        except socket.gaierror as err:
            pass

        try:
            return socket.gethostbyname(hostname+'.local')
        except socket.gaierror as err:
            pass

        return
#
#
# import paramiko, os, re, time, subprocess, socket
# from scp import SCPClient
# from py2030.utils.color_terminal import ColorTerminal
#
# class SshRemoteOriginal:
#     def __init__(self, ip=None, username=None, password=None, hostname=None):
#         self.ip = ip
#         self.username = username
#         self.password = password
#         self.hostname = hostname
#
#         self.connected = False
#         self.client = None
#
#         # these will hold exec command results
#         self.stdin = None
#         self.stdout = None
#         self.stderr = None
#
#
#
#     def __del__(self):
#         self.destroy()
#
#     def destroy(self):
#         if self.connected:
#             self.disconnect()
#
#     def connect(self):
#         if not self.ip:
#             print "no ip for hostname ({0}), can't connect".format(self.hostname)
#             return False
#
#         # if self.connected:
#         #     return None
#         self.client = paramiko.SSHClient()
#         self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#         try:
#             self.client.connect(self.ip, username=self.username, password=self.password)
#         except paramiko.ssh_exception.AuthenticationException as err:
#             ColorTerminal().fail('[SshRemote] ssh authentication failed on host {0} ({1})'.format(self.ip, self.hostname))
#             self.connected = False
#             return False
#
#         ColorTerminal().green('ssh connection established with {0} (hostname: {1})'.format(self.ip, self.hostname))
#         self.connected = True
#         return True
#
#     def disconnect(self):
#         if self.client:
#             self.client.close()
#             ColorTerminal().yellow('ssh connection closed with {0} (hostname: {1})'.format(self.ip, self.hostname))
#             self.client = None
#
#     def cmd(self, command, wait=True):
#         print "ssh-cmd:\n", command
#         self.stdin, self.stdout, self.stderr = self.client.exec_command(command)
#         if wait:
#             for line in self.stdout:
#                 pass
#             for line in self.stderr:
#                 try:
#                     print '[STDERR]',str(line.strip('\n'))
#                 except UnicodeEncodeError as err:
#                     print '[STDERR] (unicode issue with printing error);'
#                     print err
#
#     def put(self, local_file_path, remote_file_name):
#         print "ssh-put:", local_file_path, remote_file_name
#         with SCPClient(self.client.get_transport()) as scp:
#             scp.put(local_file_path, remote_file_name)
#
#     def get(self, remote_file_name):
#         print "ssh-get:", remote_file_name
#         with SCPClient(self.client.get_transport()) as scp:
#             scp.get(remote_file_name)
