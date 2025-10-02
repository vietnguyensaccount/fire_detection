#!/bin/bash

videos=("video1.mp4" "video2.mp4")

i=1
for video in "${videos[@]}"; do
  ffmpeg -re -stream_loop -1 -i "$video" -c copy -f rtsp "rtsp://localhost:8554/stream$i" &
  i=$((i+1))
done

wait

