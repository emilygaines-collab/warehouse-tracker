import asyncio
import threading
import sqlite3
import os

from bleak import BleakScanner
from flask import Flask, jsonify, request
from flask_cors import CORS

# -----------------------------
# FLASK SETUP
# -----------------------------
app = Flask(__name__)
CORS(app)

print("LOADING NEW SERVER")
print("RUNNING FILE:", os.path.abspath(__file__))

# -----------------------------
# DATABASE
# -----------------------------
def get_db():
    return sqlite3.connect("warehouse.db")

# -----------------------------
# IN-MEMORY EMPLOYEE DATA
# -----------------------------
employees = {
    "Emily": {"rssi": None},
    "Candace": {"rssi": None},
    "Madeline": {"rssi": None}
}

# -----------------------------
# BLE SCANNER
# -----------------------------
async def scanner():
    while True:
        devices = await BleakScanner.discover(timeout=2, return_adv=True)

        for address, (device, advertisement) in devices.items():

            if not device.name:
                continue

            if device.name == "Em":
                employees["Emily"]["rssi"] = advertisement.rssi
                print("Emily:", advertisement.rssi)

            elif device.name == "Madeline":
                employees["Madeline"]["rssi"] = advertisement.rssi
                print("Madeline:", advertisement.rssi)

            elif device.name == "This Device":
                employees["Candace"]["rssi"] = advertisement.rssi
                print("Candace:", advertisement.rssi)

        await asyncio.sleep(10)

def run_scanner():
    asyncio.run(scanner())

# start BLE thread
threading.Thread(target=run_scanner, daemon=True).start()

# -----------------------------
# ROUTES
# -----------------------------
@app.route("/location")
def location():
    print("API returning:", employees)
    return jsonify(employees)

@app.route("/assign_tag", methods=["POST"])
def assign_tag():
    data = request.json

    employee_name = data["employee_name"]
    tag_id = data["tag_id"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO employees (employee_name, tag_id)
        VALUES (?, ?)
    """, (employee_name, tag_id))

    conn.commit()
    conn.close()

    return jsonify({"success": True})

# -----------------------------
# START SERVER
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)