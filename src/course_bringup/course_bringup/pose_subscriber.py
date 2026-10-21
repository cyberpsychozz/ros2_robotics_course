"""Inspect the relayed pose stream with a configurable QoS profile."""

import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy

try:
    from turtlesim_msgs.msg import Pose as TurtlePose
except ModuleNotFoundError:  # Jazzy keeps the interface in turtlesim.
    from turtlesim.msg import Pose as TurtlePose  # type: ignore[no-redef]


class PoseSubscriber(Node):
    """Log the first pose received with the requested reliability."""

    def __init__(self):
        super().__init__('pose_subscriber')

        self.declare_parameter('subscriber_reliability', 'reliable')
        reliability_name = self.get_parameter('subscriber_reliability').value

        policies = {
            'reliable': ReliabilityPolicy.RELIABLE,
            'best_effort': ReliabilityPolicy.BEST_EFFORT,
        }

        if reliability_name not in policies:
            raise ValueError(
                'subscriber_reliability must be reliable or best_effort'
            )

        qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=policies[reliability_name],
            durability=DurabilityPolicy.VOLATILE,
        )

        self.received_count = 0
        self.subscription = self.create_subscription(
            TurtlePose, 'sensor_pose', self.on_pose, qos
        )
        self.get_logger().info(
            f'Subscribing to sensor_pose with {reliability_name}'
        )

    def on_pose(self, message):
        """Report when the first compatible message arrives."""
        self.received_count += 1
        if self.received_count == 1:
            self.get_logger().info(
                f'First pose received: x={message.x:.2f}, y={message.y:.2f}'
            )


def main(args=None):
    """Run the subscriber until interrupted."""
    rclpy.init(args=args)
    node = None
    try:
        node = PoseSubscriber()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
