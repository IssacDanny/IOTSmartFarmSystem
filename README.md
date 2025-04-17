to run the program
1. change directory to SmartFarm backEnd\src\main
2. run python ResApi.py

to test, open another terminal and type:
authentication: curl.exe -X POST http://127.0.0.1:5000/login -u <userName>:<passWord> (Read the database for inserted data)
registration: curl.exe -X POST http://127.0.0.1:5000/registration -H "Content-Type: application/json" -d "{\"username\":\"<UserName>\", \"email\":\"<Email>\", \"password\":\"<Password>\", \"device_name\":\"<DeviceName>\"}"


