# sys and config
import sys
from pathlib import Path 
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent)) # add root to Python search path due to I wanna load config.config_loader
from config.config_loader import FactoryConfig

import time

# omniverse lib
import omni.ui as ui

# factory project
from omniverse_extension.omniverse_factory_twin.factory_log import FactoryLog

class HudPanelWidget:
    def __init__(self):
        self._window = None
        self.build_ui()
        

    def build_ui(self):
        self._window = ui.Window(
            "Factory Monitor",
            width = 380,
            height = 800,
        )
        with self._window.frame:
            self._root_stack = ui.VStack(spacing=6)
            self._render_all()
            
    def _render_all(self):
        self._root_stack.clear()