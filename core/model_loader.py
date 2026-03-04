import os
import torch
import requests

MODEL_URL = "https://drive.google.com/file/d/1PnuPX74RrKRLnPvSex-YKr0h-aq2niPk/view?usp=drive_link"
MODEL_PATH = "final_model.pt"


def download_model():
    if not os.path.exists(MODEL_PATH):
        print("Downloading model...")

        response = requests.get(MODEL_URL, stream=True)
        with open(MODEL_PATH, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        print("Model downloaded successfully.")


def load_model(model_path=None):

    download_model()

    model = torch.load(MODEL_PATH, map_location="cpu")
    model.eval()

    device = "cpu"

    return model, device

