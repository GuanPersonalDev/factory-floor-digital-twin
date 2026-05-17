import paho.mqtt.client as mqtt
import json
import queue
import threading
from typing import Callable, Optional
from omniverse_extension.Tool.debug import DebugLogger

class MqttClient:
    def __init__(self, host: str, port: int):
        # init MQTT
        self.host_ = host
        self.port_ = port
        self.client_ = None
        self._message_queue: queue.Queue = queue.Queue()
        self._logger = DebugLogger()
        self._logger.enable = True
       
    def connect(self, topics: list[str]):
        try:
            self.client_ = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
            self.client_.on_connect = lambda c, u, f, rc, p: self.on_connect(c, topics, rc)
            self.client_.on_message = self.on_message
            self.client_.connect(self.host_, self.port_)
            self.client_.loop_start()
        except Exception as e:
            print(f"[Mqtt Client] Connect error: {e}")
    
    def disconnect(self):
        if self.client_:
            self.client_.loop_stop()
            self.client_.disconnect()
            self._logger.log("[Mqtt Client] Disconnect end")

    def on_connect(self, client, topics: list[str], reason_code):
        if reason_code == 0:
            self._logger.log(f"[Mqtt Client] Connect success: {self.host_}:{self.port_}")
            for topic in topics:
                client.subscribe(topic)
                self._logger.log(f"[Mqtt Client] Subscribe: {topic}")
        else:
            self._logger.log(f"[Mqtt Client] Connect fail: {reason_code}")

    def on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            self._message_queue.put((msg.topic, data))
        except json.JSONDecodeError as e:
            self._logger.log(f"[Mqtt Client] Json parse error: {e}")
        except Exception as e:
            print(f"[Mqtt Client] Message process error: {e}")
    
    def poll(self) -> list[tuple[str, dict]]:
        messages = []
        try:
            while True:
                messages.append(self._message_queue.get_nowait())
        except queue.Empty:
            pass
        return messages