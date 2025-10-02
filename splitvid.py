import subprocess

# First, get the duration of the video
import ffmpeg
probe = ffmpeg.probe('input.mp4')
duration = float(probe['format']['duration'])
half = duration / 2

# Split first half
subprocess.run([
    'ffmpeg', '-i', 'input.mp4', '-t', str(half),
    '-c', 'copy', 'output_part1.mp4'
])

# Split second half
subprocess.run([
    'ffmpeg', '-ss', str(half), '-i', 'input.mp4',
    '-c', 'copy', 'output_part2.mp4'
])

