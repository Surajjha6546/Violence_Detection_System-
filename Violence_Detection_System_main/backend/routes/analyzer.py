import cv2
import numpy as np

def analyze_video(video_path):
    cap = cv2.VideoCapture(video_path)
    frames = []

    while len(frames) < 30:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (320, 240))
        frames.append(frame)

    cap.release()

    motion_score = compute_motion(frames)

    if motion_score >= 0.55:
        decision = True
    elif motion_score <= 0.25:
        decision = False
    else:
        decision = "ambiguous"

    return {
        "motion_score": round(motion_score, 3),
        "is_violent": decision,
        "confidence": round(motion_score, 2)
    }


def compute_motion(frames):
    if len(frames) < 2:
        return 0.0

    diffs = []
    for i in range(1, len(frames)):
        diff = np.mean(
            np.abs(frames[i].astype(float) - frames[i - 1].astype(float))
        )
        diffs.append(diff)

    avg_motion = np.mean(diffs)
    peak_motion = np.max(diffs)

    score = (0.4 * avg_motion + 0.6 * peak_motion) / 80.0
    return min(score, 1.0)
