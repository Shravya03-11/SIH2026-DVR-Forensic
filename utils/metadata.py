"""
utils/metadata.py — Video Metadata Extraction Utility
ASSIGNED TO: Member 3
YOUR TASKS:
  [ ] The extract_metadata function is ready — test it with your video
  [ ] Add a function to detect if timestamps are suspicious (e.g., year 1970 = reset to epoch)
  [ ] Add UTC conversion for timestamps
"""

import os
import datetime


def extract_metadata(filepath: str) -> dict:
    """
    Extract metadata from a video file using OpenCV (no moviepy needed).
    Returns a dict of video properties.
    """
    import cv2

    cap = cv2.VideoCapture(filepath)

    if not cap.isOpened():
        return {"error": "Could not open video file"}

    fps       = cap.get(cv2.CAP_PROP_FPS)
    width     = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height    = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frames    = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration  = frames / fps if fps > 0 else 0

    cap.release()

    file_stat = os.stat(filepath)
    created_at = datetime.datetime.fromtimestamp(file_stat.st_ctime)

    return {
        "Duration (seconds)": round(duration, 2),
        "Duration (readable)": str(datetime.timedelta(seconds=int(duration))),
        "FPS":                 round(fps, 2),
        "Width (px)":          width,
        "Height (px)":         height,
        "Resolution":          f"{width} x {height}",
        "Total Frames":        frames,
        "File Size (MB)":      round(file_stat.st_size / (1024 * 1024), 2),
        "File Created":        created_at.strftime("%Y-%m-%d %H:%M:%S"),
    }


def normalize_timestamp(raw_timestamp: str, source_timezone: str = "IST") -> str:
    """
    Normalize a timestamp to UTC.
    TODO (Member 3): Implement proper timezone conversion using pytz or datetime
    """
    # Placeholder — Member 3 should implement real timezone conversion
    return f"{raw_timestamp} (UTC+0 normalized)"


def generate_timeline_data(metadata: dict, num_cameras: int = 4) -> list:
    """
    Generate fake multi-camera timeline data for visualization.
    TODO (Member 3): Replace with real extracted timestamps when available
    """
    import random
    base_time = datetime.datetime(2024, 8, 15, 14, 0, 0)
    events = []

    for cam in range(1, num_cameras + 1):
        start_offset = random.randint(0, 600)
        duration     = random.randint(300, 3600)
        start        = base_time + datetime.timedelta(seconds=start_offset)
        end          = start + datetime.timedelta(seconds=duration)

        events.append({
            "Camera":     f"CAM-{cam:02d}",
            "Start Time": start.strftime("%Y-%m-%d %H:%M:%S"),
            "End Time":   end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration":   f"{duration // 60}m {duration % 60}s",
            "Status":     random.choice(["✅ Normal", "✅ Normal", "⚠️ Motion Detected", "🔴 Gap Detected"]),
            "Start":      start,
            "Finish":     end,
            "Task":       f"CAM-{cam:02d}",
        })

    return events
