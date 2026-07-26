<div align="center">

# YUGĒN
### Autonomous Intelligent Surveillance Platform

**Edge AI • Robotics • Computer Vision • IoT**

<img src="assets/rover_front.jpg" width="400" alt="Minimal Rover Illustration">

</div>

---

## 📖 Vision

Modern surveillance systems are often fixed, expensive, and unable to adapt to changing environments. Yugēn explores a mobile, AI-enabled approach by combining robotics, edge computing, and computer vision into a modular surveillance platform. 

**Yugēn — A Modular Edge AI Robotics Platform for Autonomous Surveillance**

---

## ❓ Why Yugēn?
Traditional security cameras are limited by their field of view. Blind spots are inevitable, and dynamic situations require flexible monitoring solutions that fixed cameras cannot provide. Yugēn provides an autonomous, omnidirectional rover equipped with real-time computer vision to patrol, detect events, and adapt to its environment autonomously.

---

## 🚀 Features

### Vision
* **Live Stream**: Real-time MJPEG/JPEG streaming from ESP32-CAM.
* **Object Detection**: YOLOv8-powered person and vehicle tracking.
* **Face Recognition**: Integrated `dlib` facial matching for known entities.

### Navigation
* **Remote Control**: Instant manual control via low-latency WebSocket.
* **Obstacle Avoidance**: Future integration of depth sensing.
* **Speed Control**: Dynamic PWM motor adjustment.

### Connectivity
* **Wi-Fi**: Wireless telemetry and streaming.
* **Web Dashboard**: Centralized Python/OpenCV control center.
* **OTA Updates**: Ready for over-the-air firmware upgrades.

### Intelligence
* **YOLO Detection**: Multi-threaded AI inference without dropping frame rates.
* **Motion Detection**: Frame-by-frame analysis for anomaly detection.
* **AI Alerts**: Automated video evidence capture and logging.

---

## 🏗️ System Architecture

```text
            Dashboard
                 │
        WiFi / WebSocket
                 │
────────────────────────────────
        Communication Layer
────────────────────────────────
                 │
      ESP32 Main Controller
                 │
 ┌─────────┬─────────┬─────────┐
 │         │         │         │
Vision  Navigation Telemetry Motors
 │         │         │         │
Camera Ultrasonic  Logs     PWM
```

---

## ⚙️ Hardware

### Wiring Diagram
```text
ESP32
  ↓
Camera & Serial Comms
  ↓
L298N Motor Drivers
  ↓
Left & Right Motors (Mecanum)
  ↓
Ultrasonic (Planned)
  ↓
Li-ion Power Distribution
```

<p align="center">
  <img src="assets/rover_front.jpg" width="45%" alt="Yugēn Rover Front View">
  <img src="assets/rover_side.jpg" width="45%" alt="Yugēn Rover Side View">
</p>

* **Microcontroller**: ESP32 / ESP32-CAM
* **Motor Drivers**: 2x L298N Dual H-Bridge
* **Actuators**: 4x DC Gear Motors with Mecanum Wheels
* **Power**: Custom Li-ion battery pack

---

## 💻 Software Stack
* **AI & Vision**: OpenCV, YOLOv8 (Ultralytics), `face_recognition` (dlib)
* **Backend**: Python, WebSockets, NumPy
* **Firmware**: C++ / Arduino Core (ESP32)

---

## 🎥 Demo
*(Link to `assets/demo.gif` or YouTube video showing the Yugēn dashboard and rover in action)*

---

## 🗺️ Roadmap

### Version 1
──────────
✔ Remote Control
✔ Camera
✔ Live Streaming
✔ AI Dashboard

### Version 2
──────────
✔ Object Detection
✔ Face Recognition
□ Automated Event Recording

### Version 3
──────────
□ Autonomous Patrol
□ Smart Alerts (Telegram/AWS)
□ Edge AI Optimization (Edge TPU)

### Version 4
──────────
□ SLAM Mapping
□ Multi-Robot Swarm Coordination
□ Autonomous Charging Dock

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
* **Cross-platform**: Runs on Windows, Linux, and macOS without recompilation.

---

## 🔬 Future Research
* **Edge AI acceleration**: Moving YOLO inference directly to the rover using dedicated VPUs.
* **Multi-camera coordination**: Data fusion from multiple Yugēn rovers in a swarm.
* **Autonomous patrol planning**: AI-driven route optimization based on historical anomaly data.
* **Sensor fusion**: Combining optical flow with IMU/LiDAR for robust odometry.
* **Low-power optimization**: Sleep states and wake-on-motion for extended patrols.

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
