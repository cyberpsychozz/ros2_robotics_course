# ПР04: параметры, отказ и проверка исправления

Дата опыта: 2026-10-17 (Asia/Novosibirsk). Команды запускал Codex в локальном окружении автора: Ubuntu 26.04.1 LTS, ROS 2 Lyrical, Python 3.14.4. Это реальные запуски ROS и измерения, а не пример ожидаемого вывода; визуальное качество движения не оценивалось.

Для изоляции от нод автора использовался `ROS_DOMAIN_ID=174`; для тестов — `175`. Все созданные сценарием patrol/turtlesim завершены после опыта. Комплект `v1-w06` накопительный и содержит манифест PR04; SHA-256 архива: `6eda53e1c566f7f0a7e09d7afe1e5a6f3b98397175a7e57dede9a84c6d14d0fe`.

## Подготовка

```bash
cd /home/cyberpsychoz/ros2_robotics_course
source /opt/ros/lyrical/setup.bash
colcon build --symlink-install --packages-select turtle_bringup patrol
source install/setup.bash
```

Сценарий `tools/record_pr04.py` задаёт отдельный домен, удаляет `XDG_CURRENT_DESKTOP` и `DESKTOP_SESSION`, устанавливает `QT_QPA_PLATFORMTHEME=none`, `QT_STYLE_OVERRIDE=Fusion`, `QT_QPA_PLATFORM=xcb` для рабочего запуска окна в этой среде. Издатель использует `/turtle1/cmd_vel`, поэтому remap для текущего кода не требуется. Тип позы здесь `turtlesim_msgs/msg/Pose`; для Jazzy в CI предусмотрен импорт `turtlesim.msg.Pose`.

## Ветка с намеренным дефектом

Ветка: `codex/pr04-frequency-defect`, коммит `bef5b95798d36d6077f178f0d3eaeb60d2856ad9`. В ней из `validate_values()` убрана только строка ограничения `publish_hz`; ограничения скорости и поворота сохранены. Отдельная рабочая копия создана командой:

```bash
git worktree add -b codex/pr04-frequency-defect /tmp/ros2-pr04-defect HEAD
```

После копирования реализации и удаления проверки частоты создан указанный коммит. Опытом управляет та же версия сценария основной ветки:

```bash
python3 tools/record_pr04.py --source /tmp/ros2-pr04-defect --expect-broken --output evidence/pr04/broken-commands.md
```

Перед нулём подтверждены 10→5 Гц. При `publish_hz=0.0` параметр принимается, старый таймер останавливается и удаляется, затем вычисление `1.0 / self.publish_hz` вызывает `ZeroDivisionError: division by zero`. Процесс ноды завершается; CLI не получает ответ и останавливается сценарием по таймауту. Следовательно, поток команд прекращается. Ниже сохранён настоящий вывод; полный стек также есть в `broken-commands-patrol.txt`.

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

### Стек отказа ноды

```text
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/tmp/ros2-pr04-defect/src/patrol/patrol/patrol.py", line 133, in <module>
    main()
    ~~~~^^
  File "/tmp/ros2-pr04-defect/src/patrol/patrol/patrol.py", line 123, in main
    rclpy.spin(node)
    ~~~~~~~~~~^^^^^^
  File "/opt/ros/lyrical/lib/python3.14/site-packages/rclpy/__init__.py", line 324, in spin
    executor.spin_once()
    ~~~~~~~~~~~~~~~~~~^^
  File "/opt/ros/lyrical/lib/python3.14/site-packages/rclpy/executors.py", line 1033, in spin_once
    self._spin_once_impl(timeout_sec)
    ~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^
  File "/opt/ros/lyrical/lib/python3.14/site-packages/rclpy/executors.py", line 1025, in _spin_once_impl
    raise exception
  File "/opt/ros/lyrical/lib/python3.14/site-packages/rclpy/task.py", line 351, in _execute_coroutine_step
    result = coro.send(None)
  File "/opt/ros/lyrical/lib/python3.14/site-packages/rclpy/executors.py", line 683, in handler
    await call_coroutine()
  File "/opt/ros/lyrical/lib/python3.14/site-packages/rclpy/executors.py", line 617, in _execute
    response = await await_or_execute(srv.callback, request, srv.srv_type.Response())
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/ros/lyrical/lib/python3.14/site-packages/rclpy/executors.py", line 139, in await_or_execute
    return callback(*args)
  File "/opt/ros/lyrical/lib/python3.14/site-packages/rclpy/parameter_service.py", line 142, in _set_parameters_callback
    result = node.set_parameters_atomically([param])
  File "/opt/ros/lyrical/lib/python3.14/site-packages/rclpy/node.py", line 820, in set_parameters_atomically
    return self._set_parameters_atomically(parameter_list)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^
  File "/opt/ros/lyrical/lib/python3.14/site-packages/rclpy/node.py", line 840, in _set_parameters_atomically
    return self._set_parameters_atomically_common(parameter_list)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^
  File "/opt/ros/lyrical/lib/python3.14/site-packages/rclpy/node.py", line 944, in _set_parameters_atomically_common
    self._call_post_set_parameters_callback(parameter_list)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^
  File "/opt/ros/lyrical/lib/python3.14/site-packages/rclpy/node.py", line 1038, in _call_post_set_parameters_callback
    callback(parameter_list)
    ~~~~~~~~^^^^^^^^^^^^^^^^
  File "/tmp/ros2-pr04-defect/src/patrol/patrol/patrol.py", line 81, in apply
    self.timer = self.create_timer(1.0 / self.publish_hz, self.tick)
                                   ~~~~^~~~~~~~~~~~~~~~~
ZeroDivisionError: division by zero

```

## Та же проверка после восстановления

Основная ветка `lab_4` содержит проверку конечности и диапазона 1–30 Гц до изменения параметров или таймера. Для исправленной версии выполнен тот же сценарий команд:

```bash
python3 tools/record_pr04.py --source . --output evidence/pr04/fixed-commands.md
```

При 10 Гц измерено около 10.000 Гц; после установки 5.0 — около 5.000 Гц. Ноль отклонён с объяснением, `ros2 param get` по-прежнему возвращает 5.0, измерение после отказа по-прежнему показывает около 5 Гц. Изменения `linear_speed=0.8` и `turn_rate=-0.5` подтверждены сообщением `Twist`.

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

## Тесты чистой функции и состояния ноды

`test_parameters.py` проверяет чистую `validate_values`: допустимые 10.0 и 5.0, границы 1 и 30 Гц, ноль, отрицательную частоту, выход за диапазон, NaN и обе бесконечности для каждого параметра, неверные типы, границы скорости и поворота.

`test_node_parameters.py` проверяет замену единственного таймера при 10→5, сохранение того же объекта таймера и параметра 5.0 при отклонении нуля/отрицательной частоты/NaN, изменение скоростей без замены таймера, отклонение всего атомарного набора и неверных начальных значений.

Точный регрессионный тест до восстановления проверки (исходники из отдельной рабочей копии):

```bash
ROS_DOMAIN_ID=175 ROS_LOG_DIR=/tmp/pr04-test-logs PYTHONPATH="/tmp/ros2-pr04-defect/src/patrol:$PYTHONPATH" python3 -m pytest '/tmp/ros2-pr04-defect/src/patrol/test/test_node_parameters.py::test_rejected_frequency_preserves_parameter_and_timer[0.0]' -q
```

```text
F                                                                        [100%]
=================================== FAILURES ===================================
__________ test_rejected_frequency_preserves_parameter_and_timer[0.0] __________

node = <patrol.patrol.Patrol object at 0x7bf4f960c830>, hz = 0.0

    @pytest.mark.parametrize('hz', [0.0, -1.0, float('nan')])
    def test_rejected_frequency_preserves_parameter_and_timer(node, hz):
        """Keep the accepted 5 Hz parameter and timer after an invalid proposal."""
        assert node.set_parameters_atomically([
            Parameter('publish_hz', value=5.0)]).successful
        old_timer = node.timer
>       result = node.set_parameters_atomically([Parameter('publish_hz', value=hz)])
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

/tmp/ros2-pr04-defect/src/patrol/test/test_node_parameters.py:46: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/opt/ros/lyrical/lib/python3.14/site-packages/rclpy/node.py:820: in set_parameters_atomically
    return self._set_parameters_atomically(parameter_list)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/ros/lyrical/lib/python3.14/site-packages/rclpy/node.py:840: in _set_parameters_atomically
    return self._set_parameters_atomically_common(parameter_list)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/ros/lyrical/lib/python3.14/site-packages/rclpy/node.py:944: in _set_parameters_atomically_common
    self._call_post_set_parameters_callback(parameter_list)
/opt/ros/lyrical/lib/python3.14/site-packages/rclpy/node.py:1038: in _call_post_set_parameters_callback
    callback(parameter_list)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <patrol.patrol.Patrol object at 0x7bf4f960c830>
updates = [<rclpy.parameter.Parameter object at 0x7bf4f96651d0>]

    def apply(self, updates):
        """Apply accepted values and replace the timer only when needed."""
        changed = {p.name: p.value for p in updates}
    
        old_hz = self.publish_hz
    
        self.linear_speed = changed.get('linear_speed', self.linear_speed)
        self.turn_rate = changed.get('turn_rate', self.turn_rate)
        self.publish_hz = changed.get('publish_hz', self.publish_hz)
    
        if self.publish_hz != old_hz:
            self.timer.cancel()
            self.destroy_timer(self.timer)
>           self.timer = self.create_timer(1.0 / self.publish_hz, self.tick)
                                           ^^^^^^^^^^^^^^^^^^^^^
E           ZeroDivisionError: division by zero

/tmp/ros2-pr04-defect/src/patrol/patrol/patrol.py:81: ZeroDivisionError
=========================== short test summary info ============================
FAILED ../../../tmp/ros2-pr04-defect/src/patrol/test/test_node_parameters.py::test_rejected_frequency_preserves_parameter_and_timer[0.0]
1 failed in 0.40s

```

Тот же тест на исправленной версии после подключения workspace:

```bash
ROS_DOMAIN_ID=175 ROS_LOG_DIR=/tmp/pr04-test-logs python3 -m pytest 'src/patrol/test/test_node_parameters.py::test_rejected_frequency_preserves_parameter_and_timer[0.0]' -q
```

```text
.                                                                        [100%]
1 passed in 0.37s

```

Подробный запуск чистой функции:

```bash
python3 -m pytest src/patrol/test/test_parameters.py -v
```

```text
============================= test session starts ==============================
platform linux -- Python 3.14.4, pytest-9.0.2, pluggy-1.6.0 -- /usr/bin/python3
cachedir: .pytest_cache
rootdir: /home/cyberpsychoz/ros2_robotics_course/src/patrol
plugins: ament_pep257-0.20.6, ament_lint-0.20.6, ament_flake8-0.20.6, ament_xmllint-0.20.6, launch_testing_ros-0.29.9, ament_mypy-0.20.6, ament_copyright-0.20.6, launch_testing-3.9.8, cov-5.0.0, typeguard-4.4.4, colcon-core-0.21.3
collecting ... collected 30 items

src/patrol/test/test_parameters.py::test_valid_frequency[10.0] PASSED    [  3%]
src/patrol/test/test_parameters.py::test_valid_frequency[5.0] PASSED     [  6%]
src/patrol/test/test_parameters.py::test_valid_frequency[1.0] PASSED     [ 10%]
src/patrol/test/test_parameters.py::test_valid_frequency[30.0] PASSED    [ 13%]
src/patrol/test/test_parameters.py::test_outside_range[0-publish_hz-invalid_values0] PASSED [ 16%]
src/patrol/test/test_parameters.py::test_outside_range[1-linear_speed-invalid_values1] PASSED [ 20%]
src/patrol/test/test_parameters.py::test_outside_range[2-turn_rate-invalid_values2] PASSED [ 23%]
src/patrol/test/test_parameters.py::test_nonfinite[nan-0] PASSED         [ 26%]
src/patrol/test/test_parameters.py::test_nonfinite[nan-1] PASSED         [ 30%]
src/patrol/test/test_parameters.py::test_nonfinite[nan-2] PASSED         [ 33%]
src/patrol/test/test_parameters.py::test_nonfinite[inf-0] PASSED         [ 36%]
src/patrol/test/test_parameters.py::test_nonfinite[inf-1] PASSED         [ 40%]
src/patrol/test/test_parameters.py::test_nonfinite[inf-2] PASSED         [ 43%]
src/patrol/test/test_parameters.py::test_nonfinite[-inf-0] PASSED        [ 46%]
src/patrol/test/test_parameters.py::test_nonfinite[-inf-1] PASSED        [ 50%]
src/patrol/test/test_parameters.py::test_nonfinite[-inf-2] PASSED        [ 53%]
src/patrol/test/test_parameters.py::test_nonnumeric[0-True] PASSED       [ 56%]
src/patrol/test/test_parameters.py::test_nonnumeric[0-False] PASSED      [ 60%]
src/patrol/test/test_parameters.py::test_nonnumeric[0-5.0] PASSED        [ 63%]
src/patrol/test/test_parameters.py::test_nonnumeric[0-None] PASSED       [ 66%]
src/patrol/test/test_parameters.py::test_nonnumeric[1-True] PASSED       [ 70%]
src/patrol/test/test_parameters.py::test_nonnumeric[1-False] PASSED      [ 73%]
src/patrol/test/test_parameters.py::test_nonnumeric[1-5.0] PASSED        [ 76%]
src/patrol/test/test_parameters.py::test_nonnumeric[1-None] PASSED       [ 80%]
src/patrol/test/test_parameters.py::test_nonnumeric[2-True] PASSED       [ 83%]
src/patrol/test/test_parameters.py::test_nonnumeric[2-False] PASSED      [ 86%]
src/patrol/test/test_parameters.py::test_nonnumeric[2-5.0] PASSED        [ 90%]
src/patrol/test/test_parameters.py::test_nonnumeric[2-None] PASSED       [ 93%]
src/patrol/test/test_parameters.py::test_speed_boundaries[0.0--1.0] PASSED [ 96%]
src/patrol/test/test_parameters.py::test_speed_boundaries[1.0-1.0] PASSED [100%]

============================== 30 passed in 0.34s ==============================

```

Итоговые `python3 -m pytest src/patrol/test -q`, сборка и `colcon test` записаны в `tests.txt`. Существующий `test_copyright` пропущен штатным декоратором шаблона: в исходниках нет авторских заголовков; функциональные тесты и проверки flake8/pep257 выполнены.

## Сервис: запрос, действие: цель

Вызов `/clear` передаёт один запрос очистки следа и получает один ответ о завершении. Цель `/turtle1/rotate_absolute` задаёт поворот, который выполняется во времени, допускает feedback о ходе, отмену и итоговый результат; в этой работе действие только обнаружено командой `ros2 action list -t`, цель поворота не отправлялась.

Собственные IDL и action-сервер не добавлялись. Реальные выводы `/clear` и `ros2 action list -t` приведены в разделе исправленной версии выше.

## Учёт времени

В `report.json` поле `time` содержит норматив из условия (2 академических часа и 2 часа самостоятельной работы), а не подтверждённые фактические затраты автора. Основание явно записано в `time.basis`; перед сдачей автор может уточнить свои фактические часы отдельным evidence-коммитом.
