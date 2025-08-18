import cv2

cap = cv2.VideoCapture("rtsp://localhost:8554/mystream")

if not cap.isOpened():
    print("❌ Could not open RTSP stream.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to read frame.")
        break
    resized_frame = cv2.resize(frame, (640, 360))  # or (480, 270) or any small size
    cv2.imshow('Fire Detection', resized_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
