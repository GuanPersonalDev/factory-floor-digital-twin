# system
from dataclasses import dataclass, field

# omniverse lib
import omni.ui as ui

# Factory
from .style_sheet import FactoryStyleSheet as FactoryStyle

@dataclass
class OverviewUnitInfo:
    label: str
    context: str
    alarm_level: str 

class OverviewData:
    def get_data(self) -> list[OverviewUnitInfo]:
        result = []
        result.append(OverviewUnitInfo(label="Floor", context="???", alarm_level="NORMAL"))
        result.append(OverviewUnitInfo(label="Machine count", context="???", alarm_level="NORMAL"))
        result.append(OverviewUnitInfo(label="Warning/Error Count", context="???", alarm_level="NORMAL"))
        result.append(OverviewUnitInfo(label="Redraw time", context="??:??", alarm_level="NORMAL"))
        return result

class FactoryOverview:
    def __init__(self):
        self._view_data = OverviewData()
        self._root_stack = None
    
    def build(self):
        self._root_stack = ui.VStack()

    def bind_view_data(self, data: OverviewData):
        self._view_data = data

    def redraw(self):
        # TODO: only redraw label
        self._root_stack.clear()
        with self._root_stack:
            with ui.ZStack(height=60):
                ui.Rectangle(style=FactoryStyle.overview_bar_bg)

                with ui.HStack():
                    ui.Spacer(width=8)
                    counter = 0
                    for unit_data in self._view_data.get_data():
                        if counter > 0:
                            with ui.ZStack(width=1):
                                ui.Rectangle(style=FactoryStyle.overview_bar_divider)
                        with ui.VStack(spacing=3):
                            ui.Spacer()
                            ui.Label(unit_data.label, height=18, style=FactoryStyle.overview_bar_label, alignment=ui.Alignment.CENTER)
                            context_style = (
                                FactoryStyle.overview_context_error if unit_data.alarm_level == "ERROR" else
                                FactoryStyle.overview_context_warning if unit_data.alarm_level == "WARNING" else
                                FactoryStyle.overview_context_normal
                            )
                            ui.Label(unit_data.context, height=22, style=context_style, alignment=ui.Alignment.CENTER)
                            ui.Spacer()
                        counter += 1
                ui.Spacer(width=8)