from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_component import EntityComponent
from .camera_fetcher import fetch_single_frame, fetch_frame_sequence, load_manual_image, set_external_api_url
from .entities import DetectionImageEntity, ObjectStatusEntity
import os
import json
from datetime import datetime
import logging

_LOGGER = logging.getLogger(__name__)

# Folder untuk simpan gambar dan json hasil (Folder to save detection images and json)
MEDIA_DIR = "media/yolo_rtsp_integration"

async def async_setup_services(hass: HomeAssistant, integration_dir: str):
    """Register Home Assistant service to trigger inference pipeline.
    # Daftar servis Home Assistant untuk jalankan pipeline inference
    """
    if not os.path.exists(MEDIA_DIR):
        os.makedirs(MEDIA_DIR)

    component = hass.data["yolo_rtsp_integration"].setdefault("component", EntityComponent(_LOGGER, "yolo_rtsp_integration", hass))

    async def handle_process(call: ServiceCall):
        """Service handler: fetch image(s), run inference, update entities.
        # Handler servis: ambil gambar, buat inference, update entiti
        """
        # Get params from service call or config
        rtsp_url = call.data.get("camera_url")
        model_path = call.data.get("model_path")
        fetch_mode = call.data.get("fetch_mode", "single")
        sequence_length = int(call.data.get("sequence_length", 5))
        frame_interval = int(call.data.get("frame_interval", 1))
        manual_image_path = call.data.get("manual_image")
        # Fetch image(s)
        if fetch_mode == "single":
            frame = fetch_single_frame(rtsp_url)
            frames = [frame] if frame is not None else []
        elif fetch_mode == "sequence":
            frames = fetch_frame_sequence(rtsp_url, count=sequence_length, interval=frame_interval)
        elif fetch_mode == "manual":
            frame = load_manual_image(manual_image_path)
            frames = [frame] if frame is not None else []
        else:
            frames = []
        if not frames:
            print("No frames fetched. Takde gambar diambil.")
            return
        # Load model
        model = load_yolo_model(model_path)
        valid, msg = validate_yolo_model(model)
        if not valid:
            print(f"Model not valid: {msg} | Model tak valid: {msg}")
            return
        # Run inference on all frames
        for idx, frame in enumerate(frames):
            result_img, detections = run_inference(model, frame)
            # Save detection image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            img_filename = f"detect_{timestamp}_{idx+1}.jpg"
            img_path = os.path.join(MEDIA_DIR, img_filename)
            cv2.imwrite(img_path, result_img)
            # Save detection JSON
            json_filename = f"detect_{timestamp}_{idx+1}.json"
            json_path = os.path.join(MEDIA_DIR, json_filename)
            with open(json_path, "w") as jf:
                json.dump(detections, jf, indent=2)
            # Update or create entities
            img_entity = DetectionImageEntity(f"Detection Image {idx+1}", img_path)
            obj_entity = ObjectStatusEntity(f"Object Status {idx+1}", detections)
            # Register/update entities in HA
            await component.async_add_entities([img_entity, obj_entity], update_before_add=True)
            print(f"Detection image saved: {img_path} | Gambar dikesan disimpan.")
            print(f"Detection JSON saved: {json_path} | JSON hasil disimpan.")

    # Register the service
    hass.services.async_register(
        "yolo_rtsp_integration",
        "process",
        handle_process,
        schema=None
    )
    print("Service yolo_rtsp_integration.process registered. | Servis didaftarkan.")
