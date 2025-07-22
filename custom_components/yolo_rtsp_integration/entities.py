from homeassistant.helpers.entity import Entity
from homeassistant.const import ATTR_ATTRIBUTION
import os
import json

class DetectionImageEntity(Entity):
    """Entity to store and expose the latest detection image.
# Kelas ni simpan dan tunjuk gambar hasil pengesanan terkini."""
    def __init__(self, name: str, image_path: str):
        self._name = name
        self._image_path = image_path
        self._attr = None

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._image_path  # Lokasi gambar (Image path)

    @property
    def extra_state_attributes(self):
        return {
            ATTR_ATTRIBUTION: "YOLO RTSP Integration",  # Sumber integrasi ni (Integration source)
            "image_path": self._image_path,  # Lokasi gambar (Image path)
        }

    def update_image(self, image_path: str):
        self._image_path = image_path  # Update lokasi gambar baru
        self.schedule_update_ha_state()  # Bagi Home Assistant tahu dah update

class ObjectStatusEntity(Entity):
    """Entity to store and expose detection JSON as attributes.
# Kelas ni simpan dan tunjuk hasil pengesanan dalam bentuk JSON."""
    def __init__(self, name: str, detection_json: list):
        self._name = name
        self._detection_json = detection_json

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return len(self._detection_json)  # Bilangan objek dikesan (Number of detected objects)

    @property
    def extra_state_attributes(self):
        # Flatten detection JSON for attributes
        # Rata hasil pengesanan untuk dijadikan atribut
        attrs = {f"object_{i+1}": obj for i, obj in enumerate(self._detection_json)}
        attrs[ATTR_ATTRIBUTION] = "YOLO RTSP Integration"  # Sumber
        attrs["json"] = json.dumps(self._detection_json)  # Simpan sebagai JSON
        return attrs

    def update_detection(self, detection_json: list):
        self._detection_json = detection_json  # Update hasil pengesanan baru
        self.schedule_update_ha_state()  # Bagi Home Assistant tahu dah update
