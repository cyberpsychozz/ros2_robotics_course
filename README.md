# ROS 2 Robotics Course

ПР01 исследует граф готовых нод `turtlesim` и проверяет изоляцию через `ROS_DOMAIN_ID`. Проверено на Ubuntu 24.04 и ROS 2 Jazzy. В этой работе ROS-пакет и собственная нода не создаются.

## Локальный опыт

Откройте три Bash-терминала в одной среде. В каждом выполните:

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=67
```

Если в аудитории выделена другая пара доменов, используйте её во всех шагах.

**Терминал A — симулятор:**

```bash
ros2 run turtlesim turtlesim_node
```

**Терминал B — управление:**

```bash
ros2 run turtlesim turtle_teleop_key
```

Нажимайте стрелки при фокусе на терминале B.

**Терминал C — наблюдение** (из корня репозитория):

```bash
mkdir -p evidence/pr01
ros2 doctor --report > evidence/pr01/doctor.txt 2>&1
ros2 node list --no-daemon --spin-time 2
ros2 topic list -t
ros2 node info /turtlesim
POSE_TYPE=$(ros2 topic type /turtle1/pose)
ros2 topic echo /turtle1/pose --once
ros2 topic hz /turtle1/pose
```

Оставьте `ros2 topic hz` работать не менее 10 секунд и завершите `Ctrl+C`. Запишите выводы в `evidence/pr01/graph.md`.

## Разрыв и восстановление

Симулятор в A остаётся в исходном домене. Остановите управление в B через `Ctrl+C`, затем запустите его в другом домене:

```bash
export ROS_DOMAIN_ID=17
ros2 run turtlesim turtle_teleop_key
```

В C, где уже задан `POSE_TYPE`, выполните:

```bash
export ROS_DOMAIN_ID=17
ros2 node list --no-daemon --spin-time 2
timeout 5s ros2 topic echo /turtle1/pose "$POSE_TYPE" --once > evidence/pr01/pose-broken.txt 2>&1
printf 'exit=%s\n' "$?"
```

Ожидается только `/teleop_turtle` и `exit=124`. Пустой `pose-broken.txt` допустим: сообщений нет.

Остановите управление в B и запустите его снова после `export ROS_DOMAIN_ID=67`. В C повторите:

```bash
export ROS_DOMAIN_ID=67
ros2 node list --no-daemon --spin-time 2
timeout 5s ros2 topic echo /turtle1/pose "$POSE_TYPE" --once > evidence/pr01/pose-fixed.txt 2>&1
printf 'exit=%s\n' "$?"
```

Ожидаются обе ноды, сообщение позы и `exit=0`. Внесите фактические наблюдения и объяснение в `graph.md`. Изменение `ROS_DOMAIN_ID` влияет только на новые процессы, поэтому управление нужно запускать заново.

## Проверка сдачи

Course kit версии `v1-w03` скачивается по URL и SHA-256, закреплённым в `.github/workflows/ci.yml`. После распаковки в `.course-kit/`:

```bash
python3 -m json.tool evidence/pr01/environment.json > /dev/null
python3 .course-kit/v1/tools/check_practice.py PR01 --submission .
```

CI проверяет JSON и комплектность evidence. Поведение GUI и доставку сообщений подтверждают локальные наблюдения и демонстрация на защите.

## ПР02: пакет `turtle_bringup`

Работайте из корня репозитория. На Ubuntu 24.04 подключите ROS 2 Jazzy и задайте один домен во всех терминалах. Пакет содержит launch-файл для готовой ноды turtlesim, а не собственную ноду.

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=67
colcon build --symlink-install --packages-select turtle_bringup
source install/setup.bash
ros2 pkg prefix turtle_bringup
ls "$(ros2 pkg prefix turtle_bringup)/share/turtle_bringup/launch"
ros2 launch turtle_bringup sim.launch.py
```

Оставьте launch работающим в терминале A. В терминале B с тем же ROS и доменом проверьте `ros2 node list --no-daemon --spin-time 2` и начальную позу через `ros2 topic echo /turtle1/pose --once`. Отправьте команду движения:

```bash
ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
ros2 topic echo /turtle1/pose --once
```

Для опыта с ошибкой запустите публикацию того же `Twist` в `/cmd_vel` с `--rate 1 --wait-matching-subscriptions 0`. Пока издатель работает, сравните `ros2 topic info /cmd_vel --verbose` и `ros2 topic info /turtle1/cmd_vel --verbose`. Остановите издателя через `Ctrl+C`, замените только имя топика на `/turtle1/cmd_vel` и повторите публикацию и проверку. Затем остановите издателя и launch через `Ctrl+C`.

Наблюдения сохранены в `evidence/pr02/commands.md`, типы сообщений — в `evidence/pr02/types.md`. Локальная проверка:

```bash
python3 -m py_compile src/turtle_bringup/launch/sim.launch.py
python3 .course-kit/v1/tools/check_practice.py PR02 --submission .
```

CI собирает пакет и проверяет установку launch-файла. Движение черепахи и остановку ноды через `Ctrl+C` проверяют локально.
