import os
from ultralytics import YOLO
import ultralytics
import glob
from PIL import Image
# Set your local project directory
HOME = os.path.curdir
DATASET_DIR = os.path.abspath("datasets/fire-8")

# Check environment and install required packages if needed
ultralytics.checks()



# Train the model
model = YOLO("yolov8s.pt")
model.train(data=os.path.join(DATASET_DIR, "data.yaml"), epochs=25, imgsz=800)

# Validate the model
model.val(data=os.path.join(DATASET_DIR, "data.yaml"))

# Predict on test images
model.predict(
    source=os.path.join(DATASET_DIR, "test", "images"),
    conf=0.25,
    save=True
)

# Show a few predicted images
predicted_images = glob.glob(os.path.join(HOME, "runs", "detect", "predict", "*.jpg"))
for img_path in predicted_images[:3]:
    Image.open(img_path).show()

# Predict on a local video file
video_path = os.path.join(HOME, "forest-fire_5.mp4")
if os.path.exists(video_path):
    model.predict(source=video_path, conf=0.25, save=True)
