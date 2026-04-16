import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json
import random

MACHINES = ["machine_01", "machine_02", "machine_03"]
PUBLISH_INTERVAL = 1.0 # second

class MachinePublisher(Node):
    def __init__(self):
        super().__init__("machine_publisher")

        self.publishers_ = {
            machine: self.create_publisher(String, f"/factory/{machine}/status", 10)
            for machine in MACHINES
        }

        self.timer = self.create_timer(PUBLISH_INTERVAL, self.publishMachineData)
        self.get_logger().info("MachinePublisher has already activated")
        pass

    def generateMachineData(self, machine_id):
        return{
            "machine_id": machine_id,
            "temperature": round(random.uniform(60.0, 95.0), 1),
            "vibration": round(random.uniform(0.1, 5.0), 2),
            "status": random.choice(["running", "running", "running", "warning", "erro"]),
        }

    def publishMachineData(self):
        for machine_id, publisher in self.publishers_.items():
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