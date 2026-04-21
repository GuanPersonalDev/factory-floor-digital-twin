import omni.ext
from .mqtt_client import MqttClient

class BaseMqttExtension(omni.ext.IExt):
    
    MQTT_HOST = "localhost"
    MQTT_PORT = 1883
    MQTT_TOPICS: list[str] = []

    def on_startup(self, ext_id):
        print(f"[{self.__class__.__name__}] activated")
        self.mqttClient_ = MqttClient(self.MQTT_HOST, self.MQTT_PORT)
        self.mqttClient_.setMessageCallback(self.onMqttMessage)
        self.mqttClient_.connect(self.MQTT_TOPICS)
        self.onExtensionStartup(ext_id)

    def onExtensionStartup(self):
        pass

    def onExtensionShutdown(self):
        pass
        
    def onMqttMessage(self, topic: str, data: dict):
        raise NotImplementedError