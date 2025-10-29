import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

# ROS2 Launch System will look for this function definition #
def generate_launch_description():

    # Get Package Description and Directory #
    package_description = "my_rb1_description"
    package_directory = get_package_share_directory(package_description)

    # Load URDF File #
    urdf_file = "my_rb1_robot.urdf"
    robot_desc_path = os.path.join(package_directory, "urdf", urdf_file)
    print("URDF Loaded !")
    
    # Joint State Publisher GUI # -> To visualize Movable joints
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui_node',
        output='screen',
        emulate_tty=True,
    )
    
    # Robot State Publisher (RSP) # -> To visualize Fixed joints
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher_node',
        output='screen',
        emulate_tty=True,
        parameters=[{'use_sim_time': True,
                     'robot_description': ParameterValue(
                                            Command(['xacro ', robot_desc_path]),
                                            value_type=str
                                        )}]
    )

    # Load RViz Configuration File #
    rviz_config_file = "config.rviz"
    rviz_config_path = os.path.join(package_directory, "rviz", rviz_config_file)
    print("RViz Config Loaded !")

    # Rviz2 Launch Configuration (RViz)#
    rviz2_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2_node',
        output='screen',
        emulate_tty=True,
        parameters=[{'use_sim_time': True}],
        arguments=['-d', rviz_config_path]
    )

    # Create and Return the Launch Description Object #
    return LaunchDescription(
        [
            joint_state_publisher_gui_node,
            robot_state_publisher_node,
            rviz2_node,
        ]

    )