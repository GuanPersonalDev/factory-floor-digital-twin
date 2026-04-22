# Factory Floor Digital Twin - Architecture

## Data flow
WSL2 ROS2 Publisher
    -> /factory/machine_xx/status (ROS2 Topic)
    -> ros2_to_mqtt.py (Bridge)
    -> factory/machine_xx/status (MQTT Topic)
    -> Docker Mosquitto (Broker)
    -> Omniverse Kit Extension
    -> USD Scene Color Update

## Components
- ros2_publisher/mahine_publisher.py
- bridge/ros2_to_mqtt.py
- bridge/config.py
- omniverse_extension/omniverse_factory_twin/
    - extension.py
    - base_extension.py
    - mqtt_client.py