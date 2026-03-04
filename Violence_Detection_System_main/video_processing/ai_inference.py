import torch
from torchvision import transforms
from PIL import Image

from training.model import build_model

DEVICE = "cpu"
MODEL_PATH = "models/violence_model.pt"

_model = None
_transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize([0.5]*3, [0.5]*3)
])


def _load_model():
    global _model
    if _model is None:
        _model = build_model()
        _model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
        _model.to(DEVICE)
        _model.eval()
    return _model


def predict_violence_score(frames):
    model = _load_model()
    scores = []

    with torch.no_grad():
        for frame in frames:
            img = Image.fromarray(frame).convert("RGB")
            img = _transform(img).unsqueeze(0).to(DEVICE)

            logit = model(img)
            prob = torch.sigmoid(logit).item()
            scores.append(prob)

    return float(sum(scores) / len(scores)) if scores else 0.0
