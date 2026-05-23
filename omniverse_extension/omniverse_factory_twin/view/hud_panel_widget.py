# sys and config
import sys
from pathlib import Path 
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent)) # add root to Python search path due to I wanna load config.config_loader
from config.config_loader import FactoryConfig

import time

# omniverse lib
import omni.ui as ui

# factory project
from ..factory_log import FactoryLog
from .factory_overview import FactoryOverview, OverviewData
from .machine_info_list import MachineInfoList, MachineInfoListData
from .alert_machines_view import AlertMachinesView

class HudPanelWidget:
    def __init__(self, config: FactoryConfig):
        self._window = None
        self._config = config
        self._factory_overview = None
        self._machine_info_list = None
        self._alert_machines_view = None
        self.build_ui()
       

    def build_ui(self):
        self._window = ui.Window(
            "Factory Monitor",
            width = 480,
            height = 800,
        )

        with self._window.frame:
            self._root_stack = ui.VStack(spacing=6)
            self._factory_overview = FactoryOverview()
            self._alert_machines_view = AlertMachinesView(self._config)
            self._machine_info_list = MachineInfoList()
            self.render_all()

    def bind_overview_data(self, overview_info: OverviewData):
        self._factory_overview.bind_view_data(overview_info)
    
    def bind_machine_info_list_data(self, list_data: MachineInfoListData):
        self._machine_info_list.bind_list_data(list_data)
 
            
    def render_all(self):
        self._root_stack.clear()
        with self._root_stack:
            self._factory_overview.redraw()
            self._alert_machines_view.redraw()
            self._machine_info_list.redraw()

    def destroy(self):
        if self._window:
            self._window.frame.clear()
            self._window.destroy()
            self._factory_overview = None
            self._alert_machines_view = None
            self._machine_info_list = None
            self._root_stack = None
            self._window = None