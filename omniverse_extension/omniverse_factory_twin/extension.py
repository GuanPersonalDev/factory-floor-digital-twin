import omni.ext
import omni.kit.commands
import paho.mqtt.client as mqtt
import json
import threading
from .base_extension import BaseMqttExtension

class FactoryTwinExtension(BaseMqttExtension):

    MQTT_BROKER_HOST = "localhost"
    MQTT_BROKER_PORT = 1883
    MQTT_TOPICS = [
        "factory/machine_01/status",
        "factory/machine_02/status",
        "factory/machine_03/status",
    ]

    def onExtensionStartup(self, ext_id):
        print("[Factory Twin] Extension activate")

    def onExtensionShutdown(self):
        print("[Factory Twin] Extension end")

    def onMqttMessage(self, topic: str, data: dict):
        print(f"[Factory Twin] get message: {topic} -> {data}")
        # TODO: update usd scene