# Реальные команды и вывод PR04

ROS_DOMAIN_ID=174; ROS_DISTRO=lyrical

Источник patrol: `/home/cyberpsychoz/ros2_robotics_course`.

Окно turtlesim: без XDG_CURRENT_DESKTOP и DESKTOP_SESSION; QT_QPA_PLATFORMTHEME=none, QT_STYLE_OVERRIDE=Fusion, QT_QPA_PLATFORM=xcb.

Фоновый запуск: `ros2 launch turtle_bringup sim.launch.py`; лог `fixed-commands-simulator.txt`.

Фоновый запуск: `/usr/bin/python3 -m patrol.patrol`; лог `fixed-commands-patrol.txt`.

```console
$ ros2 param get /patrol publish_hz
Double value is: 10.0

[exit=0]
```

```console
$ ros2 topic hz /turtle1/cmd_vel
average rate: 9.996
	min: 0.099s max: 0.101s std dev: 0.00057s window: 9
average rate: 10.000
	min: 0.099s max: 0.101s std dev: 0.00051s window: 19
average rate: 10.002
	min: 0.099s max: 0.101s std dev: 0.00048s window: 29
average rate: 9.999
	min: 0.099s max: 0.101s std dev: 0.00051s window: 39
average rate: 9.999
	min: 0.099s max: 0.101s std dev: 0.00047s window: 49
average rate: 10.001
	min: 0.099s max: 0.101s std dev: 0.00045s window: 59

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
average rate: 4.997
	min: 0.200s max: 0.201s std dev: 0.00035s window: 4
average rate: 4.998
	min: 0.199s max: 0.201s std dev: 0.00042s window: 9
average rate: 4.999
	min: 0.199s max: 0.201s std dev: 0.00037s window: 14
average rate: 4.999
	min: 0.199s max: 0.201s std dev: 0.00042s window: 19
average rate: 5.000
	min: 0.199s max: 0.201s std dev: 0.00039s window: 24

[exit=124]
```

```console
$ ros2 param set /patrol publish_hz 0.0
Setting parameter failed: publish_hz must be finite and within 1.0, 30.0

[exit=0]
```

```console
$ ros2 param get /patrol publish_hz
Double value is: 5.0

[exit=0]
```

```console
$ ros2 topic hz /turtle1/cmd_vel
average rate: 4.998
	min: 0.200s max: 0.200s std dev: 0.00016s window: 4
average rate: 5.000
	min: 0.200s max: 0.200s std dev: 0.00020s window: 9
average rate: 4.999
	min: 0.199s max: 0.201s std dev: 0.00031s window: 14
average rate: 5.000
	min: 0.199s max: 0.201s std dev: 0.00034s window: 19
average rate: 4.999
	min: 0.199s max: 0.201s std dev: 0.00033s window: 24

[exit=124]
```

```console
$ ros2 param set /patrol linear_speed 0.8
Set parameter successful

[exit=0]
```

```console
$ ros2 param set /patrol turn_rate -0.5
Set parameter successful

[exit=0]
```

```console
$ ros2 topic echo /turtle1/cmd_vel --once
linear:
  x: 0.8
  y: 0.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: -0.5
---

[exit=0]
```

```console
$ ros2 topic type /turtle1/pose
turtlesim_msgs/msg/Pose

[exit=0]
```

```console
$ ros2 service call /clear std_srvs/srv/Empty '{}'
waiting for service to become available...
requester: making request: std_srvs.srv.Empty_Request()

response:
std_srvs.srv.Empty_Response()


[exit=0]
```

```console
$ ros2 action list -t
/turtle1/rotate_absolute [turtlesim_msgs/action/RotateAbsolute]

[exit=0]
```

Все утверждения сценария выполнены.
