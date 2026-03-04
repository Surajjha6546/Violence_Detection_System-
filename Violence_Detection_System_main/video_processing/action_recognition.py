import torch
import torchvision
import cv2
import numpy as np

model = torchvision.models.video.r3d_18(weights="KINETICS400_V1")
model.eval()

AGGRESSIVE_ACTIONS = {
    "fighting",
    "wrestling",
    "punching another person",
    "pushing another person",
    "shoving",
    "kicking another person"
}

with open("kinetics_labels.txt", "r") as f:
    LABELS = [line.strip().lower() for line in f.readlines()]

CLIP_LEN = 16
TOP_K = 5


def _build_clip(frame_paths):
    frames = []

    for path in frame_paths[:CLIP_LEN]:
        img = cv2.imread(path)
        if img is None:
            continue

        img = cv2.resize(img, (112, 112))
        img = img[:, :, ::-1]  # BGR → RGB
        frames.append(img)

    if len(frames) < CLIP_LEN:
        return None

    clip = np.stack(frames)
    clip = torch.tensor(clip).permute(3, 0, 1, 2).float() / 255.0
    return clip.unsqueeze(0)


def action_analysis(frame_paths):
    """
    Returns:
    {
      ai_support: bool,
      aggression_score: float,
      top_actions: [(label, confidence)]
    }
    """
    clip = _build_clip(frame_paths)
    if clip is None:
        return {
            "ai_support": False,
            "aggression_score": 0.0,
            "top_actions": []
        }

    with torch.no_grad():
        outputs = model(clip)
        probs = torch.softmax(outputs, dim=1)[0]

    top_probs, top_idxs = torch.topk(probs, TOP_K)

    top_actions = []
    aggression_score = 0.0

    for p, idx in zip(top_probs, top_idxs):
        label = LABELS[idx.item()]
        conf = float(p.item())
        top_actions.append((label, round(conf, 2)))

        if label in AGGRESSIVE_ACTIONS:
            aggression_score = max(aggression_score, conf)

    ai_support = aggression_score >= 0.35

    return {
        "ai_support": ai_support,
        "aggression_score": round(aggression_score, 2),
        "top_actions": top_actions
    }
