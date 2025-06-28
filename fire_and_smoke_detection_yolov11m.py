import cv2
import time

from ultralytics import YOLO
from collections import deque

# Load YOLO model
model = YOLO('yolov11m-best.pt')

# RTSP camera feed
rtsp_url = 'rtsp://username:password@ip_address:port/stream'
cap = cv2.VideoCapture(rtsp_url)

if not cap.isOpened():
    print(" Error: Cannot open camera stream")
    exit()

#  Detection parameters
detection_window = deque()
watch_mode = False
watch_mode_end_time = 0

print(" Fire/Smoke detection started...")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print(" Error: Failed to grab frame")
            break

        current_time = time.time()

        # Run YOLO detection
        results = model(frame, verbose=False)
        detections = results[0].boxes
        labels = results[0].names

        fire_detected = False

        if detections is not None and len(detections) > 0:
            for box in detections:
                class_id = int(box.cls[0])
                label = labels[class_id].lower()
                if label in ['fire', 'smoke']:
                    fire_detected = True
                    break

        if fire_detected:
            detection_window.append(current_time)

        # Remove detections older than 3 seconds
        while detection_window and current_time - detection_window[0] > 3:
            detection_window.popleft()

        # Trigger detection if >=5 in 3 seconds
        if len(detection_window) >= 5 and not watch_mode:
            print(" fire / smoke detected")
            watch_mode = True
        elif  len(detection_window) + 1 == 5:
            watch_mode_end_time = current_time + 10

        # Check next 10s
        if watch_mode:
            if current_time > watch_mode_end_time:
                if not fire_detected:
                    detection_window.clear()
                    watch_mode = False
                    print(" Resetting...")

        #  Display
        cv2.imshow('Fire Detection', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print(" Interrupted by user. Exiting...")

finally:
    cap.release()
    cv2.destroyAllWindows()
