import cv2
import tempfile
import os
from core.inference import predict_video_core


def run_camera_detection(model, device, threshold=0.5):

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Cannot access camera")
        return

    frames = []

    print("Camera detection started. Press Q to exit.")

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        frames.append(frame)

        label = "Scanning..."
        color = (0, 255, 0)

        # once we collect enough frames
        if len(frames) == 32:

            temp_path = tempfile.mktemp(suffix=".avi")

            height, width, _ = frames[0].shape

            writer = cv2.VideoWriter(
                temp_path,
                cv2.VideoWriter_fourcc(*'XVID'),
                10,
                (width, height)
            )

            for f in frames:
                writer.write(f)

            writer.release()

            result = predict_video_core(
                temp_path,
                model,
                device,
                threshold
            )

            score = result["confidence"]

            if result["is_violent"]:
                label = f"VIOLENCE DETECTED ({score:.2f})"
                color = (0, 0, 255)
            else:
                label = f"SAFE ({score:.2f})"
                color = (0, 255, 0)

            os.remove(temp_path)

            frames = []

        # draw overlay text
        cv2.rectangle(frame, (0, 0), (500, 40), color, -1)

        cv2.putText(
            frame,
            label,
            (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        cv2.imshow("Violence Detection Camera", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
