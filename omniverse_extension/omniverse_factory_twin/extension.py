import omni.ext
import omni.kit.commands
import paho.mqtt.client as mqtt
import json
import threading

MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = 1883
MACHINE_TOPICS = [
    "factory/machine_01/status",
    "factory/machine_02/status",
    "factory/machine_03/status",
]

class FactoryTwinExtension(omni.ext.IExt):

    def on_startup(self, ext_id):
        print("[Factory Twin] Extension activate")
        self.mqttClient_ = None
        self.isRunning_ = False
        self.connectMqtt()

    def on_shutdown(self):
        print("[Factory Twin] Extension end")
        if self.mqttClient_:
            self.mqttClient_.loop_stop()
            self.mqttClient_.disconnect()
        
    def connectMqtt(self):
        # connect to MQTT
        try:
            self.mqttClient_ = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
            self.mqttClient_.on_connect = self.onMqttConnect
            self.mqttClient_.on_message = self.onMqttMessage
            self.mqttClient_.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
            self.mqttClient_.loop_start()
            print(f"[Factory Twin] connecting to MQTT: {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
        except Exception as e:
            print(f"[Factory Twin] MQTT connect error: {e}")
    
    def onMqttConnect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            print("[Factory Twin] Connect to MQTT success")
            for topic in MACHINE_TOPICS:
                client.subscribe(topic)
                print(f"[Factory Twin] Subscribe: {topic}")
        else:
            print(f"[Factory Twin] Connect to MQTT fail: {reason_code}")
        pass

    def onMqttMessage(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            print(f"[Factory Twin] Get message: {msg.topic} -> {data}")
        except Exception as e:
            print(f"[Factory Twin] Message error: {e}")
