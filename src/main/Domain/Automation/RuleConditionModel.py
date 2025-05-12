import operator
from abc import ABC, abstractmethod

class Condition(ABC):
    def __init__(self, Description: dict):
        self.Description = Description
    @abstractmethod
    def evaluate(self, SensorData: dict) -> bool:
        pass

class ThresholdCondition(Condition):
    def evaluate(self, SensorData: dict) -> bool: #return value of <threshold> <comparator> <sensor data>
        threshold = self.Description["Threshold"]
        comparator = self.Description["Operation"]
        data = SensorData[self.Description["Kind"]]
        ops = {
            "<=": operator.le,
            ">=": operator.ge,
            ">": operator.gt,
            "<": operator.lt,
            "==": operator.eq,
            "!=": operator.ne,
        }

        if comparator not in ops:
            raise ValueError(f"Unsupported comparator: {comparator}")

        return ops[comparator](threshold, data)
