import cv2
import time
import json
import os
from collections import deque
from ultralytics import YOLO

# Load model once
model_path = "yolov11m.pt"
model = YOLO(model_path)

# File paths
cams_file = "camera_config.json"
detections_json = "detections.json"

# Read all cameras
if os.path.exists(cams_file):
    with open(cams_file, 'r') as f:
        cams_data = json.load(f)
    cameras = cams_data.get("cameras", [])
else:
    cameras = []

# Check status
cameras = [c for c in cameras if c.get("status") == "running"]

# Open all RTSP streams
caps = []
for cam in cameras:
    rtsp_url = cam["rtsp"]
    cap = cv2.VideoCapture(0 if rtsp_url == "0" else rtsp_url)
    caps.append((cam["id"], cap, deque(), 0, 0))  # (id, cap, history, cooldown_until, last_detect_time)

print(f"Started AI worker on {len(caps)} cameras")

while True:
    now = time.time()
    for idx, (cid, cap, history, cooldown_until, last_detect_time) in enumerate(caps):
        ret, frame = cap.read()
        if not ret:
            continue

        # cooldown
        if now < cooldown_until:
            continue

        if now - last_detect_time >= 3:
            count = 0
            results = model(frame, verbose=False)
            boxes = results[0].boxes
            labels = results[0].names

            fire_detected = False
            label = None

            if boxes is not None and len(boxes) > 0:
                for box in boxes:
                    cls = int(box.cls[0])
                    label = labels[cls].lower()
                    if label in ['fire', 'smoke']:
                        fire_detected = True
                        break

            if fire_detected:
                print(cid)
                count = count + 1
                history.append(now)
                ts = time.strftime('%Y-%m-%d_%H-%M-%S')
                thumb_dir = os.path.join("thumbnails", str(cid))
                os.makedirs(thumb_dir, exist_ok=True)
                img_path = os.path.join(thumb_dir, f"{ts}.jpg")
                cv2.imwrite(img_path, frame)

                # Update detections.json
                record = {
                    "camera_id": cid,
                    "timestamp": ts,
                    "status": label,
                    "thumbnail": os.path.relpath(img_path, "thumbnails")  # path relative to thumbnails
                }

                if os.path.exists(detections_json):
                    with open(detections_json, 'r') as f:
                        data = json.load(f)
                else:
                    data = []

                if count % 3 == 0:
                    data.append(record)

                with open(detections_json, 'w') as f:
                    json.dump(data, f, indent=2)

            # Alert trigger
            history = deque([t for t in history if now - t < 10])
            if len(history) >= 3:
                cooldown_until = now + 30
                history.clear()

            last_detect_time = now

        # update tuple
        caps[idx] = (cid, cap, history, cooldown_until, last_detect_time)

