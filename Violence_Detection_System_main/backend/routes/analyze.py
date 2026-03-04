from fastapi import APIRouter, UploadFile, File
import tempfile
import shutil
import os
from datetime import datetime

from services.analyzer import analyze_video
from services.storage import save_incident

router = APIRouter()

@router.post("")
def analyze(video: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        shutil.copyfileobj(video.file, tmp)
        video_path = tmp.name

    result = analyze_video(video_path)

    incident = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "motion_score": result["motion_score"],
        "is_violent": result["is_violent"],
        "confidence": result["confidence"]
    }

    incident_id = save_incident(incident)

    os.remove(video_path)

    return {
        "incident_id": incident_id,
        **incident
    }
