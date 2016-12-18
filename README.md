# py2030 [![Build Status](https://api.travis-ci.org/markkorput/py2030.svg)](https://travis-ci.org/markkorput/py2030)
_current version: 0.2.0_

python application to control video playback for video installations using multiple Raspberry PIs


## Install

```shell
pip install py2030
```

## Usage

First you need a config file for your project which contains the profiles (configurations)
for all machines. Create a minimal config file in your current directory using the following command:

```shell
python -m py2030.yaml > config.yml
```


Now you can run a py2030 application using the following command:
```shell
python -m py2030.app -v
```

The -v flag is optional and runs the application in verbose mode so you get some feedback.
Running with the default generated yaml should give something like this:

```shell
DEBUG:py2030.component_manager:config file: config.yml
DEBUG:py2030.component_manager:profile: <your computer hostname>
DEBUG:py2030.component_manager:triggering start_event: start
```

### py2030.app options

Use -v or --verbose to enable verbose mode:
```shell
python -m py2030.app -v
```

Use -y, --yml, --yaml or --config-file to specify the location of the config file
Default value: config.yml
```shell
python -m py2030.app -y project.config.yml
```

Use -p or --profile to specify which profile to use
Default value: the machine's network hostname with all dots (.) replaced for underscores (\_)
```shell
python -m py2030.app -p master
```

### config.yml documentation
TODO, for now have a look at [the example projects](https://github.com/markkorput/py2030/tree/master/examples/).
