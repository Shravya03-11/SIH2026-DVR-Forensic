"""
utils/metadata.py — Video Metadata & Forensic Timeline Utility
ASSIGNED TO: Member 3

Responsibilities:
- Extract real video metadata
- Extract available creation/start timestamps
- Detect suspicious timestamps
- Convert timestamps to UTC
- Generate timeline for actual recordings
- Extract evidence frames
- Provide forensic observations
"""

import os
import datetime
import subprocess
import json
from zoneinfo import ZoneInfo


# ============================================================
# BASIC HELPERS
# ============================================================

def format_duration(seconds: float) -> str:
    """Convert seconds into HH:MM:SS format."""

    seconds = max(0, float(seconds))

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def format_timestamp(seconds: float) -> str:
    """Convert video position into HH:MM:SS.ms."""

    seconds = max(0, float(seconds))

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    milliseconds = int(round((seconds - int(seconds)) * 1000))

    if milliseconds == 1000:
        secs += 1
        milliseconds = 0

    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{milliseconds:03d}"


# ============================================================
# FFPROBE
# ============================================================

def get_ffprobe_metadata(filepath: str) -> dict:
    """
    Extract detailed container and video-stream metadata
    using FFprobe.
    """

    try:
        command = [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            filepath,
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return {}

        data = json.loads(result.stdout)

        output = {}

        fmt = data.get("format", {})
        tags = fmt.get("tags", {}) or {}

        output["format"] = fmt.get("format_name")
        output["format_long_name"] = fmt.get("format_long_name")
        output["format_duration"] = fmt.get("duration")
        output["bit_rate"] = fmt.get("bit_rate")

        # Case-insensitive metadata lookup
        normalized_tags = {
            str(k).lower(): v
            for k, v in tags.items()
        }

        creation_time = (
            normalized_tags.get("creation_time")
            or normalized_tags.get("date")
            or normalized_tags.get("datetime")
            or normalized_tags.get("creationdate")
        )

        output["creation_time"] = creation_time

        # Find first video stream
        for stream in data.get("streams", []):

            if stream.get("codec_type") != "video":
                continue

            stream_tags = stream.get("tags", {}) or {}

            normalized_stream_tags = {
                str(k).lower(): v
                for k, v in stream_tags.items()
            }

            output["codec"] = stream.get("codec_name")
            output["codec_long_name"] = stream.get(
                "codec_long_name"
            )
            output["profile"] = stream.get("profile")

            output["pixel_format"] = stream.get(
                "pix_fmt"
            )

            output["color_space"] = stream.get(
                "color_space"
            )

            output["bit_rate"] = (
                stream.get("bit_rate")
                or output.get("bit_rate")
            )

            output["stream_duration"] = stream.get(
                "duration"
            )

            output["start_time"] = stream.get(
                "start_time"
            )

            if not output.get("creation_time"):
                output["creation_time"] = (
                    normalized_stream_tags.get(
                        "creation_time"
                    )
                )

            # Frame rate
            output["avg_frame_rate"] = stream.get(
                "avg_frame_rate"
            )

            output["r_frame_rate"] = stream.get(
                "r_frame_rate"
            )

            break

        return output

    except (
        FileNotFoundError,
        subprocess.SubprocessError,
        json.JSONDecodeError,
        OSError,
    ):
        return {}


# ============================================================
# METADATA EXTRACTION
# ============================================================

def extract_metadata(filepath: str) -> dict:
    """
    Extract real metadata from a video using OpenCV
    and FFprobe.
    """

    import cv2

    cap = cv2.VideoCapture(filepath)

    if not cap.isOpened():
        return {
            "error": "Could not open video file"
        }

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(
        cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    )
    height = int(
        cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    )
    frames = int(
        cap.get(cv2.CAP_PROP_FRAME_COUNT)
    )

    duration = (
        frames / fps
        if fps > 0
        else 0
    )

    cap.release()

    file_stat = os.stat(filepath)

    created_at = datetime.datetime.fromtimestamp(
        file_stat.st_ctime
    )

    metadata = {
        "File Name": os.path.basename(filepath),

        "Duration (seconds)": round(
            duration,
            2,
        ),

        "Duration (readable)": format_duration(
            duration
        ),

        "FPS": round(
            fps,
            2,
        ),

        "Width (px)": width,

        "Height (px)": height,

        "Resolution": (
            f"{width} x {height}"
        ),

        "Total Frames": frames,

        "File Size (MB)": round(
            file_stat.st_size
            / (1024 * 1024),
            2,
        ),

        "File Created": created_at.strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
    }

    # --------------------------------------------------------
    # FFprobe metadata
    # --------------------------------------------------------

    ffprobe_data = get_ffprobe_metadata(
        filepath
    )

    if ffprobe_data.get("creation_time"):

        metadata["Embedded Creation Time"] = (
            ffprobe_data["creation_time"]
        )

    if ffprobe_data.get("format"):

        metadata["Container Format"] = (
            ffprobe_data["format"]
        )

    if ffprobe_data.get("format_long_name"):

        metadata["Container Description"] = (
            ffprobe_data["format_long_name"]
        )

    if ffprobe_data.get("codec"):

        metadata["Video Codec"] = (
            ffprobe_data["codec"]
        )

    if ffprobe_data.get("codec_long_name"):

        metadata["Codec Description"] = (
            ffprobe_data["codec_long_name"]
        )

    if ffprobe_data.get("profile"):

        metadata["Codec Profile"] = (
            ffprobe_data["profile"]
        )

    if ffprobe_data.get("pixel_format"):

        metadata["Pixel Format"] = (
            ffprobe_data["pixel_format"]
        )

    if ffprobe_data.get("start_time") is not None:

        metadata["Video Start Time"] = (
            ffprobe_data["start_time"]
        )

    if ffprobe_data.get("bit_rate"):

        try:
            bitrate = float(
                ffprobe_data["bit_rate"]
            )

            metadata["Bitrate (kbps)"] = round(
                bitrate / 1000,
                2,
            )

        except (
            ValueError,
            TypeError,
        ):
            pass

    # --------------------------------------------------------
    # Timestamp analysis
    # --------------------------------------------------------

    embedded_timestamp = metadata.get(
        "Embedded Creation Time"
    )

    if embedded_timestamp:

        suspicious = is_suspicious_timestamp(
            embedded_timestamp
        )

        metadata["Timestamp Status"] = (
            "⚠️ Suspicious / Invalid"
            if suspicious
            else "✅ Valid"
        )

        metadata["Normalized UTC"] = (
            normalize_timestamp(
                embedded_timestamp
            )
        )

        metadata["Timestamp Source"] = (
            "Embedded video metadata"
        )

    else:

        metadata["Timestamp Status"] = (
            "ℹ️ No embedded timestamp found"
        )

        metadata["Normalized UTC"] = (
            "Not available"
        )

        metadata["Timestamp Source"] = (
            "File system timestamp only"
        )

    return metadata


# ============================================================
# TIMESTAMP FORENSICS
# ============================================================

def parse_timestamp(
    timestamp,
    source_timezone="Asia/Kolkata",
):
    """
    Parse a timestamp into an aware datetime object.
    """

    if timestamp is None:
        return None

    try:

        raw = str(timestamp).strip()

        # Unix epoch
        if raw.isdigit():

            value = int(raw)

            return datetime.datetime.fromtimestamp(
                value,
                tz=datetime.timezone.utc,
            )

        cleaned = raw

        if cleaned.endswith("Z"):

            cleaned = (
                cleaned[:-1]
                + "+00:00"
            )

        try:

            dt = datetime.datetime.fromisoformat(
                cleaned
            )

        except ValueError:

            formats = [
                "%d-%m-%Y %H:%M:%S",
                "%Y-%m-%d %H:%M:%S",
                "%m/%d/%y %H:%M:%S",
                "%Y:%m:%d %H:%M:%S",
                "%d/%m/%Y %H:%M:%S",
            ]

            dt = None

            for fmt in formats:

                try:

                    dt = datetime.datetime.strptime(
                        cleaned,
                        fmt,
                    )

                    break

                except ValueError:
                    continue

            if dt is None:
                return None

        if dt.tzinfo is None:

            dt = dt.replace(
                tzinfo=ZoneInfo(
                    source_timezone
                )
            )

        return dt

    except (
        ValueError,
        TypeError,
        OverflowError,
        OSError,
    ):
        return None


def is_suspicious_timestamp(
    timestamp,
) -> bool:
    """
    Detect timestamps that may indicate an incorrectly
    configured or reset DVR clock.

    Dates before 2000 are treated as suspicious.
    """

    dt = parse_timestamp(
        timestamp
    )

    if dt is None:
        return True

    return dt.year < 2000


def get_timestamp_reason(
    timestamp,
) -> str:
    """
    Explain why a timestamp is suspicious or valid.
    """

    if timestamp is None:
        return "No timestamp was found."

    dt = parse_timestamp(
        timestamp
    )

    if dt is None:
        return (
            "Timestamp format could not be interpreted."
        )

    if dt.year < 2000:

        if dt.year == 1970:

            return (
                "Timestamp is near the Unix epoch "
                "(1970), which may indicate a reset "
                "or missing DVR clock."
            )

        return (
            "Timestamp is earlier than 2000 and "
            "may not represent a genuine recording date."
        )

    return (
        "Timestamp falls within a modern date range."
    )


def normalize_timestamp(
    raw_timestamp: str,
    source_timezone: str = "Asia/Kolkata",
) -> str:
    """
    Convert a source/DVR timestamp to UTC.
    """

    dt = parse_timestamp(
        raw_timestamp,
        source_timezone,
    )

    if dt is None:

        return (
            f"Invalid timestamp: "
            f"{raw_timestamp}"
        )

    utc_dt = dt.astimezone(
        datetime.timezone.utc
    )

    return utc_dt.strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )


# ============================================================
# RECORDING TIMELINE
# ============================================================

def get_file_creation_datetime(
    metadata: dict,
) -> datetime.datetime:
    """
    Retrieve the file creation timestamp.
    """

    created = metadata.get(
        "File Created"
    )

    try:

        dt = datetime.datetime.strptime(
            created,
            "%Y-%m-%d %H:%M:%S",
        )

        return dt.astimezone()

    except (
        ValueError,
        TypeError,
    ):

        return datetime.datetime.now().astimezone()


def get_recording_timeline(
    metadata: dict,
    camera_name: str = "CAM-01",
) -> list:
    """
    Create a timeline using the actual video metadata.

    Suspicious embedded timestamps are never treated
    as trustworthy recording dates.
    """

    duration = float(
        metadata.get(
            "Duration (seconds)",
            0,
        )
    )

    embedded_timestamp = metadata.get(
        "Embedded Creation Time"
    )

    embedded_is_suspicious = (
        is_suspicious_timestamp(
            embedded_timestamp
        )
        if embedded_timestamp
        else False
    )

    # --------------------------------------------------------
    # Determine recording start
    # --------------------------------------------------------

    start = None
    timestamp_source = ""

    if (
        embedded_timestamp
        and not embedded_is_suspicious
    ):

        start = parse_timestamp(
            embedded_timestamp
        )

        if start:

            timestamp_source = (
                "Embedded video timestamp"
            )

    if start is None:

        start = get_file_creation_datetime(
            metadata
        )

        if embedded_timestamp:

            timestamp_source = (
                "File creation timestamp "
                "(embedded timestamp suspicious "
                "or unavailable)"
            )

        else:

            timestamp_source = (
                "File creation timestamp "
                "(no embedded timestamp)"
            )

    finish = (
        start
        + datetime.timedelta(
            seconds=duration
        )
    )

    # --------------------------------------------------------
    # Status
    # --------------------------------------------------------

    if embedded_is_suspicious:

        status = (
            "⚠️ Suspicious Timestamp"
        )

    elif embedded_timestamp:

        status = "✅ Normal"

    else:

        status = (
            "ℹ️ No Embedded Timestamp"
        )

    return [
        {
            "Camera": camera_name,

            "Start Time": start.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

            "End Time": finish.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

            "Duration": format_duration(
                duration
            ),

            "Status": status,

            "Timestamp Source": (
                timestamp_source
            ),

            "Start": start,

            "Finish": finish,

            "Task": camera_name,
        }
    ]


def generate_timeline_data(
    metadata: dict,
    num_cameras: int = 1,
) -> list:
    """
    Backward-compatible wrapper.

    Does NOT generate fake camera data.
    """

    return get_recording_timeline(
        metadata,
        camera_name="CAM-01",
    )


# ============================================================
# MULTIPLE EVIDENCE FILE TIMELINE
# ============================================================

def build_multi_camera_timeline(
    metadata_list: list,
) -> list:
    """
    Build a timeline from multiple actual evidence files.

    Each metadata dictionary represents one uploaded
    camera/evidence recording.
    """

    timeline = []

    for index, metadata in enumerate(
        metadata_list,
        start=1,
    ):

        camera_name = (
            metadata.get(
                "Camera",
                f"CAM-{index:02d}",
            )
        )

        events = get_recording_timeline(
            metadata,
            camera_name=camera_name,
        )

        timeline.extend(events)

    return timeline


def detect_timeline_gaps(
    timeline: list,
) -> list:
    """
    Detect gaps between recordings after sorting
    timeline events chronologically.
    """

    if len(timeline) < 2:
        return []

    sorted_events = sorted(
        timeline,
        key=lambda item: item["Start"],
    )

    gaps = []

    for previous, current in zip(
        sorted_events,
        sorted_events[1:],
    ):

        if current["Start"] > previous["Finish"]:

            gap_seconds = (
                current["Start"]
                - previous["Finish"]
            ).total_seconds()

            gaps.append(
                {
                    "Camera": current["Camera"],
                    "Gap Start": previous["Finish"],
                    "Gap End": current["Start"],
                    "Gap Duration": format_duration(
                        gap_seconds
                    ),
                    "Gap Seconds": round(
                        gap_seconds,
                        2,
                    ),
                    "Status": "🔴 Recording Gap",
                }
            )

    return gaps


# ============================================================
# EVIDENCE FRAME EXTRACTION
# ============================================================

def extract_frame(
    filepath: str,
    timestamp_seconds: float,
):
    """
    Extract a frame at a specific video position.

    Returns:
        frame_rgb, frame_number, actual_seconds
    """

    import cv2

    cap = cv2.VideoCapture(
        filepath
    )

    if not cap.isOpened():
        return None, None, None

    fps = cap.get(
        cv2.CAP_PROP_FPS
    )

    if fps <= 0:
        fps = 25.0

    total_frames = int(
        cap.get(
            cv2.CAP_PROP_FRAME_COUNT
        )
    )

    duration = (
        total_frames / fps
        if total_frames > 0
        else 0
    )

    timestamp_seconds = max(
        0,
        min(
            float(timestamp_seconds),
            max(0, duration - 0.001),
        ),
    )

    frame_number = int(
        round(
            timestamp_seconds * fps
        )
    )

    frame_number = max(
        0,
        min(
            frame_number,
            max(0, total_frames - 1),
        ),
    )

    cap.set(
        cv2.CAP_PROP_POS_FRAMES,
        frame_number,
    )

    success, frame = cap.read()

    actual_frame = cap.get(
        cv2.CAP_PROP_POS_FRAMES
    )

    cap.release()

    if not success:
        return None, None, None

    actual_frame_number = max(
        0,
        int(actual_frame) - 1,
    )

    actual_seconds = (
        actual_frame_number / fps
    )

    frame_rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB,
    )

    return (
        frame_rgb,
        actual_frame_number,
        actual_seconds,
    )


def generate_evidence_frames(
    filepath: str,
    number_of_frames: int = 6,
) -> list:
    """
    Extract evenly spaced evidence frames from
    the actual uploaded video.
    """

    import cv2

    cap = cv2.VideoCapture(
        filepath
    )

    if not cap.isOpened():
        return []

    fps = cap.get(
        cv2.CAP_PROP_FPS
    )

    total_frames = int(
        cap.get(
            cv2.CAP_PROP_FRAME_COUNT
        )
    )

    cap.release()

    if fps <= 0 or total_frames <= 0:
        return []

    duration = (
        total_frames / fps
    )

    number_of_frames = max(
        1,
        min(
            int(number_of_frames),
            12,
        ),
    )

    if number_of_frames == 1:

        positions = [0]

    else:

        positions = [
            i * duration
            / (number_of_frames - 1)
            for i in range(
                number_of_frames
            )
        ]

    evidence = []

    for index, position in enumerate(
        positions
    ):

        (
            frame,
            frame_number,
            actual_seconds,
        ) = extract_frame(
            filepath,
            position,
        )

        if frame is None:
            continue

        evidence.append(
            {
                "Index": index + 1,
                "Frame Number": frame_number,
                "Timestamp Seconds": round(
                    actual_seconds,
                    3,
                ),
                "Timestamp": format_timestamp(
                    actual_seconds
                ),
                "Position (%)": round(
                    (
                        actual_seconds
                        / duration
                        * 100
                    )
                    if duration > 0
                    else 0,
                    1,
                ),
                "Frame": frame,
            }
        )

    return evidence


# ============================================================
# FORENSIC FINDINGS
# ============================================================

def generate_forensic_findings(
    metadata: dict,
) -> list:
    """
    Generate human-readable observations based only
    on the actual extracted metadata.
    """

    findings = []

    embedded = metadata.get(
        "Embedded Creation Time"
    )

    # Timestamp
    if embedded:

        if is_suspicious_timestamp(
            embedded
        ):

            findings.append(
                {
                    "Severity": "WARNING",
                    "Finding": (
                        "Suspicious embedded timestamp"
                    ),
                    "Details": (
                        f"The source contains "
                        f"'{embedded}'. "
                        f"{get_timestamp_reason(embedded)}"
                    ),
                }
            )

        else:

            findings.append(
                {
                    "Severity": "INFO",
                    "Finding": (
                        "Embedded timestamp available"
                    ),
                    "Details": (
                        "A recording timestamp was found "
                        "inside the video metadata and "
                        "can be normalized to UTC."
                    ),
                }
            )

    else:

        findings.append(
            {
                "Severity": "INFO",
                "Finding": (
                    "No embedded recording timestamp"
                ),
                "Details": (
                    "The source file does not expose a "
                    "usable creation timestamp through "
                    "the available metadata."
                ),
            }
        )

    # Codec
    codec = metadata.get(
        "Video Codec"
    )

    if codec:

        findings.append(
            {
                "Severity": "INFO",
                "Finding": (
                    "Video stream successfully identified"
                ),
                "Details": (
                    f"Detected video codec: {codec}."
                ),
            }
        )

    # Resolution
    width = metadata.get(
        "Width (px)",
        0,
    )

    height = metadata.get(
        "Height (px)",
        0,
    )

    if width and height:

        findings.append(
            {
                "Severity": "INFO",
                "Finding": (
                    "Video dimensions available"
                ),
                "Details": (
                    f"Recorded at {width} × {height}."
                ),
            }
        )

    # Duration
    duration = float(
        metadata.get(
            "Duration (seconds)",
            0,
        )
    )

    if duration > 0:

        findings.append(
            {
                "Severity": "INFO",
                "Finding": (
                    "Recording duration verified"
                ),
                "Details": (
                    f"Detected recording length: "
                    f"{format_duration(duration)}."
                ),
            }
        )

    return findings