import cv2
import os

def extract_frames(video_path, max_frames=40, sample_every=5):
    if not isinstance(video_path, str) or not os.path.exists(video_path):
        raise ValueError("Invalid video path")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError("Cannot open video")

    frames = []
    idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if idx % sample_every == 0:
            frame = cv2.resize(frame, (224, 224))
            frames.append(frame)

            if len(frames) >= max_frames:
                break
        idx += 1

    cap.release()

    if len(frames) == 0:
        raise RuntimeError("No frames extracted")

    return frames
