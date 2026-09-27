# ПР02 — типы сообщений

Типы проверены в ROS 2 Jazzy командами `ros2 interface show geometry_msgs/msg/Twist` и `ros2 topic type /turtle1/pose`.

| Топик | Тип сообщения | Направление и назначение |
| --- | --- | --- |
| `/turtle1/cmd_vel` | `geometry_msgs/msg/Twist` | Команда линейной и угловой скорости для `/turtlesim`. |
| `/turtle1/pose` | `turtlesim/msg/Pose` | Состояние черепахи, публикуемое `/turtlesim`: координаты, угол и текущие скорости. |

`Twist` содержит два вектора `geometry_msgs/msg/Vector3`:

```text
Vector3 linear
  float64 x
  float64 y
  float64 z
Vector3 angular
  float64 x
  float64 y
  float64 z
```

В опыте заданы `linear.x = 1.0` (движение вперёд) и `angular.z = 0.5` (поворот). Остальные компоненты равны нулю. Одна публикация задаёт кратковременное движение; без повторных команд turtlesim останавливается.

`turtlesim/msg/Pose` содержит `x`, `y`, `theta` (положение и угол), `linear_velocity` и `angular_velocity`. Все пять полей имеют тип `float32`. Наличие правильного типа `Twist` недостаточно для доставки: в опыте `/cmd_vel` и `/turtle1/cmd_vel` были разными топиками.
