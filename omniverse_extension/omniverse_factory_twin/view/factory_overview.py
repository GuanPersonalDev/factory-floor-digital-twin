# system
from dataclasses import dataclass, field

# omniverse lib
import omni.ui as ui

@dataclass
class OverviewUnitInfo:
    label: str
    context: str
    is_alarm: bool

class OverviewInfo:
    def get_data(self) -> list[OverviewUnitInfo]:
        result = []
        result.append(OverviewUnitInfo(label="Floor", context="1F", is_alarm=False))
        result.append(OverviewUnitInfo(label="Machine count", context="3", is_alarm=False))
        result.append(OverviewUnitInfo(label="Warning/Error Count", context="1", is_alarm=True))
        result.append(OverviewUnitInfo(label="Redraw time", context="08:00", is_alarm=False))
        return result

class FactoryOverview:
    def __init__(self):
        self._view_data = OverviewInfo()

    def bind_view_data(self, data: OverviewInfo):
        self._view_data = data

    def redraw(self):
        print(f"[Factory Twin] Redraw factory overview")
        with ui.HStack(height=48, spacing=0):
            for unit_data in self._view_data.get_data():
                with ui.VStack(width=ui.Fraction(1), spacing=2):
                    ui.Label(unit_data.label, height=14, style={"color": 0xFF888888, "font_size": 11})
                    color = 0xFFBA7517 if unit_data.is_alarm else 0xFFFFFFFF
                    ui.Label(unit_data.context, height=22, style={"color": color, "font_size": 14, "font_weight":"bold"})