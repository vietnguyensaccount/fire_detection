FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ai_worker.py /app/

COPY yolov11m.pt /app/

RUN pip install ultralytics opencv-python

ENTRYPOINT ["python", "ai_worker.py"]

