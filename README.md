<div align="center">

# YUGĒN
### Autonomous Intelligent Surveillance Platform

**Edge AI • Robotics • Computer Vision • IoT**

<img src="media/hero.png" width="800" alt="Yugēn Hero Banner">

</div>

---

## 📖 Vision

Yugēn is a modular robotics research platform exploring edge AI, computer vision, and autonomous surveillance.

Instead of fixed security cameras with inevitable blind spots, Yugēn proposes a mobile, AI-enabled approach by combining robotics, edge computing, and real-time vision into a flexible platform.

---

## 📊 Repository Status

| Module | Status |
| :--- | :--- |
| 🟢 Hardware Prototype | Completed |
| 🟢 Manual Control | Completed |
| 🟢 AI Dashboard | Completed |
| 🟢 Camera Streaming | Completed |
| 🟡 AI Optimization | In Progress |
| 🟡 Autonomous Patrol | In Progress |
| ⚪ SLAM Mapping | Planned |
| ⚪ Multi-Robot Swarm | Planned |

---

## 🚀 Capabilities

### ✅ Current Capabilities
* **Live Camera Streaming**: Real-time MJPEG/JPEG streaming from ESP32-CAM.
* **Web Dashboard**: Centralized Python/OpenCV control center.
* **Manual Control**: Low-latency WebSocket integration for remote piloting.
* **YOLO Detection**: YOLOv8-powered person and vehicle tracking.
* **Face Recognition**: Integrated `dlib` facial matching for known entities.

### 🚧 Planned Features
* **Obstacle Avoidance**: Integration of depth/ultrasonic sensing.
* **Autonomous Patrol**: Point-to-point route planning.
* **SLAM**: Simultaneous Localization and Mapping.
* **Multi-Robot Coordination**: Swarm logic for distributed surveillance.

---

## 🏗️ System Architecture

```text
              Web Dashboard
                     │
             WebSocket / HTTP
                     │
          ┌───────────────────┐
          │      ESP32        │
          └───────────────────┘
      ┌────────┬────────┬────────┐
      │        │        │        │
   Camera Motor Ctrl Sensors Telemetry
      │
 Video Stream
      │
AI Processing (Python)
      │
YOLO + Face Recognition
```

---

## 📸 Visual Gallery

<p align="center">
  <img src="media/rover_top.jpg" width="45%" alt="Rover Top View">
  <img src="media/rover_front.jpg" width="45%" alt="Rover Front View">
</p>
<p align="center">
  <img src="media/rover_side.jpg" width="45%" alt="Rover Side View">
  <img src="media/rover_angle.jpg" width="45%" alt="Rover Angle View">
</p>

<p align="center">
  <img src="media/dashboard.png" width="800" alt="Dashboard View">
</p>

---

## ⚙️ Hardware Specifications

| Component | Description |
| :--- | :--- |
| **Controller** | ESP32 DevKit |
| **Camera** | ESP32-CAM |
| **Motor Driver** | 2x L298N Dual H-Bridge |
| **Motors** | 4 × DC Gear Motors |
| **Wheels** | Mecanum |
| **Power** | Custom Li-ion Battery Pack |
| **Connectivity** | Wi-Fi (802.11 b/g/n) |

---

## 📈 System Metrics

| Property | Value |
| :--- | :--- |
| **Platform** | ESP32 |
| **AI Model** | YOLOv8 (Nano/Small) |
| **Programming** | C++, Python |
| **Vision** | OpenCV, dlib |
| **Communication**| WebSockets, Serial |
| **Control** | Wi-Fi |
| **Drive** | Omnidirectional (Mecanum) |
| **Status** | Research Prototype |

### Performance Estimates
| Metric | Value |
| :--- | :--- |
| **Camera FPS** | ~15-20 FPS |
| **Dashboard Latency** | ~100-150 ms |
| **Detection Speed** | ~10-15 FPS (Host PC dependent) |
| **Wi-Fi Range** | ~20–30 m |
| **Battery Runtime** | ~40-60 min |

---

## 🧠 Engineering Decisions

### Why ESP32?
* **Integrated Wi-Fi**: Essential for live video telemetry and remote commands.
* **Cost-effective**: Perfect for a scalable, multi-rover system.
* **Large ecosystem**: Robust libraries for motor PWM and WebSockets.

### Why YOLO?
* **Real-time inference**: Best balance of speed and accuracy for edge devices.
* **Widely adopted**: Excellent community support and pre-trained weights.
* **Good accuracy**: Reliable detection for humans and vehicles in varied lighting.

### Why Python Dashboard?
* **Rapid development**: Fast iteration for UI and backend logic.
* **AI integration**: Native support for OpenCV, PyTorch, and YOLO.
* **Cross-platform**: Runs on Windows, Linux, and macOS.

### Why Mecanum Wheels?
* **Omnidirectional movement**: Essential for complex maneuvering in tight spaces.
* **Better indoor navigation**: Allows strafing without rotating the chassis.
* **Easy lateral movement**: Suitable for tracking targets while maintaining camera lock.

---

## ⚠️ Current Limitations
Being transparent about the current state of the platform:
* **Manual navigation only**: Autonomous pathing is still in development.
* **Single camera**: Relies on a single fixed-angle ESP32-CAM.
* **Requires Wi-Fi**: Needs an active network to stream to the host processing PC.
* **No autonomous mapping**: SLAM is not yet implemented.
* **Limited battery runtime**: Heavy motor usage drains the battery quickly.

---

## 🗺️ Roadmap Timeline

```text
V1 (Current)
│
├── Manual Control
├── Camera Integration
├── Live Streaming
├── YOLO Dashboard
│
V2
│
├── Obstacle Avoidance
├── Automated Event Recording
├── Enhanced Telemetry
│
V3
│
├── Autonomous Patrol
├── Smart Alerts (AWS/Telegram)
├── Edge TPU Acceleration
│
V4
│
├── SLAM Mapping
├── Swarm Robotics
├── Docking & Autonomous Charging
```

---

## 🚀 Installation & Getting Started

1. **Firmware Deployment**: Flash `firmware/motor_control/esp32_car.ino` and `firmware/camera/esp32_camera_car.ino` to their respective ESP32 modules.
2. **AI Setup**: 
   ```bash
   pip install opencv-python ultralytics face_recognition websocket-client
   ```
3. **Run Dashboard**: 
   ```bash
   python dashboard/backend/ai_dashboard_pro.py
   ```

---

*Yugēn — Designed for the future of decentralized autonomous surveillance.*
