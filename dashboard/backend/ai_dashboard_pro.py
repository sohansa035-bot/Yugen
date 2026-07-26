import cv2
import numpy as np
import websocket
import threading
import face_recognition
import os
import math
import time
import logging
import datetime
from ultralytics import YOLO

# --- 1. SYSTEM CONFIGURATION ---
# Configure Professional Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("CarDashboard")

class SmartCarSystem:
    def __init__(self, ip_address, model_type="ai/vision/yolov8n.pt", confidence=0.60, frame_skip=3, face_tolerance=0.50):
        """
        Initialize the AI Surveillance System.
        """
        # --- Connection Settings ---
        self.esp32_ip = ip_address
        self.ws_url = f"ws://{self.esp32_ip}/Camera"
        
        # --- AI Settings ---
        self.known_faces_dir = "known_faces"
        self.min_confidence = confidence
        self.frame_skip = frame_skip
        self.face_tolerance = face_tolerance
        
        # --- Recording Settings ---
        self.recording = False
        self.video_writer = None
        self.recordings_dir = "recordings"
        if not os.path.exists(self.recordings_dir):
            os.makedirs(self.recordings_dir)
        
        # --- System State ---
        self.running = True
        self.latest_frame = None
        self.latest_frame_bytes = None
        self.last_packet_time = time.time()
        self.frame_lock = threading.Lock()
        self.ws = None
        self.frame_count = 0
        
        # --- Cache for Optimization ---
        self.cached_yolo_boxes = []
        self.cached_faces = []
        
        # --- FPS Calculation ---
        self.prev_frame_time = 0
        self.new_frame_time = 0
        
        # --- Load YOLO Model ---
        logger.info(f"Loading Object Detection Model: {model_type}...")
        try:
            self.yolo_model = YOLO(model_type)
        except Exception as e:
            logger.error(f"Failed to load model. Did you run the download command? Error: {e}")
            self.running = False
        
        # --- Load Face Recognition Data ---
        self.known_face_encodings = []
        self.known_face_names = []
        self._load_known_faces()

    def _load_known_faces(self):
        """Loads and encodes faces from the directory with error checking."""
        if not os.path.exists(self.known_faces_dir):
            os.makedirs(self.known_faces_dir)
            logger.warning(f"Created folder '{self.known_faces_dir}'. Please add .jpg photos.")
            return

        logger.info("Scanning for known faces...")
        try:
            files = os.listdir(self.known_faces_dir)
            loaded_count = 0
            for filename in files:
                if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    path = os.path.join(self.known_faces_dir, filename)
                    try:
                        image = face_recognition.load_image_file(path)
                        encodings = face_recognition.face_encodings(image)
                        
                        if encodings:
                            self.known_face_encodings.append(encodings[0])
                            name = os.path.splitext(filename)[0].capitalize()
                            self.known_face_names.append(name)
                            loaded_count += 1
                            logger.info(f"  [+] Loaded Identity: {name}")
                        else:
                            logger.warning(f"  [-] Skipping {filename}: No face found.")
                    except Exception as e:
                        logger.error(f"  [!] Error processing {filename}: {e}")
            
            if loaded_count == 0:
                logger.warning("No faces loaded. Recognition will treat everyone as 'UNKNOWN'.")
        except Exception as e:
            logger.error(f"Failed to access directory: {e}")

    def _on_message(self, ws, message):
        """WebSocket Callback: Stores raw bytes."""
        with self.frame_lock:
            self.latest_frame_bytes = message
            self.last_packet_time = time.time()

    def _on_error(self, ws, error):
        logger.error(f"WebSocket Error: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        logger.warning("WebSocket Connection Closed.")

    def _on_open(self, ws):
        logger.info(f"Successfully connected to Car at {self.ws_url}")

    def start_stream(self):
        """Starts the WebSocket client."""
        if self.ws:
            try:
                self.ws.close()
            except:
                pass
        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )
        wst = threading.Thread(target=self.ws.run_forever)
        wst.daemon = True
        wst.start()

    def toggle_recording(self, frame_shape):
        """Toggles video recording state."""
        if not self.recording:
            # Start Recording
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = os.path.join(self.recordings_dir, f"evidence_{timestamp}.mp4")
            
            # Initialize VideoWriter
            # mp4v is a good general codec. format: (width, height)
            height, width, _ = frame_shape
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(filename, fourcc, 20.0, (width, height))
            
            self.recording = True
            logger.info(f"STARTED RECORDING: {filename}")
        else:
            # Stop Recording
            self.recording = False
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None
            logger.info("STOPPED RECORDING")

    def draw_hud(self, frame, fps, connected=True):
        """Draws the Heads-Up Display (Overlay)."""
        height, width, _ = frame.shape
        
        # 1. FPS Counter (Top Left)
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (140, 50), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
        cv2.putText(frame, f"FPS: {int(fps)}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        # 2. Recording Status (Top Right)
        if self.recording:
            # Flashing effect
            if int(time.time() * 2) % 2 == 0: # Flash every 0.5s
                cv2.circle(frame, (width - 40, 30), 10, (0, 0, 255), -1)
            cv2.putText(frame, "REC", (width - 100, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        # 3. System Status (Bottom Right)
        if connected:
            status_text = "SYSTEM ONLINE"
            status_color = (0, 255, 0)
        else:
            status_text = "SIGNAL LOST"
            status_color = (0, 0, 255)
            text_size = cv2.getTextSize("SIGNAL LOST", cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)[0]
            cx = (width - text_size[0]) // 2
            cy = (height + text_size[1]) // 2
            cv2.putText(frame, "SIGNAL LOST", (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

        cv2.putText(frame, status_text, (width - 250, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)

    def process_ai(self, frame, run_inference=True):
        """Runs YOLO and Face Recognition."""
        if run_inference:
            # 1. YOLOv8
            results = self.yolo_model(frame, stream=True, verbose=False, agnostic_nms=True)
            self.cached_yolo_boxes = [] 
            
            for result in results:
                for box in result.boxes:
                    conf = float(box.conf[0])
                    if conf > self.min_confidence:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        cls = int(box.cls[0])
                        class_name = self.yolo_model.names[cls]
                        label = f"{class_name} {int(conf * 100)}%"
                        self.cached_yolo_boxes.append((x1, y1, x2, y2, label, class_name))

            # 2. Face Recognition
            small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            face_locs = face_recognition.face_locations(rgb_small)
            face_encs = face_recognition.face_encodings(rgb_small, face_locs)
            
            self.cached_faces = [] 

            for encoding, loc in zip(face_encs, face_locs):
                face_distances = face_recognition.face_distance(self.known_face_encodings, encoding)
                best_match_index = np.argmin(face_distances) if len(face_distances) > 0 else None
                
                name = "UNKNOWN"
                color = (0, 0, 255) # Red

                if best_match_index is not None and face_distances[best_match_index] < self.face_tolerance:
                    name = self.known_face_names[best_match_index]
                    color = (0, 255, 0) # Green

                top, right, bottom, left = [coord * 2 for coord in loc]
                self.cached_faces.append((top, right, bottom, left, name, color))

        # Drawing Phase
        for (x1, y1, x2, y2, label, class_name) in self.cached_yolo_boxes:
            draw_box = True
            color = (255, 0, 255)
            
            if class_name == 'person':
                has_face = False
                for (ft, fr, fb, fl, fname, fcolor) in self.cached_faces:
                    fcx = fl + (fr - fl) // 2
                    fcy = ft + (fb - ft) // 2
                    if x1 < fcx < x2 and y1 < fcy < y2:
                        has_face = True
                        break
                
                if has_face:
                    draw_box = False 
                else:
                    color = (0, 255, 255) # Yellow
                    label = "Person (No Face)"

            if draw_box:
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                t_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
                cv2.rectangle(frame, (x1, y1 - 20), (x1 + t_size[0], y1), color, -1)
                cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

        for (top, right, bottom, left, name, color) in self.cached_faces:
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.rectangle(frame, (left, bottom - 30), (right, bottom), color, cv2.FILLED)
            cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

        return frame

    def run(self):
        """Main Loop."""
        self.start_stream()
        logger.info("Initializing Display...")
        logger.info("Press 'Q' to Quit. Press 'R' to Record Video.")

        last_reconnect_time = 0

        while self.running:
            self.new_frame_time = time.time()
            time_diff = self.new_frame_time - self.prev_frame_time
            fps = 1 / time_diff if self.prev_frame_time > 0 and time_diff > 0 else 0
            self.prev_frame_time = self.new_frame_time

            frame_bytes = None
            with self.frame_lock:
                if self.latest_frame_bytes is not None:
                    frame_bytes = self.latest_frame_bytes
                    self.latest_frame_bytes = None

            if frame_bytes is not None:
                try:
                    np_arr = np.frombuffer(frame_bytes, dtype=np.uint8)
                    decoded_img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                    if decoded_img is not None:
                        self.latest_frame = decoded_img
                except Exception as e:
                    logger.error(f"Decode error: {e}")

            # Connection Watchdog
            is_connected = True
            time_since_last_packet = time.time() - self.last_packet_time
            if time_since_last_packet > 1.0:
                print(f"DEBUG: No data for {time_since_last_packet:.1f}s")

            if time_since_last_packet > 4.0:
                is_connected = False
                if time_since_last_packet > 6.0 and time.time() - last_reconnect_time > 10.0:
                    logger.warning("Signal lost (>6s). Attempting reconnect...")
                    self.start_stream()
                    last_reconnect_time = time.time()

            if self.latest_frame is not None:
                should_run_inference = (self.frame_count % self.frame_skip == 0)
                display_frame = self.latest_frame.copy()
                
                # Process AI
                processed_frame = self.process_ai(display_frame, run_inference=should_run_inference)
                
                # Add HUD
                self.draw_hud(processed_frame, fps, connected=is_connected)
                
                # Handle Recording
                if self.recording and self.video_writer:
                    self.video_writer.write(processed_frame)
                
                # Show
                cv2.imshow("Professional AI Dashboard", processed_frame)
                self.frame_count += 1

            # Input Handling
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                self.running = False
                break
            elif key == ord('r'):
                # Toggle recording, pass shape for initialization if needed
                if self.latest_frame is not None:
                    self.toggle_recording(self.latest_frame.shape)
                else:
                    logger.warning("Cannot start recording: No video signal.")

        # Cleanup
        cv2.destroyAllWindows()
        if self.video_writer:
            self.video_writer.release()
        if self.ws:
            self.ws.close()
        logger.info("System Shutdown Complete.")

# ================= EXECUTION =================
if __name__ == "__main__":
    CAR_IP = "192.168.4.1"
    system = SmartCarSystem(
        ip_address=CAR_IP,
        model_type="ai/vision/yolov8n.pt",
        confidence=0.50,
        frame_skip=3,
        face_tolerance=0.50
    )
    system.run()