# sys and config
import sys
from pathlib import Path 
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent)) # add root to Python search path due to I wanna load config.config_loader
from config.config_loader import FactoryConfig
from config.topic_resolver import parseMqttTopic, getAllMachinesMqttPattern

# omniverse lib
from omniverse_extension.omniverse_factory_twin.factory_log import FactoryLog
import omni.kit.app
from pxr import Sdf, Gf, Usd, UsdGeom, UsdShade
import omni.usd
from omni.usd import StageEventType
import threading
from omniverse_extension.Tool.generate_material import createMaterial, removeMaterial
from omniverse_extension.Tool.debug import DebugLogger
import carb.profiler

# my tools
from .base_extension import BaseMqttExtension

class MachineInfo():
    def __init__(self, machine_id):
        self.machine_id = machine_id

    def calc_color(self, config :FactoryConfig, log :FactoryLog) -> tuple[float, float, float, float]:
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
        # print(f"[Factory Twin] {self.machine_id} operation mode: {operation_mode}, color: {color}")
        return color


class FactoryTwinExtension(BaseMqttExtension):

    MQTT_BROKER_HOST = "localhost"
    MQTT_BROKER_PORT = 1883
    MATERIAL_ROOT = "/World/StatusMaterials"
    ENABLE_LOG = False

    def onExtensionStartup(self, ext_id):
        self._logger = DebugLogger()
        self._logger.enable = self.ENABLE_LOG
        self._config = FactoryConfig()
        self._pendingUpdates = {}
        self._lock = threading.Lock()
        self._material_map: dict[tuple, UsdShade.Material] = {}
        self._collection_map: dict[str, Usd.CollectionAPI] = {}
        self._updateSub = None
        self._is_building = False
        self._stage_event_sub = omni.usd.get_context().get_stage_event_stream().create_subscription_to_pop(
            self.onStageEvent,
            name="factory twin stage ready"
        )
        self._machine_info_dic = {}
        for machine in self._config.machines:
            self._machine_info_dic[machine.machine_id] = MachineInfo(machine.machine_id)
        self._log = FactoryLog()

        stage = omni.usd.get_context().get_stage()
        self._logger.log(f"[Factory Twin] Stage: {stage}")
        self._logger.log(f"[Factory Twin] Stage is valid: {stage is not None}")
        if stage:
            self.initSource()
        else:
            self._logger.log(f"[Factory Twin] State not exist, waiting for ASSETS_LOADED")

        self._logger.log("[Factory Twin] Extension activate")

    def initSource(self):
        self._is_building = True
        try:
            self.buildMaterials()
            self._logger.log(f"[Factory Twin] Material map count: {len(self._material_map)}")
            self.buildCollections()
            self._logger.log(f"[Factory Twin] Collection map count: {len(self._collection_map)}")
            self.startUpdate()           
        finally:
            self._is_building = False

    def startUpdate(self):
         self._updateSub = omni.kit.app.get_app().get_update_event_stream().create_subscription_to_pop(
            self.onUpdate, name="factory_twin_update"
        )
    
    def onStageEvent(self, event):
        if event.type == int(StageEventType.OPENED):
            if self._is_building:
                return
            self._updateSub = None
            stage = omni.usd.get_context().get_stage()
            removeMaterial(stage, self.MATERIAL_ROOT)
            self._material_map = {}
            self._collection_map = {}
            self.initSource()

    def buildMaterials(self):
        stage = omni.usd.get_context().get_stage()
        self._logger.log(f"[Factory Twin] building materials stage: {stage}")

        for operation_mode in self._config.operation_mode:
            for severity in self._config.severityKeys:
                color = self._config.resolveColor(operation_mode, severity)
                if color in self._material_map:
                    continue
                mat_name = f"Mat_{operation_mode}_{severity}"
                self._logger.log(f"[Factory Twin] Ready to create material: {mat_name} color={color}")
                mat = createMaterial(stage, self.MATERIAL_ROOT, mat_name, color)
                self._logger.log(f"[Factory Twin] Created material: {mat}")
                self._material_map[color] = mat
        self._logger.log(f"[Factory Twin] Created {len(self._material_map)} materials")
    
    def buildCollections(self):
        stage = omni.usd.get_context().get_stage()

        for machine in self._config.machines:
            prim_path = machine.usd_prim_path
            root_prim = stage.GetPrimAtPath(prim_path)
            if not root_prim.IsValid():
                self._logger.log(f"[Factory Twin] Build collection fail, not found prim : {prim_path}")
                continue
            collection_api = Usd.CollectionAPI.Apply(root_prim, "statusOverride")
            collection_api.CreateIncludesRel().SetTargets([Sdf.Path(prim_path)])
            collection_api.CreateExpansionRuleAttr().Set("expandPrims")

            self._collection_map[machine.machine_id] = collection_api
            self._logger.log(f"[Factory Twin] Build collection end : {prim_path}")

    def getMqttTopics(self):
        return getAllMachinesMqttPattern()

    def onUpdate(self, event):
        carb.profiler.begin(1, "Digital Twin Extension: on_update")

        with self._lock:
            carb.profiler.begin(1, "Digital Twin Extension: clone info dic")
            updates = dict(self._machine_info_dic)
            carb.profiler.end(1)

        carb.profiler.begin(1, "Digital Twin Extension: for loop on update items")
        for machine_id, machine_info in updates.items():
            machine = self._config.getMachineById(machine_id)

            carb.profiler.begin(1, "Digital Twin Extension: calc color")
            color = machine_info.calc_color(self._config, self._log)
            carb.profiler.end(1)
            carb.profiler.begin(1, "Digital Twin Extension: update color")
            self.updateMachineColor(machine.machine_id, color)
            carb.profiler.end(1)

        carb.profiler.end(1)

        carb.profiler.end(1)

    def onExtensionShutdown(self):
        self._updateSub = None
        self._stage_event_sub = None
        stage = omni.usd.get_context().get_stage()
        self.removeCollections()
        removeMaterial(stage, self.MATERIAL_ROOT)
        self._logger.log("[Factory Twin] Extension end")

    def removeCollections(self):
        stage = omni.usd.get_context().get_stage()
        for machine in self._config.machines:
            root_prim = stage.GetPrimAtPath(machine.usd_prim_path)
            if not root_prim.IsValid():
                continue
            binding_api = UsdShade.MaterialBindingAPI(root_prim)
            binding_api.UnbindCollectionBinding("statusOverride")

            root_prim.RemoveAPI(Usd.CollectionAPI, "statusOverride")

    # Called by base class
    def onMqttMessage(self, topic: str, data: dict):
        self._logger.log(f"[Factory Twin] get message: {topic} -> {data}")
        machine_id, param = parseMqttTopic(topic) 
        value = data.get(param)
        self._log.record(machine_id, data)
        self._logger.log(f"{machine_id} [{param}:{value}]")

    def updateMachineColor(self, machine_id: str, color: tuple):
        try:
            collection_api = self._collection_map[machine_id]
            if collection_api is None:
                self._logger.log(f"[Factory Twin] Not found collection : {machine_id}")
                return
            material = self._material_map.get(color)
            if material is None:
                self._logger.log(f"[Factory Twin] Not found material : {color}")
                return
            root_prim = collection_api.GetPrim()
            binding_api = UsdShade.MaterialBindingAPI.Apply(root_prim)
            binding_rel = binding_api.GetCollectionBindingRel("statusOverride")
            binding_rel.SetTargets([
                collection_api.GetCollectionPath(),
                material.GetPath()
            ])

            UsdShade.MaterialBindingAPI.SetMaterialBindingStrength(
                binding_rel,
                UsdShade.Tokens.strongerThanDescendants
            )

            self._logger.log(f"[Factory Twin] {machine_id} -> Material {color}")
        except Exception as e:
            self._logger.log(f"[Factory Twin] Update color error: {machine_id} -> {e}")
            pass