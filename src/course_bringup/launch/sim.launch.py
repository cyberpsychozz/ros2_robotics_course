from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    namespace = LaunchConfiguration('namespace')
    params_file = LaunchConfiguration('params_file')
    record = LaunchConfiguration('record')
    bag_dir = LaunchConfiguration('bag_dir')
    default_params = PathJoinSubstitution([
        FindPackageShare('course_bringup'), 'config', 'patrol.yaml'
    ])

    return LaunchDescription([
        DeclareLaunchArgument('namespace', default_value='robot_a'),
        DeclareLaunchArgument('params_file', default_value=default_params),
        DeclareLaunchArgument('record', default_value='false'),
        DeclareLaunchArgument(
            'bag_dir', default_value='evidence/pr05/bag-launch'
        ),
        DeclareLaunchArgument(
            'subscriber_reliability', default_value='reliable'
        ),
        Node(
            package='patrol',
            executable='patrol',
            name='patrol',
            namespace=namespace,
            parameters=[params_file],
            remappings=[('turtle1/cmd_vel', '/turtle1/cmd_vel')],
            output='screen',
        ),
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            output='screen',
        ),
        Node(
            package='course_bringup',
            executable='pose_relay',
            name='pose_relay',
            namespace=namespace,
            output='screen',
        ),
        Node(
            package='course_bringup',
            executable='pose_subscriber',
            name='pose_subscriber',
            namespace=namespace,
            output='screen',
            parameters=[{
                'subscriber_reliability': LaunchConfiguration(
                    'subscriber_reliability'
                ),
            }],
        ),
        ExecuteProcess(
            cmd=[
                'ros2', 'bag', 'record', '-s', 'mcap', '-o', bag_dir,
                '--topics',
                PathJoinSubstitution(['/', namespace, 'sensor_pose']),
            ],
            condition=IfCondition(record),
            output='screen',
        ),
    ])
