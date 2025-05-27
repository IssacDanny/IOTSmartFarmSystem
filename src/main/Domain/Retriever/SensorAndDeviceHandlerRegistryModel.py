import json
from Infrastructure.Logging import write_log
from Infrastructure import ProcedureCall
class SADRegistry: #Sensor and Device registry
    def __init__(self, deviceInfo):
        self.deviceInfo = deviceInfo
        self.topics = {}
        self._data = {}

    def register(self, topic: str, ValueType: str):
        topic = f"{self.deviceInfo}/" + topic
        self.topics[topic] = ValueType
        self._data[ValueType] = -1  # Default value

    def handle_message(self, topic, payload):
        if topic in self.topics:
            try:
                jsonobj = json.loads(payload)
                self._data[self.topics[topic]] = jsonobj
                write_log(f"Retrieve from {self.deviceInfo}, the data: {self.get_all_data()} ")
                # ProcedureCall.InsertSensorData(self.deviceInfo, self.get_all_data()) # insert new data to DataBase
            except Exception as e:
                write_log(f"Error handling message for {topic}: {e}")

    def get_all_data(self):
        return self._data.copy()


