import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from paho.mqtt.client import mqtt
from config import MQTT_BROKER_HOST, MQTT_BROKER_PORT, TOPIC_MAP

class Ros2MqttBridge(Node):
    def __init__(self):
        super().__init__("ros2_mqtt_bridge")

        # init MQTT client
        self.mqttClient_ = mqtt.Client()

        self.get_logger().info("Ros2MqttBridge has already activated")

    def onRos2Message(self, msg, mqtt_topic):
        # get message from ROS2 and send to MQTT
        # TODO: publish msg.data to MQTT
        pass

def main(args=None):
    rclpy.init(args=args)
    node = Ros2MqttBridge()
    rclpy.spin(node)
    rclpy.shutdown()
    pass

if __name__ == "__main__":
    main()