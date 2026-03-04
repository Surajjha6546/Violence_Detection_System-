import torch
import torchvision
import cv2
import numpy as np

# ---------------- LOAD MODEL ----------------
model = torchvision.models.video.r3d_18(weights="KINETICS400_V1")
model.eval()

# ---------------- VIOLENCE-RELATED ACTIONS ----------------
# Broader than before, but still controlled
AGGRESSIVE_ACTIONS = {
    "fighting",
    "wrestling",
    "punching another person",
    "pushing another person",
    "shoving",
    "grappling"
}

# ---------------- LOAD LABELS ----------------
with open("kinetics_labels.txt", "r") as f:
    LABELS = [line.strip().lower() for line in f.readlines()]

# ---------------- PARAMETERS (TUNED) ----------------
CLIP_LEN = 16
MOTION_THRESHOLD = 18.0      # critical for real fights
DL_CONFIDENCE_THRESHOLD = 0.40  # support signal, not sole decision
TOP_K = 5


def _load_clip(frame_paths):
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


def _compute_motion(frame_paths):
    diffs = []

    for i in range(1, len(frame_paths)):
        prev = cv2.imread(frame_paths[i - 1], cv2.IMREAD_GRAYSCALE)
        curr = cv2.imread(frame_paths[i], cv2.IMREAD_GRAYSCALE)
        if prev is None or curr is None:
            continue
        diff = cv2.absdiff(prev, curr)
        diffs.append(np.mean(diff))

    if not diffs:
        return 0.0

    return float(np.mean(diffs))


def detect_violence(frame_paths):
    if len(frame_paths) < CLIP_LEN:
        return {
            "is_violent": False,
            "confidence": 0.0,
            "frame": frame_paths[0] if frame_paths else None,
            "reason": "insufficient_frames"
        }

    # ---------------- MOTION ANALYSIS ----------------
    motion_score = _compute_motion(frame_paths)

    # ---------------- DL INFERENCE ----------------
    clip = _load_clip(frame_paths)
    if clip is None:
        return {
            "is_violent": False,
            "confidence": 0.0,
            "frame": frame_paths[0],
            "reason": "clip_load_failed"
        }

    with torch.no_grad():
        outputs = model(clip)
        probs = torch.softmax(outputs, dim=1)

    top_probs, top_idxs = torch.topk(probs, TOP_K)

    aggressive_support = False
    best_conf = 0.0
    best_label = "unknown"

    for p, idx in zip(top_probs[0], top_idxs[0]):
        label = LABELS[idx.item()]
        conf = p.item()

        if label in AGGRESSIVE_ACTIONS and conf > best_conf:
            aggressive_support = True
            best_conf = conf
            best_label = label

    # ---------------- FINAL DECISION ----------------
    is_violent = (
        motion_score >= MOTION_THRESHOLD
        and aggressive_support
    )

    return {
        "is_violent": is_violent,
        "confidence": round(max(best_conf, motion_score / 40), 2),
        "frame": frame_paths[0],
        "predicted_action": best_label,
        "motion_score": round(motion_score, 2)
    }
