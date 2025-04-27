import paho.mqtt.client as mqttclient
from threading import Thread
import time
import json

# MQTT Broker and user info
BROKER_ADDRESS = "mqtt.ohstem.vn"
PORT = 1883
ACCESS_TOKEN = ""
ACCESS_USERNAME = "Tuluu"

# List of sensor data
data = [-1,     # Temperature
        -1,     # Humidity
        -1,     # Moisture
        -1,     # Lux
        -1,     # GDD
        -1,     # Status
        -1,     # Pump 1
        -1      # Pump 2
]


def subscribed(client, userdata, mid, granted_qos):
    print("Subscribed...")



#------------ Sensor data subscribe callback event ------------#

def recv_message_V1(client, userdata, message):
    print("Received Temperature: ", message.payload.decode("utf-8"))
    try:
        jsonobj = json.loads(message.payload)
        data[0] = jsonobj
    except:
        pass

def recv_message_V2(client, userdata, message):
    print("Received Humidity: ", message.payload.decode("utf-8"))
    try:
        jsonobj = json.loads(message.payload)
        data[1] = jsonobj
    except:
        pass
def recv_message_V3(client, userdata, message):
    print("Received Moisture: ", message.payload.decode("utf-8"))
    try:
        jsonobj = json.loads(message.payload)
        data[2] = jsonobj
    except:
        pass
def recv_message_V4(client, userdata, message):
    print("Received Lux: ", message.payload.decode("utf-8"))
    try:
        jsonobj = json.loads(message.payload)
        data[3] = jsonobj
    except:
        pass
def recv_message_V5(client, userdata, message):
    print("Received GDD: ", message.payload.decode("utf-8"))
    try:
        jsonobj = json.loads(message.payload)
        data[4] = jsonobj
    except:
        pass
def recv_message_V6(client, userdata, message):
    print("Received Status: ", message.payload.decode("utf-8"))
    try:
        jsonobj = json.loads(message.payload)
        data[5] = jsonobj
    except:
        pass
def recv_message_V10(client, userdata, message):
    print("Received Pump 1: ", message.payload.decode("utf-8"))
    try:
        jsonobj = json.loads(message.payload)
        data[6] = jsonobj
    except:
        pass
def recv_message_V11(client, userdata, message):
    print("Received Pump 2: ", message.payload.decode("utf-8"))
    try:
        jsonobj = json.loads(message.payload)
        data[7] = jsonobj
    except:
        pass




def connected(client, usedata, flags, rc):
    if rc == 0:
        print("Connected successfully!!")

        # Feeds subscribe, Temperature in V1, Humidity in V2, etc.
        client.subscribe("Tuluu/feeds/V1")
        client.subscribe("Tuluu/feeds/V2")
        client.subscribe("Tuluu/feeds/V3")
        client.subscribe("Tuluu/feeds/V4")
        client.subscribe("Tuluu/feeds/V5")
        client.subscribe("Tuluu/feeds/V6")
        client.subscribe("Tuluu/feeds/V10")
        client.subscribe("Tuluu/feeds/V11")
    else:
        print("Connection is failed")


client = mqttclient.Client()
client.username_pw_set(ACCESS_USERNAME, ACCESS_TOKEN)

client.on_connect = connected
client.connect(BROKER_ADDRESS, 1883)
client.loop_start()

# Callback register
client.on_subscribe = subscribed
client.message_callback_add("Tuluu/feeds/V1", lambda client, userdata, message: recv_message_V1(client, userdata, message))
client.message_callback_add("Tuluu/feeds/V2", lambda client, userdata, message: recv_message_V2(client, userdata, message))
client.message_callback_add("Tuluu/feeds/V3", lambda client, userdata, message: recv_message_V3(client, userdata, message))
client.message_callback_add("Tuluu/feeds/V4", lambda client, userdata, message: recv_message_V4(client, userdata, message))
client.message_callback_add("Tuluu/feeds/V5", lambda client, userdata, message: recv_message_V5(client, userdata, message))
client.message_callback_add("Tuluu/feeds/V6", lambda client, userdata, message: recv_message_V6(client, userdata, message))
client.message_callback_add("Tuluu/feeds/V10", lambda client, userdata, message: recv_message_V10(client, userdata, message))
client.message_callback_add("Tuluu/feeds/V11", lambda client, userdata, message: recv_message_V11(client, userdata, message))


json_data = None
def json_builder():
    global json_data
    print(f"DATA: {data}\n")
    combined_data = {
        "Temperature": data[0],
        "Humidity": data[1],
        "Moisture": data[2],
        "Lux": data[3],
        "GDD": data[4],
        "Status": data[5],
        "Pump_1": data[6],
        "Pump_2": data[7]
    }
    json_data = json.dumps(combined_data)

def sensorDataProducer():
    #TODO: implement the logic for communication with cloud server to obtain sensor data
    return json_data

if __name__ == "__main__":
    while True:
        t = Thread(target=json_builder)
        t.start()
        print(sensorDataProducer())
        time.sleep(5)





