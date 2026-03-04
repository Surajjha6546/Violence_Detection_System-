from alerts.email_alert import send_email_alert

def trigger_email_if_needed(result, source):
    if not result.get("is_violent"):
        return False

    return send_email_alert(
        to_email="RECEIVER_EMAIL@gmail.com",
        severity=result.get("severity", "High"),
        confidence=result.get("confidence", 0.0),
        source=source
    )
