#!/usr/bin/env python
import os

thisdir = os.path.dirname(__file__)
packagedir = os.path.abspath(os.path.join(thisdir, '..'))

# try:
#     import pyHoh
#     # make sure the package's root folder in the python searchpath
#     import sys
#     if packagedir not in sys.path:
#         sys.path.insert(0, packagedir)
#     # try again
#     import pyHoh

# invoking this file directly will run all tests
if __name__ == '__main__':
    import subprocess
    os.chdir(packagedir)
    subprocess.call(['python', '-m', 'unittest', 'discover'])
