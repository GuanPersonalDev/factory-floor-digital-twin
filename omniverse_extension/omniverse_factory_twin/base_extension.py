import omni.ext
import sys
from .mqtt_client import MqttClient

class BaseMqttExtension(omni.ext.IExt):
    
    MQTT_HOST = "localhost"
    MQTT_PORT = 1883

    _EXTERNAL_MODULE_PREFIXES = ('config', 'omniverse_extension.tool')

    def on_startup(self, ext_id):
        print(f"[{self.__class__.__name__}] activated")
        self.mqttClient_ = MqttClient(self.MQTT_HOST, self.MQTT_PORT)
        self.on_extension_startup(ext_id)
        self.mqttClient_.connect(self.get_mqtt_topics())

        self._update_sub = omni.kit.app.get_app().get_update_event_stream().create_subscription_to_pop(
            self._on_update, name="mqtt_poll"
        )
    
    def _on_update(self, event):
        got_message = False
        for topic, data in self.mqttClient_.poll():
            self.on_mqtt_message(topic, data)
            got_message = True
        if got_message:
            self._after_got_mqtt_message()

    def _after_got_mqtt_message(self):
        pass

    def get_mqtt_topics(self):
        return []

    def on_shutdown(self):
        print(f"[{self.__class__.__name__}] shutdown")
        self._update_sub = None
        if hasattr(self, 'mqttClient_') and self.mqttClient_:
            self.mqttClient_.disconnect()
            self.mqttClient_ = None
        self.on_extension_shutdown()
        self._purge_external_module_caches()

    def _purge_external_module_caches(self):
        for key in list(sys.modules.keys()):
            if any(key == p or key.startswith(p + '.') for p in self._EXTERNAL_MODULE_PREFIXES):
                del sys.modules[key]

    def on_extension_startup(self, ext_id):
        pass

    def on_extension_shutdown(self):
        pass
        
    def on_mqtt_message(self, topic: str, data: dict):
        raise NotImplementedError