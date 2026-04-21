import paho.mqtt.client as mqtt
import json
from typing import Callable, Optional

class MqttClient:
    def __init__(self, host: str, port: int):
        # init MQTT
        self.host_ = host
        self.port_ = port
        self.client_ = None
        self.messageCallback_: Optional[Callable] = None
        
    def setMessageCallback(self, callback: Callable):
        self.messageCallback_ = callback
        
    def connect(self, topics: list[str]):
        try:
            self.client_ = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
            self.client_.on_connect = lambda c, u, f, rc, p: self.onConnect(c, topics, rc)
            self.client_.on_message = self.onMessage
            self.client_.connect(self.host_, self.port_)
            self.client_.loop_start()
        except Exception as e:
            print(f"[Mqtt Client] Connect error: {e}")
    
    def disconnect(self):
        if self.client_:
            self.client_.loop_stop()
            self.client_.disconnect()
            print("[Mqtt Client] Disconnect end")

    def onConnect(self, client, topics: list[str], reason_code):
        if reason_code == 0:
            print(f"[Mqtt Client] Connect success: {self.host_}:{self.port_}")
            for topic in topics:
                client.subscribe(topic)
                print(f"[Mqtt Client] Subscribe: {topic}")
        else:
            print(f"[Mqtt Client] Connect fail: {reason_code}")

    def onMessage(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            if self.messageCallback_:
                self.messageCallback_(msg.topic, data)
        except json.JSONDecodeError as e:
            print(f"[Mqtt Client] Json parse error: {e}")
        except Exception as e:
            print(f"[Mqtt Client] Message process error: {e}")