import torch
import torchvision

def load_model(model_path, device=None):
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = torchvision.models.video.r3d_18(weights=None)
    model.fc = torch.nn.Linear(model.fc.in_features, 1)

    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()

    return model, device
