
from ..Automation.AutomizerModel import Automizer
from ..Controller.DeviceControllerModel import DeviceController
from ..Retriever.RetrieverModel import Retriever
class User:
    def __init__(self, userName: str, passWord: str, email: str, deviceInfo, AutomationRule: dict):
        self.userName = userName
        self.passWord = passWord
        self.email = email
        self.deviceInfo = deviceInfo
        self.automationRule = AutomationRule

        self.retriever = Retriever(userName, deviceInfo)
        self.automizer = Automizer(deviceInfo, self.retriever.mqttManager, AutomationRule)
        self.deviceController = DeviceController(deviceInfo, self.retriever.mqttManager)