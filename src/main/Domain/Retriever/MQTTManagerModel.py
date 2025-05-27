import paho.mqtt.client as mqttclient
import json
from .SensorAndDeviceHandlerRegistryModel import SADRegistry
from Infrastructure import ProcedureCall
from Infrastructure.Logging import write_log
import time

class MQTTManager:
    def __init__(self, broker, port, deviceInfo, token):
        self.deviceInfo = deviceInfo
        #retristry topics
        self.registry = SADRegistry(deviceInfo)
        self.RegistTopics()

        #establish mqtt connection
        self.client = mqttclient.Client()
        self.client.username_pw_set(deviceInfo, token)
        self.client.on_connect = self.connected
        self.client.on_subscribe = self.subscribed
        self.client.connect(broker, port)
        self.client.loop_start()
        for topic in self.registry.topics:
            self.client.message_callback_add(topic, self.create_message_handler(topic))

        self.start_data_collect_loop()

    def start_data_collect_loop(self):
        while True:
            ProcedureCall.InsertSensorData(self.deviceInfo, self.registry.get_all_data()) # insert new data to DataBase
            time.sleep(5)


    def RegistTopics(self):
        self.registry.register("feeds/V1", "Temperature")
        self.registry.register("feeds/V2", "Humidity")
        self.registry.register("feeds/V3", "Moisture")
        self.registry.register("feeds/V4", "Lux")
        self.registry.register("feeds/V5", "GDD")
        self.registry.register("feeds/V6", "Status")
        self.registry.register("feeds/V10", "Pump 1")
        self.registry.register("feeds/V11", "Pump 2")

    def connected(self, client, userdata, flags, rc):
        if rc == 0:
            write_log(f"Device {self.deviceInfo} connected to broker.")
            for topic in self.registry.topics:
                client.subscribe(topic)
        else:
            write_log(f"Device {self.deviceInfo} failed to connect.")

    def disconnect(self):
        write_log(f"Device {self.deviceInfo} disconnecting from MQTT broker...")
        self.client.loop_stop()  # Stop the background MQTT loop
        self.client.disconnect()  # Gracefully close the connection
        write_log(f"Device {self.deviceInfo} disconnected successfully.")
    def subscribed(self, client, userdata, mid, granted_qos):
        write_log(f"Device {self.deviceInfo} Subscribed to topics.")

    def create_message_handler(self, topic):
        return lambda client, userdata, message: self.registry.handle_message(topic, message.payload.decode("utf-8"))

    def json_builder(self):
        print("Current Sensor Data:")
        print(json.dumps(self.registry.get_all_data(), indent=2))

    def sensorDataProducer(self):
        return json.dumps(self.registry.get_all_data())
