from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import shutil
import os
import numpy as np
import cv2
from datetime import datetime
from collections import Counter, defaultdict

# ---------------- AI CORE ----------------
from core.model_loader import load_model
from core.inference import predict_video_core
from core.camera_detection import run_camera_detection

# ---------------- VIDEO PROCESSING ----------------
from video_processing.frame_extractor import extract_frames
from video_processing.motion_analysis import compute_motion_score

# ---------------- DATABASE ----------------
from backend.db.incidents import init_db, log_incident, fetch_incidents
from backend.db.alerts import trigger_email_if_needed

# ---------------- URL DOWNLOAD ----------------
from utils.url_downloader import download_video_from_url


# --------------------------------------------------
# APP
# --------------------------------------------------
app = FastAPI(title="Violence Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# INIT DATABASE
# --------------------------------------------------
init_db()

# --------------------------------------------------
# LOAD AI MODEL
# --------------------------------------------------
MODEL_PATH = "backend/models/final_model.pt"
THRESHOLD = 0.5

model, device = load_model(MODEL_PATH)

# --------------------------------------------------
# EVIDENCE STORAGE
# --------------------------------------------------
EVIDENCE_DIR = "backend/data/evidence"
os.makedirs(EVIDENCE_DIR, exist_ok=True)


def save_evidence_frame(frames):

    if len(frames) < 2:
        return None

    best_frame = frames[0]
    best_score = 0

    for i in range(1, len(frames)):
        score = np.mean(
            np.abs(frames[i].astype(float) - frames[i - 1].astype(float))
        )

        if score > best_score:
            best_score = score
            best_frame = frames[i]

    filename = f"evidence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    path = os.path.join(EVIDENCE_DIR, filename)

    cv2.imwrite(path, best_frame)

    return path


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


# --------------------------------------------------
# ALERTS
# --------------------------------------------------
@app.get("/alerts")
def alerts():

    rows = fetch_incidents()

    return [
        {
            "timestamp": r[0],
            "source": r[1],
            "is_violent": bool(r[2]),
            "severity": r[3],
            "confidence": r[4]
        }
        for r in rows
    ]


# --------------------------------------------------
# ANALYTICS
# --------------------------------------------------
@app.get("/analytics")
def analytics():

    rows = fetch_incidents(limit=1000)

    if not rows:
        return {
            "violence_distribution": {
                "violent": 0,
                "non_violent": 0
            },
            "severity_distribution": {
                "LOW": 0,
                "MEDIUM": 0,
                "HIGH": 0
            },
            "incidents_over_time": {}
        }

    violent = sum(1 for r in rows if r[2] == 1)
    non_violent = sum(1 for r in rows if r[2] == 0)

    severity = Counter(r[3] for r in rows)

    timeline = defaultdict(int)

    for r in rows:
        day = r[0].split(" ")[0]
        timeline[day] += 1

    return {
        "violence_distribution": {
            "violent": violent,
            "non_violent": non_violent
        },
        "severity_distribution": dict(severity),
        "incidents_over_time": dict(timeline)
    }


# --------------------------------------------------
# ANALYZE VIDEO (UPLOAD OR URL)
# --------------------------------------------------
@app.post("/analyze")
def analyze(
    video: UploadFile = File(None),
    video_url: str = Form(None)
):

    temp_video_path = None
    source = "upload" if video else video_url

    try:

        # ---------------- INPUT ----------------
        if video:

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                shutil.copyfileobj(video.file, tmp)
                temp_video_path = tmp.name

        elif video_url:

            temp_video_path = download_video_from_url(video_url)

        else:
            return {"error": "No video or URL provided"}

        # ---------------- AI MODEL ----------------
        ai_result = predict_video_core(
            video_path=temp_video_path,
            model=model,
            device=device,
            threshold=THRESHOLD
        )

        ai_score = ai_result["confidence"]
        is_violent = ai_result["is_violent"]

        # ---------------- FRAME ANALYSIS ----------------
        frames = extract_frames(
            temp_video_path,
            max_frames=40,
            sample_every=3
        )

        if not frames:
            return {"error": "No frames extracted"}

        motion = compute_motion_score(frames)

        # ---------------- SEVERITY ----------------
        if motion < 0.25:
            severity = "LOW"
        elif motion < 0.55:
            severity = "MEDIUM"
        else:
            severity = "HIGH"

        evidence = save_evidence_frame(frames)

        # ---------------- RESULT ----------------
        result = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "motion_score": round(float(motion), 3),
            "ai_score": round(float(ai_score), 3),
            "severity": severity,
            "is_violent": bool(is_violent),
            "confidence": round(float(ai_score), 3),
            "evidence_frame": evidence
        }

        # ---------------- DATABASE ----------------
        log_incident(
            source=source,
            is_violent=1 if is_violent else 0,
            severity=severity,
            confidence=result["confidence"]
        )

        # ---------------- EMAIL ALERT ----------------
        if is_violent:
            trigger_email_if_needed(result, source)

        return result

    except Exception as e:
        return {"error": str(e)}

    finally:
        if temp_video_path and os.path.exists(temp_video_path):
            try:
                os.remove(temp_video_path)
            except:
                pass


# --------------------------------------------------
# REAL-TIME CAMERA DETECTION
# --------------------------------------------------
@app.get("/camera-detection")
def camera_detection():

    run_camera_detection(
        model=model,
        device=device,
        threshold=THRESHOLD
    )

    return {"status": "Camera detection started"}
