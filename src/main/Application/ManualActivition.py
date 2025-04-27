import paho.mqtt.client as mqttclient
import json
import ast
from Domain import authBusiness

# MQTT Broker and user info
BROKER_ADDRESS = "mqtt.ohstem.vn"
PORT = 1883
ACCESS_TOKEN = ""
ACCESS_USERNAME = "Tuluu"


def connected(client, usedata, flags, rc):
    if rc == 0:
        print("Connected successfully!!")
    else:
        print("Connection is failed")


client = mqttclient.Client()
client.username_pw_set(ACCESS_USERNAME, ACCESS_TOKEN)

client.on_connect = connected
client.connect(BROKER_ADDRESS, 1883)
client.loop_start()



def activateDevice(request):
    # check authorization before perform task
    authorized, err = authBusiness.validate(request)

    if err:
        return err

    authorized = json.loads(authorized)  # the json file of token



    # TODO: implement logic for communicate with cloud to activate hardware
    if type(request) is str:
        # Convert back to type dict[str: int]
        request = ast.literal_eval(request)

    if "Pump_1" in request:
        client.publish("Tuluu/feeds/V10", request["Pump_1"])
    elif "Pump_2" in request:
        client.publish("Tuluu/feeds/V11", request["Pump_2"])
    elif "Fan" in request:
        client.publish("Tuluu/feeds/V12", request["Fan"])
    else:
        return {"error": "Invalid device"}
    return
