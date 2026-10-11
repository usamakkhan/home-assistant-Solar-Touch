"""The Solar Touch integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError

from .const import DOMAIN, CONF_DEVICE_LABEL, CONF_GOODS_ID, CONF_SOURCE, SOURCE_CLOUD, SOURCE_DIRECT
from .direct_coordinator import DirectSolarMaxCoordinator
from .device_naming import device_labels

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Solar Touch from a config entry."""
    # Persist a short device name once so additional inverters cannot renumber it.
    label = device_labels(hass.config_entries.async_entries(DOMAIN))[entry.entry_id]
    title = entry.title
    if title in ("Cloud Inverter Direct", "Solar Touch Direct"):
        title = f"{label} (LAN)"
    elif title in {
        f"Cloud Inverter ({entry.data.get('model', 'Unknown')})",
        f"Solar Touch ({entry.data.get('model', 'Unknown')})",
    }:
        title = f"{label} ({entry.data.get('model', 'Unknown')})"
    updates = {}
    if entry.data.get(CONF_DEVICE_LABEL) != label:
        updates["data"] = {**entry.data, CONF_DEVICE_LABEL: label}
    if title != entry.title:
        updates["title"] = title
    if updates:
        hass.config_entries.async_update_entry(entry, **updates)
    hass.data.setdefault(DOMAIN, {})
    
    # Keep only the selected inverter reference in integration state.
    source = entry.data.get(CONF_SOURCE, SOURCE_CLOUD)
    if source == SOURCE_DIRECT:
        coordinator = DirectSolarMaxCoordinator(hass, entry)
        await coordinator.async_config_entry_first_refresh()
        entry.runtime_data = coordinator
    elif source != SOURCE_CLOUD:
        raise ConfigEntryError(
            "This old local analyzer entry needs to be removed and re-added "
            "using Get Data Locally using Inverter IP"
        )
    hass.data[DOMAIN][entry.entry_id] = {"goods_id": entry.data.get(CONF_GOODS_ID)}
    
    _LOGGER.info("Setting up Solar Touch %s integration", source)
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        if entry.data.get(CONF_SOURCE, SOURCE_CLOUD) == SOURCE_CLOUD:
            api = getattr(getattr(entry, "runtime_data", None), "api", None)
            if api is not None:
                await api.close()
        hass.data[DOMAIN].pop(entry.entry_id)
        _LOGGER.info("Unloaded Solar Touch integration")
    
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
