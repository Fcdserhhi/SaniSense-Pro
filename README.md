## SaniSense: Smart Restroom Ecosystem

## Problem  

Public restrooms frequently suffer from poor hygiene maintenance, delayed cleaning response, overcrowding, and lack of real-time monitoring. Existing systems rely heavily on manual inspection, making it difficult to ensure cleanliness, hygiene compliance, consumable availability, and timely maintenance.

There is a need for an intelligent, low-cost, real-time restroom monitoring system that can automatically track occupancy, odor levels, hygiene conditions, cleaning activities, and maintenance requirements to improve sanitation standards, resource management, and user safety in public facilities.
 
## Solution 

The proposed solution is a **Smart Autonomous Restroom Monitoring System** built using ESP32 and IoT sensors. The system monitors restroom occupancy, odor levels, hygiene conditions, wash basin usage, consumable stock availability, and maintenance requirements in real time.

It uses sensors to detect restroom usage patterns, identify poor hygiene conditions, verify cleaning activities through water usage monitoring, and generate SOS or maintenance alerts when required. A live web dashboard provides real-time analytics and restroom status updates, enabling efficient sanitation management, faster maintenance response, and improved public hygiene standards.

## Hardware Required

| Component | Purpose |
|---|---|
| ESP32-WROOM | Main controller |
| VL53L0X Sensor | Stall occupancy detection |
| MQ135 Gas Sensor | Air quality monitoring |
| IR Sensor 1 | Entry detection |
| IR Sensor 2 | Exit detection |
| IR Sensor 3 | Basin approach detection |
| IR Sensor 4 | Consumable stock detection (soap, sanitizer, pads, dispenser items) |
| Water Sensor | Cleaning verification |
| Active Buzzer | Alerts (SOS, cleaning, restock) |
| Green LED | Vacant indicator |
| Red LED | Occupied indicator |
| Yellow LED | Warning indicator |
| Button-1 (SOS) | Emergency alert |
| Button-2 (Cleaning) | Trigger cleaning mode |
| Button-3 (Maintenance) | Trigger maintenance mode |
| Resistor 220Ω | Limit current flow to LED |
| Breadboards | Connection & power rail |

## Software Required

| Software | Purpose |
|---|---|
| Thonny IDE | Upload and run MicroPython code |
| MicroPython Firmware | Run MicroPython on ESP32-WROOM |

## Installation Steps
1. Flash MicroPython to ESP32-WROOM
2. Install required libraries
3. Upload `main.py` and `vl53l0x.py`
4. Connect sensors as per circuit diagram
5. Power ON ESP32-WROOM
6. Connect to WiFi AP:
   SSID: SmartRestroom
   Password: 12345678
7. Open browser:
   `192.168.4.1`

## Run
The dashboard starts automatically after boot.

## Circuit Diagram 

![SaniSense Circuit Diagram](circuit_image.png)

## Technical Breakdown 
1. Precise Occupancy (VL53L0X ToF)
Instead of standard PIR motion sensors—which fail if a person remains stationary—we used the VL53L0X Time-of-Flight (ToF) sensor. It uses laser ranging to measure exact distance, providing a 100% privacy-compliant way to detect if a stall is occupied.

2. Traffic Tracking (Dual IR Array)
We implemented a dual IR sensor setup at the entrance. By coding a specific trigger sequence, the system detects the direction of movement (entry vs. exit) to maintain a live "People Inside" count.

3. Hygiene Analytics (MQ135 & Algorithm)
We used an MQ135 sensor to monitor odor and air quality. The team developed a weighted algorithm that calculates a Hygiene Score. If odors are high or foot traffic exceeds a set limit, the system automatically flags the room for cleaning.

4. The Verification Loop (Water Sensor)
To ensure staff accountability, we added a Water Level Sensor. When the "Clean" button is pressed, the system captures a moisture baseline. The Hygiene Score only resets if the sensor detects actual water usage, proving that cleaning took place.

## Demo Video
[Watch Demo Video](https://drive.google.com/file/d/1qPsSYXlXrMULDD0MsDplftLNKpUN2_ml/view?usp=drivesdk)

## Dashboard 

![SaniSense Dashboard](dashboard.jpeg)

The team developed a custom web interface hosted directly on the ESP32-WROOM. It is a mobile-responsive dashboard with a 1-second refresh rate for:
1. Occupancy Status: Stalls and Basins.
2. Environmental Health: Live Odor/Air Quality readings.
3. Inventory Alerts: Soap and Dispenser levels.
4. Notifications: Emergency SOS and Maintenance requests.
