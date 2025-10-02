import cv2
import os

# ====== Config ======
video_folder = "fire_clips"     # Folder containing short fire videos
output_video = "sample_video.mp4"

# ====== Get video files ======
video_files = [f for f in os.listdir(video_folder) if f.endswith(('.mp4', '.avi', '.mov'))]
video_files.sort()  # Sort alphabetically; change if needed

if not video_files:
    print("❌ No video files found in the folder.")
    exit()

print(f"Found {len(video_files)} videos to combine.")

# ====== Initialize Writer ======
first_video_path = os.path.join(video_folder, video_files[0])
cap = cv2.VideoCapture(first_video_path)

frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS) or 25

cap.release()

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_video, fourcc, fps, (frame_width, frame_height))


# ====== Combine Videos ======
for video_file in video_files:
    video_path = os.path.join(video_folder, video_file)
    print(f"Processing {video_file}...")

    cap = cv2.VideoCapture(video_path)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)

    cap.release()

out.release()

print(f"✅ Combined video saved as {output_video}")