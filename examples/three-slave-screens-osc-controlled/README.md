# Example project
This is example project contains a config.yml file and some dummy (empty) asset files. It simulates a scenario with three raspberry PIs that will each play a different video file. A fourth computer connected to the network can give start/stop/pause commands as well as update all remote files (both config files and video files) from its local folder.

## Assumptions
The instructions below assume your computer has the py2030 package installed and is connected to a network with three raspberry pis which have the hostnames 'rpi1.local', 'rpi2.local' and 'rpi3.local' and are each already running py2030 on their respective profiles.

It is also assumed you have cd-ed into this example project folder.

## Usage

To upload files to remote devices run the following command:
```shell
python -m py2030.app -p filesync
```

To control video playback on all remote devices these 3 commands can be used:
```shell
python -m py2030.app -p control-start
python -m py2030.app -p control-pause
python -m py2030.app -p control-stop
```
