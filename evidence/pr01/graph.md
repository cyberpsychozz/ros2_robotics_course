# ПР01 — граф ROS 2 и связь между доменами

## Исправный граф

Симулятор запущен командой `ros2 run turtlesim turtlesim_node`, управление — `ros2 run turtlesim turtle_teleop_key`. При нажатии стрелок черепаха двигалась.

**Исходный `ROS_DOMAIN_ID`:** `67`. Для проверки разрыва использован домен `17`.

### Ноды

```console
$ ros2 node list --no-daemon --spin-time 2
/teleop_turtle
/turtlesim
```

| Нода | Роль |
| --- | --- |
| `/turtlesim` | Симулятор: принимает команды движения и публикует состояние черепахи. |
| `/teleop_turtle` | Читает клавиши и отправляет команды движения. |

`--no-daemon` получает свежий список без кэша ROS 2 CLI; `--spin-time 2` даёт две секунды на обнаружение участников.

### Топики и типы сообщений

```console
$ ros2 topic list -t
/parameter_events [rcl_interfaces/msg/ParameterEvent]
/rosout [rcl_interfaces/msg/Log]
/turtle1/cmd_vel [geometry_msgs/msg/Twist]
/turtle1/color_sensor [turtlesim/msg/Color]
/turtle1/pose [turtlesim/msg/Pose]
```

`/turtle1/cmd_vel` передаёт команду движения от управления к симулятору; `/turtle1/pose` передаёт положение и скорости от симулятора подписчикам. `/turtle1/color_sensor` содержит цвет под черепахой. `/rosout` служит для сообщений журнала, `/parameter_events` — для событий параметров.

### Связи ноды `/turtlesim`

```console
$ ros2 node info /turtlesim
/turtlesim
  Subscribers:
    /parameter_events: rcl_interfaces/msg/ParameterEvent
    /turtle1/cmd_vel: geometry_msgs/msg/Twist
  Publishers:
    /parameter_events: rcl_interfaces/msg/ParameterEvent
    /rosout: rcl_interfaces/msg/Log
    /turtle1/color_sensor: turtlesim/msg/Color
    /turtle1/pose: turtlesim/msg/Pose
  Service Servers:
    /clear: std_srvs/srv/Empty
    /kill: turtlesim/srv/Kill
    /reset: std_srvs/srv/Empty
    /spawn: turtlesim/srv/Spawn
    /turtle1/set_pen: turtlesim/srv/SetPen
    /turtle1/teleport_absolute: turtlesim/srv/TeleportAbsolute
    /turtle1/teleport_relative: turtlesim/srv/TeleportRelative
    /turtlesim/describe_parameters: rcl_interfaces/srv/DescribeParameters
    /turtlesim/get_parameter_types: rcl_interfaces/srv/GetParameterTypes
    /turtlesim/get_parameters: rcl_interfaces/srv/GetParameters
    /turtlesim/get_type_description: type_description_interfaces/srv/GetTypeDescription
    /turtlesim/list_parameters: rcl_interfaces/srv/ListParameters
    /turtlesim/set_parameters: rcl_interfaces/srv/SetParameters
    /turtlesim/set_parameters_atomically: rcl_interfaces/srv/SetParametersAtomically
  Service Clients:
  Action Servers:
    /turtle1/rotate_absolute: turtlesim/action/RotateAbsolute
  Action Clients:
```

Команда показывает, что `/turtlesim` подписана на команды скорости и публикует позу и цвет. Также нода предоставляет сервисы управления симуляцией и действие поворота.

### Тип и пример сообщения позы

```console
$ ros2 topic type /turtle1/pose
turtlesim/msg/Pose

$ POSE_TYPE=$(ros2 topic type /turtle1/pose)
$ ros2 topic echo /turtle1/pose --once
x: 5.655435085296631
y: 1.8770465850830078
theta: 1.9151853322982788
linear_velocity: 0.0
angular_velocity: 0.0
---
```

`POSE_TYPE` сохраняет тип сообщения для последующих проверок, когда в другом домене издатель позы не будет обнаруживаться. `--once` завершает подписку после одного сообщения. Нулевые скорости означают, что в этот момент черепаха стояла.

### Частота публикации позы

```console
$ ros2 topic hz /turtle1/pose
average rate: 62.453
    min: 0.015s max: 0.018s std dev: 0.00050s window: 64
...
average rate: 62.500
    min: 0.014s max: 0.018s std dev: 0.00051s window: 4852
```

Промежуточные повторяющиеся строки вывода опущены. Итоговая средняя частота — **62,5 Гц**. Последнее окно содержит 4852 сообщения, что при такой частоте соответствует примерно **77,6 с** наблюдения (оценка, а не отдельный замер секундомером). Поза поступала даже тогда, когда черепаха не двигалась.

## Разрыв связи между доменами

Симулятор `/turtlesim` продолжал работать в домене `67`. Управление в терминале B было остановлено и запущено заново в домене `17`:

```bash
export ROS_DOMAIN_ID=17
ros2 run turtlesim turtle_teleop_key
```

Наблюдение в терминале C после переключения в домен `17`:

```console
$ export ROS_DOMAIN_ID=17
$ ros2 node list --no-daemon --spin-time 2
/teleop_turtle

$ timeout 5s ros2 topic echo /turtle1/pose "$POSE_TYPE" --once > evidence/pr01/pose-broken.txt 2>&1
$ printf 'exit=%s\n' "$?"
exit=124
```

Файл `pose-broken.txt` пуст: за пять секунд сообщение позы не поступило. Код `124` означает, что подписчик остановлен командой `timeout`. В этом домене обнаружена `/teleop_turtle`, но не `/turtlesim`.

## Восстановление связи

Управление в терминале B было остановлено и запущено заново в исходном домене `67`:

```bash
export ROS_DOMAIN_ID=67
ros2 run turtlesim turtle_teleop_key
```

Терминал C возвращён в тот же домен; повторена та же проверка позы:

```console
$ export ROS_DOMAIN_ID=67
$ ros2 node list --no-daemon --spin-time 2
/teleop_turtle
/turtlesim

$ timeout 5s ros2 topic echo /turtle1/pose "$POSE_TYPE" --once > evidence/pr01/pose-fixed.txt 2>&1
$ printf 'exit=%s\n' "$?"
exit=0
```

Содержимое `pose-fixed.txt`:

```text
x: 9.673834800720215
y: 0.0
theta: -0.9328147172927856
linear_velocity: 2.0
angular_velocity: 0.0
---
```

Код `0` и полученная поза подтверждают восстановление связи. `ROS_DOMAIN_ID` применяется при запуске процесса: изменение переменной в терминале не меняет домен работающей ноды. Поэтому `teleop` запускался заново, а симулятор и установка ROS не менялись.

## Сравнение

| Состояние | Домен симулятора | Домен управления и наблюдения | Обнаруженные ноды | Поза / код возврата |
| --- | ---: | ---: | --- | --- |
| До разрыва | 67 | 67 | `/turtlesim`, `/teleop_turtle` | Поза получена; частота около 62,5 Гц |
| Разрыв | 67 | 17 | Только `/teleop_turtle` | За 5 с поза не пришла; `pose-broken.txt` пуст; `exit=124` |
| После восстановления | 67 | 67 | `/turtlesim`, `/teleop_turtle` | Поза в `pose-fixed.txt`; `exit=0` |
