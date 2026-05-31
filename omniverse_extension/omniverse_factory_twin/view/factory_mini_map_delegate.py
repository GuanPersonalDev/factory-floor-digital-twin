from pxr import Gf

from ..model.factory_map import CanvasLayoutInfo
from .factory_mini_map_view import FactoryRect, ZoneRect, MachineRect, MiniMapRect, FactoryMiniMapData

class FactoryMiniMapDelegate(FactoryMiniMapData):
    _PADDING = 12
    def __init__(self, layout_info: CanvasLayoutInfo):
        self.factory_rect = self._compute_factory_rect(layout_info)

    def _compute_factory_rect(self, layout_info: CanvasLayoutInfo) -> FactoryRect:
        (scene_pos, scene_width, scene_height) = self._calc_rect_info(layout_info.world_range)

        zones = {}
        for zone_id, zone_info in layout_info.zones.items():
            (zone_pos, zone_width, zone_height) = self._calc_rect_info(zone_info.world_range)
            (zone_x, zone_y) = self._calc_relative_xy(zone_pos, scene_pos)

            machines = []
            for machine_info in zone_info.machines:
                (machine_pos, machine_width, machine_height) = self._calc_rect_info(machine_info.world_range)
                (machine_x, machine_y) = self._calc_relative_xy(machine_pos, scene_pos)
                machines.append(MachineRect(
                    machine_id = machine_info.machine_id,
                    rect=MiniMapRect(x=machine_x, y=machine_y, width=machine_width, height=machine_height)
                ))
            zones[zone_id] = ZoneRect(
                zone_id=zone_id,
                rect=MiniMapRect(x=zone_x, y=zone_y, width=zone_width, height=zone_height),
                machines=machines
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
        min = world_range.GetMin()
        max = world_range.GetMax()
        width = max[0] - min[0]
        depth = max[2] - min[2]
        return (min, width, depth)

    def _calc_relative_xy(self, child_min, parent_min) -> tuple:
        """
        retun x, y
        """
        x = child_min[0] - parent_min[0]
        y = child_min[2] - parent_min[2]
        return (x, y)

    def get_data(self):
        pass
    
    def update(self, alert_machines: dict[str, str]):
        pass
