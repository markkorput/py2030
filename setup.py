#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='py2030',
      version='0.2.0',
      description='A modular swiss pocket knife for managing a network of RaspberryPIs',
      url='http://github.com/markkorput/py2030',
      author='Mark van de Korput',
      author_email='dr.theman@gmail.com',
      license='MIT',
      packages=find_packages(exclude=['tests']),
      zip_safe=True,
      test_suite='tests',
      install_requires=[
        'evento==1.0.1',
        'pyOSC==0.3.5b-5294',
        'PyYAML==3.11',
        'omxplayer-wrapper==0.0.2',
        'omxsync==0.1.1'])
