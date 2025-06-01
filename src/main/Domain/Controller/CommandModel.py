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
<<<<<<< HEAD
        key, value = next(iter(self.Parameter.items()))
        if key == "Pump_1":
            topic = f"{self.DeviceInfo}/feeds/V10"
            self.mqtt_manager.publish(topic, value)
        elif key == "Pump_2":
            topic = f"{self.DeviceInfo}/feeds/V11"
            self.mqtt_manager.publish(topic, value)
        
=======
        for key, value in self.Parameter.items():
            if key == "Pump_1":
                topic = "Tuluu/feeds/V10"
                self.mqttmanager.client.publish(topic, value)
            elif key == "Pump_2":
                topic = "Tuluu/feeds/V11"
                self.mqttmanager.client.publish(topic, value)
            else:
                continue
            
>>>>>>> ce6bb6d607d1970a0a056a452e3ca0eb3e8efae2

class ActivateFan(ActivationCommand):
    def run(self):
        write_log(f"device {self.DeviceInfo} activate Fan")
<<<<<<< HEAD
        # Publish to the correct topic based on the parameter key
        key, value = next(iter(self.Parameter.items()))
        if key == "Fan":
            topic = f"{self.DeviceInfo}/feeds/V12"
            self.mqtt_manager.publish(topic, value)
=======
            # Publish to the correct topic based on the parameter key
        for key, value in self.Parameter.items():
            if key == "Fan":
                topic = "Tuluu/feeds/V12"
                self.mqttmanager.client.publish(topic, value)
>>>>>>> ce6bb6d607d1970a0a056a452e3ca0eb3e8efae2

