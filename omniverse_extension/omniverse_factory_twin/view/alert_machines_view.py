# system
from dataclasses import dataclass
from datetime import time
from config.config_loader import FactoryConfig

# omniverse lib
import omni.ui as ui

# Factory
from .style_sheet import FactoryStyleSheet as FactoryStyle

@dataclass
class UnitAlertMachine:
    machine_id: str
    # param_name, (relative_second, value, severity)
    param_info: dict[str, tuple[float, float, str]]

class AlertMachinesData:
    def get_data(self) -> list[UnitAlertMachine]:
        result = []
        result.append(UnitAlertMachine(
            machine_id="machine_002",
            param_info=[{
                FactoryConfig.TEMPERATURE_PARAM_KEY: (0, 100, FactoryConfig.ERROR_STATE_KEY),
                FactoryConfig.VIBRATION_PARAM_KEY: (0, 9, FactoryConfig.WARNING_STATE_KEY)
            }],
        ))
        result.append(UnitAlertMachine(
            machine_id="machine_001",
            param_info=[{
                FactoryConfig.TEMPERATURE_PARAM_KEY: (0, 25, FactoryConfig.NORMAL_STATE_KEY),
                FactoryConfig.VIBRATION_PARAM_KEY: (0, 8, FactoryConfig.WARNING_STATE_KEY)
            }],
        ))
        return result

class AlertMachinesView:
    def __init__(self):
        self._data = AlertMachinesData()

    def binding_alert_machins_data(self, data: AlertMachinesData):
        self._data = data

    def redraw(self):
        FactoryStyle.draw_section_title("Alarms:")
        ui.Spacer(height=4)
        for unit_alert_machine in self._data.get_data():
            self._alert_machine_view(unit_alert_machine)

    def _alert_machine_view(self, unit_alert: UnitAlertMachine):
        pass