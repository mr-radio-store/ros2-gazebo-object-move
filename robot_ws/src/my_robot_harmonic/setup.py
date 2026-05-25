import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'my_robot_harmonic'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        # Install launch files
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        # Include package.xml
        (os.path.join('share', package_name), ['package.xml']),
        # Install URDF files
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),
        # Install config files
        (os.path.join('share', package_name, 'config'), glob('config/*')),
        # Install world files
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*')),
        # Install resource files
        (os.path.join('share', package_name, 'resource'), glob('resource/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='unicycle',
    maintainer_email='unicycle@example.com',
    description='ROS 2 Harmonic robot package for Gazebo simulation',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'teleop_harmonic = my_robot_harmonic.teleop_harmonic:main',
        ],
    },
)
