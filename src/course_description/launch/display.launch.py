"""Publish the robot description and optionally open its RViz view."""

from pathlib import Path

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription  # type: ignore[attr-defined]
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node

import xacro


def generate_launch_description():
    """Expand Xacro and launch the description publisher and viewer."""
    share = Path(get_package_share_directory('course_description'))
    model = share / 'urdf' / 'ackerman_robot.urdf.xacro'
    robot_description = xacro.process_file(str(model)).toxml()

    return LaunchDescription([
        DeclareLaunchArgument(
            'rviz', default_value='true',
            description='Open RViz alongside robot_state_publisher',
        ),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            parameters=[{'robot_description': robot_description}],
            output='screen',
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', str(share / 'rviz' / 'display.rviz')],
            # Work around Qt/Ogre resize flicker on scaled XWayland displays.
            # Keep these settings local to RViz, not the desktop or ROS nodes.
            additional_env={
                'QT_QPA_PLATFORM': 'xcb',
                'QT_ENABLE_HIGHDPI_SCALING': '0',
                'QT_AUTO_SCREEN_SCALE_FACTOR': '0',
                'QT_SCALE_FACTOR': '1',
                'QT_SCREEN_SCALE_FACTORS': '1',
            },
            condition=IfCondition(LaunchConfiguration('rviz')),
            output='screen',
        ),
    ])
