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

