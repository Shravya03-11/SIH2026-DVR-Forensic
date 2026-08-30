"""
utils/detector.py — AI Object & Face Detection Utility
ASSIGNED TO: Member 5
YOUR TASKS:
  [ ] The detect_objects function is ready — test it on a real video
  [ ] Add a function to detect motion between two frames
  [ ] Add a function to blur detected faces (privacy protection feature)
  [ ] Improve the detection summary statistics
"""

import cv2
import numpy as np


def detect_objects(frame: np.ndarray, model=None) -> tuple:
    """
    Run YOLOv8 object detection on a single frame.
    Returns (annotated_frame, list_of_detections)
    """
    if model is None:
        from ultralytics import YOLO
        model = YOLO("yolov8n.pt")  # Downloads automatically on first run

    results = model(frame, verbose=False)
    annotated = results[0].plot()   # Draws bounding boxes automatically

    detections = []
    for box in results[0].boxes:
        label = model.names[int(box.cls)]
        conf  = float(box.conf)
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        detections.append({
            "Object":     label,
            "Confidence": f"{conf:.0%}",
            "Bounding Box": f"({int(x1)},{int(y1)}) → ({int(x2)},{int(y2)})",
        })

    return annotated, detections


def detect_motion(frame1: np.ndarray, frame2: np.ndarray, threshold: int = 25) -> tuple:
    """
    Detect motion between two consecutive frames.
    Returns (motion_frame, motion_percentage)
    """
    # Convert to grayscale
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

    # Compute difference
    diff  = cv2.absdiff(gray1, gray2)
    _, thresh = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)

    # Calculate motion percentage
    motion_pct = (np.count_nonzero(thresh) / thresh.size) * 100

    # Draw motion areas on frame
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    motion_frame = frame2.copy()
    for c in contours:
        if cv2.contourArea(c) > 500:
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(motion_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    return motion_frame, motion_pct


def blur_faces(frame: np.ndarray) -> np.ndarray:
    """
    Detect and blur faces in a frame for privacy protection.
    TODO (Member 5): Implement using OpenCV face cascade
    """
    # TODO (Member 5): Use cv2.CascadeClassifier to find faces and blur them
    # Placeholder — just returns original frame
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    blurred = frame.copy()
    for (x, y, w, h) in faces:
        roi = blurred[y:y+h, x:x+w]
        roi = cv2.GaussianBlur(roi, (51, 51), 0)
        blurred[y:y+h, x:x+w] = roi

    return blurred
