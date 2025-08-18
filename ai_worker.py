# ai_worker.py
import cv2
import time
import sys
import json
import os
from collections import deque
from ultralytics import YOLO
import cv2

rtsp_url = sys.argv[2]
cap = cv2.VideoCapture(0 if rtsp_url == "0" else rtsp_url)
model_path = "yolov11m.pt"
model = YOLO(model_path)

os.makedirs("images", exist_ok=True)
detections_json = "detections.json"
history = deque()
cooldown_until = 0
last_detect_time = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    now = time.time()
    if now < cooldown_until:
        continue

    if now - last_detect_time >= 1:
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
            history.append(now)
            ts = time.strftime('%Y-%m-%d_%H-%M-%S')
            img_path = f"images/{ts}.jpg"
            cv2.imwrite(img_path, frame)

            # Update detections.json
            record = {
                "timestamp": ts,
                "status": label,
                "thumbnail": img_path
            }

            if os.path.exists(detections_json):
                with open(detections_json, 'r') as f:
                    data = json.load(f)
            else:
                data = []

            data.append(record)
            with open(detections_json, 'w') as f:
                json.dump(data, f, indent=2)

        # Alert trigger
        history = deque([t for t in history if now - t < 10])
        if len(history) >= 3:
            cooldown_until = now + 30
            history.clear()

        last_detect_time = now