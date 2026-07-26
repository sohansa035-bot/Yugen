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
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("YugenDashboard")

# Premium Engineering Palette (BGR format for OpenCV)
C_BG = (32, 16, 11)       # #0B1020
C_CARD = (39, 24, 17)     # #111827
C_ACCENT = (255, 212, 0)  # #00D4FF (Cyan)
C_SUCCESS = (94, 197, 34) # #22C55E (Green)
C_WARN = (11, 158, 245)   # #F59E0B (Amber)
C_DANGER = (68, 68, 239)  # #EF4444 (Red)
C_TEXT = (255, 255, 255)  # White
C_MUTED = (150, 150, 150) # Gray

class SmartCarSystem:
    def __init__(self, ip_address, model_type="ai/vision/yolov8n.pt", confidence=0.60, frame_skip=3, face_tolerance=0.50):
        self.esp32_ip = ip_address
        self.ws_url = f"ws://{self.esp32_ip}/Camera"
        
        self.known_faces_dir = "known_faces"
        self.min_confidence = confidence
        self.frame_skip = frame_skip
        self.face_tolerance = face_tolerance
        
        self.recording = False
        self.video_writer = None
        self.recordings_dir = "recordings"
        if not os.path.exists(self.recordings_dir):
            os.makedirs(self.recordings_dir)
        
        self.running = True
        self.latest_frame = None
        self.latest_frame_bytes = None
        self.last_packet_time = time.time()
        self.frame_lock = threading.Lock()
        self.ws = None
        self.frame_count = 0
        
        self.cached_yolo_boxes = []
        self.cached_faces = []
        
        self.prev_frame_time = 0
        self.new_frame_time = 0
        
        logger.info(f"Loading Edge Vision Model: {model_type}...")
        try:
            self.yolo_model = YOLO(model_type)
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.running = False
            
        self.known_face_encodings = []
        self.known_face_names = []
        self._load_known_faces()

    def _load_known_faces(self):
        if not os.path.exists(self.known_faces_dir):
            os.makedirs(self.known_faces_dir)
            return
        
        logger.info("Scanning for known identities...")
        for filename in os.listdir(self.known_faces_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                path = os.path.join(self.known_faces_dir, filename)
                try:
                    image = face_recognition.load_image_file(path)
                    encodings = face_recognition.face_encodings(image)
                    if encodings:
                        self.known_face_encodings.append(encodings[0])
                        self.known_face_names.append(os.path.splitext(filename)[0].capitalize())
                except Exception as e:
                    pass

    def _on_message(self, ws, message):
        with self.frame_lock:
            self.latest_frame_bytes = message
            self.last_packet_time = time.time()

    def _on_error(self, ws, error): pass
    def _on_close(self, ws, close_status_code, close_msg): pass
    def _on_open(self, ws): logger.info("Telemetry Link Established.")

    def start_stream(self):
        if self.ws:
            try: self.ws.close()
            except: pass
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
        if not self.recording:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = os.path.join(self.recordings_dir, f"event_{timestamp}.mp4")
            height, width, _ = frame_shape
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(filename, fourcc, 20.0, (width, height))
            self.recording = True
        else:
            self.recording = False
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None

    def draw_card(self, canvas, x, y, w, h, title, details, color):
        cv2.rectangle(canvas, (x, y), (x+w, y+h), C_CARD, -1)
        # Left accent border
        cv2.rectangle(canvas, (x, y), (x+5, y+h), color, -1)
        
        # Title
        cv2.putText(canvas, title, (x + 15, y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, C_TEXT, 2)
        
        # Details
        dy = y + 55
        for line in details:
            cv2.putText(canvas, line, (x + 15, dy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, C_MUTED, 1)
            dy += 25

    def build_dashboard(self, frame, fps, is_connected):
        f_h, f_w, _ = frame.shape
        panel_w = 400
        canvas = np.zeros((f_h, f_w + panel_w, 3), dtype=np.uint8)
        canvas[:] = C_BG
        
        # Overlay annotations on frame
        annotated_frame = frame.copy()
        
        active_cards = []
        
        # Process and draw YOLO
        for (x1, y1, x2, y2, conf_pct, class_name) in self.cached_yolo_boxes:
            has_face = False
            face_name = None
            if class_name == 'person':
                for (ft, fr, fb, fl, fname) in self.cached_faces:
                    fcx, fcy = fl + (fr - fl) // 2, ft + (fb - ft) // 2
                    if x1 < fcx < x2 and y1 < fcy < y2:
                        has_face = True
                        face_name = fname
                        break
                        
            color = C_SUCCESS if class_name == 'person' else C_ACCENT
            box_label = face_name.upper() if has_face else class_name.upper()
            
            # Bounding box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            cv2.rectangle(annotated_frame, (x1, y1 - 25), (x1 + max(120, len(box_label)*15), y1), color, -1)
            cv2.putText(annotated_frame, box_label, (x1 + 5, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)
            
            # Prepare card data
            details = [f"Confidence: {conf_pct}%", f"Status: Tracking"]
            active_cards.append((box_label, details, color))

        # Place the video frame
        canvas[0:f_h, 0:f_w] = annotated_frame
        
        # Draw separator line
        cv2.line(canvas, (f_w, 0), (f_w, f_h), C_ACCENT, 2)
        
        # Build Sidebar
        px = f_w + 20
        py = 30
        
        # Title
        cv2.putText(canvas, "YUGEN", (px, py), cv2.FONT_HERSHEY_DUPLEX, 1.2, C_TEXT, 2)
        cv2.putText(canvas, "Autonomous Surveillance Platform", (px, py + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, C_ACCENT, 1)
        
        py += 50
        
        # Telemetry Section
        cv2.putText(canvas, "SYSTEM TELEMETRY", (px, py), cv2.FONT_HERSHEY_SIMPLEX, 0.5, C_MUTED, 1)
        py += 20
        
        # Status Box
        net_color = C_SUCCESS if is_connected else C_DANGER
        net_text = "ONLINE - WS ACTIVE" if is_connected else "OFFLINE - SIGNAL LOST"
        cv2.rectangle(canvas, (px, py), (px + panel_w - 40, py + 40), C_CARD, -1)
        cv2.putText(canvas, "Network:", (px + 10, py + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, C_TEXT, 1)
        cv2.putText(canvas, net_text, (px + 100, py + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, net_color, 2)
        
        py += 50
        cv2.rectangle(canvas, (px, py), (px + panel_w - 40, py + 40), C_CARD, -1)
        cv2.putText(canvas, "Vision FPS:", (px + 10, py + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, C_TEXT, 1)
        cv2.putText(canvas, f"{int(fps)} FPS", (px + 100, py + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, C_ACCENT, 2)
        
        py += 60
        cv2.putText(canvas, "AI DETECTION EVENTS", (px, py), cv2.FONT_HERSHEY_SIMPLEX, 0.5, C_MUTED, 1)
        py += 20
        
        if not active_cards:
            cv2.putText(canvas, "No entities detected.", (px, py + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, C_MUTED, 1)
        
        for i, (title, details, color) in enumerate(active_cards[:3]): # Max 3 cards
            self.draw_card(canvas, px, py, panel_w - 40, 90, title, details, color)
            py += 100
            
        # Controls mapping
        py_bottom = f_h - 40
        cv2.putText(canvas, "Controls: [Q] Quit  [R] Record", (px, py_bottom), cv2.FONT_HERSHEY_SIMPLEX, 0.5, C_MUTED, 1)
        if self.recording:
            cv2.circle(canvas, (px + 230, py_bottom - 5), 6, C_DANGER, -1)
            cv2.putText(canvas, "REC", (px + 245, py_bottom), cv2.FONT_HERSHEY_SIMPLEX, 0.5, C_DANGER, 2)
            
        return canvas

    def process_ai(self, frame, run_inference=True):
        if run_inference:
            results = self.yolo_model(frame, stream=True, verbose=False, agnostic_nms=True)
            self.cached_yolo_boxes = [] 
            
            for result in results:
                for box in result.boxes:
                    conf = float(box.conf[0])
                    if conf > self.min_confidence:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        cls = int(box.cls[0])
                        class_name = self.yolo_model.names[cls]
                        self.cached_yolo_boxes.append((x1, y1, x2, y2, int(conf * 100), class_name))

            small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            face_locs = face_recognition.face_locations(rgb_small)
            face_encs = face_recognition.face_encodings(rgb_small, face_locs)
            
            self.cached_faces = [] 
            for encoding, loc in zip(face_encs, face_locs):
                face_distances = face_recognition.face_distance(self.known_face_encodings, encoding)
                best_match_index = np.argmin(face_distances) if len(face_distances) > 0 else None
                
                name = "UNKNOWN"
                if best_match_index is not None and face_distances[best_match_index] < self.face_tolerance:
                    name = self.known_face_names[best_match_index]

                top, right, bottom, left = [coord * 2 for coord in loc]
                self.cached_faces.append((top, right, bottom, left, name))

    def run(self):
        self.start_stream()
        logger.info("Initializing Yugen Dashboard...")

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
                except Exception:
                    pass

            is_connected = True
            time_since_last_packet = time.time() - self.last_packet_time
            if time_since_last_packet > 4.0:
                is_connected = False
                if time_since_last_packet > 6.0 and time.time() - last_reconnect_time > 10.0:
                    self.start_stream()
                    last_reconnect_time = time.time()

            if self.latest_frame is not None:
                should_run_inference = (self.frame_count % self.frame_skip == 0)
                display_frame = self.latest_frame.copy()
                
                self.process_ai(display_frame, run_inference=should_run_inference)
                
                # Build the beautiful dashboard
                dashboard = self.build_dashboard(display_frame, fps, is_connected)
                
                if self.recording and self.video_writer:
                    # Video writer needs the exact frame size it was initialized with
                    # We will just write the camera feed, not the whole dashboard UI
                    self.video_writer.write(display_frame)
                
                cv2.imshow("YUGEN Edge AI Interface", dashboard)
                self.frame_count += 1

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                self.running = False
                break
            elif key == ord('r'):
                if self.latest_frame is not None:
                    self.toggle_recording(self.latest_frame.shape)

        cv2.destroyAllWindows()
        if self.video_writer:
            self.video_writer.release()
        if self.ws:
            self.ws.close()
        logger.info("System Shutdown Complete.")

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