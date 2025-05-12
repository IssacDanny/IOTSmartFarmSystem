from src.main.Domain import Retriever
from src.main.Domain.Controller.DeviceControllerModel import DeviceController
from src.main.Domain.Retriever.MQTTManagerModel import MQTTManager


def test_ActivateDevice(DeviceInfo):
    controller = DeviceController(DeviceInfo)
    ActivatePumpDescription = {
        "Header": {
            "DescriptionType": "ActivationDescription",
            "User": ""
        },
        "Body": {
            "CommandType": "ActivePump",
            "Parameter": {
                "Pump_1": 1
            }
        }
    }
    ActivateFanDescription = {
        "Header": {
            "DescriptionType": "ActivationDescription",
            "User": ""
        },
        "Body": {
            "CommandType": "ActiveFan",
            "Parameter": {
                "Fan": 1
            }
        }
    }
    controller.ActiveDevice(ActivatePumpDescription)
    controller.ActiveDevice(ActivateFanDescription)

def test_RetreivingData(ACCESSNAME):
    mqttManager = MQTTManager("mqtt.ohstem.vn", 1883, ACCESSNAME, "")

if __name__ == "__main__":
    pass