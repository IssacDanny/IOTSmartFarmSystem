import json, threading, time
from Infrastructure.Logging import write_log
from Infrastructure import ProcedureCall
from Infrastructure.Fair_lock import FairLock
class SADRegistry: #Sensor and Device registry
    def __init__(self, deviceInfo):
        self.deviceInfo = deviceInfo
        self.topics = {}
        self._data = {}
        self._received = set()
        self._inserted = False
        self._lock = threading.Lock()
        self._last_data = {}

    def register(self, topic: str, ValueType: str):
        topic = f"{self.deviceInfo}/" + topic
        self.topics[topic] = ValueType
        self._data[ValueType] = -1  # Default value

    def handle_message(self, topic, payload):
        if topic not in self.topics:
            return

        try:
            value_type = self.topics[topic]
            jsonobj = json.loads(payload)
            self._data[value_type] = jsonobj
            self._received.add(value_type)
            write_log(f"Received from {self.deviceInfo}: {value_type} = {jsonobj}")

        except Exception as e:
            write_log(f"Error handling message for {topic}: {e}")

    def get_data(self):
        write_log(f"All data received from {self.deviceInfo}. Inserting to DB...")
        ProcedureCall.InsertSensorData(self.deviceInfo, self._data.copy())

    def run_background_inserter(self, interval=10):
        def loop():
            while True:
                time.sleep(interval)
                self.get_data()

        threading.Thread(target=loop, daemon=True).start()

    def _all_data_received(self, deviceInfo):
        expected = set(self._data.keys())
        missing = expected - self._received
        if missing:
            write_log(f"Still waiting for: {missing} of {deviceInfo} device")
            return False
        return True

