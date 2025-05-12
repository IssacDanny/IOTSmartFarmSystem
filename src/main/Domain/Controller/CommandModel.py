from abc import ABC, abstractmethod
from Infrastructure.Logging import write_log
class ActivationCommand(ABC):
    def __init__(self, DeviceInfo, Parameter: dict):
        self.DeviceInfo = DeviceInfo #ACCESS NAME
        self.Parameter = Parameter
    @abstractmethod
    def run(self):
        pass

class ActivatePump(ActivationCommand):
    def run(self):
        write_log(f"device {self.DeviceInfo} activate water pump")

class ActivateFan(ActivationCommand):
    def run(self):
        write_log(f"device {self.DeviceInfo} activate Fan")

