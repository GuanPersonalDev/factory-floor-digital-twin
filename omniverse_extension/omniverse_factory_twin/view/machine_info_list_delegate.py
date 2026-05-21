# factory
from ..model.machine_model import MachineModel
from .machine_info_list import MachineInfoListData, UnitRowInfo

class MachineInfoListDelegate(MachineInfoListData):
    def __init__(self):
        self._row_info_list = []

    def update(self, machines: list[MachineModel]):
        self._row_info_list.clear()
        for machine in machines:
            param = []
            for (param_str, param_info) in machine.current_param_dic.items():
                (value, unit, severity) = param_info
                param.append((param_str, value, unit, severity))
            row_info = UnitRowInfo(
                severity=machine.current_servity,
                operation_mode=machine.current_operation_mode,
                machine_id=machine.machine_id,
                param_data=param
            )
            self._row_info_list.append(row_info)
        pass

    def get_row_info_list(self) -> list[UnitRowInfo]:
        return self._row_info_list
