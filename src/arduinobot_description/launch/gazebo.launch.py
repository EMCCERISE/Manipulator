import os
from os import pathsep
from ament_index_python.packages import get_package_share_directory, get_package_prefix

from launch import LaunchDescription
from launch.actions import ExecuteProcess, DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.substitutions import EnvironmentVariable, Command, LaunchConfiguration, PathJoinSubstitution, FindExecutable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from pathlib import Path

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

ARGUMENTS = [
    DeclareLaunchArgument('world_path', default_value='',
                          description='The world path, by default is empty.world'),
]

def generate_launch_description():

    # gz_resource_path = SetEnvironmentVariable(name='GAZEBO_MODEL_PATH', value=[
    #                                             EnvironmentVariable('GAZEBO_MODEL_PATH',
    #                                                                 default_value=''),
    #                                             '/usr/share/gazebo-11/models/:',
    #                                             str(Path(get_package_share_directory('arduinobot_description')).
    #                                                 parent.resolve())])
    
    # config_arduinobot_controller = PathJoinSubstitution(
    #     [FindPackageShare('arduinobot_controller'), 'config', 'arduinobot_controller.yaml']
    # )

    # Launch args
    world_path = LaunchConfiguration('world_path')
    
    # # Get URDF via xacro
    # robot_description_command = [
    #         PathJoinSubstitution([FindExecutable(name='xacro')]),
    #         ' ',
    #         PathJoinSubstitution(
    #             [FindPackageShare('jackal_description'), 'urdf', 'jackal.urdf.xacro']
    #         ),
    #         ' ',
    #         'is_sim:=true',
    #         ' ',
    #         'gazebo_controllers:=',
    #          config_arduinobot_controller.yaml,
    #     ]
    
    # launch_arduinobot_description = IncludeLaunchDescription(
    #         PythonLaunchDescriptionSource(
    #             PathJoinSubstitution(
    #                 [FindPackageShare('arduinobot_description'),
    #                  'launch',
    #                  'display.launch.py']
    #             )
    #         ),
    #         launch_arguments=[('robot_description_command', robot_description_command)]
    #     )
    
    # # Gazebo server
    # gzserver = ExecuteProcess(
    #     cmd=['gzserver',
    #          '-s', 'libgazebo_ros_init.so',
    #          '-s', 'libgazebo_ros_factory.so',
    #          '--verbose',
    #          world_path],
    #     output='screen',
    # )

    # # Gazebo client
    # gzclient = ExecuteProcess(
    #     cmd=['gzclient'],
    #     output='screen',
    # )

    # # Spawn robot
    # spawn_robot = Node(
    #     package='gazebo_ros',
    #     executable='spawn_entity.py',
    #     name='spawn_arduinobot',
    #     arguments=['-entity',
    #                'arduinobot',
    #                '-topic',
    #                'robot_description'],
    #     output='screen',
    # )

    arduinobot_description = get_package_share_directory('arduinobot_description')
    arduinobot_description_share = get_package_prefix('arduinobot_description')
    gazebo_ros_dir = get_package_share_directory('gazebo_ros')

    model_arg = DeclareLaunchArgument(name='model', default_value=os.path.join(
                                        arduinobot_description, 'urdf', 'arduinobot.urdf.xacro'
                                        ),
                                      description='Absolute path to robot urdf file'
    )

    model_path = os.path.join(arduinobot_description, "models")
    model_path += pathsep + os.path.join(arduinobot_description_share, "share")

    env_var = SetEnvironmentVariable('GAZEBO_MODEL_PATH', model_path)

    robot_description = ParameterValue(Command(['xacro ', LaunchConfiguration('model')]),
                                       value_type=str)

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description}]
    )

    # Gazebo server
    gzserver = ExecuteProcess(
        cmd=['gzserver',
             '-s', 'libgazebo_ros_init.so',
             '-s', 'libgazebo_ros_factory.so',
             '--verbose'
             ],
        output='screen',
    )

    # Gazebo client
    gzclient = ExecuteProcess(
        cmd=['gzclient'],
        output='screen',
    )

    # Spawn robot
    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_jackal',
        arguments=['-entity',
                   'jackal',
                   '-topic',
                   'robot_description'],
        output='screen',
    )

    # start_gazebo_server = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource(
    #         os.path.join(gazebo_ros_dir, 'launch', 'gzserver.launch.py')
    #     )
    # )

    # start_gazebo_client = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource(
    #         os.path.join(gazebo_ros_dir, 'launch', 'gzclient.launch.py')
    #     )
    # )

    spawn_robot = Node(package='gazebo_ros', executable='spawn_entity.py',
                        arguments=['-entity', 'arduinobot',
                                   '-topic', 'robot_description',
                                  ],
                        output='screen'
    )

    return LaunchDescription([
        env_var,
        model_arg,
        # start_gazebo_server,
        # start_gazebo_client,
        gzserver,
        gzclient,
        robot_state_publisher_node,
        spawn_robot
    ])
