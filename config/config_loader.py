"""
Read machines.toml and thresholds.toml
provide the interface for extension
"""

import sys
from pathlib import Path
from typing import Optional

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        raise ImportError("Python version less than 3.10, try to execute pip install tomli")

_DEFAULT_CONFIG_DIR = Path(__file__).parent

class MachineConfig:
    """ One machine setting """

    def __init__(self, data: dict):
        self.machine_id = data["machine_id"]
        self.display_name = data["display_name"]
        self.usd_prim_path = data["usd_prim_path"]

    def get_ros_topic(self, param: str) -> str:
        from config.topic_resolver import get_ros2_topic
        return get_ros2_topic(self.machine_id, param)

    def get_mqtt_topic(self, param: str) -> str:
        from config.topic_resolver import get_mqtt_topic
        return get_mqtt_topic(self.machine_id, param)

    def __repr__(self):
        return f"Machine config (id={self.machine_id}, name={self.display_name})"

class FactoryConfig:
    """
    Manage machines.toml and thresholds.toml
    """
    _MACHINES_CONFIG = "machines.toml"
    _THRESHOLD_CONFIG = "thresholds.toml"

    ERROR_STATE_KEY = "ERROR"
    WARNING_STATE_KEY = "WARNING"
    NORMAL_STATE_KEY = "NORMAL"

    IDLE_MODE_KEY = "IDLE"
    RUNNING_MODE_KEY = "RUNNING"
    SHUTDOWN_MODE_KEY = "SHUTDOWN"
    OFFLINE_MODE_KEY = "OFFLINE"

    OPERATION_PARAM_KEY = "operation_mode"
    TEMPERATURE_PARAM_KEY = "temperature"
    VIBRATION_PARAM_KEY = "vibration"

    ENABLE_LOG = True

    
    def __init__(self, config_dir: Optional[str] = None):
        self._configDir = Path(config_dir) if config_dir else _DEFAULT_CONFIG_DIR
        self._machines = []
        self._thresholds = {}
        self.load()
        
    def load(self):
        machines_path = self._configDir / self._MACHINES_CONFIG
        thresholds_path = self._configDir / self._THRESHOLD_CONFIG
        if not machines_path.exists():
            raise FileNotFoundError(f"Not found machine config with path : {machines_path}")
        if not thresholds_path.exists():
            raise FileNotFoundError(f"Not found threshold config with path : {thresholds_path}")
        
        with open(machines_path, "rb") as f:
            raw_machines = tomllib.load(f)
        
        with open(thresholds_path, "rb") as f:
            self._thresholds = tomllib.load(f)
        
        self._machines = [
            MachineConfig(m) for m in raw_machines.get("machines", [])
        ]
        self._param_list = self._thresholds.get("parameter_def",{}).get("parameter_list",{})

    def get_machine_by_id(self, machine_id: str) -> Optional[MachineConfig]:
        for m in self._machines:
            if m.machine_id == machine_id:
                return m
        return None

    def compute_severity(self, param: str, value: float) -> tuple[str, int]:
        t = self._thresholds.get(param)
        if t is None:
            raise NameError(f"Not found param threshold in {self._THRESHOLD_CONFIG} with param name : {param}")
        if value >= t["error"]:
            return self.ERROR_STATE_KEY, 2
        if value >= t["warning"]:
            return self.WARNING_STATE_KEY, 1
        return self.NORMAL_STATE_KEY, 0
    
    def get_threshold_value(self, param: str, severity: str) -> float:
        t = self._thresholds.get(param)
        match severity:
            case self.ERROR_STATE_KEY:
                return t["error"]
            case self.WARNING_STATE_KEY:
                return t["warning"]
        return 0

    def get_trend_target(self, param: str) -> float:
        t = self._thresholds.get(param)
        return t["trend_target"]

    def get_trend_tau(self, param: str) -> float:
        t = self._thresholds.get(param)
        return t["trend_tau"]
        

    def get_severity_color(self, severity: str) -> tuple[float, float, float]:
        colors = self._thresholds.get("severity_color", {})
        color = colors.get(severity, [1.0, 1.0, 1.0])
        return tuple(color)

    def resolve_color(self, operation_mode: str, severity: str) -> tuple[float, float, float, float]:
        opacity = self.get_opacity(operation_mode)

        op = self._thresholds.get("operation_mode", {})
        override = op.get("override_color", {})

        if operation_mode in override:
            override_color = override[operation_mode]
            return (*override_color, opacity)
        severity_color = self.get_severity_color(severity)
        return (*severity_color, opacity)

    def get_opacity(self, operation_mode: str) -> float:
        op = self._thresholds.get("operation_mode", {})
        opacity_map = op.get("opacity", {})
        return opacity_map.get(operation_mode, 1.0)

    @property
    def machines(self) -> list[MachineConfig]:
        return self._machines
    
    @property
    def parameters(self) -> list[str]:
        return self._param_list

    @property
    def parameter_and_unit(self) -> list[tuple[str, str]]:
        result = []
        for param in self._param_list:
            t = self._thresholds.get(param)
            unit = t.get("unit", "")
            result.append((param, unit))
        return result

    @property
    def operation_mode(self) -> list[str]:
        return self._thresholds.get("operation_mode",{}).get("valid_values", {})

    @property
    def severity_keys(self) -> list[str]:
        return [self.NORMAL_STATE_KEY, self.WARNING_STATE_KEY, self.ERROR_STATE_KEY]
    
    def __repr__(self):
        return f"Factory config with {len(self._machines)} machines"


# Smoke test
if __name__ == "__main__":
    config = FactoryConfig()
    print(f"\n Loaded config : {config}\n")

    for m in config.machines:
        print(f"\t[{m.machine_id}] {m.display_name}")
        print(f"\tUSD: {m.usd_prim_path}")
        print(f"\tMQTT temperature: {m.get_mqtt_topic('temperature')}")

    print("\n--- All severity list ---")
    for s in config.severity_keys:
        print(s)

    print("\n--- Parameter and unit list ---")
    for (p, unit) in config.parameter_and_unit:
        print(f"{p}, unit: {unit}")

    print("\n--- Thresholds test ---")
    test_cases = [
        ("temperature", 60.0),
        ("temperature", 72.5),
        ("temperature", 87.0),
        ("vibration", 3.0),
        ("vibration", 6.0),
    ]

    for param, value in test_cases:
        severity, severity_level = config.compute_severity(param, value)
        color = config.get_severity_color(severity)
        color_str = "({:.1f}, {:.1f}, {:.1f})".format(*color)
        print(f"\t{param} = {value:5.1f} -> {severity:7s} color={color_str}")

    print("\n--- Display color test ---")
    resolve_cases = [
        ("RUNNING", "ERROR"),
        ("RUNNING", "WARNING"),
        ("RUNNING", "NORMAL"),
        ("IDLE", "NORMAL"),
        ("SHUTDOWN", "NORMAL"),
        ("OFFLINE", "ERROR"),
    ]
    for mode, severity in resolve_cases:
        color = config.resolve_color(mode, severity)
        print(f"\tmode={mode:8s} severity={severity:7s} -> color={color}")