from datetime import datetime

from omniverse_extension.omniverse_factory_twin.factory_log import FactoryLog
from config.config_loader import FactoryConfig

class MachineModel():
    DIRTY_FLAG_COLOR = "Color"
    def __init__(self, machine_id: str, config :FactoryConfig):
        self._config = config
        self._dirty_flag: list[str] = []
        self.machine_id = machine_id
        self.current_operation_mode: str = config.OFFLINE_MODE_KEY
        self.current_severity = self._config.NORMAL_STATE_KEY
        self.current_color: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
        self.current_param_dic: dict[str, tuple[float, str, str]] = {}
        self.param_severity_start_time_stamp: dict[str, datetime] = {
            FactoryConfig.TEMPERATURE_PARAM_KEY: datetime.now(),
            FactoryConfig.VIBRATION_PARAM_KEY: datetime.now()
        }

    def update(self, log :FactoryLog):
        self.calc_operation_mode(log)
        self.calc_severity(log)
        self.calc_color()

    def calc_operation_mode(self, log :FactoryLog):
        operation_mode = log.get_latest_mode(self.machine_id)
        if operation_mode == None:
            operation_mode = self._config.OFFLINE_MODE_KEY       
        self.current_operation_mode = operation_mode

    def calc_severity(self, log: FactoryLog):
        servity = self._config.NORMAL_STATE_KEY
        servity_level = 0
        for (p, unit) in self._config.parameter_and_unit:
            if p == self._config.OPERATION_PARAM_KEY:
                continue
            topic = log.get_machine_lastest_topic(self.machine_id, p)
            if topic == None:
                continue
            value = topic[p]
            tmp_servity, tmp_servity_level = self._config.compute_severity(p, value)
            if p in self.current_param_dic:
                ori_param_severity = self.current_param_dic[p][2]
                if tmp_servity != ori_param_severity:
                    self.param_severity_start_time_stamp[p] = datetime.now()

            self.current_param_dic[p] = (value, unit, tmp_servity)
            if tmp_servity_level > servity_level:
                servity_level = tmp_servity_level
                servity = tmp_servity
        self.current_severity = servity

    def calc_color(self):
        color = self._config.resolve_color(self.current_operation_mode, self.current_severity)
        if color != self.current_color:
            self._mark_dirty(self.DIRTY_FLAG_COLOR)
            self.current_color = color

    def _mark_dirty(self, flag: str):
        self._dirty_flag.append(flag)

    def reset_dirty_mark(self):
        self._dirty_flag.clear()

    def is_dirty(self, flag: str) -> bool:
        return flag in self._dirty_flag