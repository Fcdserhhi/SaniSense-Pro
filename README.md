# SaniSense: Smart Restroom Ecosystem

## Problem

Most restrooms are cleaned on a fixed schedule (e.g., every 3 hours), which is inefficient. This model does not account for heavy foot traffic or sudden hygiene drops. It leads to wasted resources when bathrooms are already clean and poor conditions when they are overcrowded.

---

## Solution

SaniSense transforms traditional scheduled cleaning into an intelligent on-demand maintenance system.

Using an ESP32-WROOM and multiple sensors, the system continuously monitors:
- Occupancy
- Foot traffic
- Air quality
- Cleaning verification
- Emergency alerts

This enables maintenance staff to respond only when required, improving hygiene standards while reducing unnecessary cleaning cycles.

---

## Hardware Required

| Component | Purpose |
|---|---|
| ESP32-WROOM | Main controller |
| VL53L0X Sensor | Stall occupancy detection |
| MQ135 Gas Sensor | Air quality monitoring |
| IR Sensor 1 | Entry detection |
| IR Sensor 2 | Exit detection |
| IR Sensor 3 | Basin approach detection |
| IR Sensor 4 | Dispenser stock detection |
| Water Sensor | Cleaning verification |
| Active Buzzer | Alerts (SOS, cleaning, restock) |
| Green LED | Vacant indicator |
| Red LED | Occupied indicator |
| Yellow LED | Warning indicator |
| SOS Button | Emergency alert |
| Cleaning Button | Trigger cleaning mode |
| Maintenance Button | Trigger maintenance mode |

---

## Software Required

| Software | Purpose |
|---|---|
| Thonny IDE | Upload and run MicroPython code |
| MicroPython Firmware | Run Python on ESP32-WROOM |

---

## Installation Steps

1. Flash MicroPython firmware to ESP32-WROOM
2. Install the required libraries
3. Upload `main.py` and `vl53l0x.py`
4. Connect all sensors according to the circuit diagram
5. Power ON the ESP32-WROOM
6. Connect to the WiFi Access Point:

```text
SSID: SmartRestroom
Password: 12345678
