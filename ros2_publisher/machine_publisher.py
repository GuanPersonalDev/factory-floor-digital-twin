import sys
from pathlib import Path 
sys.path.insert(0, str(Path(__file__).resolve().parent.parent)) # add root to Python search path due to I wanna load config.config_loader

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json
import random
from config.config_loader import FactoryConfig, MachineConfig
from topic_data_generator import MachineState, ScriptPhase

PUBLISH_INTERVAL = 1.0 # second

class MachinePublisher(Node):
    def __init__(self):
        super().__init__("machine_publisher")
        self._config = FactoryConfig()

        self._machine_state_list :list[MachineState] = []
        self._param_publisher_dic = {}

        for machine in self._config.machines:
            machine_state = MachineState(machine.machine_id, [])
            self._machine_state_list.append(machine_state)
            for p in self._config.parameters:
                ros_topic = machine.getRosTopic(p)
                publisher = self.create_publisher(String, ros_topic, 10)
                self._param_publisher_dic[p] = publisher

        self.timer = self.create_timer(PUBLISH_INTERVAL, self.publishMachineData)
        self.get_logger().info("MachinePublisher has already activated")
        pass

    def publishMachineData(self):
        for machine_state in self._machine_state_list:
            for param, value in machine_state.getAllTopics().items():
                data = {}
                data["machine_id"] = machine_state.machineId
                data[param] = value
                msg = String()
                msg.data = json.dumps(data)
                publisher = self._param_publisher_dic[param]
                publisher.publish(msg)

                topic = self._config.getMachineById(machine_state.machineId).getRosTopic(param)
                self.get_logger().info(f"{topic} -> {msg}")

def main(args=None):
    rclpy.init(args=args)
    node = MachinePublisher()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == "__main__":
    main()