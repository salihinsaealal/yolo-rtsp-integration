# YOLO RTSP Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![Open in HACS](https://img.shields.io/badge/-Add%20with%20HACS-41BDF5?logo=home-assistant&logoColor=white&style=flat-square)](https://my.home-assistant.io/redirect/hacs_repository/?owner=salihinsaealal&repository=yolo-rtsp-integration&category=integration)
[![Open in Home Assistant](https://img.shields.io/badge/-Open%20in%20Home%20Assistant-41BDF5?logo=home-assistant&logoColor=white&style=flat-square)](https://my.home-assistant.io/redirect/integration/?domain=yolo_rtsp_integration)
[![GitHub Repo](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white&style=flat-square)](https://github.com/salihinsaealal/yolo-rtsp-integration)

A Home Assistant custom integration for YOLO object detection on RTSP camera streams and manual images. This integration offloads all heavy processing to an external YOLOv8 inference API, keeping your Home Assistant installation lightweight and responsive.

## Architecture

```
┌─────────────────┐    HTTP API     ┌──────────────────────┐
│  Home Assistant │ ──────────────► │   YOLO API Platform  │
│   Integration   │                 │  (Docker Container)  │
│                 │ ◄────────────── │                      │
└─────────────────┘   JSON Results  └──────────────────────┘
        │                                       │
        │                                       │
        ▼                                       ▼
┌─────────────────┐                 ┌──────────────────────┐
│ RTSP Camera     │                 │ • Model Management   │
│ Entity/Manual   │                 │ • YOLOv8 Inference   │
│ Image Upload    │                 │ • React Web UI       │
└─────────────────┘                 │ • Result Storage     │
                                    └──────────────────────┘
```

## Features

### 🏠 Home Assistant Integration
- **Custom Component**: HACS-compatible installation
- **Entity Creation**: Detection results as HA entities with attributes
- **Service Calls**: Trigger inference via HA automations
- **Media Storage**: Detection images saved to HA media folder
- **JSON Export**: Detailed detection data for further processing

### 🎯 YOLO Detection
- **Multiple Input Sources**: RTSP cameras or manual image upload
- **Model Flexibility**: Upload and manage your own YOLOv8 models
- **Real-time Processing**: Fast inference with annotated result images
- **Detection Analytics**: Confidence scores, bounding boxes, object areas

### 🚀 External API Platform
- **Lightweight HA**: No heavy dependencies in Home Assistant
- **Scalable**: Run on separate hardware (mini PC, NAS, server)
- **Web Interface**: Beautiful React UI for model management and testing
- **Hardware Optimized**: CPU-only inference, works on Intel N150 mini PCs

## Quick Start

### 1. Deploy the YOLO API Platform

The inference processing runs in a separate Docker container with a web UI:

```bash
# Clone the repository
git clone https://github.com/salihinsaealal/yolo-rtsp-integration.git
cd yolo-rtsp-integration/yolo-api

# Build and run the API platform
docker-compose up -d

# Access the web UI
open http://localhost:5000/ui
```

**📖 For detailed setup instructions, see [YOLO API Documentation](yolo-api/README.md)**

### 2. Install Home Assistant Integration

#### Via HACS (Recommended)
1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click "Explore & Download Repositories"
4. Search for "YOLO RTSP Integration"
5. Download and restart Home Assistant

#### Manual Installation
1. Copy `custom_components/yolo_rtsp_integration` to your HA config directory
2. Restart Home Assistant
3. Go to Settings → Integrations → Add Integration
4. Search for "YOLO RTSP Integration"

### 3. Configure the Integration

1. **Add Integration**: Settings → Integrations → Add "YOLO RTSP Integration"
2. **API URL**: Enter your YOLO API URL (e.g., `http://192.168.1.100:5000`)
3. **Input Mode**: Choose RTSP camera or manual image upload
4. **RTSP URL**: If using RTSP mode, enter your camera stream URL

### 4. Upload YOLO Models

1. **Access Web UI**: Visit your YOLO API URL (e.g., `http://192.168.1.100:5000/ui`)
2. **Model Manager**: Upload your YOLOv8 model files (.pt, .onnx, .engine)
3. **Test Inference**: Use the Inference Tester to verify models work correctly

### 5. Use in Home Assistant

#### Service Calls

The integration provides the `yolo_rtsp_integration.run_inference` service for triggering object detection:

**Manual Image Mode (Default)**:
```yaml
service: yolo_rtsp_integration.run_inference
data:
  model_name: "best.pt"  # Your uploaded model
  image_path: "/config/www/test_image.jpg"
  fetch_mode: "manual"
```

**RTSP Camera Mode**:
```yaml
service: yolo_rtsp_integration.run_inference
data:
  model_name: "yolov8n.pt"
  camera_url: "rtsp://admin:password@192.168.1.100:554/stream"
  fetch_mode: "single"
```

**Service Parameters**:
- `model_name`: Name of the model file uploaded to the API (default: "yolov8n.pt")
- `image_path`: Path to image file for manual mode
- `camera_url`: RTSP URL for camera mode
- `fetch_mode`: "manual", "single", or "sequence" (default: "manual")
- `sequence_length`: Number of frames for sequence mode (default: 5)
- `frame_interval`: Interval between frames in seconds (default: 1)

#### Created Entities

After running inference, the integration creates the following Home Assistant entities:

**Detection Count Sensor**:
- `sensor.yolo_detection_count`: Number of objects detected
- State: Integer count (e.g., "3")
- Updated after each inference run

**Detection Image Sensor**:
- `sensor.yolo_detection_image`: Path to annotated image
- State: File path (e.g., "/config/media/yolo_rtsp_integration/detection_20250123_181500.jpg")
- Contains the annotated image with bounding boxes

**Object Status Sensor**:
- `sensor.yolo_object_status`: Detailed detection data
- State: JSON array of detected objects
- Attributes include: class, confidence, bounding box, area

#### Saved Results

Each inference run saves results to `/config/media/yolo_rtsp_integration/`:

- **JSON Results**: `detection_YYYYMMDD_HHMMSS.json` - Complete detection data
- **Annotated Images**: `detection_YYYYMMDD_HHMMSS.jpg` - Image with bounding boxes
- **Automatic Cleanup**: Configurable retention policy via API platform

#### Automation Example
```yaml
automation:
  - alias: "Detect Objects on Motion"
    trigger:
      - platform: state
        entity_id: binary_sensor.front_door_motion
        to: "on"
    action:
      - service: yolo_rtsp_integration.run_inference
        data:
          model_name: "yolov8n.pt"
      - delay: "00:00:02"
      - service: notify.mobile_app
        data:
          message: "{{ states('sensor.yolo_detection_count') }} objects detected"
          data:
            image: "{{ state_attr('sensor.yolo_detection_image', 'file_path') }}"
```

## Entities Created

The integration creates the following entities:

- **`sensor.yolo_detection_count`**: Number of objects detected
- **`sensor.yolo_detection_image`**: Detection result image with annotations
- **`sensor.yolo_object_status`**: Detailed detection data (JSON)

## Hardware Requirements

### Home Assistant
- **Minimal**: Standard HA installation requirements
- **No additional dependencies**: All processing is external

### YOLO API Platform
- **Minimum**: 2GB RAM, 2 CPU cores (Intel N150 tested)
- **Recommended**: 4GB RAM for larger models
- **Storage**: 5GB+ for Docker images and models
- **Network**: HTTP access between HA and API platform

## Supported Models

- **YOLOv8n**: Fastest, best for low-power hardware
- **YOLOv8s**: Good balance of speed and accuracy
- **YOLOv8m/l/x**: Higher accuracy, requires more resources
- **Custom Models**: Upload your own trained YOLOv8 models
- **Formats**: .pt (PyTorch), .onnx, .engine files

## Configuration Options

### Integration Config
- **API URL**: YOLO API platform endpoint
- **Input Mode**: RTSP camera or manual image upload
- **RTSP URL**: Camera stream URL (if using RTSP mode)
- **Timeout**: API request timeout (default: 60s)

### API Platform Config
- **Models**: Upload/manage via web UI
- **Memory Management**: Automatic for low-power hardware
- **Thread Limiting**: Optimized for CPU inference
- **Result Storage**: Configurable retention policy

## Troubleshooting

### Common Issues

**Integration not loading:**
- Check API URL is accessible from Home Assistant
- Verify YOLO API platform is running: `docker-compose ps`
- Check HA logs: Settings → System → Logs

**Inference failing:**
- Test models via YOLO API web UI first
- Check model format (.pt, .onnx, .engine)
- Monitor API platform logs: `docker-compose logs -f yolo-api`

**RTSP connection issues:**
- Test RTSP URL in VLC media player
- Check network connectivity and firewall
- Verify RTSP credentials and format

**Performance issues:**
- Use smaller models (YOLOv8n) for faster inference
- Monitor system resources on API platform
- Consider image resizing for large inputs

### Getting Help

1. **Check Logs**: Both HA and API platform logs
2. **Test API**: Use the web UI to isolate issues
3. **Hardware Stats**: Monitor CPU/memory usage
4. **GitHub Issues**: Report bugs with detailed information

## Development

### Project Structure
```
├── custom_components/yolo_rtsp_integration/  # Home Assistant integration
│   ├── __init__.py                          # Integration setup
│   ├── config_flow.py                       # Configuration UI
│   ├── entities.py                          # HA entity definitions
│   ├── services.py                          # Service handlers
│   └── manifest.json                        # Integration metadata
└── yolo-api/                                # External API platform
    ├── backend/                             # Flask API server
    ├── frontend/                            # React web UI
    ├── Dockerfile                           # Container build
    └── docker-compose.yml                   # Deployment config
```

### Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Test thoroughly**: Both HA integration and API platform
4. **Submit pull request**: With detailed description

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Ultralytics**: YOLOv8 implementation
- **Home Assistant**: Platform and community
- **React + Material-UI**: Beautiful web interface
- **Docker**: Containerization and deployment
