def decide_violence(human_frames, motion_score):
    if not human_frames:
        return False, "no_humans"

    if motion_score >= 18.0:
        return True, "high_motion_with_humans"

    return False, "normal_activity"
