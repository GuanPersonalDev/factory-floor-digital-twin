import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json
import random

class MachinePublisher(Node):
    def __init__(self):
        super().__init__("machine_publisher")
        # TODO: init 3 publisher
        pass

    def publishMachineData(self):
        # TODO: generate machine data and publish
        pass

def main(args=Node):
    rclpy.init(args=args)
    node = MachinePublisher()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == "__main__":
    main()