import cv2
import os
from typing import List, Optional
from PIL import Image
import numpy as np


def fetch_single_frame(rtsp_url: str, timeout: int = 5) -> Optional[np.ndarray]:
    """Fetch a single frame from the RTSP camera.
    # Ambil satu gambar dari kamera RTSP"""
    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        print(f"Error: Cannot open RTSP stream: {rtsp_url}")
        return None
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        print("Error: Failed to read frame from RTSP stream.")  # Gagal baca gambar dari RTSP
        return None
    return frame


def fetch_frame_sequence(rtsp_url: str, count: int = 5, interval: int = 1) -> List[np.ndarray]:
    """Fetch a sequence of frames from the RTSP camera.
    # Ambil beberapa gambar (sequence) dari kamera RTSP"""
    frames = []
    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        print(f"Error: Cannot open RTSP stream: {rtsp_url}")
        return frames
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    for i in range(count):
        ret, frame = cap.read()
        if not ret:
            print(f"Warning: Failed to read frame {i+1} from RTSP stream.")  # Gagal baca gambar ke-{i+1}
            break
        frames.append(frame)
        # Skip frames for interval
        # Lompat frame ikut interval
        for _ in range(interval - 1):
            cap.read()
    cap.release()
    return frames


def load_manual_image(image_path: str) -> Optional[np.ndarray]:
    """Load a manually uploaded image (for testing).
    # Baca gambar yang upload sendiri (untuk test)"""
    if not os.path.exists(image_path):
        print(f"Error: Manual image not found at {image_path}")  # Tak jumpa gambar manual
        return None
    try:
        img = Image.open(image_path)
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"Error loading manual image: {e}")  # Gagal baca gambar manual
        return None
