import sys
from pathlib import Path 
sys.path.insert(0, str(Path(__file__).resolve().parent.parent)) # add root to Python search path due to I wanna load config.config_loader

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json
import random
from config.config_loader import FactoryConfig, MachineConfig

PUBLISH_INTERVAL = 1.0 # second

class Topic():
    def __init__(self, machine :MachineConfig, param, publisher):
        self._machine_id = machine.machine_id
        self._param = param
        self._ros_topic = machine.getRosTopic(param)
        self._publisher = publisher
    
    @property 
    def machineId(self):
        return self._machine_id
    @property
    def rosTopic(self):
        return self._ros_topic

    def generateMachineData(self, config :FactoryConfig):
        data = {}
        data["machine_id"] = self.machineId
        data[self._param] = self.generateRandomData(self._param, config)
        return data

    def generateRandomData(self, parameter, config :FactoryConfig):
        match parameter:
            case "temperature":
                return round(random.uniform(60.0, 95.0), 1)
            case "vibration":
                return round(random.uniform(0.1, 5.0), 2)
            case "operation_mode":
                return random.choice(config.operation_mode)
        return None

    def publish(self, config :FactoryConfig) -> str:
        data = self.generateMachineData(config)
        msg = String()
        msg.data = json.dumps(data)
        self._publisher.publish(msg)
        return msg.data

class MachinePublisher(Node):
    def __init__(self):
        super().__init__("machine_publisher")
        self._config = FactoryConfig()

        self._top_list :list[Topic] = []
        for p in self._config.parameters:
            for machine in self._config.machines:
                ros_topic = machine.getRosTopic(p)
                publisher = self.create_publisher(String, ros_topic, 10)
                topic = Topic(machine, p, publisher)
                self._top_list.append(topic) 

        self.timer = self.create_timer(PUBLISH_INTERVAL, self.publishMachineData)
        self.get_logger().info("MachinePublisher has already activated")
        pass

    def publishMachineData(self):
        for topic in self._top_list:
            msg = topic.publish(self._config)
            self.get_logger().info(f"{topic.rosTopic} -> {msg}")

def main(args=None):
    rclpy.init(args=args)
    node = MachinePublisher()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == "__main__":
    main()