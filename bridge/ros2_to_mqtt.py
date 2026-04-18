import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import paho.mqtt.client as mqtt
from config import MQTT_BROKER_HOST, MQTT_BROKER_PORT, TOPIC_MAP

class Ros2MqttBridge(Node):
    def __init__(self):
        super().__init__("ros2_mqtt_bridge")

        # init MQTT client
        self.mqttClient_ = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.mqttClient_.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
        self.mqttClient_.loop_start()

        self.get_logger().info(f"Connected to MQTT Broker : {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
        for ros2_topic, mqtt_topic in TOPIC_MAP.items():
            self.create_subscription(
                String,
                ros2_topic,
                lambda msg, t=mqtt_topic: self.onRos2Message(msg, t),
                10
            )
        self.get_logger().info("Ros2MqttBridge has already activated")

    def onRos2Message(self, msg, mqtt_topic):
        # get message from ROS2 and send to MQTT
        self.mqttClient_.publish(mqtt_topic, msg.data)
        self.get_logger().info(f"Published: {mqtt_topic} -> {msg.data}")
        pass

def main(args=None):
    rclpy.init(args=args)
    node = Ros2MqttBridge()
    rclpy.spin(node)
    rclpy.shutdown()
    pass

if __name__ == "__main__":
    main()