# Реальные команды и вывод PR04

ROS_DOMAIN_ID=174; ROS_DISTRO=lyrical

Источник patrol: `/tmp/ros2-pr04-defect`.

Окно turtlesim: без XDG_CURRENT_DESKTOP и DESKTOP_SESSION; QT_QPA_PLATFORMTHEME=none, QT_STYLE_OVERRIDE=Fusion, QT_QPA_PLATFORM=xcb.

Фоновый запуск: `ros2 launch turtle_bringup sim.launch.py`; лог `broken-commands-simulator.txt`.

Фоновый запуск: `/usr/bin/python3 -m patrol.patrol`; лог `broken-commands-patrol.txt`.

```console
$ ros2 param get /patrol publish_hz
Double value is: 10.0

[exit=0]
```

```console
$ ros2 topic hz /turtle1/cmd_vel
WARNING: topic [/turtle1/cmd_vel] does not appear to be published yet
average rate: 10.003
	min: 0.100s max: 0.100s std dev: 0.00019s window: 9
average rate: 10.001
	min: 0.099s max: 0.101s std dev: 0.00029s window: 19
average rate: 9.999
	min: 0.099s max: 0.101s std dev: 0.00034s window: 29
average rate: 10.000
	min: 0.099s max: 0.101s std dev: 0.00033s window: 39

[exit=124]
```

```console
$ ros2 param set /patrol publish_hz 5.0
Set parameter successful

[exit=0]
```

```console
$ ros2 param get /patrol publish_hz
Double value is: 5.0

[exit=0]
```

```console
$ ros2 topic hz /turtle1/cmd_vel
average rate: 4.999
	min: 0.200s max: 0.201s std dev: 0.00039s window: 4
average rate: 5.001
	min: 0.200s max: 0.201s std dev: 0.00031s window: 9
average rate: 5.000
	min: 0.200s max: 0.201s std dev: 0.00027s window: 14
average rate: 5.000
	min: 0.199s max: 0.201s std dev: 0.00028s window: 19
average rate: 5.000
	min: 0.199s max: 0.201s std dev: 0.00030s window: 24

[exit=124]
```

```console
$ ros2 param set /patrol publish_hz 0.0

[exit=124]
```

После запроса нуля процесс patrol завершился; ZeroDivisionError подтверждён в логе ноды.

Все утверждения сценария выполнены.
