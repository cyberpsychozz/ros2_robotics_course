"""Check the expected attachment of the lidar."""

from pathlib import Path
import xml.etree.ElementTree as ET

import xacro


def test_lidar_parent():
    """The lidar must be attached directly to the chassis."""
    model = (
        Path(__file__).resolve().parents[1]
        / 'urdf'
        / 'ackerman_robot.urdf.xacro'
    )
    document = xacro.process_file(str(model))
    robot = ET.fromstring(document.toxml())

    joint = robot.find("./joint[@name='lidar_joint']")
    assert joint is not None, 'Missing lidar_joint'

    parent = joint.find('parent')
    assert parent is not None, 'Missing lidar parent'
    assert parent.get('link') == 'base_link'