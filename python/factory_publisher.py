
# This is the node which simulate sensor in factory
# publish temperature and state to ROS2 Topic

import rclpy
from rclpy.node import Node
from std_msgs import Float32, String

class FactoryPublisher(Node):
    def __init__(self):
        super().__init__('factory_publisher')
        self._publisher_dic = {}
        # machine * 3
        for i in range(3):
            self._init_machine_publisher(i)

    def _init_machine_publisher(self, index):
        folder = f'factory/machine{index}'
        temp_name = f'{folder}/temperature'
        status_name = f'{folder}/status'
        self._generate_publisher(Float32, temp_name, 10)
        self._generate_publisher(String, status_name, 10)

    def _generate_publisher(self, msg_type, name, buffer_size):
        result = self.create_publisher(msg_type, name, buffer_size)
        if name not in self._publisher_dic:
            self._publisher_dic[name] = self.create_publisher(msg_type, name, buffer_size)