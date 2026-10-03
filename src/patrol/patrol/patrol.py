from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose


class Patrol(Node):
    def __init__(self):
        super().__init__('patrol')
        self.latest_pose = None
        self.pose_sub = self.create_subscription(
            Pose, '/turtle1/pose', self.on_pose, 10
        )

    def on_pose(self, message):
        self.latest_pose = message


def choose_command(pose: Pose | None) -> Twist:
    """Return the command for the most recently received pose."""
    command = Twist()

    if pose is None:
        return command

    command.linear.x = 0.5
    command.angular.z = 0.3

    return command


def main(args=None):
    rclpy.init(args=args)
    node = Patrol()

    publisher = node.create_publisher(Twist, 'cmd_vel', 10)

    def tick():
        publisher.publish(choose_command(node.latest_pose))

    timer = node.create_timer(0.1, tick)

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        timer.cancel()
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
