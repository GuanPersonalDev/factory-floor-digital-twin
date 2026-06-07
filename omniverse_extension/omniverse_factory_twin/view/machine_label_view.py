import asyncio
from dataclasses import dataclass

import omni.ui as ui
import omni.ui.scene as sc
from omni.kit.viewport.registry import RegisterScene
from pxr import UsdGeom, Usd

from ..factory_events import FactoryEventType, get_event_stream
from ..model.machine_model import MachineModel
from ..model.machine_prim_solver import get_machine_prim_path

@dataclass
class LabelState:
    is_hover: bool = False
    jump_task: asyncio.Task | None = None
    visible: bool = False

class MachineLabel:
    def __init__(self, machine_id: str, display_name: str, position=(0, 0, 0)):
        self.position = position
        print(f"{machine_id} label pos : {self.position}")
        self.machine_id = machine_id
        self.display_name = display_name
        self.state = LabelState()
        self.label: sc.Label | None = None

    def set_visible(self, visible: bool):
        self.state.visible = visible
        if self.label:
            self.label.visible = visible

    def cancel_jump_task(self):
        if not self.state:
            return
        if self.state.jump_task and not self.state.jump_task.done():
            self.state.jump_task.cancel()
            self.state.jump_task = None

    def set_jump_task(self, duration: float):
        self.state.jump_task = asyncio.ensure_future(self._hide_after(duration))

    async def _hide_after(self, duration: float):
        await asyncio.sleep(duration)
        if not self.state:
            return

        self.state.jump_task = None
        if not self.state.is_hover:
            self.set_visible(False)

    def show_from_hover(self):
        if not self.state:
            return
        self.state.is_hover = True
        self.set_visible(True)
        self.cancel_jump_task()

    def hide_from_hover(self):
        if not self.state:
            return
        self.state.is_hover = False
        self.cancel_jump_task()
        self.set_visible(False)

    def destroy(self):
        self.cancel_jump_task()
        if self.label:
            self.label.destroy()
            self.label = None
        
class MachineLabelView():
    LAYER_NAME = "factory_machine_label_layer"

    _LABEL_Z_OFFSET = 0.0

    def __init__(self):
        self._labels: dict[str, MachineLabel] = {}

        self._scene_view: sc.SceneView | None = None
        self._viewport_layer = None
        self._event_sub = None

    def build(self, stage, machines: list[MachineModel]):
        bbox_cache = UsdGeom.BBoxCache(time=Usd.TimeCode.Default(),includedPurposes=[UsdGeom.Tokens.default_])
        for machine in machines:
            pos = self._calc_position(stage, bbox_cache, machine)
            if not pos:
                continue
            label = MachineLabel(machine_id=machine.machine_id, display_name=machine.machine_id, position=pos)
            self._labels[machine.machine_id] = label

        self._event_sub = get_event_stream().create_subscription_to_pop_by_type(
            int(FactoryEventType.CAMERA_JUMPED),
            self._onfactory_event,
            name="factory machine label events",
        )

        self._viewport_layer = RegisterScene(self._build_label_layer, self.LAYER_NAME)
                    
    def _calc_position(self, stage, bbox_cache: UsdGeom.BBoxCache, machine: MachineModel):
        prim_path = get_machine_prim_path(machine.machine_id)
        prim = stage.GetPrimAtPath(prim_path)
        if not prim or not prim.IsValid():
            return None

        bbox = bbox_cache.ComputeWorldBound(prim).ComputeAlignedBox()
        min_p = bbox.GetMin()
        max_p = bbox.GetMax()
        
        x = (min_p[0] + max_p[0]) * 0.5
        y = (min_p[1] + max_p[1]) * 0.5
        z = max_p[2] + self._LABEL_Z_OFFSET

        return (x, y, z)

    def _onfactory_event(self, event):
        print(f"camera jump event")
        if event.type != int(FactoryEventType.CAMERA_JUMPED):
            return

        machine_id = event.payload["machine_id"]
        if not machine_id:
            return
        
        self._show_from_jump(machine_id, duration=3.0)

    def _build_label_layer(self, viewport_window):
        for label in self._labels.values():
            x, y, z = label.position
            label_text = label.display_name
            with sc.Transform(transform=sc.Matrix44.get_translation_matrix(x, y, z)):
                label.label = sc.Label(label_text, alignment=ui.Alignment.CENTER, size=20, visible=label.state.visible)

        return self

    """ 
    Viewport Scene Layer instance needs
    """
    @property
    def name(self):
        return self.LAYER_NAME

    @property
    def visible(self):
        return True

    @visible.setter
    def visible(self, value):
        pass

    @property
    def categories(self):
        return []


    def _show_from_jump(self, machine_id: str, duration: float):
        label = self._labels.get(machine_id)
        if not label:
            return
        state = label.state
        if state is None:
            return
        if state.is_hover:
            label.set_visible(True)
            return
        
        print(f"label show from jump")
        label.cancel_jump_task()
        label.set_visible(True)
        label.set_jump_task(duration)

    def destroy(self):
        for label in self._labels.values():
            label.destroy()
        self._labels.clear()

        if self._viewport_layer:
            self._viewport_layer.destroy()
            self._viewport_layer = None

        if self._event_sub:
            self._event_sub = None

