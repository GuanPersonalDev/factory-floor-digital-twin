import sys
from pathlib import Path 
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent)) # add root to Python search path due to I wanna load config.config_loader
from config.config_loader import FactoryConfig

from collections import deque
import time
class MachineLog:
    MAX_COUNT = 50

    def __init__(self, machine_id: str):
        self._machine_id = machine_id
        self._logs: deque[tuple[float, dict]] = deque(maxlen=self.MAX_COUNT)

    def append(self, data: dict):
        self._logs.append((time.time(), data))

    def get_latest_by_topic(self, topic: str) -> dict | None:
        for timestamp, data in reversed(self._logs):
            if topic in data:
                return data
        return None
        
class FactoryLog:
    def __init__(self):
        self._config = FactoryConfig()
        self._machines: dict[str, MachineLog] = {}
        
    def record(self, machine_id: str, data: dict):
        if machine_id not in self._machines:
            self._machines[machine_id] = MachineLog(machine_id)
        self._machines[machine_id].append(data)

    def get_latest_mode(self, machine_id: str) -> str | None:
        log = self._machines.get(machine_id)
        if log is None:
            return None
        result = log.get_latest_by_topic(self._config.OPERATION_PARAM_KEY)
        if result is None:
            return None
        return result.get(self._config.OPERATION_PARAM_KEY)

    def get_machine_lastest_topic(self, machine_id: str, topic: str) -> dict | None:
        if machine_id not in self._machines:
            return None
        log = self._machines.get(machine_id)
        return log.get_latest_by_topic(topic)
        
        
"""
Test code
"""

def test_machine_log():
    print("=== Machine log smoke test ===")
    log = MachineLog("machine_01")
    assert log.get_latest_by_topic("operation_mode") is None
    print("Not found log search pass")

    log.append({"operation_mode": "RUNNING"})
    log.append({"temperature": 72.3})
    log.append({"vibration": 1.2})
    log.append({"operation_mode": "RUNNING"})
    log.append({"temperature": 69.5})
    log.append({"vibration": 1.0})
    log.append({"operation_mode": "SHUTDOWN"})

    result = log.get_latest_by_topic("temperature")
    assert result == {"temperature": 69.5}, f"Expect: 69.5, actual: {result}"
    print("Search newest temperature pass")

    result = log.get_latest_by_topic("vibration")
    assert result == {"vibration": 1.0}, f"Expect: 1.0, actual: {result}"
    print("Search newest vibration pass")

    result = log.get_latest_by_topic("operation_mode")
    assert result == {"operation_mode": "SHUTDOWN"}, f"Expect: SHUTDOWN, actual: {result}"
    print("Search newest operation mode pass")

    assert log.get_latest_by_topic("no_topic") is None
    print("Not found log search pass")

    pass

def test_factory_log():
    print("\n=== Factory log smoke test ===")
    factory = FactoryLog()
    
    result = factory.get_latest_mode("machine_01")
    assert result is None
    print("Not found search pass")

    factory.record("machine_01", {"operation_mode": "RUNNING"})
    factory.record("machine_01", {"temperature": 72.3})
    factory.record("machine_01", {"vibration": 1.2})
    factory.record("machine_01", {"operation_mode": "OFFLINE"})

    result = factory.get_latest_mode("machine_01")
    assert result == "OFFLINE", f"Expect: OFFLINE, actual: {result}"
    print("Search latest mode pass")

    factory.record("machine_02", {"operation_mode": "IDLE"})
    factory.record("machine_02", {"operation_mode": "SHUTDOWN"})

    assert factory.get_latest_mode("machine_01") == "OFFLINE", f"Expect: OFFLINE, actual: {result}"
    assert factory.get_latest_mode("machine_02") == "SHUTDOWN", f"Expect: SHUTDOWN, actual: {result}"
    print("Distinct log in diff machine pass")
    pass

if __name__ == "__main__":
    test_machine_log()
    test_factory_log()
    print("\nAll test passed")