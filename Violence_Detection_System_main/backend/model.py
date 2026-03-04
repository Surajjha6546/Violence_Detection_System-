import torch.nn as nn
import torchvision

def build_model():
    model = torchvision.models.video.r3d_18(weights="KINETICS400_V1")
    model.fc = nn.Linear(model.fc.in_features, 1)
    return model
