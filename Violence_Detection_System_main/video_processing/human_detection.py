# video_processing/human_detection.py

import cv2

HOG = cv2.HOGDescriptor()
HOG.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

def detect_humans(frames):
    if not isinstance(frames, list):
        raise ValueError("detect_humans expects list of frames")

    if len(frames) == 0:
        raise ValueError("No frames for human detection")

    human_frames = []

    for frame in frames:
        rects, _ = HOG.detectMultiScale(frame, winStride=(8, 8))
        if len(rects) > 0:
            human_frames.append(frame)

    if not isinstance(human_frames, list):
        raise ValueError("Human detection output invalid")

    return human_frames
