import os
import shutil
from datetime import datetime

def save_evidence(frame_path):
    os.makedirs("storage/evidence", exist_ok=True)
    name = datetime.now().strftime("%Y%m%d_%H%M%S_") + os.path.basename(frame_path)
    dest = os.path.join("storage/evidence", name)
    shutil.copy(frame_path, dest)
    return dest
