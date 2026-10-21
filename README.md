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

## ПР03: пакет `patrol`

Нода подписывается на `/turtle1/pose`, сохраняет последнюю позу и раз в `0.1` с публикует команду `Twist`. При отсутствии позы команда имеет нулевые скорости. Код издателя использует относительное имя `cmd_vel`, чтобы можно было показать разрыв графа и затем исправить его через remap.

В каждом терминале подключите ROS 2 и используйте один `ROS_DOMAIN_ID`:

```bash
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=67
```

Из корня репозитория соберите оба пакета и подключите workspace:

```bash
colcon build --symlink-install --packages-select turtle_bringup patrol
source install/setup.bash
```

Запустите `ros2 launch turtle_bringup sim.launch.py` в терминале A. В терминале B выполните `ros2 run patrol patrol`. Терминал C покажет, что у `/turtle1/cmd_vel` пока нет издателя: `ros2 topic info /turtle1/cmd_vel --verbose`. Остановите `patrol` через `Ctrl+C` и запустите его с правильным именем:

```bash
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

В терминале C повторите `ros2 topic info /turtle1/cmd_vel --verbose`, затем измеряйте `ros2 topic hz /turtle1/cmd_vel` не меньше 10 секунд. После остановки `patrol` дождитесь фактической остановки черепахи. Проверки кода и сдачи:

```bash
python3 -m pytest -q src/patrol/test/test_command.py
colcon test --packages-select patrol --event-handlers console_direct+
colcon test-result --verbose
python3 .course-kit/v1/tools/check_practice.py PR03 --submission .
```

Выводы и наблюдения находятся в `evidence/pr03/demo.md`, результаты тестов — в `evidence/pr03/tests.txt`.

## ПР04: параметры работающей ноды

Локальный опыт выполнен на Ubuntu 26.04.1 и ROS 2 Lyrical. CI использует
зафиксированный выше образ Jazzy; импорт Pose поддерживает обе среды.
В каждом терминале подключите ROS и workspace и задайте одинаковый домен:

```bash
source /opt/ros/lyrical/setup.bash
export ROS_DOMAIN_ID=67
colcon build --symlink-install --packages-select turtle_bringup patrol
source install/setup.bash
```

В терминале A запустите симулятор (для данной системы нужна настройка Qt):

```bash
env -u XDG_CURRENT_DESKTOP -u DESKTOP_SESSION \
  QT_QPA_PLATFORMTHEME=none QT_STYLE_OVERRIDE=Fusion QT_QPA_PLATFORM=xcb \
  ros2 launch turtle_bringup sim.launch.py
```

В терминале B выполните `ros2 run patrol patrol`. Текущий издатель уже использует
`turtle1/cmd_vel`; дополнительный remap не нужен. В терминале C:

```bash
ros2 param get /patrol publish_hz
ros2 topic hz /turtle1/cmd_vel
# Завершите измерение Ctrl+C, затем:
ros2 param set /patrol publish_hz 5.0
ros2 topic hz /turtle1/cmd_vel
# Снова Ctrl+C, затем:
ros2 param set /patrol publish_hz 0.0
ros2 param get /patrol publish_hz
ros2 topic hz /turtle1/cmd_vel
```

Частота меняется с 10 до 5 Гц. Ноль отклоняется; параметр остаётся 5.0 и поток
продолжает идти с частотой 5 Гц. `on-set` проверяет весь предложенный набор,
`post-set` обновляет поля после принятия; таймер заменяется только при смене
частоты. Значения при запуске также проверяются до создания таймера.

Для повторения записанного опыта автоматически, в отдельном домене 174:

```bash
python3 tools/record_pr04.py --source . --output /tmp/pr04-repeat.md
```

Ветка `codex/pr04-frequency-defect` сохраняет намеренный дефект: проверка частоты
отключена, поэтому после установки нуля возникает `ZeroDivisionError`.
Исходники этой ветки можно открыть в отдельной рабочей копии, передать её путь
в `--source` и добавить `--expect-broken` к сценарию. Он запускает собственные
patrol/turtlesim, записывает настоящий вывод и завершает свои процессы в конце.

Проверки реализации и отчёта:

```bash
export ROS_DOMAIN_ID=175
python3 -m pytest src/patrol/test
colcon test --packages-select patrol --event-handlers console_direct+
colcon test-result --verbose
python3 .course-kit/v1/tools/check_practice.py PR04 --submission .
```

Команды, измерения и сравнение запроса сервиса с целью действия сохранены в
`evidence/pr04/parameters.md`; итоги проверок — в `evidence/pr04/tests.txt`.
Для PR04 локально и в CI используется course kit `v1-w06` с зафиксированными
URL и SHA-256 из workflow. Предыдущие отчёты относятся к своим версиям комплекта.

## ПР05: launch, QoS и повтор записи

`course_bringup` запускает глобальный `turtlesim` и ноды `patrol`, `pose_relay`,
`pose_subscriber` в `/robot_a`. `pose_relay` читает `/turtle1/pose` и предлагает
`/robot_a/sensor_pose` с QoS `best_effort`. Выход `patrol` переназначен на
`/turtle1/cmd_vel`. Исходный YAML параметров —
`src/course_bringup/config/patrol.yaml`; профиль издателя при replay —
`config/qos-overrides.yaml`.

В каждом терминале подключите одну и ту же среду ROS и workspace. Локально
проверено с ROS 2 Lyrical; в CI используется Jazzy:

```bash
source /opt/ros/lyrical/setup.bash
colcon build --symlink-install --packages-select turtle_bringup patrol course_bringup
source install/setup.bash
ros2 launch course_bringup sim.launch.py subscriber_reliability:=reliable record:=false
```

Нода-подписчик сообщает о несовместимой `RELIABILITY` и не получает позу.
Остановите launch через `Ctrl+C` и повторите с
`subscriber_reliability:=best_effort`: в логе появится `First pose received`.
Аргумент `namespace` меняет пространство имён; `params_file` принимает иной YAML.
Для условной записи укажите свободный каталог:

```bash
ros2 launch course_bringup sim.launch.py \
  subscriber_reliability:=best_effort record:=true \
  bag_dir:=evidence/pr05/bag-new
```

После нескольких секунд остановите launch через `Ctrl+C`, чтобы recorder
закрыл MCAP. Для проверки сохранённого bag сначала остановите живую систему.
В терминале A запустите только подписчик с `reliable`, затем в B проиграйте bag:

```bash
ros2 run course_bringup pose_subscriber --ros-args \
  -r __ns:=/robot_a -p subscriber_reliability:=reliable
```

```bash
ros2 bag play evidence/pr05/bag \
  --qos-profile-overrides-path config/qos-overrides.yaml
```

Снова нет сообщения. Остановите подписчик, запустите его с
`subscriber_reliability:=best_effort` и повторно проиграйте **тот же** bag:
первое сообщение будет получено. Диагностика двух режимов и живого потока —
в `evidence/pr05/qos-before.txt` и `qos-after.txt`; метаданные MCAP — в
`evidence/pr05/bag-metadata.yaml`. Отчёт проверяется командой:

```bash
python3 .course-kit/v1/tools/check_practice.py PR05 --submission .
```
