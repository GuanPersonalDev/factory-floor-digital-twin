import sys
from pathlib import Path 
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent)) # add root to Python search path due to I wanna load config.config_loader
from config.config_loader import FactoryConfig
from config.topic_resolver import parseMqttTopic, getAllMachinesMqttPattern
from omniverse_extension.omniverse_factory_twin.factory_log import FactoryLog

import omni.kit.app
from pxr import Sdf, Gf, UsdGeom
import omni.usd
import threading
from .base_extension import BaseMqttExtension

# MACHINE_USD_PATHS = {
#     "factory/machine_01/status": "/World/Machine_01",
#     "factory/machine_02/status": "/World/Machine_02",
#     "factory/machine_03/status": "/World/Machine_03",
# }

class MachineInfo():
    def __init__(self, machine_id):
        self.machine_id = machine_id

    def calc_color(self, config :FactoryConfig, log :FactoryLog) -> list[float]:
        operation_mode = log.getLatestMode(self.machine_id)
        if operation_mode == None:
            operation_mode = config.OFFLINE_MODE_KEY
        servity = "NORMAL"
        servity_level = 0
        for p in config.parameters:
            if p == config.OPERATION_PARAM_KEY:
                continue
            topic = log.getMachineLastestTopic(self.machine_id, p)
            if topic == None:
                continue
            value = topic[p]
            tmp_servity, tmp_servity_level = config.computeSeverity(p, value)
            if tmp_servity_level > servity_level:
                servity_level = tmp_servity_level
                servity = tmp_servity
            
        color = config.resolveColor(operation_mode, servity)
        print(f"[Factory Twin] {self.machine_id} operation mode: {operation_mode}, color: {color}")
        opacity = config.getOpacity(operation_mode)
        result = list(color)
        result.append(opacity)
        return result


class FactoryTwinExtension(BaseMqttExtension):

    MQTT_BROKER_HOST = "localhost"
    MQTT_BROKER_PORT = 1883

    def onExtensionStartup(self, ext_id):
        self._config = FactoryConfig()
        self._pendingUpdates = {}
        self._lock = threading.Lock()
        self._updateSub = omni.kit.app.get_app().get_update_event_stream().create_subscription_to_pop(
            self.onUpdate, name="factory_twin_update"
        )
        self._machine_info_dic = {}
        for machine in self._config.machines:
            self._machine_info_dic[machine.machine_id] = MachineInfo(machine.machine_id)
        self._log = FactoryLog()
        print("[Factory Twin] Extension activate")

    def getMqttTopics(self):
        return getAllMachinesMqttPattern()

    def onUpdate(self, event):
        with self._lock:
            updates = dict(self._machine_info_dic)
        for machine_id, machine_info in updates.items():
            machine = self._config.getMachineById(machine_id)
            color = machine_info.calc_color(self._config, self._log)
            
            self.updateMachineColor(machine.usd_prim_path, color)

    def onExtensionShutdown(self):
        self._updateSub = None
        print("[Factory Twin] Extension end")

    # Called by base class
    def onMqttMessage(self, topic: str, data: dict):
        print(f"[Factory Twin] get message: {topic} -> {data}")
        machine_id, param = parseMqttTopic(topic) 
        value = data.get(param)
        self._log.record(machine_id, data)
        for p, v in self._machine_info_dic[machine_id].params.items():
            print(f"{machine_id} [{p}:{v}]")

    def updateMachineColor(self, usd_path: str, color: Gf.Vec4f):
        try:
            stage = omni.usd.get_context().get_stage()
            prim = stage.GetPrimAtPath(usd_path)
            if not prim.IsValid():
                print(f"[Factory Twin] Not found prim: {usd_path}")
                return
            gprim = UsdGeom.Gprim(prim)
            gprim.GetDisplayColorAttr().Set(
                [(color[0], color[1], color[2])]
            )
            gprim.GetDisplayOpacityAttr().Set([color[3]])
        except Exception as e:
            print(f"[Factory Twin] Update color error: {usd_path} -> {e}")