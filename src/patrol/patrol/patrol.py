"""Publish parameter-controlled velocity commands for turtlesim."""

import math

from geometry_msgs.msg import Twist
from rcl_interfaces.msg import SetParametersResult
import rclpy
from rclpy.node import Node
try:
    from turtlesim_msgs.msg import Pose
except ModuleNotFoundError:  # Jazzy keeps the interfaces in turtlesim.
    from turtlesim.msg import Pose


class Patrol(Node):
    """Validate parameter proposals before applying accepted changes."""

    def __init__(self, **kwargs):
        super().__init__('patrol', **kwargs)
        self.latest_pose = None

        self.declare_parameter('publish_hz', 10.0)
        self.declare_parameter('linear_speed', 0.5)
        self.declare_parameter('turn_rate', 0.3)

        self.publish_hz = self.get_parameter('publish_hz').value
        self.linear_speed = self.get_parameter('linear_speed').value
        self.turn_rate = self.get_parameter('turn_rate').value

        ok, reason = validate_values(
            self.publish_hz, self.linear_speed, self.turn_rate)
        if not ok:
            self.destroy_node()
            raise ValueError(reason)

        self.pose_sub = self.create_subscription(
            Pose, '/turtle1/pose', self.on_pose, 10
        )

        self.publisher = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)

        self.timer = self.create_timer(1.0 / self.publish_hz, self.tick)

        self.add_on_set_parameters_callback(self.validate)
        self.add_post_set_parameters_callback(self.apply)

    def on_pose(self, message):
        """Remember the latest pose."""
        self.latest_pose = message

    def tick(self):
        """Publish a command using the currently accepted settings."""
        command = choose_command(
            self.latest_pose, self.linear_speed, self.turn_rate
        )
        self.publisher.publish(command)

    def validate(self, updates):
        """Check the complete proposal without changing active state."""
        proposed = {p.name: p.value for p in updates}
        ok, reason = validate_values(
            proposed.get('publish_hz', self.publish_hz),
            proposed.get('linear_speed', self.linear_speed),
            proposed.get('turn_rate', self.turn_rate)
        )
        return SetParametersResult(successful=ok, reason=reason)

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
            self.timer = self.create_timer(1.0 / self.publish_hz, self.tick)


def validate_values(publish_hz, linear_speed, turn_rate):
    """Return validity and an explanation for three proposed settings."""
    limits = (
        ('publish_hz', publish_hz, 1.0, 30.0),
        ('linear_speed', linear_speed, 0.0, 1.0),
        ('turn_rate', turn_rate, -1.0, 1.0)
    )

    for param, value, minimum, maximum in limits:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return False, f'{param} must be a number'
        if not math.isfinite(value) or not minimum <= value <= maximum:
            return False, f'{param} must be finite and within {minimum}, {maximum}'

    return True, ''


def choose_command(
    pose: Pose | None, linear_speed: float, turn_rate: float
) -> Twist:
    """Return the command for the most recently received pose."""
    command = Twist()

    if pose is None:
        return command

    command.linear.x = linear_speed
    command.angular.z = turn_rate

    return command


def main(args=None):
    """Run the patrol node until interrupted."""
    rclpy.init(args=args)
    node = None

    try:
        node = Patrol()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
