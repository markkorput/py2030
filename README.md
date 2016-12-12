# py2030
python application to manage synchronised video playback for video installations on Raspberry Pis

## Install

```shell
pip install py2030
```

## usage

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
