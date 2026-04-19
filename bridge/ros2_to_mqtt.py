import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import paho.mqtt.client as mqtt
import time
from config import MQTT_BROKER_HOST, MQTT_BROKER_PORT, TOPIC_MAP

class Ros2MqttBridge(Node):
    def __init__(self):
        super().__init__("ros2_mqtt_bridge")

        # init MQTT client
        self.mqttClient_ = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.connectMqtt()
        self.mqttClient_.loop_start()

        for ros2_topic, mqtt_topic in TOPIC_MAP.items():
            self.create_subscription(
                String,
                ros2_topic,
                lambda msg, t=mqtt_topic: self.onRos2Message(msg, t),
                10
            )
        self.get_logger().info("Ros2MqttBridge has already activated")

    def connectMqtt(self):
        # connect to MQTT Broker with retry
        retryCount = 0
        maxRetries = 5
        while retryCount < maxRetries:
            try:
                self.mqttClient_.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
                self.get_logger().info(f"Connected to MQTT Broker : {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
                return
            except Exception as e:
                retryCount += 1
                self.get_logger().warn(f"connect fail ({retryCount}/{maxRetries}): {e}")
                time.sleep(2)
        raise RuntimeError("Connect to MQTT Broker fail")
                

    def onRos2Message(self, msg, mqtt_topic):
        # get message from ROS2 and send to MQTT
        try:
            data = json.loads(msg.data)
            self.mqttClient_.publish(mqtt_topic, msg.data)
            self.get_logger().info(f"Published: {mqtt_topic} -> {msg.data}")
        except json.JSONDecodeError as e:
            self.get_logger().warn(f"JSON parse error: {e}")
        except Exception as e:
            self.get_logger().warn(f"Publish error: {e}")
            

    def destroy_node(self):
        # clean up the connection of MQTT when node end
        self.mqttClient_.loop_stop()
        self.mqttClient_.disconnect()
        print("Breakout the connection of MQTT")
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = Ros2MqttBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    pass

if __name__ == "__main__":
    main()