# sys and config
from config.config_loader import FactoryConfig

# factory project
from ..factory_log import FactoryLog
from .machine_model import MachineModel
from ..view.factory_overview_delegate import FactoryOverviewDelegate
from ..view.factory_overview import OverviewData
from ..view.machine_info_list_delegate import MachineInfoListDelegate
from ..view.alert_machines_view_delegate import AlertMachinesViewDelegate

from .factory_map import compute_layout
from ..view.factory_mini_map_delegate import FactoryMiniMapDelegate
from ..view.factory_mini_map_view import FactoryMiniMapData

"""
Manage all machine model
update and setting dirty flag to machine if it changed,
provide some method that could return all machine or machines with specific flag
"""
class AllMachine:
    def __init__(self, config: FactoryConfig):
        self._factory_overview_delegate = FactoryOverviewDelegate()
        self._machine_info_list_delegate = MachineInfoListDelegate()
        self._alert_machines_view_delegate = AlertMachinesViewDelegate(config)
        self._machine_model_dic: dict[str, MachineModel] = {}
        for machine in config.machines:
            self._machine_model_dic[machine.machine_id] = MachineModel(machine.machine_id, config)

        self._mini_map_delegate = None

    def build_stage_elements(self, stage, config: FactoryConfig):
        layout_info = compute_layout(stage, config.zone_prim_map)
        self._mini_map_delegate = FactoryMiniMapDelegate(layout_info)

    def update(self, log: FactoryLog):
        for machine_model in self._machine_model_dic.values():
            machine_model.update(log)
        machines = self._machine_model_dic.values()
        self._factory_overview_delegate.update(machines)
        self._machine_info_list_delegate.update(machines)
        self._alert_machines_view_delegate.update(machines, log)
        if self._mini_map_delegate:
            self._mini_map_delegate.update(self._machine_model_dic)

    def get_overview_delegate(self) -> OverviewData:
        return self._factory_overview_delegate

    def get_machine_info_list_delegate(self) -> MachineInfoListDelegate:
        return self._machine_info_list_delegate

    def get_alert_machines_view_delegate(self) -> AlertMachinesViewDelegate:
        return self._alert_machines_view_delegate

    def get_mini_map_delegate(self) -> FactoryMiniMapData:
        return self._mini_map_delegate

    def get_all_machines(self) -> list[MachineModel]:
        return list(self._machine_model_dic.values())

    def get_dirty_machines(self, flag: str) -> list[MachineModel]:
        result = []
        for machine_model in self._machine_model_dic.values():
            if machine_model.is_dirty(flag):
                result.append(machine_model)
        return result

    def clear_last_check_flags(self):
        for machine_model in self._machine_model_dic.values():
            machine_model.reset_dirty_mark()