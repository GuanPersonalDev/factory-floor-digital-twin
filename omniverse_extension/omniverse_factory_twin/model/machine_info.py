from omniverse_extension.omniverse_factory_twin.factory_log import FactoryLog
from config.config_loader import FactoryConfig

class MachineInfo():
    def __init__(self, machine_id):
        self.machine_id = machine_id
        self.current_color: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)

    def calc_color(self, config :FactoryConfig, log :FactoryLog) -> tuple[float, float, float, float]:
        operation_mode = log.get_latest_mode(self.machine_id)
        if operation_mode == None:
            operation_mode = config.OFFLINE_MODE_KEY
        servity = "NORMAL"
        servity_level = 0
        for p in config.parameters:
            if p == config.OPERATION_PARAM_KEY:
                continue
            topic = log.get_machine_lastest_topic(self.machine_id, p)
            if topic == None:
                continue
            value = topic[p]
            tmp_servity, tmp_servity_level = config.compute_severity(p, value)
            if tmp_servity_level > servity_level:
                servity_level = tmp_servity_level
                servity = tmp_servity
            
        color = config.resolve_color(operation_mode, servity)
        # print(f"[Factory Twin] {self.machine_id} operation mode: {operation_mode}, color: {color}")
        return color

    def record_color(self, color: tuple[float, float, float, float]):
        self.current_color = color

    def is_same_color(self, color: tuple[float, float, float, float]) -> bool:
        return self.current_color == color

