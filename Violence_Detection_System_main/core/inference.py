import torch
import cv2
import numpy as np


def extract_frames(video_path, max_frames=32):

    cap = cv2.VideoCapture(video_path)

    frames = []

    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if total == 0:
        cap.release()
        return frames

    step = max(1, total // max_frames)

    count = 0

    while cap.isOpened():

        ret, frame = cap.read()

        if not ret:
            break

        if count % step == 0:

            frame = cv2.resize(frame, (224, 224))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = frame / 255.0

            frames.append(frame)

            if len(frames) >= max_frames:
                break

        count += 1

    cap.release()

    return frames


def preprocess(frames):

    frames = np.array(frames)

    # shape: [T, H, W, C]

    frames = torch.tensor(frames, dtype=torch.float32)

    # [T,H,W,C] → [T,C,H,W]
    frames = frames.permute(0, 3, 1, 2)

    # [T,C,H,W] → [C,T,H,W]
    frames = frames.permute(1, 0, 2, 3)

    # [C,T,H,W] → [1,C,T,H,W]
    frames = frames.unsqueeze(0)

    return frames


def predict_video_core(video_path, model, device, threshold=0.5):

    frames = extract_frames(video_path)

    if len(frames) == 0:
        return {
            "confidence": 0.0,
            "is_violent": False
        }

    clip = preprocess(frames).to(device)

    with torch.no_grad():

        outputs = model(clip)

        score = torch.sigmoid(outputs).item()

    is_violent = score >= threshold

    return {
        "confidence": float(score),
        "is_violent": bool(is_violent)
    }
