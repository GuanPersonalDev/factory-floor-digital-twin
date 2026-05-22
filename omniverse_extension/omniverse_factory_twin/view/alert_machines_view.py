# system
from dataclasses import dataclass

# omniverse lib
import omni.ui as ui

# Factory
from .style_sheet import FactoryStyleSheet as FactoryStyle



class AlertMachinesView:
    def __init__(self):
        pass

    def redraw(self):
        FactoryStyle.draw_section_title("Alarms:")
        pass