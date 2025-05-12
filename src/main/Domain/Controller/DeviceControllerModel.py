from ..Controller.ActivationGeneratorModel import ActivationGenerator

class DeviceController:
    def __init__(self, DeviceInfo):
        self.DeviceInfo = DeviceInfo
        self.ActGen = ActivationGenerator()

    async def ActiveDevice(self, ActivateDescription):
        command = self.ActGen.generate(self.DeviceInfo, ActivateDescription)
        command.run()

