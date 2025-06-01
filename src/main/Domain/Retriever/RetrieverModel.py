import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState
from datetime import datetime
from .MQTTManagerModel import MQTTManager
from Infrastructure import ProcedureCall
from Infrastructure.Logging import write_log
class Retriever:
    def __init__(self, userName, DeviceInfo):
        self.userName = userName
        self.DeviceInfo = DeviceInfo #ACCESS NAME
        self.mqttManager = MQTTManager("mqtt.ohstem.vn", 1883, self.DeviceInfo, "")

    async def StopConsumeData(self):
        self.mqttManager.disconnect()

    async def startPublishData(self, webSocket: WebSocket):
        last_seen = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Start from now
        history_sent = False
        try:
            old_data = ProcedureCall.RetrieveHistoricalSensorData(self.userName, last_seen)
            while True:
                try:
                    new_data = ProcedureCall.RetrieveNewSensorData(self.userName, last_seen)

                    # Send only once
                    if not history_sent:
                        await webSocket.send_json({
                            "type": "initial",
                            "old_data": old_data,
                            "new_data": new_data
                        })
                        history_sent = True

                    else:
                        await webSocket.send_json({
                            "type": "update",
                            "new_data": new_data
                        })

                    if new_data:
                        if not isinstance(new_data, list):
                            write_log(f"[ERROR] new_data is not a list! Received: {type(new_data)}")
                            break

                        if isinstance(new_data, list) and new_data:
                            last_seen = new_data[-1]["timestamp"].replace("T", " ")
                    else:
                        last_seen = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    await asyncio.sleep(1)

                except WebSocketDisconnect:
                    write_log(f"WebSocket disconnected: {self.userName}")
                    break


        except Exception as e:
            write_log(f"WebSocket error: {e}")


        finally:

            try:

                if webSocket.application_state != WebSocketState.DISCONNECTED:
                    await webSocket.close()

                write_log(f"[CLOSE] WebSocket cleanly closed for {self.userName}")

            except RuntimeError as e:

                write_log(f"[CLOSE ERROR] Double close attempt: {e}")




