from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from Application.SystemModel import System
import uvicorn, jwt

system = System()
app = FastAPI()

@app.post("/login")
async def login(request: Request):
    result = system.Login(request)
    if isinstance(result, tuple):  # (message, status_code)
        return JSONResponse(content={"message": result[0]}, status_code=result[1])
    return result
@app.post("/registration")
async def registration(request: Request):
    UserDescription = await request.json()
    return system.Registration(UserDescription)

@app.post("/AutomationRule")
async def set_rule(request: Request):
    RuleDescription = await request.json()
    return system.SetRule(request, RuleDescription)

@app.post("/activateDevice")
async def activate_device(request: Request):
    ActivationDescription = await request.json()
    return system.ManualActivation(request, ActivationDescription)


@app.websocket("/ws/data")
async def websocket_data(websocket: WebSocket):
    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=1008)  # Policy Violation
        return

    try:
        payload = jwt.decode(token, "secret", algorithms=["HS256"])
        username = payload.get("username")  # Optional: extract username
        user = system.userManager.get(username)
        await websocket.accept()
        await user.retriever.startPublishData(websocket)

    except jwt.ExpiredSignatureError:
        await websocket.close(code=4001)
    except jwt.InvalidTokenError:
        await websocket.close(code=4002)
    except WebSocketDisconnect:
        print("Client disconnected.")


if __name__ == "__main__":
    uvicorn.run("RestApi:app", host="127.0.0.1", port=8000, reload=True)