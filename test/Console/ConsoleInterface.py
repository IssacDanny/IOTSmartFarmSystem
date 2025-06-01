import time, asyncio, requests, websockets, queue, operator, json, threading
from datetime import datetime
from requests.auth import HTTPBasicAuth

class ConsoleApp:
    def __init__(self):
        self.username = ""
        self.DataQueue = queue.Queue()
        self.token = None
        self.base_url = "http://127.0.0.1:8000"
        self.isRunning = False
        self.tasks = []
        self.loop_thread = None
        self.loop = None
        self.websocket = None

    async def run(self):
        try:
            self.isRunning = True
            while self.isRunning:
                print("\n--- SmartFarm Console ---")
                print("1. Register")
                print("2. Login")
                print("3. Send Activation Command")
                print("4. Set Automation Rule")
                print("5. Logout")

                choice = input("Choose an option (1-5): ")

                if choice == "1":
                    self.register()
                elif choice == "2":
                    await self.login()
                elif choice == "3":
                    self.send_activation()
                elif choice == "4":
                    self.set_automation_rule()
                elif choice == "5":
                    await self.exit()
                    break
                else:
                    print("Invalid choice. Try again.")

                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await self.exit()

    async def exit(self):
        print("Shutting down...")
        self.isRunning = False

        # Stop loop from other thread
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)

        if self.loop_thread:
            self.loop_thread.join(timeout=5)
            print("Finish shutting down.")

    def start_background_loop(self):
        def run_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.isRunning = True
            ws_task = self.loop.create_task(self.websocket_connection())
            log_task = self.loop.create_task(self.process_data_queue())
            self.tasks = [ws_task, log_task]
            try:
                self.loop.run_forever()
            finally:
                print("[Loop] Cleaning up tasks...")
                for task in self.tasks:
                    task.cancel()
                self.loop.run_until_complete(asyncio.gather(*self.tasks, return_exceptions=True))
                self.loop.close()
                print("[Loop] Closed cleanly")

        self.loop_thread = threading.Thread(target=run_loop, daemon=True)
        self.loop_thread.start()

    def register(self):
        username = input("Username: ")
        password = input("Password: ")
        email = input("Email: ")
        devicename = input("Device Name: ")

        payload = {
            "UserName": username,
            "PassWord": password,
            "Email": email,
            "DeviceName": devicename
        }

        response = requests.post(
            f"{self.base_url}/registration",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print("Status Code:", response.status_code)
        print("Response JSON:", response.json())

    async def login(self):
        self.username = input("Username: ")
        password = input("Password: ")

        response = requests.post(
            f"{self.base_url}/login",
            auth=HTTPBasicAuth(self.username, password)
        )
        print("Status Code:", response.status_code)
        print("Response JSON:", response.json())
        self.token = response.json().get("Token")

        # start recieving data after login
        if self.token:
            self.start_background_loop()

    def send_activation(self):
        if not self.token:
            print("Please login first.")
            return
        while True:
            print("select command type:")
            print("activate pump: 1")
            print("activate fan: 2")
            commandType = input("command type: ")
            turn = input("Turn on/off(1-0): ")
            if commandType == "1":
                command = {
                    "CommandType": "ActivePump",
                    "Parameter": {
                        "Pump_1": int(turn)
                    }
                }
                break
            elif commandType == "2":
                command = {
                    "CommandType": "ActiveFan",
                    "Parameter": {
                        "Fan": int(turn)
                    }
                }
                break
            else:
                print("Wrong option, please choose again")

        payload = {
            "Header": {
                "DescriptionType": "ActivationDescription",
                "User": self.username
            },
            "Body": command
        }

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        response = requests.post(f"{self.base_url}/activateDevice", json=payload, headers=headers)
        print("Status Code:", response.status_code)
        print("Response JSON:", response.json())

    def set_automation_rule(self):
        ops = {
            "<=": operator.le,
            ">=": operator.ge,
            ">": operator.gt,
            "<": operator.lt,
            "==": operator.eq,
            "!=": operator.ne,
        }

        dataTypes = {
            "Lux": -1,
            "Humidity": -1,
            "Moisture": -1,
            "Temperature": -1
        }

        if not self.token:
            print("Please login first.")
            return

        while True:
            print("Choose your option")
            print("1. ADD")
            print("2. UPDATE")
            operationType = input("choose your option(1-2): ")
            if operationType == "1":
                operationType = "ADD"
                break
            elif operationType == "2":
                operationType = "UPDATE"
                break
            else:
                print("wrong operation type, please choose again")

        while True:
            print("Select type of condition")
            print("1. Set threshold")
            conditionType = input("condition type: ")
            if conditionType == "1":
                while True:
                    print("threashold will be compare as follow: <threshold> <comparator> <data>")
                    print("choose your comparator type(<=, >=, >, <, ==, !=)")
                    comparator = input("comparator type: ")
                    if comparator not in ops:
                        print("wrong comparator type, please choose again")
                    else:
                        break

                while True:
                    print("choose the data type that you want to compare(Lux, Humidity, Moisture, Temperature)")
                    dataType = input("Data type: ")
                    if dataType not in dataTypes:
                        print("wrong data type, please choose again")
                    else:
                        break
                thresholdValue = int(input("input threshold value(number): "))

                threshold_description = {
                    "Operation": comparator,
                    "Threshold": thresholdValue,
                    "Kind": dataType
                }
                break

            else:
                print("wrong condition type, please choose again")

        condition = {
                "Type": "SetThreshold",
                "Description": threshold_description
        }

        while True:
            print("select command type:")
            print("activate pump: 1")
            print("activate fan: 2")

            turn = input("turn on/off(1/0): ")
            commandType = input("command type: ")
            if commandType == "1":
                command = {
                    "CommandType": "ActivePump",
                    "Parameter": {
                        "Pump_1": int(turn)
                    }
                }
                break

            elif commandType == "2":
                command = {
                    "CommandType": "ActiveFan",
                    "Parameter": {
                        "Fan": int(turn)
                    }
                }
                break
            else:
                print("Wrong command type, please choose again")

        activation_description = {
            "Header": {
                "DescriptionType": "ActivationDescription",
                "User": self.username
            },
            "Body": command
        }


        rule_description = {
            "Header": {
                "DescriptionType": "RuleDescription",
                "OperationType": operationType,
                "User": self.username
            },
            "Body": {
                "rule": {
                    "Condition": condition,
                    "Action": activation_description
                }
            }
        }

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        response = requests.post(f"{self.base_url}/AutomationRule", json=rule_description, headers=headers)
        print("Status Code:", response.status_code)
        print("Response JSON:", response.json())

    async def _run_websocket_with_logger(self):
        _ws_task = asyncio.create_task(self.websocket_connection())
        self.tasks.append(_ws_task)
        _process_task = asyncio.create_task(self.process_data_queue())
        self.tasks.append(_process_task)

    async def websocket_connection(self):
        uri = f"ws://localhost:8000/ws/data?token={self.token}"
        try:
            async with websockets.connect(uri) as websocket:
                print("[Client] Connected to WebSocket")
                while self.isRunning:
                    try:
                        message = await websocket.recv()
                        self.DataQueue.put(message)

                    except websockets.exceptions.ConnectionClosed:
                        print("[Client] Server closed connection")
                        break
                    except Exception as e:
                        print("[Client] Error receiving data:", e)
                        break
        except Exception as e:
            print("[Client] Failed to connect:", e)

    async def process_data_queue(self):
        while self.isRunning:
            if not self.DataQueue.empty():
                raw_msg = self.DataQueue.get()
                try:
                    msg = json.loads(raw_msg)
                    msg_type = msg.get("type")

                    if msg_type == "initial":
                        await self._log_historical_data(msg.get("old_data", []))

                    elif msg_type == "update":
                        await self._log_current_data(msg.get("new_data", []))

                except json.JSONDecodeError:
                    print("[Logger] Received invalid JSON")
            else:
                await asyncio.sleep(1)

    async def _log_historical_data(self, data_list):
        with open("SensorDataLogging/HistoricalData.txt", "a", encoding="utf-8") as file:
            for entry in data_list:
                ts = entry.get("timestamp", "Unknown")
                payload = entry.get("data_payload")
                if payload:
                    try:
                        parsed = json.loads(payload)
                        line = f"[{ts}] {json.dumps(parsed)}\n"
                        file.write(line)
                    except json.JSONDecodeError:
                        file.write(f"[{ts}] <Invalid JSON>\n")

    async def _log_current_data(self, data_list):
        if not data_list:
            return

        try:
            # Save the latest entry to CurrentData.txt
            latest_entry = data_list[-1]
            timestamp = latest_entry.get("timestamp", datetime.now().isoformat())
            payload = latest_entry.get("data_payload")

            if payload:
                try:
                    parsed = json.loads(payload)
                    current_line = f"[{timestamp}] {json.dumps(parsed)}\n"
                except json.JSONDecodeError:
                    current_line = f"[{timestamp}] <Invalid JSON>\n"

                with open("SensorDataLogging/CurrentData.txt", "w", encoding="utf-8") as current_file:
                    current_file.write(current_line)

            # Append all entries to HistoricalData.txt
            with open("SensorDataLogging/HistoricalData.txt", "a", encoding="utf-8") as hist_file:
                for entry in data_list:
                    ts = entry.get("timestamp", "Unknown")
                    payload = entry.get("data_payload")
                    if payload:
                        try:
                            parsed = json.loads(payload)
                            hist_file.write(f"[{ts}] {json.dumps(parsed)}\n")
                        except json.JSONDecodeError:
                            hist_file.write(f"[{ts}] <Invalid JSON>\n")

        except Exception as e:
            print(f"[Logger] Error processing new_data: {e}")


# Entry point
if __name__ == "__main__":
    #username = alice, pass = pass123
    app = ConsoleApp()
    asyncio.run(app.run())
