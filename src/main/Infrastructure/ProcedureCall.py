from fastapi.responses import JSONResponse
from datetime import datetime
import mysql.connector, json
from .Logging import write_log
# Connect to the database
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="061104",
        database="SmartFarmDB",
        autocommit=True
    )

def Fetch_users():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.callproc('FetchUser')
    for result in cur.stored_results():
        rows = result.fetchall()
        cur.close()
        return rows


def FindUser(username, email):
    conn = get_connection()
    try:
        cur = conn.cursor()

        # Prepare arguments (last is placeholder for OUT param)
        args = [username, email, 0]

        # Call procedure
        result_args = cur.callproc('CheckUserExistence', args)

        # OUT param is updated in result_args[2]
        count = result_args[2]

        cur.close()
        return count, None

    except Exception as e:
        conn.rollback()
        write_log(f"[ERROR] FindUser failed: {e}")
        return None, {"error": f"An error occurred: {str(e)}"}



def RegistUser(username, password, email, device_name):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.callproc('Registration', [username, password, email, device_name])
        conn.commit()
        cur.close()
        return JSONResponse(
                        status_code=201,
                        content={"message": "User registered successfully"}
                    )
    except Exception as e:
        conn.rollback()
        return JSONResponse(
                        status_code=500,
                        content={"error": f"Registration failed: {str(e)}"}
                    )



def AddAutomationRule(DeviceName, RuleDescription: dict):
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)

        # Step 1: Fetch existing rule
        cur.callproc('RetrieveAutomationRule', [DeviceName])
        for result in cur.stored_results():
            rows = result.fetchall()
            if rows and rows[0]['AutomationRule']:
                rule_json = json.loads(rows[0]['AutomationRule'])
                if not rule_json:
                    UpdataAutomationRule(DeviceName, RuleDescription)
                    return JSONResponse(
                        status_code=201,
                        content={"message": "Add automation rule successfully"}
                    )
            else:
                UpdataAutomationRule(DeviceName, RuleDescription)
                return JSONResponse(
                        status_code=201,
                        content={"message": "Add automation rule successfully"}
                    )

        # Step 2: Merge new rules
        existing_rules = rule_json.get("Body", {})
        count = len(existing_rules) + 1
        for _, rule_content in RuleDescription.get("Body", {}).items():
            rule_json["Body"][f"rule{count}"] = rule_content
            count += 1

        # Step 3: Update automation rule
        UpdataAutomationRule(DeviceName, rule_json)
        return JSONResponse(
                        status_code=201,
                        content={"message": "Add automation rule successfully"}
                    )

    except Exception as e:
        conn.rollback()
        return JSONResponse(
                        status_code=500,
                        content={"error": f"Add automation rule failed: {str(e)}"}
                    )

def UpdataAutomationRule(DeviceName, RuleDescription: dict):
    conn = get_connection()
    try:
        cur = conn.cursor()
        rule_json = json.dumps(RuleDescription)
        cur.callproc('UpdateAutomationRule', [DeviceName, rule_json])
        conn.commit()
        cur.close()
        return JSONResponse(
                        status_code=201,
                        content={"message": "Update automation rule successfully"}
                    )
    except Exception as e:
        conn.rollback()
        return JSONResponse(
                        status_code=500,
                        content={"error": f"Update automation rule failed: {str(e)}"}
                    )

def InsertSensorData(DeviceName, payload):
    conn = get_connection()
    try:
        cur = conn.cursor()
        data = json.dumps(payload)
        cur.callproc('insertSensorData', [DeviceName, data])
        conn.commit()
        cur.close()
        return JSONResponse(
                        status_code=201,
                        content={"message": "Insert successful"}
                    )
    except Exception as e:
        conn.rollback()
        return JSONResponse(
                        status_code=500,
                        content={"error": f"Insertion failed: {str(e)}"}
                    )

def RetrieveNewSensorData(UserName, LastSeen):
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.callproc('RetrieveNewSensorData', [UserName, LastSeen])
        for result in cur.stored_results():
            data = result.fetchall()
            if not data:
                return []  # ✅ Always return a list

            for row in data:
                if isinstance(row.get("timestamp"), datetime):
                    row["timestamp"] = row["timestamp"].isoformat()
            return data
    except Exception as e:
        write_log(f"[ERROR] RetrieveNewSensorData failed: {e}")
        return []

def RetrieveHistoricalSensorData(UserName, LastSeen):
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.callproc('RetrieveHistoricalSensorData', [UserName, LastSeen])
        for result in cur.stored_results():
            data = result.fetchall()
            if not data:
                return [{}]

            for row in data:
                if isinstance(row.get("timestamp"), datetime):
                    row["timestamp"] = row["timestamp"].isoformat()
            return data
    except Exception as e:
        write_log(f"[ERROR] RetrieveHistoricalSensorData failed: {e}")
        return []

def RetrieveLatestSensorData(DeviceName):
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.callproc('RetrieveLatestSensorData', [DeviceName])
        for result in cur.stored_results():
            data = result.fetchall()
            return data if data else []  # always return a list
    except Exception as e:
        return []

