"""
utils/detector.py — AI Object & Face Detection Utility
Complete, working implementation for the DVR/NVR Forensic Tool.
"""

import cv2
import numpy as np


# ── Object Detection ─────────────────────────────────────────────────────────
def detect_objects(frame: np.ndarray, model, conf: float = 0.25) -> tuple:
    """
    Run YOLOv8 object detection on a single BGR frame.

    Args:
        frame : numpy array (BGR image from OpenCV)
        model : loaded YOLO model (pass from st.cache_resource)
        conf  : confidence threshold (0.0 – 1.0)

    Returns:
        annotated_frame : numpy array with bounding boxes drawn (BGR)
        detections      : list of dicts  {Object, Confidence, Bounding Box}
    """
    results   = model(frame, conf=conf, verbose=False)
    annotated = results[0].plot()          # auto-draws boxes, labels, conf

    detections = []
    for box in results[0].boxes:
        label      = model.names[int(box.cls)]
        confidence = float(box.conf)
        x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
        detections.append({
            "Object":       label,
            "Confidence":   f"{confidence:.0%}",
            "Bounding Box": f"({x1},{y1}) → ({x2},{y2})",
            "conf_raw":     confidence,   # keep raw float for sorting
        })

    # Sort by confidence descending
    detections.sort(key=lambda d: d["conf_raw"], reverse=True)

    # Remove internal raw field before returning
    for d in detections:
        d.pop("conf_raw", None)

    return annotated, detections


# ── Face Detection (dedicated, using OpenCV Haar cascade) ─────────────────────
def detect_faces(frame: np.ndarray) -> tuple:
    """
    Detect faces using OpenCV's Haar Cascade classifier.

    Returns:
        annotated_frame : numpy array with rectangles drawn around faces (BGR)
        face_count      : int — number of faces found
        face_boxes      : list of (x, y, w, h) tuples
    """
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # equalizeHist improves detection in low-light / uneven lighting
    gray  = cv2.equalizeHist(gray)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE,
    )

    annotated = frame.copy()
    face_boxes = []

    if len(faces) > 0:
        for (x, y, w, h) in faces:
            face_boxes.append((x, y, w, h))
            # Draw teal rectangle
            cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 210, 200), 2)
            # Label
            cv2.putText(
                annotated, "Face",
                (x, y - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 210, 200), 2,
            )

    return annotated, len(faces), face_boxes


# ── Face Blur (privacy protection) ───────────────────────────────────────────
def blur_faces(frame: np.ndarray, blur_strength: int = 51) -> tuple:
    """
    Detect faces and apply Gaussian blur for privacy protection.

    Args:
        frame         : numpy array (BGR)
        blur_strength : kernel size for Gaussian blur (must be odd number)

    Returns:
        blurred_frame : numpy array with faces blurred (BGR)
        face_count    : int — number of faces found and blurred
    """
    # Make blur_strength odd
    if blur_strength % 2 == 0:
        blur_strength += 1

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray  = cv2.equalizeHist(gray)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))

    blurred    = frame.copy()
    face_count = 0

    if len(faces) > 0:
        for (x, y, w, h) in faces:
            face_count += 1
            roi = blurred[y: y + h, x: x + w]
            roi = cv2.GaussianBlur(roi, (blur_strength, blur_strength), 0)
            blurred[y: y + h, x: x + w] = roi
            # Draw dashed border so viewer knows a face was here
            cv2.rectangle(blurred, (x, y), (x + w, y + h), (100, 100, 100), 1)

    return blurred, face_count


# ── Motion Detection ──────────────────────────────────────────────────────────
def detect_motion(frame1: np.ndarray, frame2: np.ndarray,
                  threshold: int = 25, min_area: int = 500) -> tuple:
    """
    Detect motion between two consecutive frames.

    Args:
        frame1    : earlier frame (BGR)
        frame2    : later frame (BGR)
        threshold : pixel-difference threshold (0-255)
        min_area  : minimum contour area to count as motion

    Returns:
        motion_frame   : frame2 with green boxes around motion regions (BGR)
        motion_pct     : float — percentage of pixels that changed
        motion_regions : int   — number of distinct motion regions found
    """
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

    # Blur to reduce noise
    gray1 = cv2.GaussianBlur(gray1, (21, 21), 0)
    gray2 = cv2.GaussianBlur(gray2, (21, 21), 0)

    diff         = cv2.absdiff(gray1, gray2)
    _, thresh    = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)
    thresh       = cv2.dilate(thresh, None, iterations=2)   # fill small gaps

    motion_pct   = (np.count_nonzero(thresh) / thresh.size) * 100

    contours, _  = cv2.findContours(thresh, cv2.RETR_EXTERNAL,
                                     cv2.CHAIN_APPROX_SIMPLE)
    motion_frame   = frame2.copy()
    motion_regions = 0

    for c in contours:
        if cv2.contourArea(c) > min_area:
            motion_regions += 1
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(motion_frame, (x, y), (x + w, y + h),
                          (0, 255, 0), 2)
            cv2.putText(
                motion_frame, "Motion",
                (x, y - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2,
            )

    return motion_frame, round(motion_pct, 2), motion_regions


# ── Scan Video for Key Events ─────────────────────────────────────────────────
def scan_video_for_events(video_path: str, model,
                           sample_every: int = 30,
                           conf: float = 0.25) -> list:
    """
    Scan entire video, sampling every `sample_every` frames,
    and return a list of events (frame number + detections).

    Returns:
        events : list of dicts {frame, timestamp_sec, detections, object_count}
    """
    cap    = cv2.VideoCapture(video_path)
    fps    = cap.get(cv2.CAP_PROP_FPS) or 25
    events = []
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % sample_every == 0:
            _, detections = detect_objects(frame, model, conf=conf)
            if detections:
                events.append({
                    "frame":          frame_idx,
                    "timestamp_sec":  round(frame_idx / fps, 2),
                    "timestamp":      _sec_to_hms(frame_idx / fps),
                    "detections":     detections,
                    "object_count":   len(detections),
                    "objects_found":  list({d["Object"] for d in detections}),
                })
        frame_idx += 1

    cap.release()
    return events


def _sec_to_hms(seconds: float) -> str:
    """Convert seconds to HH:MM:SS string."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"
