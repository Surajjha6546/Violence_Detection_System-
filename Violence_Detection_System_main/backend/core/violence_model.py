import torch
import torchvision
import torchvision.transforms as transforms
import cv2
import numpy as np
import os


THRESHOLD = 0.5


class ViolenceModel:
    def __init__(self, model_path="models/final_model.pt"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}")

        # Load r3d_18 architecture (same as training)
        self.model = torchvision.models.video.r3d_18(weights=None)
        self.model.fc = torch.nn.Linear(self.model.fc.in_features, 1)

        self.model.load_state_dict(
            torch.load(model_path, map_location=self.device)
        )

        self.model.to(self.device)
        self.model.eval()

        # Correct normalization for Kinetics pretrained backbone
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.43216, 0.394666, 0.37645],
                std=[0.22803, 0.22145, 0.216989]
            )
        ])

    def predict_video(self, video_path, clip_len=16):
        cap = cv2.VideoCapture(video_path)

        frames = []
        clip_probs = []
        timestamps = []

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_index = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_index += 1

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = self.transform(frame)
            frames.append(frame)

            # When enough frames collected → make clip
            if len(frames) == clip_len:
                clip = torch.stack(frames, dim=1)  # (3, T, H, W)
                clip = clip.unsqueeze(0).to(self.device)  # (1, 3, T, H, W)

                with torch.no_grad():
                    output = self.model(clip)
                    prob = torch.sigmoid(output).item()

                clip_probs.append(prob)

                if prob > THRESHOLD:
                    timestamps.append(frame_index / fps)

                frames = []

        cap.release()

        if not clip_probs:
            return {
                "decision": "Non-Violent",
                "confidence": 0.0,
                "segments": []
            }

        avg_prob = float(np.mean(clip_probs))
        decision = "Violent" if avg_prob > THRESHOLD else "Non-Violent"

        return {
            "decision": decision,
            "confidence": round(avg_prob, 4),
            "threshold": THRESHOLD,
            "segments": timestamps
        }
