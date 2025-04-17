from flask import jsonify
import mysql.connector

# Connect to the database
connection = mysql.connector.connect(
    host="localhost",        # MySQL host (localhost for local)
    user="root",    # MySQL username
    password="061104", # MySQL password
    database="SmartFarmDB" # Name of your database
)

cur = connection.cursor()
def Authenticate(username, password):
    return cur.callproc('Authenticate', [username, password])

def FindUser(username, email):
    try:
        # Declare an output variable for the user count
        cur.execute("SET @user_count = 0;")

        # Call the procedure to check if the user exists
        cur.callproc('CheckUserExistence', [username, email, '@user_count'])

        # Retrieve the result (user count)
        cur.execute("SELECT @user_count;")
        result = cur.fetchone()
        return result[0], None


    except Exception as e:
        # Rollback in case of error
        connection.rollback()
        return None, jsonify({"error": f"An error occurred: {str(e)}"}), 500

def RegistUser(username, password, email, device_name):
    # Call the stored procedure to insert data into Users and Devices table
    cur.callproc('Registration', [username, password, email, device_name])

    # Commit the transaction
    connection.commit()

    return jsonify({"message": "User registered successfully"}), 201

def InsertSensorData(DeviceName, payload):
    return cur.callproc('insertSensorData', [DeviceName, payload])

def RetrieveSensorData(UserName):
    # Call the stored procedure to insert data into Users and Devices table
    cur.callproc('retrieveDeviceDataByUserName', [UserName])
    for result in cur.stored_results():
        return result.fetchall()  #retrieve the data_payload


