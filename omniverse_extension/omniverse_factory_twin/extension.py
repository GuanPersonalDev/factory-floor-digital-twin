# sys and config
import sys
from pathlib import Path 
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent)) # add root to Python search path due to I wanna load config.config_loader
from config.config_loader import FactoryConfig
from config.topic_resolver import parse_mqtt_topic, get_all_machines_mqtt_pattern

# omniverse lib
import omni.usd
from omni.usd import StageEventType

# tools
from .base_extension import BaseMqttExtension
from omniverse_extension.tool.debug import DebugLogger

# factory project
from omniverse_extension.omniverse_factory_twin.factory_log import FactoryLog
from omniverse_extension.omniverse_factory_twin.prim_render_manager import PrimRenderManager
from omniverse_extension.omniverse_factory_twin.view.hud_panel_widget import HudPanelWidget

class FactoryTwinExtension(BaseMqttExtension):

    MQTT_BROKER_HOST = "localhost"
    MQTT_BROKER_PORT = 1883

    def on_extension_startup(self, ext_id):
        self._logger = DebugLogger()
        self._config = FactoryConfig()
        self._logger.enable = self._config.ENABLE_LOG
        self._log = FactoryLog()
        self._prim_render_manager = PrimRenderManager(self._config, self._log)
        self._hud = HudPanelWidget()

        self._updateSub = None
        self._stage_event_sub = omni.usd.get_context().get_stage_event_stream().create_subscription_to_pop(
            self.on_stage_event,
            name="factory twin stage ready"
        )

        stage = omni.usd.get_context().get_stage()
        self._logger.log(f"[Factory Twin] Stage: {stage}")
        self._logger.log(f"[Factory Twin] Stage is valid: {stage is not None}")
        if stage:
            self._prim_render_manager.init_source()
        else:
            self._logger.log(f"[Factory Twin] State not exist, waiting for ASSETS_LOADED")

        self._logger.log("[Factory Twin] Extension activate")
    
    def on_stage_event(self, event):
        if event.type == int(StageEventType.OPENED):
            if self._prim_render_manager.is_building:
                return
            self._updateSub = None
            self._prim_render_manager.init_source()

    def on_extension_shutdown(self):
        self._updateSub = None
        self._stage_event_sub = None
        self._prim_render_manager.dispose()
        self._logger.log("[Factory Twin] Extension end")

    def get_mqtt_topics(self):
        return get_all_machines_mqtt_pattern()

    # Called by base class
    def on_mqtt_message(self, topic: str, data: dict):
        self._logger.log(f"[Factory Twin] get message: {topic} -> {data}")
        machine_id, param = parse_mqtt_topic(topic) 
        value = data.get(param)
        self._log.record(machine_id, data)
        self._logger.log(f"{machine_id} [{param}:{value}]")
