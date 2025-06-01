from abc import ABC, abstractmethod
from Infrastructure.Logging import write_log
from src.main.Domain.Retriever.MQTTManagerModel import MQTTManager

class ActivationCommand(ABC):
    def __init__(self, DeviceInfo, mqtt_manager, Parameter: dict):
        self.DeviceInfo = DeviceInfo #ACCESS NAME
        self.Parameter = Parameter
        self.mqtt_manager = mqtt_manager

    @abstractmethod
    def run(self):
        pass

class ActivatePump(ActivationCommand):
    def run(self):
        write_log(f"device {self.DeviceInfo} activate water pump")
        # Publish to the correct topic based on the parameter key

        key, value = next(iter(self.Parameter.items()))
        if key == "Pump_1":
            topic = f"{self.DeviceInfo}/feeds/V10"
            self.mqtt_manager.publish(topic, value)
        elif key == "Pump_2":
            topic = f"{self.DeviceInfo}/feeds/V11"
            self.mqtt_manager.publish(topic, value)
        


class ActivateFan(ActivationCommand):
    def run(self):
        write_log(f"device {self.DeviceInfo} activate Fan")
        # Publish to the correct topic based on the parameter key
        key, value = next(iter(self.Parameter.items()))
        if key == "Fan":
            topic = f"{self.DeviceInfo}/feeds/V12"
            self.mqtt_manager.publish(topic, value)


