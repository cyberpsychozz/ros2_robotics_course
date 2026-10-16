"""Check finite values and inclusive parameter limits without creating a node."""

from patrol.patrol import validate_values
import pytest


@pytest.mark.parametrize('hz', [10.0, 5.0, 1.0, 30.0])
def test_valid_frequency(hz):
    """Accept both the 10-to-5 change and the frequency boundaries."""
    assert validate_values(hz, 0.5, 0.3) == (True, '')


@pytest.mark.parametrize('index, name, invalid_values', [
    (0, 'publish_hz', [0.0, -1.0, 0.9, 30.1]),
    (1, 'linear_speed', [-0.1, 1.1]),
    (2, 'turn_rate', [-1.1, 1.1]),
])
def test_outside_range(index, name, invalid_values):
    """Reject out-of-range values and identify the offending parameter."""
    for value in invalid_values:
        proposal = [10.0, 0.5, 0.3]
        proposal[index] = value
        ok, reason = validate_values(*proposal)
        assert not ok
        assert name in reason


@pytest.mark.parametrize('index', [0, 1, 2])
@pytest.mark.parametrize('value', [float('nan'), float('inf'), -float('inf')])
def test_nonfinite(index, value):
    """Reject NaN and either infinity in every setting."""
    proposal = [10.0, 0.5, 0.3]
    proposal[index] = value
    assert not validate_values(*proposal)[0]


@pytest.mark.parametrize('value', [True, False, '5.0', None])
@pytest.mark.parametrize('index', [0, 1, 2])
def test_nonnumeric(index, value):
    """Reject booleans and values that are not numbers."""
    proposal = [10.0, 0.5, 0.3]
    proposal[index] = value
    assert not validate_values(*proposal)[0]


@pytest.mark.parametrize('speed, turn', [(0.0, -1.0), (1.0, 1.0)])
def test_speed_boundaries(speed, turn):
    """Accept the inclusive boundaries for speed and turn rate."""
    assert validate_values(10.0, speed, turn) == (True, '')
