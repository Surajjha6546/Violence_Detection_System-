from datetime import datetime

def log_incident(source_type, source_value, result):
    with open("storage/incidents.log", "a") as f:
        f.write(
            f"{datetime.now()} | "
            f"{source_type} | "
            f"{source_value} | "
            f"Violent={result['is_violent']} | "
            f"Severity={result['severity']}\n"
        )
