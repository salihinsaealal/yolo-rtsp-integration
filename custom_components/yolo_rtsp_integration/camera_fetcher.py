import requests
from typing import Optional, Dict, Any

# These functions now send requests to the external YOLO API.

EXTERNAL_API_URL = None  # Will be set from config


def set_external_api_url(url: str):
    global EXTERNAL_API_URL
    EXTERNAL_API_URL = url


def fetch_single_frame(rtsp_url: str) -> Optional[Dict[str, Any]]:
    """Send RTSP URL to external YOLO API for single frame inference.
    Return API response (dict) or None on error."""
    if not EXTERNAL_API_URL:
        print("External YOLO API URL not set.")
        return None
    try:
        resp = requests.post(EXTERNAL_API_URL + "/inference", json={"rtsp_url": rtsp_url, "mode": "single"}, timeout=30)
        if resp.status_code == 200:
            return resp.json()
        print(f"API error: {resp.status_code} {resp.text}")
        return None
    except Exception as e:
        print(f"Error contacting external YOLO API: {e}")
        return None


def fetch_frame_sequence(rtsp_url: str, count: int = 5, interval: int = 1) -> Optional[Dict[str, Any]]:
    """Send RTSP URL to external YOLO API for sequence inference."""
    if not EXTERNAL_API_URL:
        print("External YOLO API URL not set.")
        return None
    try:
        resp = requests.post(EXTERNAL_API_URL + "/inference", json={"rtsp_url": rtsp_url, "mode": "sequence", "count": count, "interval": interval}, timeout=60)
        if resp.status_code == 200:
            return resp.json()
        print(f"API error: {resp.status_code} {resp.text}")
        return None
    except Exception as e:
        print(f"Error contacting external YOLO API: {e}")
        return None


def load_manual_image(image_path: str) -> Optional[Dict[str, Any]]:
    """Send manual image file to external YOLO API for inference."""
    if not EXTERNAL_API_URL:
        print("External YOLO API URL not set.")
        return None
    try:
        with open(image_path, "rb") as f:
            files = {"image": f}
            resp = requests.post(EXTERNAL_API_URL + "/inference", files=files, data={"mode": "manual"}, timeout=30)
            if resp.status_code == 200:
                return resp.json()
            print(f"API error: {resp.status_code} {resp.text}")
            return None
    except Exception as e:
        print(f"Error contacting external YOLO API: {e}")
        return None
