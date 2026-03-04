import json
import os

DATA_FILE = "backend/data/incidents.json"

def load_incidents():
    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_incident(incident):
    incidents = load_incidents()
    incident["id"] = len(incidents) + 1
    incidents.append(incident)

    with open(DATA_FILE, "w") as f:
        json.dump(incidents, f, indent=2)

    return incident["id"]
