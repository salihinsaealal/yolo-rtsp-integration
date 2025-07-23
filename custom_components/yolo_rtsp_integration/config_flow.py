import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_CAMERA_URL, CONF_MODEL_PATH, CONF_FETCH_MODE, CONF_SEQUENCE_LENGTH, CONF_FRAME_INTERVAL

FETCH_MODES = ["single", "sequence", "manual"]

CONF_API_URL = "external_api_url"

FIELD_LABELS = {
    CONF_API_URL: "YOLO API URL (e.g. http://192.168.8.238:5000)",
    CONF_CAMERA_URL: "RTSP Camera Stream URL (e.g. rtsp://user:pass@ip:port/stream)",
}
FIELD_HELP = {
    CONF_API_URL: "Enter the URL of your YOLO API server. This is the address where the inference API and web UI are running.",
    CONF_CAMERA_URL: "Enter the RTSP stream URL for your camera. Only needed if not using manual image mode.",
}

class YoloRtspConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for YOLO RTSP Integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Require external API URL
            if not user_input.get(CONF_API_URL):
                errors[CONF_API_URL] = "YOLO API URL is required."
                return self.async_show_form(
                    step_id="user",
                    data_schema=self._get_schema(user_input.get(CONF_FETCH_MODE)),
                    description_placeholders=FIELD_HELP,
                    errors=errors,
                )
            # Only require camera_url if not manual mode
            if user_input.get(CONF_FETCH_MODE) != "manual" and not user_input.get(CONF_CAMERA_URL):
                errors[CONF_CAMERA_URL] = "RTSP Camera Stream URL is required unless using manual mode."
                return self.async_show_form(
                    step_id="user",
                    data_schema=self._get_schema(user_input.get(CONF_FETCH_MODE)),
                    description_placeholders=FIELD_HELP,
                    errors=errors,
                )
            # Optionally: Validate API URL is reachable
            import aiohttp
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(user_input[CONF_API_URL] + "/api/models", timeout=5) as resp:
                        if resp.status != 200:
                            errors[CONF_API_URL] = "YOLO API not reachable or invalid response."
                            return self.async_show_form(
                                step_id="user",
                                data_schema=self._get_schema(user_input.get(CONF_FETCH_MODE)),
                                description_placeholders=FIELD_HELP,
                                errors=errors,
                            )
            except Exception:
                errors[CONF_API_URL] = "Could not connect to YOLO API URL. Please check the address and try again."
                return self.async_show_form(
                    step_id="user",
                    data_schema=self._get_schema(user_input.get(CONF_FETCH_MODE)),
                    description_placeholders=FIELD_HELP,
                    errors=errors,
                )
            return self.async_create_entry(title="YOLO RTSP Integration", data=user_input)
        return self.async_show_form(
            step_id="user",
            data_schema=self._get_schema(None),
            description_placeholders=FIELD_HELP,
            errors=errors,
        )

    @staticmethod
    def _get_schema(fetch_mode=None):
        # Only require camera_url if not manual
        import voluptuous as vol
        from .const import CONF_CAMERA_URL
        if fetch_mode == "manual":
            return vol.Schema({
                vol.Required(CONF_API_URL, description=FIELD_LABELS[CONF_API_URL]): str,
                vol.Required(CONF_FETCH_MODE, default="manual"): vol.In(FETCH_MODES),
                vol.Optional(CONF_SEQUENCE_LENGTH, default=5): int,
                vol.Optional(CONF_FRAME_INTERVAL, default=1): int,
            })
        else:
            return vol.Schema({
                vol.Required(CONF_API_URL, description=FIELD_LABELS[CONF_API_URL]): str,
                vol.Required(CONF_CAMERA_URL, description=FIELD_LABELS[CONF_CAMERA_URL]): str,
                vol.Required(CONF_FETCH_MODE, default="single"): vol.In(FETCH_MODES),
                vol.Optional(CONF_SEQUENCE_LENGTH, default=5): int,
                vol.Optional(CONF_FRAME_INTERVAL, default=1): int,
            })

    @staticmethod
    def _get_schema(fetch_mode=None):
        # Only require camera_url if not manual
        if fetch_mode == "manual":
            return vol.Schema({
                vol.Required(CONF_FETCH_MODE, default="manual"): vol.In(FETCH_MODES),
                vol.Optional(CONF_SEQUENCE_LENGTH, default=5): int,
                vol.Optional(CONF_FRAME_INTERVAL, default=1): int,
            })
        else:
            return vol.Schema({
                vol.Required(CONF_CAMERA_URL): str,
                vol.Required(CONF_FETCH_MODE, default="single"): vol.In(FETCH_MODES),
                vol.Optional(CONF_SEQUENCE_LENGTH, default=5): int,
                vol.Optional(CONF_FRAME_INTERVAL, default=1): int,
            })
