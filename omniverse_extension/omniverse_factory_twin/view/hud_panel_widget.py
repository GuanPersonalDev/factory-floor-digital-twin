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
from .factory_overview import FactoryOverview

class HudPanelWidget:
    def __init__(self):
        self._window = None
        self._factory_overview = None
        print(f"[Factory Twin] panel widge init")
        self.build_ui()
        

    def build_ui(self):
        self._window = ui.Window(
            "Factory Monitor",
            width = 480,
            height = 800,
        )

        print(f"[Factory Twin] before with window frame")
        with self._window.frame:
            self._root_stack = ui.VStack(spacing=6)
            self._factory_overview = FactoryOverview()
            print(f"[Factory Twin] with window frame")
            self._render_all()
            
    def _render_all(self):
        self._root_stack.clear()
        self._factory_overview.redraw()

    def destroy(self):
        if self._window:
            self._window.frame.clear()
            self._window.destroy()
            self._factory_overview = None
            self._root_stack = None
            self._window = None