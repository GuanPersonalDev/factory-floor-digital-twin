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
        self.onExtensionStartup(ext_id)
        self.mqttClient_.connect(self.MQTT_TOPICS)

    def on_shutdown(self):
        print(f"[{self.__class__.__name__}] shutdown")
        self.onExtensionShutdown()
        if hasattr(self, 'mqttClient_') and self.mqttClient_:
            self.mqttClient_.disconnect()
            self.mqttClient_ = None

    def onExtensionStartup(self, ext_id):
        pass

    def onExtensionShutdown(self):
        pass
        
    def onMqttMessage(self, topic: str, data: dict):
        raise NotImplementedError