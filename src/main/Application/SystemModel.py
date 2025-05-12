import time, base64
from . import authBusiness
from fastapi.responses import JSONResponse
from Domain.User.UserManagerModel import UserManager
from Domain.Automation.AutomizerManagerModel import Automizer_Manager
from Domain.Controller.ControllerManagerModel import Controller_Manager
from Domain.Retriever.RetrieverManagerModel import RetrieverManager


class System:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(System, cls).__new__(cls)
            cls._instance.userManager = UserManager()
            cls._instance.automizerManager = Automizer_Manager()
            cls._instance.controllerManager = Controller_Manager()
            cls._instance.retrieverManager = RetrieverManager()

        return cls._instance

    def Login(self, request):
        auth_header = request.headers.get("authorization")

        if not auth_header or not auth_header.startswith("Basic "):
            return JSONResponse(
                        status_code=401,
                        content={"error": "Missing credentials"}
                    )

        # Decode the Base64 encoded credentials
        encoded_credentials = auth_header.split(" ")[1]
        decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")

        username, password = decoded_credentials.split(":", 1)

        result = self.userManager.Authenticate(username, password)

        if result:
            user_name = result[0]
            password_db = result[1]

            if username != user_name or password != password_db:
                return JSONResponse(
                        status_code=401,
                        content={"error": "Invalid credentials"}
                    )
            else:
                return JSONResponse(
                    status_code=200,
                    content={"Token": f"{authBusiness.createJWT(username, 'secret', True)}"}
                )
        else:
            return JSONResponse(
                        status_code=401,
                        content={"error": "Invalid credentials"}
                    )

    def Registration(self, UserDescription):
        # Register user
        return self.userManager.set(UserDescription)

    def SetRule(self, request, RuleDescription):
        # check authorization before perform task
        authorized, err = authBusiness.validate(request)
        if err:
            return err

        # set rule
        return self.automizerManager.submit_request(RuleDescription)

    def ManualActivation(self, request, ActivationDescription):
        # check authorization before perform task
        authorized, err = authBusiness.validate(request)
        if err:
            return err

        # Activate Device
        return self.controllerManager.submit_request(ActivationDescription)

    def stop(self):
        time.sleep(10)
        self.controllerManager.stop()


