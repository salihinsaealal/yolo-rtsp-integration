# YOLO Inference Platform

A beautiful, modern web platform for YOLO model management and inference testing. Built with Flask backend, React frontend, and designed for easy deployment with Docker.

## Features

### 🎯 Model Management
- **Drag & Drop Upload**: Easy model upload with progress tracking
- **Model Library**: View all uploaded models with metadata (size, date)
- **Quick Actions**: Download, delete, and manage your YOLO models
- **Format Support**: .pt, .onnx, .engine model files

### 🔍 Inference Testing
- **Dual Input Modes**: Upload images or connect to RTSP streams
- **Real-time Results**: View annotated images with detection overlays
- **Detection Analytics**: Detailed object detection results with confidence scores
- **Export Options**: Download result images and JSON data

### 🎨 Modern UI
- **Dark Theme**: Beautiful, eye-friendly dark interface
- **Smooth Animations**: Framer Motion powered transitions
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Material Design**: Clean, professional Material-UI components

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- At least 2GB RAM and 2 CPU cores recommended

### 1. Clone and Build
```bash
git clone <your-repo>
cd yolo-api

# Build the Docker image
docker-compose build
```

### 2. Run the Platform
```bash
# Start the service
docker-compose up -d

# Check status
docker-compose ps
```

### 3. Access the Platform
- **Web UI**: http://localhost:5000/ui
- **API**: http://localhost:5000/api

### 4. Upload Your Models
1. Navigate to the Model Manager tab
2. Drag and drop your YOLO model files (.pt, .onnx, .engine)
3. Wait for upload completion

### 5. Test Inference
1. Go to the Inference Tester tab
2. Select your uploaded model
3. Choose input method:
   - **Image Upload**: Drag and drop test images
   - **RTSP Stream**: Enter your camera's RTSP URL
4. Click "Run Inference" and view results

## API Endpoints

### Models
- `GET /api/models` - List all models
- `POST /api/models` - Upload new model
- `DELETE /api/models/<name>` - Delete model
- `GET /api/models/<name>` - Download model

### Inference
- `POST /api/inference` - Run inference
  - Form data: `model`, `image` (file) OR `rtsp_url`
  - Returns: annotated image (base64), detections JSON, result URLs

### Results
- `GET /api/results/<filename>` - Download result files

## Home Assistant Integration

This platform is designed to work seamlessly with the YOLO RTSP Home Assistant integration:

1. **Set API URL**: Configure your HA integration to point to `http://<your-server-ip>:5000`
2. **Upload Models**: Use the web UI to manage your YOLO models
3. **Test First**: Verify your models work correctly using the inference tester
4. **Automate**: Let Home Assistant call the API for automated detection

## Configuration

### Environment Variables
- `FLASK_APP`: Application entry point (default: app.py)
- `PYTHONUNBUFFERED`: Python output buffering (default: 1)

### Volume Mounts
- `./data/models`: Persistent model storage
- `./data/uploads`: Temporary upload storage  
- `./data/results`: Inference result storage

### Ports
- `5000`: Web UI and API access

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

## Troubleshooting

### Common Issues

**Models not loading:**
- Check file format (.pt, .onnx, .engine)
- Ensure sufficient disk space
- Verify model file is not corrupted

**RTSP connection failed:**
- Test RTSP URL in VLC or similar player first
- Check network connectivity and firewall settings
- Verify RTSP credentials and stream format

**Inference timeout:**
- Large images may take longer to process
- Check available system resources (RAM, CPU)
- Consider using smaller input images

**UI not loading:**
- Ensure Docker container is running: `docker-compose ps`
- Check container logs: `docker-compose logs yolo-api`
- Verify port 5000 is not blocked by firewall

### Performance Tips
- Use GPU-enabled Docker images for faster inference
- Optimize model size and format for your use case
- Monitor resource usage with `docker stats`

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review container logs: `docker-compose logs`
3. Open an issue on GitHub with detailed error information

## License

MIT License - see LICENSE file for details.
