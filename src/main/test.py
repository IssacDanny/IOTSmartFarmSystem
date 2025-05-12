
import time, asyncio, requests, websockets
from requests.auth import HTTPBasicAuth
from datetime import datetime
from Infrastructure.Logging import write_log
from Infrastructure import ProcedureCall
from Application.SystemModel import System
from Domain.User.UserManagerModel import UserManager

def create_ActivationDescriptions():
    List = []
    for i in range(1, 5):
        ActivationDescription = {
            "Header": {
                "DescriptionType": "ActivationDescription",
                "User": f"user{i}"
            },
            "Body": {
                "CommandType": "ActivePump",
                "Parameter": {
                    "Duration": i
                }
            }
        }
        List.append(ActivationDescription)

    for i in range(5,10):
        ActivationDescription = {
            "Header": {
                "DescriptionType": "ActivationDescription",
                "User": f"user{i}"
            },
            "Body": {
                "CommandType": "ActiveLight",
                "Parameter": {
                    "Duration": i,
                    "Intensity": i
                }
            }
        }
        List.append(ActivationDescription)

    return List

def create_RuleDescription():
    List = []
    for i in range(1, 5):
        ActivationDescription = {
            "Header": {
                "DescriptionType": "ActivationDescription",
                "User": ""
            },
            "Body": {
                "CommandType": "ActivePump",
                "Parameter": {
                    "Duration": i * 10
                }
            }
        }

        threshold_description = {
            "Operation": "<",
            "Threshold": 25,
            "Kind": "Temperature"
        }

        RuleDescription = {
            "Header": {
                "DescriptionType": "RuleDescription",
                "User": f"user{i}"
            },
            "Body": {
                "rule": {
                    "Condition": {
                        "Type": "SetThreshold",
                        "Description": threshold_description
                    },
                    "Action": ActivationDescription
                },
            }
        }

        List.append(RuleDescription)

    for i in range(5, 10):
        ActivationDescription = {
            "Header": {
                "DescriptionType": "ActivationDescription",
                "User": ""
            },
            "Body": {
                "CommandType": "ActiveLight",
                "Parameter": {
                    "Duration": i * 10,
                    "Intensity": i * 2
                }
            }
        }

        threshold_description = {
            "Operation": ">",
            "Threshold": 25,
            "Kind": "Temperature"
        }

        RuleDescription = {
            "Header": {
                "DescriptionType": "RuleDescription",
                "User": f"user{i}"
            },
            "Body": {
                "rule": {
                    "Condition": {
                        "Type": "SetThreshold",
                        "Description": threshold_description
                    },
                    "Action": ActivationDescription
                },
            }
        }
        List.append(RuleDescription)

    return List


async def test_UserManager():
    tasks = set()
    manager = UserManager()
    userRule = create_RuleDescription()
    userActivate = create_ActivationDescriptions()

    #set user
    for i in range(1, 10):
        DummyUserDescription = {"UserName": f"user{i}"}
        manager.set(DummyUserDescription)
    #enforce and addrule for each user
    for i in range(1, 10):
        user = manager.get(f"user{i}")
        task = asyncio.create_task(user.automizer.EnforceRule())
        tasks.add(task)
        await user.automizer.AddRule(userRule[i - 1])

    #user activate device
    for i in range(1, 10):
        user = manager.get(f"user{i}")
        task = asyncio.create_task(user.deviceController.ActiveDevice(userActivate[i - 1]))
        tasks.add(task)
    #quiting
    for i in range(1, 10):
        user = manager.get(f"user{i}")
        task = asyncio.create_task(user.automizer.StopEnforcing())
        tasks.add(task)

    #wait for all task to finish
    await asyncio.gather(*tasks)
    print("All tasks finished.")

def test_InsertUser():
    userDescription = {
        "UserName": "User123",
        "PassWord": "000000",
        "Email": "User123@gmail.com",
        "DeviceName": "Tuluu"
    }
    manager = UserManager()
    manager.set(userDescription)

async def test_InsertRule():
    ActivationDescription = {
        "Header": {
            "DescriptionType": "ActivationDescription",
            "User": "User123"
        },
        "Body": {
            "CommandType": "ActivePump",
            "Parameter": {
                "Pump_1": 1
            }
        }
    }

    threshold_description = {
        "Operation": ">",
        "Threshold": 25,
        "Kind": "Temperature"
    }

    RuleDescription = {
        "Header": {
            "DescriptionType": "RuleDescription",
            "User": f"User{123}"
        },
        "Body": {
            "rule": {
                "Condition": {
                    "Type": "SetThreshold",
                    "Description": threshold_description
                },
                "Action": ActivationDescription
            },
        }
    }

    manager = UserManager()
    tasks = set()
    task = asyncio.create_task(manager.store["User123"].automizer.AddRule(RuleDescription))
    tasks.add(task)
    await asyncio.gather(*tasks)
    print("All tasks finished.")

def test_getdata():
    data = {
        "Temperature": 25,
        "Humidity": 60,
        "Moisture": 50,
        "Lux": 1000,
        "GDD": 200,
        "Status": 1,
        "Pump_1": 0,
        "Fan": 0
    }
    last_seen = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #ProcedureCall.InsertSensorData("alice_device", data)
    old_data = ProcedureCall.RetrieveHistoricalSensorData('alice', last_seen)
    history_sent = False
    try:
        while True:
            new_data = ProcedureCall.RetrieveNewSensorData("alice", last_seen)

            # Send only once
            if not history_sent:
                print({
                    "type": "initial",
                    "old_data": old_data,
                    "new_data": new_data
                })

                history_sent = True
            elif new_data:
                print({
                    "type": "update",
                    "new_data": new_data
                })

            if new_data:
                if isinstance(new_data, list) and new_data:
                    last_seen = new_data[-1]["timestamp"].replace("T", " ")

                break

            break

    except Exception as e:
        print("WebSocket error:", e)

def test_system():
    ActivationDescription = {
        "Header": {
            "DescriptionType": "ActivationDescription",
            "User": "alice"
        },
        "Body": {
            "CommandType": "ActivePump",
            "Parameter": {
                "Pump_1": 1
            }
        }
    }
    system = System()
    time.sleep(10)
    system.controllerManager.stop()
    system.automizerManager.stop()

def test_APi():
    url = "http://127.0.0.1:8000/test-request"

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer test_token"
    }

    payload = {
        "message": "Hello from client!",
        "user": "john_doe"
    }

    response = requests.post(url, json=payload, headers=headers)

    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())

def send_authentication(username, password):
    url = "http://127.0.0.1:8000/login"

    response = requests.post(url, auth=HTTPBasicAuth(username, password))

    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())
    return response.json().get("Token")

def send_Resgistration(username, password, email, devicename):
    url = "http://127.0.0.1:8000/registration"

    headers = {
        "Content-Type": "application/json",
        "Authorization": ""
    }

    payload = {
        "UserName": username,
        "PassWord": password,
        "Email": email,
        "DeviceName": devicename
    }

    response = requests.post(url, json=payload, headers=headers)

    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())

def send_ActivationRule(UserName: str, token):
    url = "http://127.0.0.1:8000/activateDevice"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    payload = {
        "Header": {
            "DescriptionType": "ActivationDescription",
            "User": f"{UserName}"
        },
        "Body": {
            "CommandType": "ActivePump",
            "Parameter": {
                "Pump_1": 1
            }
        }
    }

    response = requests.post(url, json=payload, headers=headers)

    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())

def set_AutomationRule(UserName, token):
    url = "http://127.0.0.1:8000/AutomationRule"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    ActivationDescription = {
        "Header": {
            "DescriptionType": "ActivationDescription",
            "User": f"{UserName}"
        },
        "Body": {
            "CommandType": "ActivePump",
            "Parameter": {
                "Pump_1": 1
            }
        }
    }

    threshold_description = {
        "Operation": ">",
        "Threshold": 25,
        "Kind": "Temperature"
    }

    RuleDescription = {
        "Header": {
            "DescriptionType": "RuleDescription",
            "OperationType": "ADD",
            "User": f"{UserName}"
        },
        "Body": {
            "rule": {
                "Condition": {
                    "Type": "SetThreshold",
                    "Description": threshold_description
                },
                "Action": ActivationDescription
            },
        }
    }


    response = requests.post(url, json=RuleDescription, headers=headers)

    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())

async def test_websocket_connection(token):
    uri = f"ws://localhost:8000/ws/data?token={token}"

    try:
        async with websockets.connect(uri) as websocket:
            print("[Client] Connected to WebSocket")

            # Receive JSON data (historical + new data)
            while True:
                try:
                    message = await websocket.recv()
                    print("[Server]", message)
                except websockets.exceptions.ConnectionClosed:
                    print("[Client] Server closed connection")
                    break
                except Exception as e:
                    print("[Client] Error receiving data:", e)
                    break

    except Exception as e:
        print("[Client] Failed to connect:", e)


if __name__ == "__main__":
    #send_Resgistration("JohnDoe", "john123", "john.doe@gmail.com", "John_Device")
    token = send_authentication("alice", "pass123")
    #send_ActivationRule("JohnDoe", token)
    #set_AutomationRule("JohnDoe", token)
    asyncio.run(test_websocket_connection(token))
