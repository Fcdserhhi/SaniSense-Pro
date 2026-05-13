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
| IR Sensor-1 | Entry detection |
| IR Sensor-2 | Exit detection |
| IR Sensor-3 | Basin approach detection |
| IR Sensor-4 | Consumable stock detection (soap, sanitizer, pads, dispenser items) |
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
| Jumper Wires | Connecting components |

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

## Features

* **Real-Time Occupancy Monitoring**
  Uses IR sensors and VL53L0X distance sensor to detect restroom usage, stall occupancy, and approximate user count in real time.

* **Odor & Hygiene Monitoring**
  MQ135 gas sensor continuously monitors odor levels inside the restroom to estimate hygiene conditions and detect poor sanitation.

* **Hygiene Compliance Tracking**
  Basin-area IR sensing helps determine whether users approached the wash basin after restroom usage, enabling basic handwash compliance estimation.

* **Smart Cleaning Requirement Detection**
  The system intelligently decides when cleaning is required based on restroom usage count, hygiene score, odor level, and sanitation conditions.

* **Dedicated Cleaning Mode**
  A cleaning mode button allows cleaning staff to temporarily pause restroom operation during maintenance and sanitation procedures. The system enters maintenance state and resumes normal monitoring after cleaning verification.

* **Cleaning Verification System**
  Water usage monitoring and odor comparison are used to verify whether cleaning staff actually performed sanitation procedures properly before reopening the restroom.

* **Consumable Stock Monitoring**
  IR-based dispenser monitoring detects low availability of consumables such as soap, tissue paper, sanitary products, or liquid dispensers.

* **Maintenance Request System**
  Dedicated maintenance button allows users or staff to report issues such as clogging, leakage, or restroom malfunction instantly.

* **SOS Emergency Assistance**
  Emergency SOS button can be used by users to request immediate assistance during medical or safety emergencies.

* **Live IoT Dashboard**
  A real-time web dashboard displays occupancy status, hygiene score, odor readings, water usage, stock availability, maintenance status, and cleaning alerts.

* **Visual & Audio Alerts**
  LEDs and buzzer provide instant local alerts for restroom occupancy, cleaning requirements, maintenance requests, and emergency situations.

* **Adaptive Hygiene Scoring**
  The system dynamically updates hygiene score based on restroom usage patterns, odor conditions, basin usage, and cleaning verification results.

* **Low-Cost Smart Infrastructure Solution**
  Designed using ESP32 and affordable sensors, making it suitable for smart city deployments, public facilities, schools, hospitals, malls, and transportation hubs.
  
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
