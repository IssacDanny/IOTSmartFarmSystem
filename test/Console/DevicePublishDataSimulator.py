import asyncio
import json
import random
from datetime import datetime
import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="061104",
        database="SmartFarmDB",
        autocommit=True
    )


async def simulate_device_data(device_id: int, interval: float = 2.0, count: int = 10):
    for i in range(count):
        try:
            # Random simulated sensor data
            payload_sql = f"""
            INSERT INTO DeviceData (device_id, data_payload)
            VALUES (
                {device_id},
                JSON_OBJECT(
                    'Temperature', {random.randint(20, 35)},
                    'Humidity', {random.randint(40, 80)},
                    'Moisture', {random.randint(20, 50)},
                    'Lux', {random.randint(300, 1500)},
                    'GDD', {random.randint(100, 250)},
                    'Status', 1,
                    'Pump_1', {random.choice([0, 1])},
                    'Fan', {random.choice([0, 1])}
                )
            )
            """
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute(payload_sql)
                print(f"[SIM] Inserted row {i+1}/{count} for device_id={device_id}")
        except Exception as e:
            print(f"[SIM] Error on insert {i+1}: {e}")

        await asyncio.sleep(interval)

if __name__ == "__main__":
    asyncio.run(simulate_device_data(1))