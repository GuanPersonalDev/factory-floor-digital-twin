# sys and config
import sys
from pathlib import Path 
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent)) # add root to Python search path due to I wanna load config.config_loader
from config.config_loader import FactoryConfig

import time

# omniverse lib
import omni.ui as ui
from omni.kit.viewport.utility import get_active_viewport_window

# factory project
from .style_sheet import FactoryStyleSheet as FactoryStyle
from ..factory_log import FactoryLog
from .factory_overview import FactoryOverview, OverviewData
from .machine_info_list import MachineInfoList, MachineInfoListData
from .alert_machines_view import AlertMachinesView, AlertMachinesData

class HudPanelWidget:
    def __init__(self, config: FactoryConfig):
        self._window = None
        self._frame = None
        self._config = config
        self._factory_overview = None
        self._machine_info_list = None
        self._alert_machines_view = None
        self.build_on_viewport_window()

    def build_on_viewport_window(self):
        viewport_window = get_active_viewport_window()
        if not viewport_window:
            print(f"build on view port fail")
            return
        self._frame = viewport_window.get_frame("factory_monitor_hud")

        self._factory_overview = FactoryOverview()
        self._alert_machines_view = AlertMachinesView(self._config)
        self._machine_info_list = MachineInfoList()

        with self._frame:
            with ui.ZStack():
                with ui.HStack():
                    ui.Spacer()
                    with ui.VStack(width=480):
                        ui.Spacer(height=150)
                        with ui.ZStack():
                            # ui.Rectangle(style=FactoryStyle.mini_map_bg)
                            with ui.ScrollingFrame(
                                horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                                vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                                style=FactoryStyle.viewport_window_hud_scroll_frame,
                            ):
                                with ui.VStack():
                                    self._factory_overview.build()
                                    self._alert_machines_view.build()
                                    self._machine_info_list.build()
                                    ui.Spacer(height=10)


    def build_ui(self):
        self._window = ui.Window(
            "Factory Monitor",
            width = 480,
            height = 800,
        )
        self._frame = self._window.frame
        self._factory_overview = FactoryOverview()
        self._alert_machines_view = AlertMachinesView(self._config)
        self._machine_info_list = MachineInfoList()

        with self._frame:
            with ui.VStack(spacing=6):
                self._factory_overview.build()
                self._alert_machines_view.build()
                self._machine_info_list.build()
                ui.Spacer(height=10)

    

    def bind_overview_data(self, overview_info: OverviewData):
        self._factory_overview.bind_view_data(overview_info)
    
    def bind_machine_info_list_data(self, list_data: MachineInfoListData):
        self._machine_info_list.bind_list_data(list_data)

    def bind_alert_machines_view_data(self, alert_machines_view_data: AlertMachinesData):
        self._alert_machines_view.binding_alert_machins_data(alert_machines_view_data)
 
            
    def render_all(self):
        self._factory_overview.redraw()
        self._alert_machines_view.redraw()
        self._machine_info_list.redraw()

    def destroy(self):
        if self._frame:
            self._frame.clear()
            self._factory_overview = None
            self._alert_machines_view = None
            self._machine_info_list = None
            self._frame = None

        if self._window:
            self._window.destroy()
            self._window = None