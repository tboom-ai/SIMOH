from ultralytics import YOLO
import cv2
import numpy as np

# Load trained YOLO model
model = YOLO('assets/best_helmet.pt')  # Path to the trained model

# Initialize the camera
cap = cv2.VideoCapture(0)  # try (0) for main webcam computer, (1) for external webcam, or other way around
if not cap.isOpened():
    print("Error: Cannot open camera")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to grab frame")
        break

    # YOLO detection and tracking
    results = model.track(
        source=frame,
        conf=0.6,
        persist=True,
        save=False,
        tracker='assets/bytetrack_helmet.yaml', # optimized tracking
        verbose=False
    )

    annotated_frame = results[0].plot()

    # Show the frame with detections
    cv2.imshow('Helmet Check', annotated_frame)

    # Press 'q' to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close any open windows
cap.release()
cv2.destroyAllWindows()
