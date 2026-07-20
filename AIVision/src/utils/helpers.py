"""Shared helper functions used across the ai-vision pipeline."""

import json
import os
from datetime import datetime, timedelta, timezone

import yaml


def load_config(config_path: str) -> dict:
    """Load the YAML pipeline configuration file."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def load_camera_info(camera_info_path: str) -> dict:
    """Load static camera metadata (id, location, resolution, fps)."""
    with open(camera_info_path, "r") as f:
        return json.load(f)


def ensure_output_dirs(config: dict) -> None:
    """Create all output directories declared in the config if they don't exist."""
    out = config["output"]
    for key in ("crops_dir", "annotated_video_dir", "metadata_dir"):
        os.makedirs(out[key], exist_ok=True)


def frame_index_to_timestamp(frame_idx: int, fps: float, base_time: datetime = None) -> str:
    """Convert a frame index into an ISO-8601 timestamp string.

    If `base_time` isn't given, timestamps are relative to "now" at pipeline start,
    which is fine for offline processing where only relative timing matters.
    """
    base_time = base_time or datetime.now(timezone.utc)
    elapsed_seconds = frame_idx / fps if fps > 0 else 0
    ts = base_time + timedelta(seconds=elapsed_seconds)
    return ts.isoformat()


def make_track_key(camera_id: str, tracker_id: int) -> str:
    """Build a globally-unique track id by namespacing the tracker's local id with the camera id."""
    return f"{camera_id}_{int(tracker_id):05d}"
