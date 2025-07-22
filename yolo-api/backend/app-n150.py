from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import os
import cv2
import numpy as np
from ultralytics import YOLO
import json
import uuid
from datetime import datetime
import shutil
from PIL import Image
import io
import base64
import torch
import gc
import psutil

# N150 optimizations
torch.set_num_threads(2)  # Limit threads for N150
os.environ['OMP_NUM_THREADS'] = '2'
os.environ['MKL_NUM_THREADS'] = '2'

# Note: PyTorch 2.0.1 doesn't have add_safe_globals, but weights_only defaults to False

app = Flask(__name__, static_folder='/app/frontend/build/static', static_url_path='/static')
CORS(app)

# Configuration
MODELS_DIR = "/app/models"
UPLOADS_DIR = "/app/uploads"
RESULTS_DIR = "/app/results"

# Ensure directories exist
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Store loaded models in memory (limit to 1 for N150)
loaded_models = {}
MAX_LOADED_MODELS = 1

def get_memory_usage():
    """Get current memory usage"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # MB

def clear_model_cache():
    """Clear model cache to free memory"""
    global loaded_models
    loaded_models.clear()
    gc.collect()
    torch.cuda.empty_cache() if torch.cuda.is_available() else None

def get_model_info(model_path):
    """Get model information"""
    try:
        stat = os.stat(model_path)
        return {
            "name": os.path.basename(model_path),
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "path": model_path
        }
    except Exception as e:
        return None

def load_model(model_path):
    """Load YOLO model with caching and memory management"""
    global loaded_models
    
    # Clear cache if we have too many models loaded
    if len(loaded_models) >= MAX_LOADED_MODELS:
        clear_model_cache()
    
    if model_path in loaded_models:
        return loaded_models[model_path]
    
    try:
        print(f"Loading model: {model_path}")
        print(f"Memory before loading: {get_memory_usage():.1f} MB")
        
        # Load model with CPU device explicitly (PyTorch 2.0.1 defaults to weights_only=False)
        model = YOLO(model_path)
        model.to('cpu')  # Ensure CPU inference
        
        loaded_models[model_path] = model
        
        print(f"Memory after loading: {get_memory_usage():.1f} MB")
        
        return model
    except Exception as e:
        print(f"Error loading model {model_path}: {e}")
        return None

def fetch_rtsp_frame(rtsp_url, timeout=10):
    """Fetch single frame from RTSP stream"""
    try:
        cap = cv2.VideoCapture(rtsp_url)
        cap.set(cv2.CAP_PROP_TIMEOUT, timeout * 1000)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer for N150
        
        if not cap.isOpened():
            return None, "Cannot open RTSP stream"
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return None, "Failed to read frame from RTSP stream"
        
        return frame, None
    except Exception as e:
        return None, str(e)

def run_inference(model, image):
    """Run YOLO inference on image with N150 optimizations"""
    try:
        print(f"Starting inference, memory: {get_memory_usage():.1f} MB")
        
        # Resize image if too large (N150 optimization)
        h, w = image.shape[:2]
        if max(h, w) > 640:
            scale = 640 / max(h, w)
            new_w, new_h = int(w * scale), int(h * scale)
            image = cv2.resize(image, (new_w, new_h))
            print(f"Resized image from {w}x{h} to {new_w}x{new_h}")
        
        # Use model.predict() with N150-specific settings
        results = model.predict(
            source=image,
            conf=0.25,
            verbose=False,
            device='cpu',
            half=False,  # Disable half precision for CPU
            augment=False,  # Disable augmentation for speed
            agnostic_nms=False,  # Standard NMS
            max_det=100  # Limit detections for memory
        )
        
        # Draw results on image
        annotated_image = results[0].plot()
        
        # Extract detection data
        detections = []
        if results[0].boxes is not None:
            boxes = results[0].boxes
            for i in range(len(boxes)):
                box = boxes.xyxy[i].cpu().numpy()
                conf = float(boxes.conf[i].cpu().numpy())
                cls = int(boxes.cls[i].cpu().numpy())
                
                # Get class name
                class_name = model.names[cls] if cls in model.names else str(cls)
                
                # Calculate area
                x1, y1, x2, y2 = box
                area = (x2 - x1) * (y2 - y1)
                img_area = image.shape[0] * image.shape[1]
                relative_area = area / img_area
                
                detections.append({
                    "class": class_name,
                    "confidence": round(conf, 3),
                    "bbox": [int(x1), int(y1), int(x2), int(y2)],
                    "area": round(relative_area, 4)
                })
        
        print(f"Inference complete, memory: {get_memory_usage():.1f} MB")
        
        # Force garbage collection after inference
        gc.collect()
        
        return annotated_image, detections, None
    except Exception as e:
        print(f"Inference error: {e}")
        print(f"Memory during error: {get_memory_usage():.1f} MB")
        return None, [], str(e)

# API Routes (same as original, just using optimized functions)

@app.route('/api/models', methods=['GET'])
def list_models():
    """List all available models"""
    try:
        models = []
        for filename in os.listdir(MODELS_DIR):
            if filename.endswith(('.pt', '.onnx', '.engine')):
                model_path = os.path.join(MODELS_DIR, filename)
                info = get_model_info(model_path)
                if info:
                    models.append(info)
        
        return jsonify({"models": models})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/models', methods=['POST'])
def upload_model():
    """Upload a new model"""
    try:
        if 'model' not in request.files:
            return jsonify({"error": "No model file provided"}), 400
        
        file = request.files['model']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Validate file extension
        if not file.filename.endswith(('.pt', '.onnx', '.engine')):
            return jsonify({"error": "Invalid file type. Only .pt, .onnx, .engine files allowed"}), 400
        
        # Save file
        filename = file.filename
        filepath = os.path.join(MODELS_DIR, filename)
        file.save(filepath)
        
        # Clear model cache when new model is uploaded
        clear_model_cache()
        
        # Get model info
        info = get_model_info(filepath)
        
        return jsonify({"message": "Model uploaded successfully", "model": info})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/models/<model_name>', methods=['DELETE'])
def delete_model(model_name):
    """Delete a model"""
    try:
        model_path = os.path.join(MODELS_DIR, model_name)
        
        if not os.path.exists(model_path):
            return jsonify({"error": "Model not found"}), 404
        
        # Remove from loaded models cache
        if model_path in loaded_models:
            del loaded_models[model_path]
            gc.collect()
        
        os.remove(model_path)
        
        return jsonify({"message": "Model deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/models/<model_name>', methods=['GET'])
def download_model(model_name):
    """Download a model"""
    try:
        model_path = os.path.join(MODELS_DIR, model_name)
        
        if not os.path.exists(model_path):
            return jsonify({"error": "Model not found"}), 404
        
        return send_file(model_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/inference', methods=['POST'])
def run_inference_api():
    """Run inference on image or RTSP stream"""
    try:
        print(f"Inference request received, memory: {get_memory_usage():.1f} MB")
        
        # Get model name
        model_name = request.form.get('model') or request.json.get('model')
        if not model_name:
            return jsonify({"error": "Model name required"}), 400
        
        model_path = os.path.join(MODELS_DIR, model_name)
        if not os.path.exists(model_path):
            return jsonify({"error": "Model not found"}), 404
        
        # Load model
        model = load_model(model_path)
        if model is None:
            return jsonify({"error": "Failed to load model"}), 500
        
        image = None
        error_msg = None
        
        # Handle different input types
        if 'image' in request.files:
            # File upload
            file = request.files['image']
            image_data = file.read()
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        elif request.json and 'rtsp_url' in request.json:
            # RTSP stream
            rtsp_url = request.json['rtsp_url']
            image, error_msg = fetch_rtsp_frame(rtsp_url)
        elif request.form.get('rtsp_url'):
            # RTSP from form
            rtsp_url = request.form.get('rtsp_url')
            image, error_msg = fetch_rtsp_frame(rtsp_url)
        else:
            return jsonify({"error": "No image or RTSP URL provided"}), 400
        
        if image is None:
            return jsonify({"error": error_msg or "Failed to get image"}), 400
        
        # Run inference
        annotated_image, detections, error_msg = run_inference(model, image)
        
        if annotated_image is None:
            return jsonify({"error": error_msg or "Inference failed"}), 500
        
        # Save result image
        result_id = str(uuid.uuid4())
        result_filename = f"result_{result_id}.jpg"
        result_path = os.path.join(RESULTS_DIR, result_filename)
        cv2.imwrite(result_path, annotated_image)
        
        # Convert image to base64 for response
        _, buffer = cv2.imencode('.jpg', annotated_image)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Save detection JSON
        json_filename = f"result_{result_id}.json"
        json_path = os.path.join(RESULTS_DIR, json_filename)
        with open(json_path, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "model": model_name,
                "detections": detections,
                "memory_usage_mb": get_memory_usage()
            }, f, indent=2)
        
        return jsonify({
            "result_id": result_id,
            "image_base64": img_base64,
            "detections": detections,
            "image_url": f"/api/results/{result_filename}",
            "json_url": f"/api/results/{json_filename}",
            "memory_usage_mb": round(get_memory_usage(), 1)
        })
        
    except Exception as e:
        print(f"API error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/results/<filename>')
def get_result(filename):
    """Get result file"""
    try:
        return send_from_directory(RESULTS_DIR, filename)
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@app.route('/api/status')
def get_status():
    """Get system status"""
    return jsonify({
        "memory_usage_mb": round(get_memory_usage(), 1),
        "loaded_models": len(loaded_models),
        "torch_threads": torch.get_num_threads()
    })

# Serve React frontend
@app.route('/')
@app.route('/ui')
@app.route('/ui/<path:path>')
def serve_frontend(path=''):
    """Serve React frontend"""
    try:
        if path and os.path.exists(os.path.join('/app/frontend/build', path)):
            return send_from_directory('/app/frontend/build', path)
        else:
            return send_from_directory('/app/frontend/build', 'index.html')
    except Exception as e:
        return f"Frontend not available: {e}", 404

if __name__ == '__main__':
    print(f"Starting YOLO API for N150, initial memory: {get_memory_usage():.1f} MB")
    app.run(host='0.0.0.0', port=5000, debug=False)
