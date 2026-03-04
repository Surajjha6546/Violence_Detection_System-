def final_violence_decision(motion_score, interaction_score, ai_score):
    """
    Enhanced motion-based decision logic
    """

    # Clear violent burst
    if motion_score >= 0.65:
        return {
            "is_violent": True,
            "confidence": motion_score
        }

    # Clear non-violent
    if motion_score <= 0.20:
        return {
            "is_violent": False,
            "confidence": round(1 - motion_score, 2)
        }

    # Middle region → ambiguous
    return {
        "is_violent": "ambiguous",
        "confidence": round(motion_score, 2)
    }
