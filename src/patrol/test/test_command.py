from patrol.patrol import choose_command
from turtlesim.msg import Pose


def test_without_pose():
    command = choose_command(None)
    assert command.linear.x == 0.0
    assert command.angular.z == 0.0


def test_with_pose():
    command = choose_command(Pose(x=5.0, y=5.0))
    assert command.linear.x == 0.5
    assert command.angular.z == 0.3
