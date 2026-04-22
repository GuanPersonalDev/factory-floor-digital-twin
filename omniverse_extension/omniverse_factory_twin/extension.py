import omni.kit.app
from pxr import Sdf, Gf, UsdGeom
import omni.usd
import threading
from .base_extension import BaseMqttExtension

MACHINE_USD_PATHS = {
    "factory/machine_01/status": "/World/Machine_01",
    "factory/machine_02/status": "/World/Machine_02",
    "factory/machine_03/status": "/World/Machine_03",
}

class FactoryTwinExtension(BaseMqttExtension):

    MQTT_BROKER_HOST = "localhost"
    MQTT_BROKER_PORT = 1883
    MQTT_TOPICS = list(MACHINE_USD_PATHS.keys())

    def onExtensionStartup(self, ext_id):
        self.pendingUpdates_ = {}
        self.lock_ = threading.Lock()
        self.updateSub_ = omni.kit.app.get_app().get_update_event_stream().create_subscription_to_pop(
            self.onUpdate, name="factory_twin_update"
        )
        print("[Factory Twin] Extension activate")

    def onUpdate(self, event):
        with self.lock_:
            updates = dict(self.pendingUpdates_)
            self.pendingUpdates_.clear()
        for usd_path, color in updates.items():
            self.updateMachineColor(usd_path, color)

    def onExtensionShutdown(self):
        self.updateSub_ = None
        print("[Factory Twin] Extension end")

    def onMqttMessage(self, topic: str, data: dict):
        print(f"[Factory Twin] get message: {topic} -> {data}")
        usd_path = MACHINE_USD_PATHS.get(topic)
        if not usd_path:
            return

        status = data.get("status", "unknown")
        color = self.statusToColor(status)
        with self.lock_:
            self.pendingUpdates_[usd_path] = color

    def statusToColor(self, status: str) -> Gf.Vec3f:
        colorMap = {
            "running": Gf.Vec3f(0.0, 1.0, 0.0),
            "warning": Gf.Vec3f(1.0, 1.0, 0.0),
            "error": Gf.Vec3f(1.0, 0.0, 0.0),
        }
        return colorMap.get(status, Gf.Vec3f(0.5, 0.5, 0.5))

    def updateMachineColor(self, usd_path: str, color: Gf.Vec3f):
        try:
            stage = omni.usd.get_context().get_stage()
            prim = stage.GetPrimAtPath(usd_path)
            if not prim.IsValid():
                print(f"[Factory Twin] Not found prim: {usd_path}")
                return
            UsdGeom.Gprim(prim).GetDisplayColorAttr().Set(
                [(color[0], color[1], color[2])]
            )
        except Exception as e:
            print(f"[Factory Twin] Update color error: {usd_path} -> {e}")