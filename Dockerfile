FROM ultralytics/ultralytics:latest
WORKDIR /app
COPY . .
RUN pip install flask opencv-python
CMD ["python", "ai_worker.py"]