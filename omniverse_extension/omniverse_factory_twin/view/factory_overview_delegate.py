import time

from config.config_loader import FactoryConfig

# omniverse lib
import omni.kit.app

# factory
from ..model.machine_model import MachineModel
from .factory_overview import OverviewData, OverviewUnitInfo

class FactoryOverviewDelegate(OverviewData):
    def __init__(self):
        self._machine_count: int = 0
        self._warning_count: int = 0
        self._error_count: int = 0

    def update(self, machines: list[MachineModel]):
        self._machine_count = len(machines)
        self._warning_count = 0
        self._error_count = 0
        for machine_model in machines:
            match machine_model.current_severity:
                case FactoryConfig.WARNING_STATE_KEY:
                    self._warning_count += 1
                case FactoryConfig.ERROR_STATE_KEY:
                    self._error_count += 1

    def get_data(self) -> list[OverviewUnitInfo]:
        result = []
        result.append(OverviewUnitInfo(label="Floor", context="1F", alarm_level=FactoryConfig.NORMAL_STATE_KEY))
        result.append(OverviewUnitInfo(label="Machine count", context=str(self._machine_count), alarm_level=FactoryConfig.NORMAL_STATE_KEY))
        warrning_error_total = self._warning_count + self._error_count
        warrning_error_level = FactoryConfig.ERROR_STATE_KEY if self._error_count > 0 else FactoryConfig.WARNING_STATE_KEY if self._warning_count > 0 else FactoryConfig.NORMAL_STATE_KEY
        result.append(OverviewUnitInfo(label="Warning/Error Count", context=str(warrning_error_total), alarm_level=warrning_error_level))
        result.append(OverviewUnitInfo(label="Redraw time", context=time.strftime("%H:%M:%S"), alarm_level=FactoryConfig.NORMAL_STATE_KEY))

        return result