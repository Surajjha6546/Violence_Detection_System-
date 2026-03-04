import torch.nn as nn
from torchvision import models

class ViolenceModel(nn.Module):
    def __init__(self):
        super().__init__()

        self.backbone = models.resnet18(weights=None)
        self.backbone.fc = nn.Sequential(
            nn.Linear(512, 128),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(128, 1)
        )

    def forward(self, x):
        return self.backbone(x)
