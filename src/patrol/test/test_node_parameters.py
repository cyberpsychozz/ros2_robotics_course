"""Check parameter transactions against a real rclpy node and timer."""

from patrol.patrol import Patrol
import pytest
import rclpy
from rclpy.context import Context
from rclpy.parameter import Parameter


@pytest.fixture
def context():
    """Give each test an independent ROS context."""
    ctx = Context()
    rclpy.init(context=ctx)
    yield ctx
    rclpy.try_shutdown(context=ctx)


@pytest.fixture
def node(context):
    """Destroy the node even when a regression assertion fails."""
    patrol = Patrol(context=context)
    yield patrol
    patrol.destroy_node()


def test_frequency_replaces_single_timer(node):
    """Apply 10-to-5 Hz, stop the old timer and leave one active timer."""
    old_timer = node.timer
    assert old_timer.timer_period_ns == 100_000_000
    result = node.set_parameters_atomically([Parameter('publish_hz', value=5.0)])
    assert result.successful
    assert node.get_parameter('publish_hz').value == node.publish_hz == 5.0
    assert node.timer is not old_timer
    assert node.timer.timer_period_ns == 200_000_000
    assert list(node.timers) == [node.timer]
    assert not node.timer.is_canceled()


@pytest.mark.parametrize('hz', [0.0, -1.0, float('nan')])
def test_rejected_frequency_preserves_parameter_and_timer(node, hz):
    """Keep the accepted 5 Hz parameter and timer after an invalid proposal."""
    assert node.set_parameters_atomically([
        Parameter('publish_hz', value=5.0)]).successful
    old_timer = node.timer
    result = node.set_parameters_atomically([Parameter('publish_hz', value=hz)])
    assert not result.successful
    assert result.reason
    assert node.get_parameter('publish_hz').value == node.publish_hz == 5.0
    assert node.timer is old_timer
    assert node.timer.timer_period_ns == 200_000_000
    assert not node.timer.is_canceled()
    assert list(node.timers) == [old_timer]


def test_speed_changes_without_timer_replacement(node):
    """Use new speed settings without resetting the publication timer."""
    old_timer = node.timer
    result = node.set_parameters_atomically([
        Parameter('linear_speed', value=0.8),
        Parameter('turn_rate', value=-0.5),
    ])
    assert result.successful
    assert node.linear_speed == 0.8
    assert node.turn_rate == -0.5
    assert node.timer is old_timer


def test_invalid_batch_has_no_partial_effect(node):
    """Reject an entire atomic batch before changing any field or timer."""
    old_timer = node.timer
    result = node.set_parameters_atomically([
        Parameter('linear_speed', value=0.8),
        Parameter('publish_hz', value=0.0),
    ])
    assert not result.successful
    assert node.linear_speed == node.get_parameter('linear_speed').value == 0.5
    assert node.publish_hz == node.get_parameter('publish_hz').value == 10.0
    assert node.timer is old_timer
    assert not old_timer.is_canceled()


def test_invalid_startup_override(context):
    """Reject a bad initial frequency before dividing or creating a timer."""
    with pytest.raises(ValueError, match='publish_hz'):
        Patrol(context=context, parameter_overrides=[
            Parameter('publish_hz', value=0.0)])
