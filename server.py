import asyncio
from bleak import BleakScanner
from flask import Flask, jsonify
import threading

from flask_cors import CORS


print("LOADING NEW SERVER")
import os
print("RUNNING FILE:", os.path.abspath(__file__))

app = Flask(__name__)
CORS(app)


employee = {
    "name": "Emily",
    "rssi": None
}

async def scanner():
    while True:
        devices = await BleakScanner.discover(
            timeout=2,
            return_adv=True
        )

        for address, (device, advertisement) in devices.items():

            if device.name and device.name == "Em":
                employee["rssi"] = advertisement.rssi
                print(
                    "FOUND EM:",
                    advertisement.rssi
                )

        await asyncio.sleep(10)

@app.route("/location")
def location():
    print("API returning:", employee)
    return jsonify(employee)

def run_scanner():
    asyncio.run(scanner())


threading.Thread(target=run_scanner, daemon=True).start()

app.run(host="0.0.0.0", port=5000)

