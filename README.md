Before Running the code, setup the database by running SmartFarmDB.sql file on MySQL, then changing the connection information of the get_connection function in ProcedureCall.py file in the Infrastructure directory.

FrontEnd interaction:
1. open terminal and change directory to \SmartFarm backEnd\src\main
2. run python RestApi.py
3. open new terminal and change directory to \SmartFarm backEnd\test\Console
4. run python ConsoleInterface.py
5. if you want to simulate retrieving data from device then open new terminal and change directory to \SmartFarm backEnd\test\Console,
then run python DevicePublishDataSimulator.py

Note: you can change the simulate_device_data function inside DevicePublishDataSimulator.py to publish as many data as you want.

6. to close the API, you kill the terminal that are running it.



Device interaction:
for this part, you are in charge of the following file:
+ interacting with device: CommandModel.py
+ retrieving data from device: MQTTManagerModel.py

in CommandModel.py, you need to modify the run method in two concrete class ActivatePump and ActivateFan such that it send the signal to control the device.
you should read the file ActivationGeneratorModel.py to understand how command is generated.

in MQTTManagerModel.py, you need to test whether the code run - retrieving data from device and store in database.
In case it does not function properly, you need to modify the class MQTTManager. when you modify it, you keep the interface of the class's constructor.
you should read the file SensorAndDeviceHandlerRegistryModel.py to understand how the data is handled.

to test it, you open the file DeviceConnectingTest.py. in this file, i have written a function for each test.
To run it:
1.call the function in "if __name__ == "__main__":"

2.open new terminal, change directory to \SmartFarm backEnd\test\DeviceTest

3. run python DeviceConnectingTest.py
############################################API END POINT##############################################
login: /Login
Registration: /registration
SetRule: /AutomationRule
Activate device: /activateDevice
SendWebSocket: /ws/data

###########################################MessageForeachService#######################################
login: http://127.0.0.1:5000/login -u <userName>:<passWord>

registration: curl.exe -X POST http://127.0.0.1:5000/registration
    -H "Content-Type: application/json"
    -d "<UserDescription>"

SetRule: curl.exe -X POST http://127.0.0.1:5000/AutomationRule \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d "<RuleDescription>"

Activate Device: curl.exe -X POST http://127.0.0.1:5000/AutomationRule \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d "<ActivationDescription>"

SendWebSocket: establishing a WebSocket connection to the backend at the endpoint /ws/data.
Using websocket url is ws://localhost:8000/ws/data?token=<token> to
opens a WebSocket connection to the backend server running at localhost:8000.
Includes a JWT token in the URL query string — this token authenticates the session.
The backend uses this token to verify the user before accepting the connection.

############################################UserDescription############################################
UserDescription = {
    "UserName": <userName>
    "PassWord": <passWord>
    "Email": <email>
    "DeviceName": <DeviceName>
}

############################################DeviceDataPayload###########################################
DeviceDataPayload = {
    "Temperature": <data>,
    "Humidity": <data>,
    "Moisture": <data>,
    "Lux": <data>
    "GDD": <data>,
    "Status": <data>,
    "Pump_1": <data>,
    "Fan": <data>
}


############################################ActivationDescription############################################
ActivationDescription = {
    "Header": {
        "DescriptionType": "ActivationDescription",
        "User": <UserName>
    },
    "Body": <Activation content>
    }

}

######Activation content of differences CommandType######
PumpActivation_content = {
    "CommandType": "ActivePump",
    "Parameter":{
        "Pump_1": 1 or 0
    }
}

FanActivation_content = {
    "CommandType": "ActiveFan",
    "Parameter":{
        "Fan": 1 or 0
    }
}


############################################RuleDescription############################################
RuleDescription = {
    "Header": {
        "DescriptionType": "RuleDescription",
        "OperationType": "ADD" or "UPDATE"
        "User": <UserName>
    },
    "Body": {
        "Rule1": <rule content>,
        "Rule2": <rule content>,
        "Rule3": <rule content>,
        "Rule4": <rule content>,
        ... other rules
    }
}

######Content of rule######
rule_content = {
    "Condition": {
        "Type": "<ConditionType>",
        "Description": <condition description>
    },
    "Action": ActivationDescription
}

######Description of differences condition######
Type: SetThreshold
threshold_description = {
    "Operation": <=, >=, >, <, == or !=,
    "Threshold": <value>,
    "Kind": "Temperature", "Humidity", "Moisture" or "Lux"
}

###########################################RetrievedData############################################################
format of data message:
Format 1 = {
    "type": "initial",
    "old_data": list of <Data>,
    "new_data": list of <Data>
}

Format 2 = {
    "type": "update",
    "new_data": list of <Data>
}

Data = {
    'timestamp': '2025-05-06T21:24:46',
    'data_payload': {
        "Fan": <value>,
        "GDD": <value>,
        "Lux": <value>,
        "Pump_1": <value>,
        "Status": <value>,
        "Humidity": <value>,
        "Moisture": <value>,
        "Temperature": <value>
    }
}
