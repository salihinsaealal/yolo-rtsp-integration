from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_component import EntityComponent
from .camera_fetcher import fetch_single_frame, fetch_frame_sequence, load_manual_image, set_external_api_url
from .entities import DetectionImageEntity, ObjectStatusEntity
import os
import json
from datetime import datetime
import logging
import voluptuous as vol

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
        """Service handler: send image to external YOLO API, get results, update entities.
        # Handler servis: hantar gambar ke API YOLO luaran, dapat hasil, update entiti
        """
        _LOGGER.info("YOLO inference service called")
        
        # Get params from service call
        model_name = call.data.get("model_name", "yolov8n.pt")
        fetch_mode = call.data.get("fetch_mode", "manual")
        image_path = call.data.get("image_path")  # Fixed parameter name
        camera_url = call.data.get("camera_url")
        
        # Get API URL from integration config
        config_entries = hass.config_entries.async_entries("yolo_rtsp_integration")
        if not config_entries:
            _LOGGER.error("No YOLO integration config found")
            return
        
        api_url = config_entries[0].data.get("external_api_url")
        if not api_url:
            _LOGGER.error("No YOLO API URL configured")
            return
            
        _LOGGER.info(f"Using API URL: {api_url}, Model: {model_name}, Mode: {fetch_mode}")
        
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                # Prepare the request based on mode
                if fetch_mode == "manual" and image_path:
                    # Manual image upload mode
                    if not os.path.exists(image_path):
                        _LOGGER.error(f"Image file not found: {image_path}")
                        return
                        
                    # Read and send image file to API (async)
                    def read_image_file():
                        with open(image_path, 'rb') as f:
                            return f.read()
                    
                    image_data = await hass.async_add_executor_job(read_image_file)
                    
                    data = aiohttp.FormData()
                    data.add_field('image', image_data, filename='image.jpg', content_type='image/jpeg')
                    data.add_field('model', model_name)
                    
                    async with session.post(f"{api_url}/api/inference", data=data, timeout=60) as resp:
                        if resp.status != 200:
                            _LOGGER.error(f"API request failed: {resp.status}")
                            return
                        result = await resp.json()
                        
                elif fetch_mode in ["single", "sequence"] and camera_url:
                    # RTSP camera mode
                    payload = {
                        "rtsp_url": camera_url,
                        "model": model_name
                    }
                    
                    async with session.post(f"{api_url}/api/inference", json=payload, timeout=60) as resp:
                        if resp.status != 200:
                            _LOGGER.error(f"API request failed: {resp.status}")
                            return
                        result = await resp.json()
                else:
                    _LOGGER.error(f"Invalid mode or missing parameters. Mode: {fetch_mode}, Image: {image_path}, Camera: {camera_url}")
                    return
                    
                # Process API response
                if "error" in result:
                    _LOGGER.error(f"API error: {result['error']}")
                    return
                    
                detections = result.get("detections", [])
                detection_count = len(detections)
                
                _LOGGER.info(f"Received {detection_count} detections from API")
                
                # Save results and create entities
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # Save detection JSON (async)
                json_filename = f"detection_{timestamp}.json"
                json_path = os.path.join(MEDIA_DIR, json_filename)
                
                def write_json_file():
                    with open(json_path, "w") as jf:
                        json.dump(result, jf, indent=2)
                
                await hass.async_add_executor_job(write_json_file)
                
                # Download and save annotated image if provided (async)
                img_path = None
                if "annotated_image_url" in result:
                    async with session.get(f"{api_url}{result['annotated_image_url']}") as img_resp:
                        if img_resp.status == 200:
                            img_filename = f"detection_{timestamp}.jpg"
                            img_path = os.path.join(MEDIA_DIR, img_filename)
                            
                            def write_image_file():
                                with open(img_path, "wb") as img_file:
                                    img_file.write(img_data)
                            
                            img_data = await img_resp.read()
                            await hass.async_add_executor_job(write_image_file)
                            _LOGGER.info(f"Saved annotated image: {img_path}")
                
                # Create/update entities
                detection_count_entity = DetectionImageEntity("YOLO Detection Count", str(detection_count))
                if img_path:
                    detection_image_entity = DetectionImageEntity("YOLO Detection Image", img_path)
                    await component.async_add_entities([detection_image_entity], update_before_add=True)
                    
                object_status_entity = ObjectStatusEntity("YOLO Object Status", detections)
                await component.async_add_entities([detection_count_entity, object_status_entity], update_before_add=True)
                
                _LOGGER.info(f"Detection complete: {detection_count} objects found")
                _LOGGER.info(f"Results saved: {json_path}")
                if img_path:
                    _LOGGER.info(f"Image saved: {img_path}")
                    
        except Exception as e:
            _LOGGER.error(f"Error during inference: {str(e)}")
            import traceback
            _LOGGER.error(traceback.format_exc())

    # Service schema for UI testing
    service_schema = vol.Schema({
        vol.Optional("model_name", default="yolov8n.pt"): str,
        vol.Optional("camera_url"): str,
        vol.Optional("image_path"): str,
        vol.Optional("fetch_mode", default="manual"): vol.In(["single", "sequence", "manual"]),
        vol.Optional("sequence_length", default=5): int,
        vol.Optional("frame_interval", default=1): int,
    })
    
    # Register the service
    hass.services.async_register(
        "yolo_rtsp_integration",
        "run_inference",
        handle_process,
        schema=service_schema
    )
    print("Service yolo_rtsp_integration.run_inference registered. | Servis didaftarkan.")
