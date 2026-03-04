import torch
import cv2
import numpy as np
import os
import urllib.request

from model import build_model
from config import MODEL_PATH, THRESHOLD, DEVICE


# Download model if not present
if not os.path.exists(MODEL_PATH):
    print("Downloading model...")
    url = "https://drive.google.com/file/d/1PnuPX74RrKRLnPvSex-YKr0h-aq2niPk/view?usp=drive_link"
    urllib.request.urlretrieve(url, MODEL_PATH)


# Load model
model = build_model().to(DEVICE)
model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
model.eval()


def predict_video(video_path):
    cap = cv2.VideoCapture(video_path)

    frame_probs = []
    timestamps = []

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        frame = cv2.resize(frame, (224, 224))
        frame = frame / 255.0
        frame = np.transpose(frame, (2, 0, 1))

        tensor = torch.tensor(frame).unsqueeze(0).float().to(DEVICE)

        with torch.no_grad():
            output = model(tensor)
            prob = torch.sigmoid(output).item()

        frame_probs.append(prob)

        if prob > THRESHOLD:
            timestamps.append(frame_count / fps)

    cap.release()

    avg_prob = float(np.mean(frame_probs))
    decision = "Violent" if avg_prob > THRESHOLD else "Non-Violent"

    return {
        "decision": decision,
        "confidence": round(avg_prob, 4),
        "threshold": THRESHOLD,
        "segments": timestamps
    }
