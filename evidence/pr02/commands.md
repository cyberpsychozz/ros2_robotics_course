# ПР02 — команды и наблюдения

Рабочая среда: Ubuntu 24.04, ROS 2 Jazzy. Команды сборки выполнялись из корня workspace `/home/cyberpsychoz/ros2_robotics_course`. В терминалах запуска и наблюдения должен быть один `ROS_DOMAIN_ID`.

## Три команды Linux

| Точная команда | Назначение | Полученный результат |
| --- | --- | --- |
| `source /opt/ros/jazzy/setup.bash` | Подключить базовую среду ROS 2 к текущему Bash. | После подключения доступны команды `ros2` и пакет `turtlesim`. |
| `pwd` | Показать текущий каталог и проверить, что команды выполняются из корня workspace. | `/home/cyberpsychoz/ros2_robotics_course`. |
| `ls "$(ros2 pkg prefix turtle_bringup)/share/turtle_bringup/launch"` | Проверить, что launch-файл установлен как ресурс пакета. | Найден `sim.launch.py` (также показан каталог `__pycache__`). |

`source` исполняет скрипт **в текущем терминале** и меняет его окружение. Запуск скрипта как отдельной программы создаёт новый процесс: его изменения переменных не возвращаются в текущую оболочку. Поэтому после сборки нужен `source install/setup.bash` в каждом терминале, где используется пакет.

Оператор `>` направляет стандартный вывод команды в файл и заменяет прежнее содержимое. Оператор `|` передаёт стандартный вывод одной команды на вход следующей. В сборке `2>&1 | tee evidence/pr02/build.txt` объединяет сообщения об ошибках со стандартным выводом, показывает их в терминале и одновременно сохраняет в файл. `set -o pipefail` позволяет заметить ошибку `colcon`, даже если `tee` завершился успешно.

## Сборка пакета

Пустой пакет был собран до добавления launch-файла; исходный вывод сохранён в `build-empty.txt`:

```console
$ set -o pipefail
$ colcon build --symlink-install --packages-select turtle_bringup 2>&1 | tee evidence/pr02/build-empty.txt
Starting >>> turtle_bringup
Finished <<< turtle_bringup [1.20s]
Summary: 1 package finished [1.31s]
```

После добавления `launch/sim.launch.py` и записи `share/turtle_bringup/launch` в `setup.py` пакет пересобран:

```console
$ set -o pipefail
$ colcon build --symlink-install --packages-select turtle_bringup 2>&1 | tee evidence/pr02/build.txt
Starting >>> turtle_bringup
Finished <<< turtle_bringup [1.27s]
Summary: 1 package finished [1.38s]
```

## Запуск установленного launch-файла

```console
$ source /opt/ros/jazzy/setup.bash
$ source install/setup.bash
$ ros2 pkg prefix turtle_bringup
/home/cyberpsychoz/ros2_robotics_course/install/turtle_bringup

$ ls "$(ros2 pkg prefix turtle_bringup)/share/turtle_bringup/launch"
__pycache__  sim.launch.py

$ ros2 launch turtle_bringup sim.launch.py
[INFO] [turtlesim_node-1]: process started with pid [35898]
[turtlesim_node-1] QSocketNotifier: Can only be used with threads started with QThread
[turtlesim_node-1] [INFO] [turtlesim]: Starting turtlesim with node name /turtlesim
[turtlesim_node-1] [INFO] [turtlesim]: Spawning turtle [turtle1] ...
```

Во втором терминале при работающем launch:

```console
$ ros2 node list --no-daemon --spin-time 2
/turtlesim
```

После `Ctrl+C` в терминале launch:

```console
^C[WARNING] [launch]: user interrupted with ctrl-c (SIGINT)
[INFO] [turtlesim_node-1]: process has finished cleanly [pid 35898]

$ ros2 node list --no-daemon --spin-time 2
# Нод нет.
```

Пакет и файл на диске остаются установленными после остановки. Нода `/turtlesim` существует в графе только во время работы процесса. Сообщение `QSocketNotifier` не помешало запуску и чистой остановке в этом опыте.

## Команда движения: исправный топик

Тип команды и тип позы проверены через CLI:

```console
$ ros2 interface show geometry_msgs/msg/Twist
Vector3 linear
    float64 x
    float64 y
    float64 z
Vector3 angular
    float64 x
    float64 y
    float64 z

$ ros2 topic type /turtle1/pose
turtlesim/msg/Pose
```

До публикации:

```console
$ ros2 topic echo /turtle1/pose --once
x: 5.544444561004639
y: 5.544444561004639
theta: 0.0
linear_velocity: 0.0
angular_velocity: 0.0
---
```

Опубликован один `Twist` с движением вперёд (`linear.x = 1.0`) и поворотом (`angular.z = 0.5`):

```console
$ ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist \
    '{linear: {x: 1.0}, angular: {z: 0.5}}'
publisher: beginning loop
publishing #1: geometry_msgs.msg.Twist(linear=geometry_msgs.msg.Vector3(x=1.0, y=0.0, z=0.0), angular=geometry_msgs.msg.Vector3(x=0.0, y=0.0, z=0.5))
```

После публикации получена другая поза:

```console
$ ros2 topic echo /turtle1/pose --once
x: 6.509308815002441
y: 5.796990871429443
theta: 0.5040000081062317
linear_velocity: 0.0
angular_velocity: 0.0
---
```

Координаты и угол изменились; нулевые скорости в позднем сообщении означают, что после однократной команды черепаха остановилась. Строка `publishing #1` сама по себе подтверждает только отправку сообщения; изменение позы подтверждает эффект.

## Сбой: неверное полное имя топика

Издатель отправлял тот же `Twist`, но в `/cmd_vel`:

```console
$ ros2 topic pub --rate 1 --wait-matching-subscriptions 0 \
    /cmd_vel geometry_msgs/msg/Twist \
    '{linear: {x: 1.0}, angular: {z: 0.5}}'
publisher: beginning loop
publishing #1: geometry_msgs.msg.Twist(...)
publishing #2: geometry_msgs.msg.Twist(...)
publishing #3: geometry_msgs.msg.Twist(...)
```

Пока издатель работал, проверка конечных точек показала:

```console
$ ros2 topic info /cmd_vel --verbose
Type: geometry_msgs/msg/Twist
Publisher count: 1
Node name: _ros2cli_68958
Endpoint type: PUBLISHER
Subscription count: 0

$ ros2 topic info /turtle1/cmd_vel --verbose
Type: geometry_msgs/msg/Twist
Publisher count: 0
Subscription count: 1
Node name: turtlesim
Endpoint type: SUBSCRIPTION
```

Тип сообщений совпадает, но имена топиков разные. Поэтому издатель виден в графе, а подписчик `turtlesim` к нему не подключён. `--wait-matching-subscriptions 0` позволяет издателю работать при нуле подписчиков.

## Исправление: возвращено полное имя

После остановки ошибочного издателя изменено только имя `/cmd_vel` → `/turtle1/cmd_vel`. Тип и значения `Twist` оставлены прежними:

```console
$ ros2 topic pub --rate 1 --wait-matching-subscriptions 0 \
    /turtle1/cmd_vel geometry_msgs/msg/Twist \
    '{linear: {x: 1.0}, angular: {z: 0.5}}'
publisher: beginning loop
publishing #1: geometry_msgs.msg.Twist(...)
publishing #2: geometry_msgs.msg.Twist(...)
publishing #3: geometry_msgs.msg.Twist(...)
```

Проверка во время публикации:

```console
$ ros2 topic info /cmd_vel --verbose
Unknown topic '/cmd_vel'

$ ros2 topic info /turtle1/cmd_vel --verbose
Type: geometry_msgs/msg/Twist
Publisher count: 1
Node name: _ros2cli_69483
Endpoint type: PUBLISHER
Subscription count: 1
Node name: turtlesim
Endpoint type: SUBSCRIPTION
```

После исправления черепаха **снова двигалась** (наблюдение автора опыта). Изменение позы при отправке того же `Twist` в правильный топик уже измерено выше: `x: 5.544444561004639 → 6.509308815002441`, `y: 5.544444561004639 → 5.796990871429443`, `theta: 0.0 → 0.5040000081062317`. При повторном запуске после исправления сохранены совпадение конечных точек и визуальное наблюдение движения.

| Состояние | Топик издателя | Издатели / подписчики | Наблюдение |
| --- | --- | --- | --- |
| До сбоя | `/turtle1/cmd_vel` | Команда `--once`; поза получена до и после | `x: 5.5444 → 6.5093`, `theta: 0 → 0.504` |
| Сбой | `/cmd_vel` | 1 / 0 | Издатель публикует, но у него нет подписчика `turtlesim` |
| После исправления | `/turtle1/cmd_vel` | 1 / 1 | Черепаха снова двигалась; числовой замер изменения позы при том же топике приведён выше |
