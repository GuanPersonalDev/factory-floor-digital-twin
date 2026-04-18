MQTT_BROKER_HOST = "10.255.255.254"
MQTT_BROKER_PORT = 1883

# ROS2 topic -> MQTT topic mapping
TOPIC_MAP = {
    "/factory/machine_01/status": "factory/machine_01/status",
    "/factory/machine_02/status": "factory/machine_02/status",
    "/factory/machine_03/status": "factory/machine_03/status"
}