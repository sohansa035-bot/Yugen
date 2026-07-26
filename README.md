# CarAI: Smart Car AI Surveillance System

A professional, real-time AI dashboard and surveillance system designed for a smart car equipped with an ESP32 Camera. This system integrates WebSocket video streaming, YOLOv8 object detection, and high-accuracy face recognition.

## Photos
*(Insert high-quality photos of the completed smart car, dashboard interface, and real-world testing here.)*
- `[Dashboard UI Screenshot]`
- `[Smart Car Front View]`
- `[Smart Car Side View]`

## PCB / Wiring
The hardware is built on a custom wooden chassis using a 4-wheel omnidirectional drive system.
- **Microcontroller**: ESP32-CAM module mounted on an expansion board for easy wiring and video streaming.
- **Chassis & Wheels**: Custom wooden base with 4x yellow Mecanum wheels for omnidirectional movement.
- **Power**: Custom yellow Li-ion battery pack providing power to both the motors and the microcontroller.
- **Motor Drivers**: Dual L298N motor drivers (red boards) controlling the 4 DC gear motors independently.

## ESP32 Code
The ESP32 acts as a WebSocket video server and motor controller.
- **Video Streaming**: Captures JPEG frames and streams them over a WebSocket (`ws://[ESP32_IP]/Camera`).
- **Control**: Receives commands from the dashboard for movement.
The source code is available in [esp32_camera_car.ino](esp32_camera_car.ino).

## AI Model
The AI Dashboard (`ai_dashboard_pro.py`) runs on the host PC and processes the video stream in real-time.
- **Object Detection**: Utilizes **YOLOv8** (Nano/Small models) for real-time detection of people, vehicles, and other objects.
- **Face Recognition**: Integrates `face_recognition` (dlib) for matching detected faces against a known database (`known_faces/` directory).
- **Optimization**: Uses a dedicated background thread (`_ai_worker`) and caching mechanism to ensure the display frame rate remains smooth even during heavy inference.

## Demo Video
*(Link to a YouTube or hosted video demonstrating the car navigating, detecting objects, and recognizing faces in real-time.)*
- [Watch the Demo on YouTube](#)

## Cost
| Component | Estimated Cost (USD) |
| :--- | :--- |
| ESP32-CAM Module | $5 - $10 |
| Custom Wooden Chassis & 4x Mecanum Wheels | $20 - $30 |
| Dual Motor Drivers (L298N x2) | $6 - $10 |
| Li-ion Battery Pack | $10 - $15 |
| Jumper Wires & Hardware | $5 |
| **Total Estimated Cost** | **$46 - $70** |

## Challenges
1. **WebSocket Latency**: Tuning the frame resolution and compression on the ESP32 to prevent network bottlenecks and latency during streaming.
2. **AI Inference Bottlenecks**: Running YOLOv8 and Face Recognition synchronously caused the video feed to lag.
   * **Solution**: Implemented a multi-threaded architecture with a dedicated `_ai_worker` thread and caching system to decouple display FPS from inference FPS.
3. **Face Recognition Reliability**: Handling varying lighting conditions and angles.
   * **Solution**: Added logic to first detect a `person` bounding box, then perform facial recognition within that area, coloring the box yellow if a face couldn't be clearly matched.

## Future Roadmap
- [ ] **Autonomous Navigation**: Implement SLAM (Simultaneous Localization and Mapping) or line-tracking for autonomous patrols.
- [ ] **Cloud Integration**: Push detection events and evidence recordings to an AWS S3 bucket or a Telegram bot.
- [ ] **Voice Commands**: Add a microphone module to the car or dashboard for voice-activated controls.
- [ ] **Edge AI**: Migrate lightweight object detection directly to an Edge TPU or a more powerful microcontroller (e.g., Raspberry Pi 5) mounted on the car.
