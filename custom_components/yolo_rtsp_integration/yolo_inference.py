import os
from typing import List

MODEL_DIR = "models"  # Relative to integration directory
# Folder simpan model YOLO
MODEL_EXTENSIONS = [".pt", ".onnx"]  # Supported YOLO model formats
# Jenis fail model yang disokong

def get_model_dir(base_path: str) -> str:
    """Return the absolute path to the model directory, create if missing.
    # Dapatkan lokasi folder model, buat kalau tak ada"""
    model_dir = os.path.join(base_path, MODEL_DIR)
    os.makedirs(model_dir, exist_ok=True)
    return model_dir

def list_models(base_path: str) -> List[str]:
    """List all available YOLO models in the model directory.
    # Senaraikan semua model YOLO yang ada dalam folder"""
    model_dir = get_model_dir(base_path)
    return [f for f in os.listdir(model_dir)
            if os.path.isfile(os.path.join(model_dir, f)) and os.path.splitext(f)[1] in MODEL_EXTENSIONS]

# All inference/model logic is now handled by the external YOLO API.
# This file is now a stub or can be removed if not used by UI.
def load_yolo_model(model_path: str):
    """Load a YOLO model from file. Supports YOLOv5/YOLOv8 via ultralytics/torch.hub.
    # Baca model YOLO dari fail. Support YOLOv5/v8."""
    try:
        # Try YOLOv5/YOLOv8 via ultralytics if available
        # Cuba guna ultralytics dulu kalau ada
        from ultralytics import YOLO
        model = YOLO(model_path)
        return model
    except ImportError:
        # Fallback to torch.hub for YOLOv5
        # Kalau tak jumpa, guna torch.hub untuk YOLOv5
        try:
            model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path, force_reload=True)
            return model
        except Exception as e:
            print(f"Error loading YOLO model: {e}")  # Gagal baca model YOLO
            return None
    except Exception as e:
        print(f"Error loading YOLO model: {e}")
        return None

def validate_yolo_model(model) -> Tuple[bool, str]:
    """Validate the YOLO model for compatibility.
    # Semak model YOLO ni boleh pakai ke tak"""
    try:
        # Check for required attributes
        # Semak ada ciri-ciri penting tak
        if hasattr(model, 'names') or hasattr(model, 'model'):
            return True, ""
        return False, "Model does not have required attributes."
    except Exception as e:
        return False, str(e)

def run_inference(model, image: np.ndarray) -> Tuple[np.ndarray, list]:
    """Run YOLO inference on an image. Returns image with boxes and detection JSON list.
    # Jalankan inference YOLO atas gambar. Bagi balik gambar dengan kotak dan senarai JSON objek."""
    try:
        # YOLOv8 (ultralytics)
        # Kalau model YOLOv8
        if hasattr(model, 'predict'):
            results = model.predict(image)
            boxes = results[0].boxes.xyxy.cpu().numpy() if hasattr(results[0], 'boxes') else []
            scores = results[0].boxes.conf.cpu().numpy() if hasattr(results[0], 'boxes') else []
            classes = results[0].boxes.cls.cpu().numpy() if hasattr(results[0], 'boxes') else []
            names = model.names if hasattr(model, 'names') else results[0].names
        else:
            # YOLOv5 (torch.hub)
            # Kalau model YOLOv5
            results = model(image)
            boxes = results.xyxy[0].cpu().numpy() if hasattr(results, 'xyxy') else []
            scores = boxes[:, 4] if boxes.shape[0] > 0 else []
            classes = boxes[:, 5] if boxes.shape[0] > 0 else []
            names = model.names if hasattr(model, 'names') else {}

        detections = []  # Senarai objek dikesan
        h, w = image.shape[:2]
        for i, box in enumerate(boxes):
            x1, y1, x2, y2 = map(int, box[:4])
            conf = float(scores[i]) if len(scores) > i else 0.0
            cls = int(classes[i]) if len(classes) > i else -1
            label = names[cls] if isinstance(names, dict) and cls in names else str(cls)
            # Draw rectangle
            # Lukis kotak kat gambar
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(image, f"{label} {conf:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
            # Calculate area
            # Kira keluasan objek
            obj_area = ((x2 - x1) * (y2 - y1)) / (w * h)
            # Determine recyclable
            # Semak boleh kitar semula ke tak
            recyclable = label in ["Glass", "Metal", "Paper", "Plastic"]
            detections.append({
                "class": label,
                "confidence": conf,
                "object_area": round(obj_area, 3),
                "recyclable": recyclable
            })
        return image, detections
    except Exception as e:
        print(f"Error during inference: {e}")  # Ada masalah masa inference
        return image, []
