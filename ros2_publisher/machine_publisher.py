import sys
from pathlib import Path 
sys.path.insert(0, str(Path(__file__).resolve().parent.parent)) # add root to Python search path due to I wanna load config.config_loader

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json
import random
from config.config_loader import FactoryConfig

PUBLISH_INTERVAL = 1.0 # second

class MachinePublisher(Node):
    def __init__(self):
        super().__init__("machine_publisher")
        self._config = FactoryConfig()

        self._machine_publishers_= {}
        for p in self._config.parameters:
            for machine in self._config.machines:
                machine_id = machine.machine_id
                ros_topic = machine.getRosTopic(p)
                self._machine_publishers_[machine_id] = self.create_publisher(String, ros_topic, 10)

        self.timer = self.create_timer(PUBLISH_INTERVAL, self.publishMachineData)
        self.get_logger().info("MachinePublisher has already activated")
        pass

    def generateMachineData(self, machine_id):
        data = {}
        data["machine_id"] = machine_id
        for p in self._config.parameters:
            data[p] = self.generateRandomData(p)
        return data

    def generateRandomData(self, parameter):
        match parameter:
            case "temperature":
                return round(random.uniform(60.0, 95.0), 1)
            case "vibration":
                return round(random.uniform(0.1, 5.0), 2)
            case "operation_mode":
                return random.choice(self._config.operation_mode)
        return None


    def publishMachineData(self):
        for machine_id, publisher in self._machine_publishers_.items():
            data = self.generateMachineData(machine_id)
            msg = String()
            msg.data = json.dumps(data)
            publisher.publish(msg)
            self.get_logger().info(f"{machine_id} -> {msg.data}")

def main(args=None):
    rclpy.init(args=args)
    node = MachinePublisher()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == "__main__":
    main()