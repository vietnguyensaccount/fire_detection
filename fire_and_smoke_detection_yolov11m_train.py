from ultralytics import YOLO

if __name__ == "__main__":
    # Choose your model config or weights
    model = YOLO("./yolo11m.pt")  # pretrained medium model
    
    # Train settings
    model.train(
        data="data.yaml",      # dataset config
        imgsz=640,             # training image size
        batch=8,               # adjust for suitable GPU memory
        epochs=100,            # number of epochs
        workers=10,
        device=0,              # GPU id ('cpu' for CPU)
    )
