import socket
from .utils.config_file import ConfigFile

class Yaml:
    def __init__(self):
        self.data = {
            'py2030': {
                'profiles': {
                    socket.gethostname().replace('.', '_'): {
                        'start_event': 'start'
                    }
                }
            }
        }

    def text(self):
        return ConfigFile.to_yaml(self.data)

if __name__ == '__main__':
    print(Yaml().text())
