import numpy as np

def compute_motion_score(frames):
    """
    Enhanced motion score:
    - Uses frame-to-frame differences
    - Detects sudden motion bursts
    """

    if len(frames) < 2:
        return 0.0

    diffs = []

    for i in range(1, len(frames)):
        prev = frames[i - 1].astype(float)
        curr = frames[i].astype(float)
        diff = np.mean(np.abs(curr - prev))
        diffs.append(diff)

    diffs = np.array(diffs)

    avg_motion = np.mean(diffs)
    peak_motion = np.max(diffs)

    # Normalize (empirical, demo-safe)
    avg_norm = min(avg_motion / 50.0, 1.0)
    peak_norm = min(peak_motion / 80.0, 1.0)

    # 🔥 Weighted score: burst matters more than average
    motion_score = (0.4 * avg_norm) + (0.6 * peak_norm)

    return round(float(motion_score), 3)
