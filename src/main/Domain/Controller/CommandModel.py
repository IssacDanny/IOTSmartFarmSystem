from abc import ABC, abstractmethod
from Infrastructure.Logging import write_log
from src.main.Domain.Retriever.MQTTManagerModel import MQTTManager

class ActivationCommand(ABC):
    def __init__(self, DeviceInfo, Parameter: dict):
        self.DeviceInfo = DeviceInfo #ACCESS NAME
        self.Parameter = Parameter
        self.mqttmanager = MQTTManager("mqtt.ohstem.vn", 1883, "Tuluu", "")

    @abstractmethod
    def run(self):
        pass

class ActivatePump(ActivationCommand):
    def run(self):
        write_log(f"device {self.DeviceInfo} activate water pump")
        # Publish to the correct topic based on the parameter key
        for key, value in self.Parameter.items():
            if key == "Pump_1":
                topic = "Tuluu/feeds/V10"
                self.mqttmanager.client.publish(topic, value)
            elif key == "Pump_2":
                topic = "Tuluu/feeds/V11"
                self.mqttmanager.client.publish(topic, value)
            else:
                continue
            

class ActivateFan(ActivationCommand):
    def run(self):
        write_log(f"device {self.DeviceInfo} activate Fan")
            # Publish to the correct topic based on the parameter key
        for key, value in self.Parameter.items():
            if key == "Fan":
                topic = "Tuluu/feeds/V12"
                self.mqttmanager.client.publish(topic, value)

