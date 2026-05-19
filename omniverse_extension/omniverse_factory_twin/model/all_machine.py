# sys and config
from config.config_loader import FactoryConfig

# factory project
from ..factory_log import FactoryLog
from .machine_model import MachineModel
from .factory_overview_model import FactoryOverviewModel
from ..view.factory_overview import OverviewInfo

"""
Manage all machine model
update and setting dirty flag to machine if it changed,
provide some method that could return all machine or machines with specific flag
"""
class AllMachine:
    def __init__(self, config: FactoryConfig):
        self._factory_overview_model = FactoryOverviewModel()
        self._machine_model_dic: dict[str, MachineModel] = {}
        for machine in config.machines:
            self._machine_model_dic[machine.machine_id] = MachineModel(machine.machine_id, config)

    def update(self, log: FactoryLog):
        for machine_model in self._machine_model_dic.values():
            machine_model.update(log)
        self._factory_overview_model.update(self._machine_model_dic.values())

    def get_overview_info(self) -> OverviewInfo:
        return self._factory_overview_model

    def get_dirty_machines(self, flag: str) -> list[MachineModel]:
        result = []
        for machine_model in self._machine_model_dic.values():
            if machine_model.is_dirty(flag):
                result.append(machine_model)
        return result

    def clear_last_check_flags(self):
        for machine_model in self._machine_model_dic.values():
            machine_model.reset_dirty_mark()