from dataclasses import dataclass, field

@dataclass
class MiniMapRect:
    x: float
    y: float
    width: float
    height: float   

@dataclass
class MachineRect:
    machine_id: str
    rect: MiniMapRect

@dataclass
class ZoneRect:
    zone_id: str
    rect: MiniMapRect
    machines: list[MachineRect] = field(default_factory=list)

@dataclass
class FactoryRect:
    width: float
    height: float
    zones: dict[str, ZoneRect] = field(default_factory=dict)