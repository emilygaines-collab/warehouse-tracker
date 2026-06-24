import asyncio
import threading
from bleak import BleakScanner
from flask import Flask, jsonify, request
from flask_cors import CORS

# -----------------------------
# FLASK SETUP
# -----------------------------
app = Flask(__name__)
CORS(app)

# -----------------------------
# IN-MEMORY DATA (NO DB)
# -----------------------------
employees = {
    "Emily": {"rssi": None, "tag_id": None},
    "Candace": {"rssi": None, "tag_id": None},
    "Madeline": {"rssi": None, "tag_id": None}
}

# -----------------------------
# BLE SCANNER (DEMO SAFE)
# -----------------------------
async def scanner():
    while True:
        devices = await BleakScanner.discover(timeout=3, return_adv=True)

        for address, (device, advertisement) in devices.items():

            name = device.name or advertisement.local_name or "Unknown"

            print(f"Found: {name} | {address} | RSSI: {advertisement.rssi}")

            if "Em" in name:
                employees["Emily"]["rssi"] = advertisement.rssi
                print("Emily updated")

            elif "Madeline" in name:
                employees["Madeline"]["rssi"] = advertisement.rssi
                print("Madeline updated")

            elif "Candace" in name:
                employees["Candace"]["rssi"] = advertisement.rssi
                print("Candace updated")

        await asyncio.sleep(5)

def run_scanner():
    asyncio.run(scanner())

# start BLE thread
threading.Thread(target=run_scanner, daemon=True).start()

# -----------------------------
# ROUTES
# -----------------------------
@app.route("/location")
def location():
    return jsonify(employees)

@app.route("/assign_tag", methods=["POST"])
def assign_tag():
    data = request.json

    employee_name = data["employee_name"]
    tag_id = data["tag_id"]

    if employee_name in employees:
        employees[employee_name]["tag_id"] = tag_id
    else:
        employees[employee_name] = {"rssi": None, "tag_id": tag_id}

    print("Assigned tag:", employee_name, tag_id)

    return jsonify({"success": True})

# -----------------------------
# START SERVER
# -----------------------------
if __name__ == "__main__":
    print("Starting BLE Flask server...")
    app.run(host="0.0.0.0", port=5000, debug=True)