import math, random

from data_generate_base import TrendModel, NoiseModel, AnomalyModel


# Trend Model (趨勢)
class NewtonCoolingTrend(TrendModel):
    """牛頓冷卻定律"""
    def __init__(self, idle: float, target: float, tau: float):
        self.idle = idle
        self.target = target
        self.tau = tau
        self.elapsed = 0.0

    def update(self, dt: float) -> float:
        self.elapsed += dt
        ratio = 1.0 - math.exp(-self.elapsed / self.tau)
        return self.idle + (self.target - self.idle) * ratio

# Noise (噪音)
class EMANoise(NoiseModel):
    """EMA 低通濾波"""
    def __init__(self, alpha: float, sigma: float, initial: float):
        self.alpha = alpha
        self.sigma = sigma
        self._ema_value = initial

    def update(self, base_value: float) -> float:
        raw = base_value + random.gauss(0, self.sigma)
        if self._ema_value is None:
            self._ema_value = raw
        self._ema_value = self.alpha * raw + (1- self.alpha) * self._ema_value
        return round(self._ema_value, 4)

# Anomaly (異常層)
class PoissonAnomaly(AnomalyModel):
    """泊松過程: 隨機觸發，修改趨勢模型的 target"""
    def __init__(self, trigger_prob: float, delta: float, duration: int, baseline_target: float):
        self._trigger_prob = trigger_prob
        self._delta = delta
        self._duration = duration
        self._active = False
        self._remaining = 0
        self._baseline_target = baseline_target

    def update(self, trend: TrendModel) -> None:
        if not self._active:
            if random.random() < self._trigger_prob:
                self._active = True
                self._remaining = self._duration
                trend.target = self._baseline_target + self._delta
        else:
            self._remaining -= 1
            if self._remaining <= 0:
                self._active = False
                trend.target = self._baseline_target

