from setuptools import find_packages, setup

package_name = 'ros2nodl'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    author='Ted Kern',
    author_email='ted.kern@canonical.com',
    maintainer='Ubuntu Robotics',
    maintainer_email='ubuntu-robotics@lists.launchpad.net',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        ],
        'ros2cli.command': [
            'nodl = ros2nodl.command.nodl:NoDLCommand',
        ],
        'ros2nodl.verb': [
            'show = ros2nodl.verb.show:ShowVerb',
            'validate = ros2nodl.verb.validate:ValidateVerb'
        ]
    },
)
