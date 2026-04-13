# aura-project
# 🚁 AURA — Autonomous Unified Rescue and Assessment System

AURA is a drone-based disaster response system designed to detect hazards, locate survivors, and assist rescue operations using real-time sensor data, RF communication, and autonomous navigation.

---

## ⚠️ Problem

Disaster response today is inefficient and risky:

- No real-time situational awareness  
- Rescue teams enter unknown hazardous zones  
- Survivors are often detected too late  
- Manual coordination slows everything down  

---

## 💡 Solution

AURA automates detection, assessment, and navigation using:

- Autonomous drone deployment  
- Real-time hazard detection (gas, temperature, obstacles)  
- GPS-based survivor tracking  
- RF-based communication system (no dependency on internet)  
- AI-assisted path planning (planned/expandable)  

---

## 🧠 System Architecture

### Hardware Components

- ESP32 – Main microcontroller  
- BME280 – Temperature, humidity, pressure  
- MQ2 Sensor – Gas detection  
- NEO-M8N GPS – Location tracking  
- IR Sensor – Obstacle / human detection  
- HC-12 RF Module – Long-range communication  
- Flight Controller (ArduPilot) – Drone control  

---

### Software Stack

- Arduino IDE (ESP32 firmware)
- Mission Planner (ArduPilot interface)
- Serial communication (UART)
- RF communication protocol (HC-12)
- Optional: Python bridge for telemetry

---

## 🔄 Data Flow

1. Sensors collect environmental + hazard data  
2. ESP32 processes and formats data  
3. Data transmitted via RF (HC-12)  
4. Ground station receives and visualizes data  
5. GPS enables survivor tracking + navigation  
6. Drone adjusts movement via ArduPilot  

---

## 📡 Communication System

- Fully based on RF (HC-12)  
- No Wi-Fi or external network required  
- Designed for disaster zones where infrastructure is down  

---

## 🧪 Features

- 🔥 Gas leak detection (MQ2)  
- 🌡️ Environmental monitoring (BME280)  
- 📍 GPS tracking (NEO-M8N)  
- 🚧 Obstacle detection (IR sensor)  
- 📡 Long-range RF communication  
- 🚁 Drone control via ArduPilot  
- 🧭 Planned: Survivor navigation system  

---

## 🚀 Future Improvements

- AI-based survivor detection (computer vision)  
- Autonomous path planning  
- Live mapping UI  
- Multi-drone coordination  
- Mobile app for rescue teams  

---

## 🛠️ Setup (High-Level)

### 1. Hardware Setup
- Connect sensors to ESP32  
- Connect HC-12 to UART  
- Integrate GPS module  
- Interface with flight controller  

### 2. Firmware
- Upload ESP32 code via Arduino IDE  
- Configure sensor libraries  
- Set up serial + RF communication  

### 3. Flight System
- Install and configure ArduPilot  
- Connect via Mission Planner  
- Set telemetry ports correctly  

### 4. Testing
- Verify sensor outputs  
- Check RF signal transmission  
- Validate GPS data  
- Test drone response  

---

## ⚡ Key Challenges

- Serial communication timeouts (ArduPilot issues)  
- RF signal reliability tuning  
- Sensor calibration (MQ2 is noisy)  
- Power management on drone  
- Integration between ESP32 and flight controller  

---

## 📌 Project Status

> ⚠️ Work in Progress  
Core hardware exists. Software integration and full system stability are ongoing.

---

## 🤝 Contribution

If contributing:

- Keep modules independent  
- Test before pushing changes  
- Document everything properly  

---


