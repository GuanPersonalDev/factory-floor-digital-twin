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
        self.location = data["location"]

    def getRosTopic(self, param: str) -> str:
        from config.topic_resolver import getRos2Topic
        return getRos2Topic(self.machine_id, param)

    def getMqttTopic(self, param: str) -> str:
        from config.topic_resolver import getMqttTopic
        return getMqttTopic(self.machine_id, param)

    def __repr__(self):
        return f"Machine config (id={self.machine_id}, name={self.display_name})"

class FactoryConfig:
    """
    Manage machines.toml and thresholds.toml
    """
    _MACHINES_CONFIG = "machines.toml"
    _THRESHOLD_CONFIG = "thresholds.toml"
    
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

    def getMachineById(self, machine_id: str) -> Optional[MachineConfig]:
        for m in self._machines:
            if m.machine_id == machine_id:
                return m
        return None

    def computeSeverity(self, param: str, value: float) -> str:
        t = self._thresholds.get(param)
        if t is None:
            raise NameError(f"Not found param threshold in {self._THRESHOLD_CONFIG} with param name : {param}")
        if value >= t["error"]:
            return "ERROR"
        if value >= t["warning"]:
            return "WARNING"
        return "NORMAL"

    def getSeverityColor(self, severity: str) -> list[float]:
        colors = self._thresholds.get("severity_color", {})
        return colors.get(severity, [1.0, 1.0, 1.0])

    def resolveColor(self, operation_mode: str, severity: str) -> list[float]:
        op = self._thresholds.get("operation_mode", {})
        override = op.get("override_color", {})

        if operation_mode in override:
            return override[operation_mode]
        return self.getSeverityColor(severity)

    def getOpacity(self, operation_mode: str) -> float:
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
    def operation_mode(self) -> list[str]:
        return self._thresholds.get("operation_mode",{}).get("valid_values", {})
    
    def __repr__(self):
        return f"Factory config with {len(self._machines)} machines"


# Smoke test
if __name__ == "__main__":
    config = FactoryConfig()
    print(f"\n Loaded config : {config}\n")

    for m in config.machines:
        print(f"\t[{m.machine_id}] {m.display_name}")
        print(f"\tUSD: {m.usd_prim_path}")
        print(f"\tMQTT temperature: {m.getMqttTopic('temperature')}")

    print("\n--- Parameter list ---")
    for p in config.parameters:
        print(p)

    print("\n--- Thresholds test ---")
    test_cases = [
        ("temperature", 60.0),
        ("temperature", 72.5),
        ("temperature", 87.0),
        ("vibration", 3.0),
        ("vibration", 6.0),
    ]

    for param, value in test_cases:
        severity = config.computeSeverity(param, value)
        color = config.getSeverityColor(severity)
        print(f"\t{param} = {value:5.1f} -> {severity:7s} color={color}")

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
        color = config.resolveColor(mode, severity)
        opacity = config.getOpacity(mode)
        print(f"\tmode={mode:8s} severity={severity:7s} -> color={color} opacity={opacity}")