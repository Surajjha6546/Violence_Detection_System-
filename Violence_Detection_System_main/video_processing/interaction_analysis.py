def compute_interaction_score(frames):
    # Placeholder but VALID
    # No humans ≠ error, just low interaction
    if not frames:
        return 0.0

    # You can improve later
    return 0.3 if len(frames) > 20 else 0.1
