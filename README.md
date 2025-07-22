# YOLO RTSP Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![Open in HACS](https://img.shields.io/badge/-Add%20with%20HACS-41BDF5?logo=home-assistant&logoColor=white&style=flat-square)](https://my.home-assistant.io/redirect/hacs_repository/?owner=salihinsaealal&repository=yolo-rtsp-integration&category=integration)
[![Open in Home Assistant](https://img.shields.io/badge/-Open%20in%20Home%20Assistant-41BDF5?logo=home-assistant&logoColor=white&style=flat-square)](https://my.home-assistant.io/redirect/integration/?domain=yolo_rtsp_integration)
[![GitHub Repo](https://img.shields.io/badge/-GitHub-181717?logo=github&logoColor=white&style=flat-square)](https://github.com/salihinsaealal/yolo-rtsp-integration)
[![Buy Me a Coffee](https://img.shields.io/badge/-Buy%20me%20a%20coffee-FFDD00?logo=buy-me-a-coffee&logoColor=black&style=flat-square)](https://coff.ee/salihin)

## Overview

This custom integration for Home Assistant lets you fetch images from any RTSP camera or manual upload, run YOLO object detection (YOLOv5/YOLOv8), and save the results as Home Assistant entities and files. Designed for easy model management, flexible image input, and robust output handling.

## Features
- Fetch images from RTSP camera (single or sequence)
- Manual image upload for testing
- Upload or select YOLO models (multiple formats supported)
- Run detection via Home Assistant service
- Save detection images and JSON results
- Entities for detection image and object status

## Installation
1. Copy the `yolo_rtsp_integration` folder to your Home Assistant `custom_components` directory, or add this repository to HACS as a custom integration.
2. Restart Home Assistant.
3. Configure the integration via the UI.

## Usage

### Service: `yolo_rtsp_integration.process`
Trigger detection using the Home Assistant service. Example fields:

```
camera_url: rtsp://your_camera_url
model_path: /config/custom_components/yolo_rtsp_integration/models/your_model.pt
fetch_mode: single    # or sequence or manual
sequence_length: 5    # (if sequence mode)
frame_interval: 1     # (if sequence mode)
manual_image: /config/path_to_image.jpg  # (if manual mode)
```

### Output
- Detection images and JSON files are saved in `media/yolo_rtsp_integration/`.
- Entities are created/updated for each detection:
  - Detection Image (shows path to latest detection image)
  - Object Status (attributes contain detection results)

## Model Management
- Upload YOLO models via the UI or place them in the `models` folder under the integration directory.
- Supported formats: `.pt`, `.onnx` (YOLOv5, YOLOv8, etc.)

## Example Automation
You can trigger the service from an automation, script, or manually from Developer Tools > Services.

## Support
If you find this integration useful, consider buying me a coffee!

[![Buy Me a Coffee](https://img.shields.io/badge/-Buy%20me%20a%20coffee-FFDD00?logo=buy-me-a-coffee&logoColor=black&style=flat-square)](https://coff.ee/salihin)

---

For issues or feature requests, please open an issue on GitHub.
