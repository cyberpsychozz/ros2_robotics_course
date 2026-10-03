# ПР03 — издатель команды и callback таймера

Среда: Ubuntu 24.04, ROS 2 Jazzy. Во всех терминалах используется один `ROS_DOMAIN_ID=67`. Исходные наблюдения графа, частоты и остановки черепахи предоставил автор в терминале C.

## Подготовка и проверка чистой функции

Из корня workspace:

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=67
colcon build --symlink-install --packages-select turtle_bringup patrol
source install/setup.bash
python3 -m pytest -q src/patrol/test/test_command.py
```

`choose_command(pose)` не обращается к ROS-графу и не меняет переданную позу: при `None` возвращает нулевой `Twist`, при обычном `Pose` — `linear.x = 0.5` и `angular.z = 0.3`. Оба случая проверены в `test_command.py`; результат локального запуска сохранён в `tests.txt`. Callback подписки сохраняет последнее сообщение в `node.latest_pose`, а callback таймера передаёт его в `choose_command` и публикует результат.

## Разрыв имени топика

Терминал A: `ros2 launch turtle_bringup sim.launch.py`. Терминал B: `ros2 run patrol patrol` без remap. В исходном коде издателя указано относительное имя `cmd_vel`, поэтому у ноды `/patrol` полный топик `/cmd_vel`, а `/turtlesim` подписан на `/turtle1/cmd_vel`. Совпадение типа `geometry_msgs/msg/Twist` не соединяет разные имена.

В терминале C до исправления команда `ros2 topic info /turtle1/cmd_vel --verbose` показала:

```text
Type: geometry_msgs/msg/Twist
Publisher count: 0
Subscription count: 1
Node name: turtlesim
Endpoint type: SUBSCRIPTION
```

Таким образом, у нужного топика был подписчик, но не было издателя. Для отдельной проверки ошибочного имени можно выполнить `ros2 topic info /cmd_vel --verbose`.

## Исправление через remap

После остановки `patrol` через `Ctrl+C` нода запущена с переназначением:

```bash
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

Проверка того же топика в терминале C после исправления:

```text
Type: geometry_msgs/msg/Twist
Publisher count: 1
Node name: patrol
Endpoint type: PUBLISHER
Subscription count: 1
Node name: turtlesim
Endpoint type: SUBSCRIPTION
```

Команда `source install/setup.bash` подключает собранный пакет в текущем терминале; само по себе её выполнение не меняет имя топика уже запущенной ноды. Изменение графа связано с новым запуском `patrol` с `-r`.

## Частота команды и остановка

При работающем `patrol` с remap автор выполнил `ros2 topic hz /turtle1/cmd_vel`. После более чем 10 секунд наблюдения вывод содержал:

```text
average rate: 9.999
    min: 0.099s max: 0.101s std dev: 0.00043s window: 11
...
average rate: 10.000
    min: 0.098s max: 0.102s std dev: 0.00032s window: 171
```

Измеренная частота около **10.000 Гц**, что согласуется с периодом таймера `0.1` с. Окно из 171 сообщения при такой частоте охватывает более 10 секунд.

После `Ctrl+C` в терминале `patrol` автор наблюдал, что черепаха в работающем `turtlesim` остановилась. Исчезновение издателя означает прекращение новых сообщений, но не является мгновенной командой торможения: остановку проверяли по фактическому поведению симулятора после завершения ноды.

## Жизненный цикл ноды

- `rclpy.init(args=args)` инициализирует контекст ROS 2 до создания ноды.
- `rclpy.spin(node)` обрабатывает события подписки и таймера. Пока `spin` работает, вызываются `on_pose` и `tick`.
- `on_pose` получает новую позу и сохраняет её; `tick` каждые `0.1` с выбирает команду из последней позы и публикует `Twist`.
- `Ctrl+C` вызывает `KeyboardInterrupt`, после которого таймер отменяется, нода удаляется и вызывается `rclpy.try_shutdown()`.
