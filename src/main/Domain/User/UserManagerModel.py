from .UserModel import User
from Infrastructure.Fair_lock import FairLock
from Infrastructure import ProcedureCall
import json
from fastapi.responses import JSONResponse

class UserManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(UserManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.store = self.Fetch_Users()
        self.lock = FairLock()
        self._initialized = True



    def set(self, UserDescription: dict):
        with self.lock:
            # Extract the user details
            username = UserDescription["UserName"]
            password = UserDescription["PassWord"]
            email = UserDescription["Email"]
            device_name = UserDescription["DeviceName"]


            # Validation
            if not username or not email or not password or not device_name:
                return JSONResponse({"error": "Missing required fields"}, 400)

            # check if user have existed
            count, err = ProcedureCall.FindUser(username, email)
            if count is None:
                return err

            if count > 0:
                return JSONResponse({"error": "Username or Email already exists"}, 400)

            user = User(username, password, email, device_name, {})
            self.store[UserDescription["UserName"]] = user

            # Call the stored procedure to insert data into Users and Devices table
            return ProcedureCall.RegistUser(username, password, email, device_name)



    def get(self, userName: str):
        with self.lock:
            item = self.store.get(userName)
            if item:
                return item
            else:
                print(f"Key not found: {userName}")
                return None



    def Authenticate(self, username, password):
        with self.lock:
            user = self.store.get(username)
            if user:
                if user.passWord == password:
                    return [user.userName, user.passWord]
            else:
                return []



    def Fetch_Users(self):
        rows = ProcedureCall.Fetch_users()
        users = {}
        for row in rows:
            user = User(row["username"], row["password"], row["email"], row["device_Name"], json.loads(row["AutomationRule"]))
            users.update({user.userName: user})
        return users