import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_CAMERA_URL, CONF_MODEL_PATH, CONF_FETCH_MODE, CONF_SEQUENCE_LENGTH, CONF_FRAME_INTERVAL

FETCH_MODES = ["single", "sequence", "manual"]

class YoloRtspConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for YOLO RTSP Integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Validation can be added here
            return self.async_create_entry(title="YOLO RTSP Integration", data=user_input)
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_CAMERA_URL): str,
                vol.Required(CONF_FETCH_MODE, default="single"): vol.In(FETCH_MODES),
                vol.Optional(CONF_SEQUENCE_LENGTH, default=5): int,
                vol.Optional(CONF_FRAME_INTERVAL, default=1): int,
            }),
            errors=errors,
        )
