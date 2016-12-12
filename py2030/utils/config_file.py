import os, yaml, time, shutil
import logging
logger = logging.getLogger(__name__)

from evento import Event

class ConfigFile:
    def __init__(self, path, options = {}):
        # config
        self.path = path

        # attributes
        self.previous_data = None
        self.data = None

        # events
        self.dataLoadedEvent = Event()
        self.dataChangeEvent = Event()

        # config
        self.options = {}
        self.configure(options)

    def configure(self, options):
        previous_options = self.options
        self.options.update(options)

    def load(self, options = {}):
        # already have data loaded?
        if self.data != None:
            # we'll need the {'force': True} option to force a reload
            if not 'force' in options or options['force'] != True:
                # abort
                return

        content = self.read()
        if not content:
            return

        if self.path.endswith('.yaml') or self.path.endswith('.yml'):
            self.loadYaml(content)
        else:
            logger.warning('[ConfigFile] could not determine config file data format from file name ({0}), assuming yaml'.format(self.path))
            self.loadYaml(content)

    def loadYaml(self, content):
        try:
            new_data = yaml.load(content)
        except:
            logger.warning("[ConfigFile] yaml corrupted ({0}), can't load data".format(self.path))
            return
        self.setData(new_data)

    def setData(self, new_data):
        self.previous_data = self.data
        self.data = new_data
        if self.previous_data != new_data:
            if self.previous_data == None:
                self.dataLoadedEvent(new_data, self)
            else:
                self.dataChangeEvent(new_data, self)

    def read(self):
        if not self.exists():
            logger.warning("[ConfigFile] file doesn't exist, can't read content ({0})".format(self.path))
            return None
        f = open(self.path, 'r')
        content = f.read()
        f.close()
        return content

    def get_yaml(self):
        ConfigFile.to_yaml(self.data)

    @classmethod
    def to_yaml(cls, data):
        return yaml.dump(data, default_flow_style=False)

    def write_yaml(self, data):
        self.write(ConfigFile.to_yaml(data))

    def write(self, content):
        f = open(self.path, 'w')
        f.write(content)
        f.close()

    def exists(self):
        return os.path.isfile(self.path)

    def get_value(self, path, default_value=None):
        data = self.data if self.data else {}
        names = path.split('.')
        for name in names:
            if not name in data:
                return default_value
            data = data[name]
        return data

    def backup(self, backup_path=None):
        if not backup_path:
            backup_path = self.path + '.bak.' + time.strftime('%Y%m%d.%H%M%S')

        shutil.copy(self.path, backup_path)
