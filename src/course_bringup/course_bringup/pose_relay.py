"""Relay the turtlesim pose as a best-effort sensor stream."""

import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy

try:
    from turtlesim_msgs.msg import Pose as TurtlePose
except ModuleNotFoundError:  # Jazzy keeps the interface in turtlesim.
    from turtlesim.msg import Pose as TurtlePose  # type: ignore[no-redef]


class PoseRelay(Node):
    """Republish the global turtle pose under this node's namespace."""

    def __init__(self):
        super().__init__('pose_relay')
        sensor_qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
        )
        self.publisher = self.create_publisher(
            TurtlePose, 'sensor_pose', sensor_qos
        )
        self.pose_sub = self.create_subscription(
            TurtlePose, '/turtle1/pose', self.relay_pose, 10
        )

    def relay_pose(self, message):
        """Forward the latest pose without changing the message."""
        self.publisher.publish(message)


def main(args=None):
    """Run the relay until interrupted."""
    rclpy.init(args=args)
    node = None
    try:
        node = PoseRelay()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
