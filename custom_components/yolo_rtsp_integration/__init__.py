"""
YOLO RTSP Integration - Home Assistant Custom Component
"""

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from .const import DOMAIN

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the integration from configuration.yaml (not used)."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the integration from a config entry.
    # Setup integrasi dari config entry
    """
    hass.data.setdefault(DOMAIN, {})
    # Register services for inference pipeline
    # Daftar servis untuk pipeline inference
    from .services import async_setup_services
    integration_dir = entry.entry_id  # Not used for now, but can pass integration path if needed
    await async_setup_services(hass, integration_dir)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True
