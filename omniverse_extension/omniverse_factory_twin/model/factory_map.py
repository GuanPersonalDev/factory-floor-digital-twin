from pxr import Usd, UsdGeom, Gf
from dataclasses import dataclass, field

@dataclass
class MachineLayoutInfo:
    machine_id: str
    world_range: Gf.Range3d

@dataclass
class ZoneLayoutInfo:
    zone_id: str
    world_range: Gf.Range3d
    machines: list[MachineLayoutInfo] = field(default_factory=list)

@dataclass
class CanvasLayoutInfo:
    world_range: Gf.Range3d
    zones: dict[str, ZoneLayoutInfo] = field(default_factory=dict)
    

def compute_layout(stage, zone_prim_map: dict[str, list[tuple[str, str]]]) -> CanvasLayoutInfo:
    """
    return factory layout data struct
    """
    bbox_cache = UsdGeom.BBoxCache(time=Usd.TimeCode.Default(),includedPurposes=[UsdGeom.Tokens.default_])
    canvas_range = None
    zones = {}

    for zone_id, machine_entries in zone_prim_map.items():
        zone_range = None
        machines = []
        for machine_id, prim_path in machine_entries:
            prim = stage.GetPrimAtPath(prim_path)
            if not prim.IsValid():
                continue
            machine_range = bbox_cache.ComputeWorldBound(prim).ComputeAlignedBox()
            machines.append(MachineLayoutInfo(
                machine_id= machine_id,
                world_range=machine_range
            ))
        zone_range = machine_range if zone_range is None else Gf.Range3d.GetUnion(zone_range, machine_range)

        if zone_range is None:
            continue
        zones[zone_id] = ZoneLayoutInfo(
            zone_id=zone_id,
            world_range=zone_range,
            machines=machines
        )
        canvas_range = zone_range if canvas_range is None else Gf.Range3d.GetUnion(canvas_range, zone_range)

    return CanvasLayoutInfo(world_range=canvas_range, zones=zones)