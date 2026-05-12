from abc import ABC, abstractmethod

class TrendModel(ABC):
    """長期趨勢"""
    @abstractmethod
    def update(self, dt: float) -> float:
        """回傳基準值"""
        pass

class NoiseModel(ABC):
    """穩態波動，對基準值加入有色噪音"""
    @abstractmethod
    def update(self, base_value: float) -> float:
        """接收基準值，回傳加入噪音後的值"""
        pass

class AnomalyModel(ABC):
    """異常事件:改變趨勢模型的目標參數"""
    @abstractmethod
    def update(self, trend: TrendModel) -> None:
        """操作trend的內部狀態"""
        pass

class SensorSimulator:
    def __init__(self, trend: TrendModel, noise: NoiseModel, anomaly: AnomalyModel, dt: float = 1.0):
        self.trend = trend
        self.noise = noise
        self.anomaly = anomaly
        self.dt = dt

    def next_value(self) -> float:
        self.anomaly.update(self.trend)
        base = self.trend.update(self.dt)
        result = self.noise.update(base)
        return result

