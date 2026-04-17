MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = 1883

# ROS2 topic -> MQTT topic mapping
TOPIC_MAP = {
    "/factory/machine_01/statue": "factory/machine_01/status",
    "/factory/machine_02/statue": "factory/machine_02/status",
    "/factory/machine_03/statue": "factory/machine_03/status"
}