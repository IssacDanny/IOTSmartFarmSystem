from ..Controller.ActivationGeneratorModel import ActivationGenerator

class DeviceController:
    def __init__(self, DeviceInfo, mqtt_manager):
        self.DeviceInfo = DeviceInfo
        self.ActGen = ActivationGenerator()
        self.mqtt_manager = mqtt_manager

    async def ActiveDevice(self, ActivateDescription):
        command = self.ActGen.generate(self.DeviceInfo, self.mqtt_manager, ActivateDescription)
        command.run()

