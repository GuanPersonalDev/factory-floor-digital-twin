import sys
from pathlib import Path 
sys.path.insert(0, str(Path(__file__).resolve().parent.parent)) # add root to Python search path due to I wanna load config.config_loader
from config.config_loader import FactoryConfig
import time
import random
from data_generate_implement import NewtonCoolingTrend, EMANoise, PoissonAnomaly
from data_generate_base import SensorSimulator

from dataclasses import dataclass, field


@dataclass
class ScriptPhase:
    operation_mode: str
    # infinity when duration is None
    duration: float | None = None

class MachineState:
    def __init__(self, machine_id: str, script_sequence: list[ScriptPhase] | None = None):
        self._config = FactoryConfig()
        self._machine_id = machine_id
        self._script_sequence = script_sequence or []
        self._sequenct_progress = 0
        self._current_phase_start_time: float = time.time()
        self._is_terminated: bool = False
        
        self._param_simulator: dict[str, SensorSimulator] = {
            self._config.TEMPERATURE_PARAM_KEY: SensorSimulator(
                trend= NewtonCoolingTrend(idle=25.0, target=self._config.get_trend_target(self._config.TEMPERATURE_PARAM_KEY), tau=self._config.get_trend_tau(self._config.TEMPERATURE_PARAM_KEY)),
                noise= EMANoise(alpha=1.0, sigma=0.3, initial= 25.0),
                anomaly= PoissonAnomaly(trigger_prob=0.005, delta_warning=10.0, delta_error=25.0, duration=30, baseline_target=65.0)
            ),
            self._config.VIBRATION_PARAM_KEY: SensorSimulator(
                trend= NewtonCoolingTrend(idle= 2.0, target=self._config.get_trend_target(self._config.VIBRATION_PARAM_KEY), tau=self._config.get_trend_tau(self._config.VIBRATION_PARAM_KEY)),
                noise = EMANoise(alpha=0.15, sigma=0.3, initial= 2.0),
                anomaly= PoissonAnomaly(trigger_prob= 0.005, delta_warning=3.5, delta_error=9.0, duration=30, baseline_target= 2.0)
            )
        }

    @property
    def machine_id(self) -> str:
        return self._machine_id
        
    def get_current_mode(self) -> str | None:
        if len(self._script_sequence) < 1:
            return self._config.RUNNING_MODE_KEY

        if self._is_terminated:
            return None
        
        if self._sequenct_progress >= len(self._script_sequence):
            return self._config.SHUTDOWN_MODE_KEY

        current_phase = self._script_sequence[self._sequenct_progress]
       
        if current_phase.duration is None:
            self._is_terminated = True
            return current_phase.operation_mode

        elapsed = time.time() - self._current_phase_start_time
        if elapsed >= current_phase.duration:
            self._sequenct_progress += 1
            self._current_phase_start_time = time.time()
            return self.get_current_mode()
        
        return current_phase.operation_mode


    def get_param_value(self, param: str):
        mode = self.get_current_mode()
        if mode is None:
            return None
        if param == self._config.OPERATION_PARAM_KEY:
            return mode

        if mode == self._config.SHUTDOWN_MODE_KEY or mode == self._config.OFFLINE_MODE_KEY:
            return None
        value = self._param_simulator[param].next_value()
        return value

    def get_all_topics(self) -> dict:
        result = {}
        first_check = self._config.OPERATION_PARAM_KEY
        operation_mode = self.get_param_value(first_check)
        if operation_mode is not None:
            result[first_check] = operation_mode
            for param in self._config.parameters:
                if param == first_check:
                    continue
                param_value = self.get_param_value(param)
                if param_value is not None:
                    result[param] = param_value
        return result
            
