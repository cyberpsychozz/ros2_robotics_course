"""Check velocity selection with and without a received pose."""

from patrol.patrol import choose_command, Pose


def test_without_pose():
    """Stay still until a pose has arrived, regardless of configured speeds."""
    command = choose_command(None, 0.8, -0.7)
    assert command.linear.x == 0.0
    assert command.angular.z == 0.0


def test_with_pose():
    """Use the supplied settings rather than hardcoded default velocities."""
    command = choose_command(Pose(x=5.0, y=5.0), 0.8, -0.7)
    assert command.linear.x == 0.8
    assert command.angular.z == -0.7
