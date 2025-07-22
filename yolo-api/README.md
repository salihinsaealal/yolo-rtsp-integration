# YOLO Inference Platform

A beautiful, modern web platform for YOLO model management and inference testing. **Optimized for low-power hardware** like Intel N150 mini PCs with 2GB RAM. Built with Flask backend, React frontend, and CPU-only PyTorch for maximum compatibility.

## Features

### 🎯 Model Management
- **Drag & Drop Upload**: Easy model upload with progress tracking
- **Model Library**: View all uploaded models with metadata (size, date)
- **Quick Actions**: Download, delete, and manage your YOLO models
- **Format Support**: .pt, .onnx, .engine model files
- **Memory Monitoring**: Real-time memory usage tracking

### 🔍 Inference Testing
- **Dual Input Modes**: Upload images or connect to RTSP streams
- **Real-time Results**: View annotated images with detection overlays
- **Detection Analytics**: Detailed object detection results with confidence scores
- **Export Options**: Download result images and JSON data
- **Auto Image Resizing**: Optimizes large images for low-memory systems

### 🎨 Modern UI
- **Dark Theme**: Beautiful, eye-friendly dark interface
- **Smooth Animations**: Framer Motion powered transitions
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Material Design**: Clean, professional Material-UI components

### ⚡ Hardware Optimizations
- **CPU-Only PyTorch**: No CUDA dependencies, works on any hardware
- **Memory Management**: Aggressive garbage collection and model caching
- **Thread Limiting**: Optimized for low-power CPUs (2 threads)
- **Image Preprocessing**: Auto-resize large images to reduce memory usage

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- **Minimum**: 2GB RAM, 2 CPU cores (Intel N150 tested and working)
- **Recommended**: 4GB RAM for larger models

### 1. Clone and Build
```bash
git clone https://github.com/salihinsaealal/yolo-rtsp-integration.git
cd yolo-rtsp-integration/yolo-api

# Build the optimized Docker image
docker-compose build
```

### 2. Run the Platform
```bash
# Start the service
docker-compose up -d

# Check status
docker-compose ps

# Monitor logs
docker-compose logs -f yolo-api
```

### 3. Access the Platform
- **Web UI**: http://localhost:5000/ui
- **API**: http://localhost:5000/api
- **Status**: http://localhost:5000/api/status (memory usage)

### 4. Upload Your Models
1. Navigate to the Model Manager tab
2. Drag and drop your YOLO model files (.pt, .onnx, .engine)
3. Wait for upload completion
4. **Tip**: Use YOLOv8n or YOLOv8s for better performance on low-power hardware

### 5. Test Inference
1. Go to the Inference Tester tab
2. Select your uploaded model
3. Choose input method:
   - **Image Upload**: Drag and drop test images
   - **RTSP Stream**: Enter your camera's RTSP URL
4. Click "Run Inference" and view results
5. **Monitor memory usage** in the results JSON

## API Endpoints

### Models
- `GET /api/models` - List all models
- `POST /api/models` - Upload new model
- `DELETE /api/models/<name>` - Delete model
- `GET /api/models/<name>` - Download model

### Inference
- `POST /api/inference` - Run inference
  - Form data: `model`, `image` (file) OR `rtsp_url`
  - Returns: annotated image (base64), detections JSON, memory usage

### System
- `GET /api/status` - System status (memory, loaded models, threads)
- `GET /api/results/<filename>` - Download result files

## Home Assistant Integration

This platform is designed to work seamlessly with the YOLO RTSP Home Assistant custom integration:

1. **Set API URL**: Configure your HA integration to point to `http://<your-server-ip>:5000`
2. **Upload Models**: Use the web UI to manage your YOLO models
3. **Test First**: Verify your models work correctly using the inference tester
4. **Automate**: Let Home Assistant call the API for automated detection

See the [main README](../README.md) for Home Assistant integration details.

## Hardware Compatibility

### Tested Hardware
- ✅ **Intel N150 Mini PC** (2GB RAM) - Primary target
- ✅ **Raspberry Pi 4** (4GB RAM)
- ✅ **Standard x86_64** systems
- ✅ **ARM64** systems (Apple Silicon, etc.)

### Performance Guidelines
- **2GB RAM**: Use YOLOv8n models, single model loading
- **4GB+ RAM**: Use YOLOv8s/m models, multiple model caching
- **CPU-only**: Inference takes 2-10 seconds depending on image size and model

## Configuration

### Environment Variables (docker-compose.yml)
```yaml
environment:
  - PYTHONUNBUFFERED=1
  - FLASK_APP=app.py
  # Hardware optimizations
  - OMP_NUM_THREADS=2
  - MKL_NUM_THREADS=2
  - TORCH_NUM_THREADS=2
```

### Volume Mounts
- `./data/models`: Persistent model storage
- `./data/uploads`: Temporary upload storage  
- `./data/results`: Inference result storage

### Memory Management
- **Model Caching**: Limited to 1 model for 2GB systems
- **Garbage Collection**: Automatic after each inference
- **Image Resizing**: Max 640px to reduce memory usage

## Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend Development
```bash
cd frontend
npm install
npm start
```

### Architecture
- **Backend**: Flask + CPU-only PyTorch + Ultralytics YOLO
- **Frontend**: React + Material-UI + Framer Motion
- **Deployment**: Multi-stage Docker build
- **Optimization**: Memory management, thread limiting, image preprocessing

## Troubleshooting

### Common Issues

**"Could not create a primitive" error:**
- This was fixed in the optimized version with CPU-only PyTorch
- Ensure you're using the latest Docker image

**Models not loading:**
- Check file format (.pt, .onnx, .engine)
- Verify sufficient disk space
- Check memory usage with `/api/status`

**Out of memory errors:**
- Use smaller YOLO models (YOLOv8n instead of YOLOv8l)
- Reduce input image size
- Monitor memory with `docker stats`

**RTSP connection failed:**
- Test RTSP URL in VLC first
- Check network connectivity
- Verify RTSP credentials

**Slow inference:**
- Expected on CPU-only systems (2-10 seconds)
- Use smaller models for faster inference
- Consider image resizing

### Performance Monitoring
```bash
# Monitor container resources
docker stats yolo-inference-platform

# Check memory usage via API
curl http://localhost:5000/api/status

# View detailed logs
docker-compose logs -f yolo-api
```

## Optimization Tips

### For Low-Power Hardware
1. **Use YOLOv8n models** (smallest, fastest)
2. **Limit concurrent requests** (single-threaded inference)
3. **Monitor memory usage** regularly
4. **Use smaller input images** when possible
5. **Clean up old results** periodically

### Model Selection
- **YOLOv8n**: Best for N150, fastest inference
- **YOLOv8s**: Good balance, requires 3GB+ RAM
- **YOLOv8m/l/x**: High accuracy, requires 4GB+ RAM

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review container logs: `docker-compose logs yolo-api`
3. Check system resources: `docker stats`
4. Monitor memory usage: `curl http://localhost:5000/api/status`
5. Open an issue on GitHub with:
   - Hardware specifications
   - Model size and type
   - Error logs
   - Memory usage stats

## License

MIT License - see LICENSE file for details.
