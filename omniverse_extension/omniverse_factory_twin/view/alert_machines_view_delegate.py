from datetime import datetime

from config.config_loader import FactoryConfig
# factory
from ..factory_log import FactoryLog
from ..model.machine_model import MachineModel
from .alert_machines_view import UnitAlertMachine, AlertMachinesData

class AlertMachinesViewDelegate(AlertMachinesData):
    def __init__(self):
        super().__init__()
        self._alert_machines: list[UnitAlertMachine] = []

    def get_data(self) -> list[UnitAlertMachine]:
        return self._alert_machines

    def update(self, machines: list[MachineModel], log: FactoryLog):
        self._alert_machines.clear()
        for machine in machines:
            if machine.current_severity == FactoryConfig.NORMAL_STATE_KEY:
                continue
            alert_machine = UnitAlertMachine(
                machine_id=machine.machine_id,
                severity=machine.current_severity,
                alert_param_info={},
                alert_param_plot={}
            )
            self._alert_machines.append(alert_machine)
            for (param_str, param_info) in machine.current_param_dic.items():
                (value, unit, severity) = param_info
                if severity == FactoryConfig.NORMAL_STATE_KEY:
                    continue

                start_time = machine.param_severity_start_time_stamp[param_str]
                alert_elapsed_time = (datetime.now() -  start_time).total_seconds()
                alert_machine.alert_param_info[param_str] = (alert_elapsed_time, value, severity, unit)

                # param_name, (relative_second, value)
                history = log.get_machine_topic_history(machine.machine_id, param_str, self.plot_half_data_count)
                now = datetime.now()
                plot_data: list[tuple[int, float]] = []
                for (ts, data) in history:
                    if param_str in data:
                        second = (ts - now).total_seconds()
                        plot_data.append((int(second), data[param_str]))
                alert_machine.alert_param_plot[param_str] = plot_data

