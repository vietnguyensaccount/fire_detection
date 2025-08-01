import cv2
import time
import json
import os
from collections import deque
from ultralytics import YOLO

video_path = 'rtsp://localhost:8554/other'
detections_json = 'detections.json'
thumbnails_folder = 'thumbnails'
os.makedirs(thumbnails_folder, exist_ok=True)

model = YOLO('yolov11m.pt')

cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("Error: Cannot open video.")
    exit()

detection_history = deque()
cooldown_until = 0
last_detection_time = 0
last_json_save_time = time.time()

detection_records = []

print("Detection started (optimized for NVIDIA Jetson / CUDA)...")

try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        current_time = time.time()

        if current_time < cooldown_until:
            cv2.imshow('Fire Detection (Cooldown)', frame)
        else:
            # Detect once every second
            if current_time - last_detection_time >= 1:
                results = model(frame, verbose=False)
                detections = results[0].boxes
                labels = results[0].names

                fire_smoke_detected = False
                detected_label = None

                if detections is not None and len(detections) > 0:
                    for box in detections:
                        class_id = int(box.cls[0])
                        label = labels[class_id].lower()
                        if label in ['fire', 'smoke']:
                            fire_smoke_detected = True
                            detected_label = label
                            break

                if fire_smoke_detected:
                    detection_history.append(current_time)
                    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                    thumb_filename = f"{timestamp.replace(':', '-')}.jpg"
                    thumb_path = os.path.join(thumbnails_folder, thumb_filename)
                    cv2.imwrite(thumb_path, frame)

                    detection_records.append({
                        "status": detected_label,
                        "timestamp": timestamp,
                        "thumbnail": thumb_filename
                    })

                    print(f"Detected {detected_label} at {timestamp}")

                while detection_history and current_time - detection_history[0] > 10:
                    detection_history.popleft()

                if len(detection_history) >= 3:
                    last3 = list(detection_history)[-3:]
                    seconds = [int(t) for t in last3]

                    # Check for 3 consecutive seconds (e.g., 100, 101, 102)
                    if seconds[1] == seconds[0] + 1 and seconds[2] == seconds[1] + 1:
                        print("Detected fire/smoke for 3 consecutive seconds")

                        # Append only the third detection
                        if os.path.exists(detections_json):
                            with open(detections_json, 'r') as f:
                                existing = json.load(f)
                                if not isinstance(existing, list):
                                    existing = []
                        else:
                            existing = []

                        existing.append(detection_records[-1])

                        with open(detections_json, 'w') as f:
                            json.dump(existing, f, indent=2)

                        print(f" Saved to {detections_json}")

                        cooldown_until = current_time + 30
                        detection_history.clear()

                last_detection_time = current_time
            resized_frame = cv2.resize(frame,(600,300))
            cv2.imshow('Fire Detection', resized_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Interrupted by user.")

finally:
    cap.release()
    cv2.destroyAllWindows()

    with open(detections_json, 'w') as f:
        json.dump(detection_records, f, indent=2)
    print(f"Final detections saved to {detections_json}")
