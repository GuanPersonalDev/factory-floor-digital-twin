from pxr import Gf

# factory
from ..model.machine_model import MachineModel
from ..model.factory_map import CanvasLayoutInfo
from .factory_mini_map_view import FactoryRect, ZoneRect, MachineRect, MiniMapRect, FactoryMiniMapData

class FactoryMiniMapDelegate(FactoryMiniMapData):
    _PADDING = 12
    def __init__(self, layout_info: CanvasLayoutInfo):
        self.factory_rect = self._compute_factory_rect(layout_info)
        print(f"factory rect[{self.factory_rect.rect}]")
        for (_, zone_rect) in self.factory_rect.zones.items():
            print(f"zone rect: id[{zone_rect.zone_id}], rect[{zone_rect.rect}]")
            for machine_rect in zone_rect.machines:
                print(f"machine rect: id[{machine_rect.machine_id}], rect[{machine_rect.rect}]")

    def _compute_factory_rect(self, layout_info: CanvasLayoutInfo) -> FactoryRect:
        (scene_pos, scene_width, scene_height) = self._calc_rect_info(layout_info.world_range)

        zones = {}
        for zone_id, zone_info in layout_info.zones.items():
            (zone_pos, zone_width, zone_height) = self._calc_rect_info(zone_info.world_range)
            (zone_x, zone_y) = self._calc_relative_xy(zone_pos, zone_height, scene_pos, scene_height)

            machines = []
            for machine_info in zone_info.machines:
                (machine_pos, machine_width, machine_height) = self._calc_rect_info(machine_info.world_range)
                (machine_x, machine_y) = self._calc_relative_xy(machine_pos, machine_height, scene_pos, scene_height)
                machines.append(MachineRect(
                    machine_id = machine_info.machine_id,
                    severity_level = 0,
                    rect=MiniMapRect(x=machine_x, y=machine_y, width=machine_width, height=machine_height)
                ))
            zones[zone_id] = ZoneRect(
                zone_id=zone_id,
                rect=MiniMapRect(x=zone_x, y=zone_y, width=zone_width, height=zone_height),
                machines=machines,
                severity_level=0
            )
        return FactoryRect(
            rect=MiniMapRect(
                x=0,
                y=0,
                width=scene_width,
                height=scene_height,               
            ),
            zones=zones
        )

    def _calc_rect_info(self, world_range) -> tuple:
        """
        return world_pos, width, height(depth)
        """
        min_pos = world_range.GetMin()
        max_pos = world_range.GetMax()
        width = max_pos[0] - min_pos[0]
        depth = max_pos[1] - min_pos[1]
        return (min_pos, width, depth)

    def _calc_relative_xy(self, child_min, child_height, parent_min, parent_height) -> tuple:
        """
        retun x, y
        """
        x = child_min[0] - parent_min[0]
        y = child_min[1] - parent_min[1]
        # revert y axis duto to direction in 2D is diff with 3D space
        y = parent_height - y - child_height
        return (x, y)

    def get_data(self):
        pass
    
    def update(self, machines: dict[str, MachineModel]):
        for zone_id, zone in self.factory_rect.zones.items():
            zone_temp_severity = 0
            for machine in zone.machines:
                machine_model = machines[machine.machine_id]
                severity_level = machine_model.current_severity_level
                machine.severity_level = severity_level
                zone_temp_severity = max(zone_temp_severity, severity_level)
            zone.severity_level = zone_temp_severity
